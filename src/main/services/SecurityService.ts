import crypto from "crypto";
import { safeStorage } from "electron";
import { ConfigService } from "./ConfigService";
import { devLog, devError } from "../logger";

export class SecurityService {
  private readonly PIN_MIN_LENGTH = 4;
  private readonly MAX_PIN_ATTEMPTS = 5;
  private readonly LOCKOUT_BASE_MS = 30000;

  constructor(private configService: ConfigService) {}

  private hashPin(pin: string): string {
    const salt = crypto.randomBytes(16).toString("hex");
    const hash = crypto.createHmac("sha256", salt).update(pin).digest("hex");
    return `${salt}:${hash}`;
  }

  private safeCompare(a: string, b: string): boolean {
    // Constant-time comparison. If lengths differ, perform a dummy compare
    // against `a` to avoid leaking length-based timing information, then
    // return false.
    const bufA = Buffer.from(a, "utf8");
    const bufB = Buffer.from(b, "utf8");
    if (bufA.length !== bufB.length) {
      try {
        crypto.timingSafeEqual(bufA, bufA);
      } catch {
        /* noop */
      }
      return false;
    }
    return crypto.timingSafeEqual(bufA, bufB);
  }

  private verifyPinInternal(pin: string, storedHash: string): boolean {
    if (!storedHash.includes(":")) {
      // Legacy format (SHA-256 direct)
      const legacyHash = crypto.createHash("sha256").update(pin).digest("hex");
      return this.safeCompare(legacyHash, storedHash);
    }

    const [salt, hash] = storedHash.split(":");
    const currentHash = crypto
      .createHmac("sha256", salt)
      .update(pin)
      .digest("hex");
    return this.safeCompare(currentHash, hash);
  }

  public async verifyPin(pin: string): Promise<boolean> {
    if (typeof pin !== "string") return false;

    const config = this.configService.getConfig();
    if (!config.security?.enabled || !config.security.pinHash) {
      // Sécurité désactivée ou pas de hash : le handler considère que c'est bon.
      return true;
    }

    // Anti-brute-force : pendant la période de verrouillage, on refuse sans
    // même comparer le PIN.
    const now = Date.now();
    if (config.security.lockedUntil && now < config.security.lockedUntil) {
      devLog("SecurityService: PIN verification locked out");
      return false;
    }

    const isValid = this.verifyPinInternal(pin, config.security.pinHash);

    if (!isValid) {
      const failedAttempts = (config.security.failedAttempts || 0) + 1;
      const security = { ...config.security, failedAttempts };
      // Backoff exponentiel une fois le seuil d'essais dépassé.
      if (failedAttempts >= this.MAX_PIN_ATTEMPTS) {
        const overflow = failedAttempts - this.MAX_PIN_ATTEMPTS;
        security.lockedUntil = now + this.LOCKOUT_BASE_MS * 2 ** overflow;
      }
      await this.configService.saveConfig({ security });
      return false;
    }

    // Succès : on réinitialise le compteur et on migre éventuellement le hash.
    const needsMigration = !config.security.pinHash.includes(":");
    const hadFailures =
      !!config.security.failedAttempts || !!config.security.lockedUntil;
    if (needsMigration || hadFailures) {
      if (needsMigration) {
        devLog("SecurityService: Migrating PIN to new hash format");
      }
      await this.configService.saveConfig({
        security: {
          ...config.security,
          pinHash: needsMigration ? this.hashPin(pin) : config.security.pinHash,
          failedAttempts: 0,
          lockedUntil: 0,
        },
      });
    }

    return isValid;
  }

  public async setPin(pin: string): Promise<boolean> {
    if (typeof pin !== "string" || pin.length < this.PIN_MIN_LENGTH) {
      throw new Error(
        `Le PIN doit faire au moins ${this.PIN_MIN_LENGTH} caractères`,
      );
    }

    const newHash = this.hashPin(pin);
    await this.configService.saveConfig({
      security: { enabled: true, pinHash: newHash },
    });
    return true;
  }

  public async disablePin(pin: string): Promise<boolean> {
    if (typeof pin !== "string") return false;

    const config = this.configService.getConfig();
    // Si déjà désactivé
    if (!config.security?.enabled || !config.security.pinHash) {
      await this.configService.saveConfig({
        security: { enabled: false, pinHash: null },
      });
      return true;
    }

    if (this.verifyPinInternal(pin, config.security.pinHash)) {
      await this.configService.saveConfig({
        security: { enabled: false, pinHash: null },
      });
      return true;
    }

    return false;
  }

  public isEnabled(): boolean {
    const config = this.configService.getConfig();
    return !!(config.security && config.security.enabled);
  }

  // Secure Encryption/Decryption (s'appuie sur DPAPI/Keychain via safeStorage)
  public encryptData(data: string): string {
    if (!safeStorage || !safeStorage.isEncryptionAvailable()) {
      // On refuse de stocker des identifiants : sans chiffrement OS, un fallback
      // base64 serait du clair trivialement réversible. Mieux vaut échouer net.
      throw new Error(
        "Chiffrement sécurisé indisponible : impossible de stocker les identifiants.",
      );
    }
    return safeStorage.encryptString(data).toString("base64");
  }

  public decryptData(encryptedData: string): string | null {
    if (!safeStorage || !safeStorage.isEncryptionAvailable()) {
      devError("Decryption unavailable: OS encryption not available");
      return null;
    }
    try {
      return safeStorage.decryptString(Buffer.from(encryptedData, "base64"));
    } catch (e) {
      devError("Decryption failed:", e);
      return null;
    }
  }
}
