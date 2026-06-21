import { BrowserWindow, dialog } from "electron";
import { safeHandle } from "./utils";
import { SessionService } from "../services/SessionService";
import { RiotAutomationService } from "../services/RiotAutomationService";
import { RiotSessionService } from "../services/riot/RiotSessionService";
import { LaunchGameData } from "./types";
import { parsePayload, idSchema, launchGameDataSchema } from "./schemas";

export function registerRiotHandlers(
  getWin: () => BrowserWindow | null,
  launchGame: (data: LaunchGameData) => Promise<void>,
  getStatus: () => Promise<{ status: string; accountId?: string }>,
  sessionService: SessionService,
  automationService: RiotAutomationService,
  riotSessionService: RiotSessionService,
) {
  safeHandle("select-riot-path", async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog({
      title: "Sélectionner l'exécutable Riot Client",
      filters: [{ name: "Executables", extensions: ["exe"] }],
      properties: ["openFile"],
    });
    return canceled ? null : filePaths[0];
  });

  safeHandle(
    "auto-detect-paths",
    async () => await automationService.autoDetectPaths(),
  );

  safeHandle("switch-account", async (_e, id) => {
    const validId = parsePayload(idSchema, id, "switch-account");
    await sessionService.switchAccount(validId);

    const status = await getStatus();
    const win = getWin();
    if (win && !win.isDestroyed()) {
      win.webContents.send("status-updated", status);
    }

    return { success: true, id: validId };
  });

  safeHandle("launch-game", async (_e, data: LaunchGameData | string) => {
    const validated = parsePayload(launchGameDataSchema, data, "launch-game");
    if (typeof validated === "string") {
      await launchGame({ launcherType: "riot", gameId: validated });
    } else {
      await launchGame(validated as LaunchGameData);
    }
    return true;
  });

  safeHandle("riot-capture-session", async (_e, id) => {
    const validId = parsePayload(idSchema, id, "riot-capture-session");
    return riotSessionService.captureSession(validId);
  });

  safeHandle("riot-has-session", async (_e, id) => {
    const validId = parsePayload(idSchema, id, "riot-has-session");
    return riotSessionService.hasSession(validId);
  });
}
