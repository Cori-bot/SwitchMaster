import fs from "fs-extra";
import path from "path";
import os from "os";
import { devDebug } from "../logger";
import { RiotLoginEvent } from "../../shared/types";

export type { RiotLoginEvent } from "../../shared/types";

interface WatchOptions {
  timeoutMs?: number;
  pollIntervalMs?: number;
  onEvent?: (e: RiotLoginEvent) => void;
  signal?: AbortSignal;
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Map de codes RSO connus → message FR. La ligne de télémétrie Riot étant déjà
 * auto-descriptive (errorDescription), cette map n'est qu'un complément pour les
 * codes `x-rso-error-id`.
 */
const RSO_CODE_MESSAGES: Record<string, string> = {
  // Observé juste avant un captcha / après des tentatives répétées.
  "40005803":
    "Riot a rejeté la tentative (captcha requis ou trop de tentatives). Connecte-toi manuellement cette fois.",
};

function friendlyFromRsoCode(code: string): string {
  return (
    RSO_CODE_MESSAGES[code] ??
    `Échec d'authentification Riot (code ${code}). Vérifie tes identifiants puis réessaie.`
  );
}

function friendlyFromDescription(desc?: string): string {
  if (!desc) {
    return "Échec de la connexion à Riot. Vérifie ton nom d'utilisateur et ton mot de passe.";
  }
  const d = desc.toLowerCase();
  if (d.includes("rate") || d.includes("too many") || d.includes("throttl")) {
    return "Trop de tentatives de connexion. Patiente quelques minutes avant de réessayer.";
  }
  if (
    d.includes("credential") ||
    d.includes("password") ||
    d.includes("auth_failure") ||
    d.includes("invalid")
  ) {
    return "Identifiants Riot incorrects (nom d'utilisateur ou mot de passe).";
  }
  if (d.includes("captcha")) {
    return "Riot demande une vérification captcha — connecte-toi manuellement cette fois.";
  }
  if (
    d.includes("multifactor") ||
    d.includes("two_factor") ||
    d.includes("2fa")
  ) {
    return "Authentification à deux facteurs (2FA) requise — saisis le code reçu dans le client Riot.";
  }
  if (d.includes("ban") || d.includes("suspend")) {
    return "Ce compte Riot est suspendu ou banni.";
  }
  if (d.includes("maintenance") || d.includes("unavailable")) {
    return "Les serveurs Riot sont indisponibles (maintenance). Réessaie plus tard.";
  }
  return `Échec de la connexion Riot : ${desc}`;
}

/**
 * Analyse UNE ligne de log du Riot Client et renvoie un verdict de connexion,
 * ou `null` si la ligne n'est pas pertinente. Fonction pure (testable).
 *
 * Repères vérifiés dans de vrais logs (format `<temps>| <NIVEAU>| <composant>: <message>`):
 *  - "rc-auth: SendLoginTelemetry: isloginSucessful: 1, authenticationType: ..." → succès
 *    d'une connexion FRAÎCHE (identifiants frappés acceptés). isloginSucessful: 0 → échec.
 *  - "rso-authenticator: ... x-rso-error-id <code>" → erreur RSO (mauvais identifiants /
 *    captcha / rate-limit).
 *  - 'CaptchaEvent__v6 with: {"action":"shown|failed|succeeded"}' → état du captcha.
 *
 * NOTE anti-faux-positif : on IGNORE volontairement
 * "riot-login: SendLoginTelemetryWithStaySignedIn: ... loginType: noLongLivedSession |
 *  longLivedSessionRejected", émise au DÉMARRAGE du client (aucune session persistée à
 * restaurer) et qui n'est PAS le résultat d'une frappe d'identifiants.
 */
export function parseRiotLogLine(line: string): RiotLoginEvent | null {
  // 1) Restauration de session "Rester connecté" (composant riot-login).
  //    isloginSucessful: 1 → la session persistée a été restaurée (déjà connecté).
  //    isloginSucessful: 0 → AUCUNE session valide au démarrage : ce n'est PAS un
  //    échec de frappe, la connexion par identifiants va prendre le relais → on
  //    n'émet rien de bloquant (info silencieuse).
  const staySignedIn =
    /SendLoginTelemetryWithStaySignedIn:\s*isloginSucessful:\s*(\d)/i.exec(
      line,
    );
  if (staySignedIn) {
    if (staySignedIn[1] === "1") {
      return {
        phase: "success",
        message: "Session Riot restaurée (déjà connecté).",
        raw: line.trim(),
      };
    }
    return {
      phase: "info",
      message: "Aucune session Riot mémorisée — connexion par identifiants.",
      raw: line.trim(),
    };
  }

  // 2) Verdict faisant autorité : connexion FRAÎCHE via identifiants (rc-auth).
  //    NB: la faute de frappe "isloginSucessful" est dans la vraie chaîne Riot.
  const rcAuth = /SendLoginTelemetry:\s*isloginSucessful:\s*(\d)/i.exec(line);
  if (rcAuth) {
    if (rcAuth[1] === "1") {
      return {
        phase: "success",
        message: "Connexion à Riot réussie.",
        raw: line.trim(),
      };
    }
    const descMatch =
      /errorDescription:\s*(.+?)(?:,\s*(?:loginType|authenticationType)\b|$)/i.exec(
        line,
      );
    return {
      phase: "error",
      message: friendlyFromDescription(descMatch?.[1]?.trim()),
      raw: line.trim(),
    };
  }

  // 3) Erreur RSO avec identifiant d'erreur (mauvais identifiants / rate-limit /
  //    captcha). Le service rso-authenticator n'émet x-rso-error-id que sur une
  //    réponse RSO non-2xx → toute occurrence = échec côté Riot.
  const rso = /x-rso-error-id\s+(\d+)/i.exec(line);
  if (rso) {
    const code = rso[1];
    return {
      phase: "error",
      code,
      message: friendlyFromRsoCode(code),
      raw: line.trim(),
    };
  }

  // 4) 2FA (multifactor) requise pour finir la connexion.
  if (
    /\bmultifactor\b/i.test(line) &&
    /auth|login|rso|mfa|factor/i.test(line)
  ) {
    return {
      phase: "captcha",
      message:
        "Authentification à deux facteurs (2FA) requise — saisis le code reçu dans le client Riot.",
      raw: line.trim(),
    };
  }

  // 5) Événement captcha (le suffixe de version __v6 peut changer → on relâche).
  const cap = /CaptchaEvent\w*\s+with:\s*\{[^}]*"action":"(\w+)"/i.exec(line);
  if (cap) {
    const action = cap[1].toLowerCase();
    if (action === "shown" || action === "displayed") {
      return {
        phase: "captcha",
        message:
          "Riot demande une vérification captcha — connecte-toi manuellement cette fois.",
        raw: line.trim(),
      };
    }
    if (action === "failed") {
      return {
        phase: "error",
        message: "Échec de la vérification captcha de Riot.",
        raw: line.trim(),
      };
    }
    // succeeded → information, non bloquant.
    return { phase: "info", message: "Captcha validé.", raw: line.trim() };
  }

  return null;
}

export class RiotLogService {
  private readonly logsDir: string;

