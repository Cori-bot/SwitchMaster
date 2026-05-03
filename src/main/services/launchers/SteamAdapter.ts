import { spawn, exec } from "child_process";
import util from "util";
import path from "path";
import fs from "fs-extra";
import { app } from "electron";
import { devDebug, devError } from "../../logger";
import { LauncherAdapter } from "../../interfaces/ILauncherService";

const execAsync = util.promisify(exec);

const DEFAULT_STEAM_PATHS = [
  "C:\\Program Files (x86)\\Steam",
  "C:\\Program Files\\Steam",
];

const SSFN_GLOB_PREFIX = "ssfn";

/**
 * Steam launcher adapter implementing the TcNo capture/restore profile model.
 * Note: Steam does not allow scripted credential entry, so `login` is omitted.
 */
export class SteamAdapter implements LauncherAdapter {
  public readonly id = "steam";
  public readonly displayName = "Steam";

  /** Resolved Steam installation directory, cached after first detection. */
  private steamPathCache: string | null = null;

  public async isInstalled(): Promise<boolean> {
    const detected = await this.detectSteamPath();
    return detected !== null;
  }

  public async killProcesses(): Promise<void> {
    try {
      await execAsync("taskkill /F /IM steam.exe /T");
    } catch (e) {
      devDebug(
        "Steam taskkill ignore (no processes):",
        e instanceof Error ? e.message : e,
      );
    }
  }

  public async launchClient(args: string[] = []): Promise<void> {
    const steamPath = await this.detectSteamPath();
    if (!steamPath) {
      throw new Error("Steam installation not found");
    }
    const exe = path.join(steamPath, "steam.exe");
    if (!(await fs.pathExists(exe))) {
      throw new Error(`steam.exe not found at: ${exe}`);
    }
    const child = spawn(exe, args, { detached: true, stdio: "ignore" });
    child.unref();
  }

  public async captureProfile(accountId: string): Promise<void> {
    const steamPath = await this.requireSteamPath();
    const profileDir = this.getProfileDir(accountId);
    await fs.ensureDir(profileDir);

    const configDir = path.join(steamPath, "config");
    await this.copyIfExists(
      path.join(configDir, "loginusers.vdf"),
      path.join(profileDir, "loginusers.vdf"),
    );
    await this.copyIfExists(
      path.join(configDir, "config.vdf"),
      path.join(profileDir, "config.vdf"),
    );

    // Copy ssfn* files (sentry files) from steam root.
    try {
      const entries = await fs.readdir(steamPath);
      const ssfnFiles = entries.filter((f) => f.startsWith(SSFN_GLOB_PREFIX));
      for (const f of ssfnFiles) {
        await fs.copy(path.join(steamPath, f), path.join(profileDir, f), {
          overwrite: true,
        });
      }
    } catch (e) {
      devError("captureProfile ssfn copy error:", e);
    }
  }

  public async restoreProfile(accountId: string): Promise<void> {
    const steamPath = await this.requireSteamPath();
    const profileDir = this.getProfileDir(accountId);
    if (!(await fs.pathExists(profileDir))) {
      throw new Error(`Steam profile snapshot not found: ${accountId}`);
    }

    const configDir = path.join(steamPath, "config");
    await fs.ensureDir(configDir);

    await this.copyIfExists(
      path.join(profileDir, "loginusers.vdf"),
      path.join(configDir, "loginusers.vdf"),
    );
    await this.copyIfExists(
      path.join(profileDir, "config.vdf"),
      path.join(configDir, "config.vdf"),
    );

    try {
      const entries = await fs.readdir(profileDir);
      const ssfnFiles = entries.filter((f) => f.startsWith(SSFN_GLOB_PREFIX));
      for (const f of ssfnFiles) {
        await fs.copy(path.join(profileDir, f), path.join(steamPath, f), {
          overwrite: true,
        });
      }
    } catch (e) {
      devError("restoreProfile ssfn copy error:", e);
    }

    // Set AutoLoginUser in registry to the saved one (best-effort).
    await this.setAutoLoginUser(accountId);
  }

  // --- helpers ---

  private getProfileDir(accountId: string): string {
    return path.join(app.getPath("userData"), "profiles", this.id, accountId);
  }

  private async requireSteamPath(): Promise<string> {
    const p = await this.detectSteamPath();
    if (!p) throw new Error("Steam installation not found");
    return p;
  }

  private async detectSteamPath(): Promise<string | null> {
    if (this.steamPathCache) return this.steamPathCache;

    // Try registry first.
    try {
      const { stdout } = await execAsync(
        'reg query "HKCU\\Software\\Valve\\Steam" /v SteamPath',
      );
      const match = stdout.match(/SteamPath\s+REG_SZ\s+(.+)/i);
      if (match && match[1]) {
        const regPath = match[1].trim().replace(/\//g, "\\");
        if (await fs.pathExists(regPath)) {
          this.steamPathCache = regPath;
          return regPath;
        }
      }
    } catch (e) {
      devDebug(
        "Steam registry probe failed:",
        e instanceof Error ? e.message : e,
      );
    }

    // Fallback to default install paths.
    for (const p of DEFAULT_STEAM_PATHS) {
      if (await fs.pathExists(p)) {
        this.steamPathCache = p;
        return p;
      }
    }
    return null;
  }

  private async copyIfExists(src: string, dst: string): Promise<void> {
    if (await fs.pathExists(src)) {
      await fs.copy(src, dst, { overwrite: true });
    }
  }

  private async setAutoLoginUser(accountId: string): Promise<void> {
    try {
      await execAsync(
        `reg add "HKCU\\Software\\Valve\\Steam" /v AutoLoginUser /t REG_SZ /d "${accountId}" /f`,
      );
    } catch (e) {
      devDebug("setAutoLoginUser failed:", e instanceof Error ? e.message : e);
    }
  }
}

// TODO: implement UbisoftAdapter and BattleNetAdapter following the same model.
