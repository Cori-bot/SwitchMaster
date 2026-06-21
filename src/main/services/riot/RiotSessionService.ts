import fs from "fs-extra";
import path from "path";
import os from "os";
import { app } from "electron";
import { devError } from "../../logger";

/**
 * Bascule de comptes Riot par capture/restauration des fichiers de session du
 * Riot Client (modèle TcNo), au lieu de taper le mot de passe.
 *
 * ⚠️ EXPÉRIMENTAL — manipule des fichiers locaux du launcher Riot (zone grise
 * CGU ; aucun rapport avec l'anti-cheat Vanguard, qui protège le jeu). Toujours
 * opt-in ; un backup de la session courante est fait avant toute restauration.
 * La session peut expirer (~72 h) -> on retombe alors sur la frappe clavier.
 */
const RIOT_SESSION_FILES: Array<[string, string]> = [
  ["Data", "RiotGamesPrivateSettings.yaml"],
  ["Config", "RiotClientSettings.yaml"],
];
const KEY_FILE = "RiotGamesPrivateSettings.yaml";

export class RiotSessionService {
  private riotClientDir(): string {
    const localAppData =
      process.env.LOCALAPPDATA || path.join(os.homedir(), "AppData", "Local");
    return path.join(localAppData, "Riot Games", "Riot Client");
  }

  /** N'autorise que des caractères sûrs (anti path-traversal). */
  private safeId(accountId: string): string {
    return accountId.replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 64);
  }

  private profileDir(accountId: string): string {
    return path.join(
      app.getPath("userData"),
      "profiles",
      "riot",
      this.safeId(accountId),
    );
  }

  /** Une session a-t-elle été capturée pour ce compte ? */
  async hasSession(accountId: string): Promise<boolean> {
    return fs.pathExists(path.join(this.profileDir(accountId), KEY_FILE));
  }

  /** Capture (lecture seule) la session Riot actuellement connectée. */
  async captureSession(accountId: string): Promise<boolean> {
    const base = this.riotClientDir();
    const keySrc = path.join(base, "Data", KEY_FILE);
    if (!(await fs.pathExists(keySrc))) {
      // Pas de session persistée détectée -> rien à capturer.
      return false;
    }
    const dest = this.profileDir(accountId);
    await fs.ensureDir(dest);
    for (const [sub, file] of RIOT_SESSION_FILES) {
      const src = path.join(base, sub, file);
      if (await fs.pathExists(src)) {
        await fs.copy(src, path.join(dest, file), { overwrite: true });
      }
    }
    return true;
  }

  /**
   * Restaure la session capturée du compte (backup de la session courante
   * d'abord). Lève une Error si aucun snapshot n'existe.
   */
  async restoreSession(accountId: string): Promise<void> {
    const snap = this.profileDir(accountId);
    if (!(await fs.pathExists(path.join(snap, KEY_FILE)))) {
      throw new Error(`Aucune session Riot capturée pour ${accountId}`);
    }
    const base = this.riotClientDir();
    const backup = path.join(
      app.getPath("userData"),
      "profiles",
      "riot",
      "__backup__",
    );
    await fs.ensureDir(backup);

    // 1) Backup de la session courante (réversible).
    for (const [sub, file] of RIOT_SESSION_FILES) {
      const cur = path.join(base, sub, file);
      if (await fs.pathExists(cur)) {
        try {
          await fs.copy(cur, path.join(backup, file), { overwrite: true });
        } catch (e) {
          devError("[RiotSession] backup error:", e);
        }
      }
    }

    // 2) Restauration du snapshot.
    for (const [sub, file] of RIOT_SESSION_FILES) {
      const snapFile = path.join(snap, file);
      if (await fs.pathExists(snapFile)) {
        await fs.ensureDir(path.join(base, sub));
        await fs.copy(snapFile, path.join(base, sub, file), {
          overwrite: true,
        });
      }
    }
  }
}