  constructor(logsDir?: string) {
    this.logsDir =
      logsDir ??
      path.join(
        process.env.LOCALAPPDATA || path.join(os.homedir(), "AppData", "Local"),
        "Riot Games",
        "Riot Client",
        "Logs",
        "Riot Client Logs",
      );
  }

  /** Chemin du fichier de log Riot le plus récemment modifié, ou null. */
  private async newestLog(): Promise<string | null> {
    try {
      const entries = await fs.readdir(this.logsDir);
      let newest: { file: string; mtime: number } | null = null;
      for (const name of entries) {
        if (!name.toLowerCase().endsWith(".log")) continue;
        const full = path.join(this.logsDir, name);
        try {
          const st = await fs.stat(full);
          if (!newest || st.mtimeMs > newest.mtime) {
            newest = { file: full, mtime: st.mtimeMs };
          }
        } catch {
          /* fichier disparu entre readdir et stat */
        }
      }
      return newest ? newest.file : null;
    } catch {
      return null;
    }
  }

  /** Lit l'intervalle d'octets [start, end[ d'un fichier en UTF-8. */
  private readSlice(file: string, start: number, end: number): Promise<string> {
    return new Promise((resolve, reject) => {
      if (end <= start) {
        resolve("");
        return;
      }
      let data = "";
      const stream = fs.createReadStream(file, {
        start,
        end: end - 1, // borne inclusive
        encoding: "utf8",
      });
      stream.on("data", (chunk) => (data += chunk));
      stream.on("end", () => resolve(data));
      stream.on("error", reject);
    });
  }

