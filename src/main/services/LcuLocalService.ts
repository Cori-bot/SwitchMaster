import fs from "fs-extra";
import path from "path";
import os from "os";
import https from "https";
import { devError } from "../logger";

interface LcuLockfile {
  port: number;
  password: string;
  protocol: string;
}

export interface LcuActiveAccount {
  gameName: string;
  tagLine: string;
  riotId: string;
}

/**
 * Lecture seule du Riot Client local pour détecter le compte actuellement
 * connecté (confort d'affichage uniquement).
 *
 * ⚠️ L'API LCU/Riot Client locale n'est PAS supportée par Riot. Ce service est
 * strictement opt-in, en lecture seule : aucune écriture, aucune automation,
 * aucune interaction avec l'anti-cheat. À documenter côté UI (risque CGU).
 */
export class LcuLocalService {
  private readonly REQUEST_TIMEOUT_MS = 3000;

  private getLockfilePath(): string {
    const localAppData =
      process.env.LOCALAPPDATA || path.join(os.homedir(), "AppData", "Local");
    return path.join(
      localAppData,
      "Riot Games",
      "Riot Client",
      "Config",
      "lockfile",
    );
  }

  /** Parse le lockfile (`name:pid:port:password:protocol`) ou null si absent. */
  async readLockfile(): Promise<LcuLockfile | null> {
    try {
      const content = await fs.readFile(this.getLockfilePath(), "utf8");
      const parts = content.trim().split(":");
      if (parts.length < 5) return null;
      const port = Number(parts[2]);
      const password = parts[3];
      const protocol = parts[4];
      if (!port || !password) return null;
      return { port, password, protocol };
    } catch {
      // Lockfile absent => Riot Client non lancé.
      return null;
    }
  }

  async isRiotClientRunning(): Promise<boolean> {
    return (await this.readLockfile()) !== null;
  }

  /** Renvoie le compte Riot connecté localement, ou null. */
  async getActiveAccount(): Promise<LcuActiveAccount | null> {
    const lock = await this.readLockfile();
    if (!lock) return null;
    try {
      const data = await this.localGet(
        lock,
        "/player-account/aliases/v1/active",
      );
      if (!data) return null;
      const gameName = (data["game_name"] ?? data["gameName"]) as
        | string
        | undefined;
      const tagLine = (data["tag_line"] ?? data["tagLine"]) as
        | string
        | undefined;
      if (!gameName || !tagLine) return null;
      return { gameName, tagLine, riotId: `${gameName}#${tagLine}` };
    } catch (err) {
      devError("[LCU] getActiveAccount failed:", (err as Error).message);
      return null;
    }
  }

  private localGet(
    lock: LcuLockfile,
    endpoint: string,
  ): Promise<Record<string, unknown> | null> {
    return new Promise((resolve, reject) => {
      const auth = Buffer.from(`riot:${lock.password}`).toString("base64");
      const req = https.request(
        {
          host: "127.0.0.1",
          port: lock.port,
          path: endpoint,
          method: "GET",
          rejectUnauthorized: false, // certificat self-signed du client local
          headers: { Authorization: `Basic ${auth}` },
        },
        (res) => {
          let body = "";
          res.on("data", (c) => (body += c));
          res.on("end", () => {
            const status = res.statusCode ?? 0;
            if (status >= 200 && status < 300) {
              try {
                resolve(
                  body ? (JSON.parse(body) as Record<string, unknown>) : null,
                );
              } catch {
                resolve(null);
              }
            } else {
              reject(new Error(`LCU HTTP ${status}`));
            }
          });
        },
      );
      req.on("error", reject);
      req.setTimeout(this.REQUEST_TIMEOUT_MS, () =>
        req.destroy(new Error("LCU timeout")),
      );
      req.end();
    });
  }
}
