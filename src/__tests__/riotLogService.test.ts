import { describe, it, expect, afterEach } from "vitest";
import fs from "fs-extra";
import path from "path";
import os from "os";
import {
  RiotLogService,
  parseRiotLogLine,
} from "../main/services/RiotLogService";

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

// Lignes réelles extraites de vrais logs du Riot Client (format
// `<temps>| <NIVEAU>| <composant>: <message>`).
const L = {
  noise:
    "003607.817|   OKAY| patch-proxy: HandleProductPatchlineStatusUpdate: productId: league_of_legends, patchlineId: live, status: UpToDate, progress: 0",
  http400:
    "000002.240|  ERROR| Remoting: HTTP Response 400 to GET '/rso-auth/v1/authorization'",
  staySignedInEmpty:
    "000001.780|   OKAY| SDK: riot-login: SendLoginTelemetryWithStaySignedIn: isloginSucessful: 0, errorDescription: Persisted login state is empty, loginType: noLongLivedSession",
  staySignedInRejected:
    "000005.000|   OKAY| SDK: riot-login: SendLoginTelemetryWithStaySignedIn: isloginSucessful: 0, errorDescription: Failed to authenticate with persisted login state, loginType: longLivedSessionRejected",
  staySignedInOk:
    "000006.000|   OKAY| SDK: riot-login: SendLoginTelemetryWithStaySignedIn: isloginSucessful: 1, authenticationType: persisted",
  freshSuccess:
    "001110.000|   OKAY| rc-auth: SendLoginTelemetry: isloginSucessful: 1, authenticationType: ,",
  freshFailCreds:
    "001110.000|   OKAY| rc-auth: SendLoginTelemetry: isloginSucessful: 0, errorDescription: auth_failure, authenticationType: ,",
  freshFailRate:
    "001110.000|   OKAY| rc-auth: SendLoginTelemetry: isloginSucessful: 0, errorDescription: rate_limited, authenticationType: ,",
  rsoErrorCode:
    "001104.000|  ERROR| SDK: rso-authenticator: RSO Authenticator x-rso-error-id 40005803",
  captchaShown:
    '001103.500|   OKAY| telemetry: Sending telemetry to schema riotclient__CaptchaEvent__v6 with: {"action":"shown","riotclientMetadata":{"riotclientURL":"/login"},"type":"hcaptcha"}',
  captchaSucceeded:
    '001103.500|   OKAY| telemetry: Sending telemetry to schema riotclient__CaptchaEvent__v6 with: {"action":"succeeded","riotclientMetadata":{"riotclientURL":"/login"},"type":"hcaptcha"}',
  captchaFailed:
    '001103.500|   OKAY| telemetry: Sending telemetry to schema riotclient__CaptchaEvent__v6 with: {"action":"failed","riotclientMetadata":{"riotclientURL":"/login"},"type":"hcaptcha"}',
  multifactor:
    "001110.000|   OKAY| SDK: rso-auth: auth response type multifactor required for login",
};

describe("parseRiotLogLine", () => {
  it("détecte un succès de connexion fraîche (rc-auth)", () => {
    const e = parseRiotLogLine(L.freshSuccess);
    expect(e?.phase).toBe("success");
  });

  it("détecte un échec d'identifiants (auth_failure)", () => {
    const e = parseRiotLogLine(L.freshFailCreds);
    expect(e?.phase).toBe("error");
    expect(e?.message.toLowerCase()).toContain("identifiants");
  });

  it("détecte un rate-limit", () => {
    const e = parseRiotLogLine(L.freshFailRate);
    expect(e?.phase).toBe("error");
    expect(e?.message.toLowerCase()).toContain("tentatives");
  });

  it("traite la session restaurée comme un succès", () => {
    const e = parseRiotLogLine(L.staySignedInOk);
    expect(e?.phase).toBe("success");
  });

  it("N'EST PAS une erreur quand aucune session persistée au démarrage (anti-faux-positif)", () => {
    // C'est le bruit de démarrage : pas de session à restaurer, la frappe prend
    // le relais. Surtout ne pas lever d'erreur de login ici.
    expect(parseRiotLogLine(L.staySignedInEmpty)?.phase).toBe("info");
    expect(parseRiotLogLine(L.staySignedInRejected)?.phase).toBe("info");
  });

  it("détecte un code d'erreur RSO et capture le code", () => {
    const e = parseRiotLogLine(L.rsoErrorCode);
    expect(e?.phase).toBe("error");
    expect(e?.code).toBe("40005803");
  });

  it("détecte un captcha affiché (action manuelle requise)", () => {
    expect(parseRiotLogLine(L.captchaShown)?.phase).toBe("captcha");
  });

  it("traite un captcha validé comme info, un captcha échoué comme erreur", () => {
    expect(parseRiotLogLine(L.captchaSucceeded)?.phase).toBe("info");
    expect(parseRiotLogLine(L.captchaFailed)?.phase).toBe("error");
  });

  it("détecte la 2FA (multifactor)", () => {
    const e = parseRiotLogLine(L.multifactor);
    expect(e?.phase).toBe("captcha");
    expect(e?.message).toContain("2FA");
  });

  it("ignore le bruit non pertinent", () => {
    expect(parseRiotLogLine(L.noise)).toBeNull();
    expect(parseRiotLogLine(L.http400)).toBeNull();
    expect(parseRiotLogLine("")).toBeNull();
  });
});