  /**
   * Surveille le log Riot le plus récent à la recherche du verdict de connexion.
   * Démarre à la FIN du log courant pour ne lire que ce qui est écrit après la
   * frappe des identifiants, et bascule sur un nouveau fichier si le client en
   * crée un (chaque lancement = un nouveau log). Émet chaque événement via
   * `onEvent` et résout sur le premier verdict définitif (success/error/captcha),
   * ou `null` au timeout / si annulé.
   */
  async watchForOutcome(
    opts: WatchOptions = {},
  ): Promise<RiotLoginEvent | null> {
    const timeoutMs = opts.timeoutMs ?? 30000;
    const pollIntervalMs = opts.pollIntervalMs ?? 750;
    const deadline = Date.now() + timeoutMs;

    let currentFile = await this.newestLog();
    let position = 0;
    if (currentFile) {
      try {
        position = (await fs.stat(currentFile)).size;
      } catch {
        position = 0;
      }
    }

    while (Date.now() < deadline) {
      if (opts.signal?.aborted) return null;
      await delay(pollIntervalMs);
      if (opts.signal?.aborted) return null;

      const newest = await this.newestLog();
      if (newest && newest !== currentFile) {
        currentFile = newest;
        position = 0;
      }
      if (!currentFile) continue;

      let size = 0;
      try {
        size = (await fs.stat(currentFile)).size;
      } catch {
        continue;
      }
      if (size <= position) continue;

      let chunk = "";
      try {
        chunk = await this.readSlice(currentFile, position, size);
      } catch (e) {
        devDebug("RiotLogService readSlice error:", e);
        continue;
      }
      position = size;

      for (const line of chunk.split(/\r?\n/)) {
        if (!line) continue;
        const evt = parseRiotLogLine(line);
        if (!evt) continue;
        opts.onEvent?.(evt);
        if (
          evt.phase === "success" ||
          evt.phase === "error" ||
          evt.phase === "captcha"
        ) {
          return evt;
        }
      }
    }
    return null;
  }

  /**
   * Récupère les derniers verdicts d'erreur/captcha du log courant (diagnostic
   * à la demande, ex: après un échec pour expliquer pourquoi). Lit la fin du
   * fichier le plus récent et conserve les `max` derniers événements bloquants.
   */
  async getRecentLoginErrors(max = 5): Promise<RiotLoginEvent[]> {
    const file = await this.newestLog();
    if (!file) return [];
    let size = 0;
    try {
      size = (await fs.stat(file)).size;
    } catch {
      return [];
    }
    // On ne lit que la fin du fichier (au plus 256 Ko) pour rester léger.
    const start = Math.max(0, size - 256 * 1024);
    let chunk = "";
    try {
      chunk = await this.readSlice(file, start, size);
    } catch {
      return [];
    }
    const events: RiotLoginEvent[] = [];
    for (const line of chunk.split(/\r?\n/)) {
      if (!line) continue;
      const evt = parseRiotLogLine(line);
      if (evt && (evt.phase === "error" || evt.phase === "captcha")) {
        events.push(evt);
      }
    }
    return events.slice(-max);
  }
}