describe("RiotLogService.watchForOutcome", () => {
  const tmpDirs: string[] = [];
  const mkDir = () => {
    const d = fs.mkdtempSync(path.join(os.tmpdir(), "sm-riotlog-"));
    tmpDirs.push(d);
    return d;
  };

  afterEach(() => {
    for (const d of tmpDirs.splice(0)) {
      try {
        fs.removeSync(d);
      } catch {
        /* noop */
      }
    }
  });

  it("résout sur le verdict de succès écrit après le démarrage de la surveillance", async () => {
    const dir = mkDir();
    const file = path.join(dir, "2026-01-01T00-00-00_1_Riot Client.log");
    fs.writeFileSync(file, L.noise + "\n" + L.staySignedInEmpty + "\n");

    const svc = new RiotLogService(dir);
    const events: string[] = [];
    const p = svc.watchForOutcome({
      timeoutMs: 3000,
      pollIntervalMs: 20,
      onEvent: (e) => events.push(e.phase),
    });

    // Laisse la baseline (fin de fichier) se figer avant d'ajouter la suite.
    await delay(80);
    fs.appendFileSync(file, L.freshSuccess + "\n");

    const outcome = await p;
    expect(outcome?.phase).toBe("success");
  });

  it("ne se déclenche pas sur le bruit de démarrage (faux-positif), puis voit l'échec réel", async () => {
    const dir = mkDir();
    const file = path.join(dir, "2026-01-01T00-00-00_1_Riot Client.log");
    fs.writeFileSync(file, L.noise + "\n");

    const svc = new RiotLogService(dir);
    const p = svc.watchForOutcome({ timeoutMs: 3000, pollIntervalMs: 20 });

    await delay(80);
    // Bruit de démarrage (ne doit PAS résoudre), puis vrai échec.
    fs.appendFileSync(file, L.staySignedInEmpty + "\n");
    await delay(80);
    fs.appendFileSync(file, L.freshFailCreds + "\n");

    const outcome = await p;
    expect(outcome?.phase).toBe("error");
  });

  it("résout null au timeout sans verdict", async () => {
    const dir = mkDir();
    const file = path.join(dir, "2026-01-01T00-00-00_1_Riot Client.log");
    fs.writeFileSync(file, L.noise + "\n");
    const svc = new RiotLogService(dir);
    const outcome = await svc.watchForOutcome({
      timeoutMs: 120,
      pollIntervalMs: 20,
    });
    expect(outcome).toBeNull();
  });

  it("retourne [] quand le dossier de logs n'existe pas", async () => {
    const svc = new RiotLogService(
      path.join(os.tmpdir(), "sm-riotlog-does-not-exist-xyz"),
    );
    expect(await svc.getRecentLoginErrors()).toEqual([]);
    const outcome = await svc.watchForOutcome({
      timeoutMs: 80,
      pollIntervalMs: 20,
    });
    expect(outcome).toBeNull();
  });
});

describe("RiotLogService.getRecentLoginErrors", () => {
  it("extrait les derniers verdicts d'erreur/captcha du log courant", async () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "sm-riotlog-"));
    try {
      const file = path.join(dir, "2026-01-01T00-00-00_1_Riot Client.log");
      fs.writeFileSync(
        file,
        [L.noise, L.freshFailCreds, L.noise, L.captchaShown, L.http400].join(
          "\n",
        ) + "\n",
      );
      const svc = new RiotLogService(dir);
      const errors = await svc.getRecentLoginErrors();
      expect(errors.length).toBe(2);
      expect(errors.map((e) => e.phase)).toEqual(["error", "captcha"]);
    } finally {
      fs.removeSync(dir);
    }
  });
});
