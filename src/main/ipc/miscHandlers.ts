import { ipcMain, dialog, app, BrowserWindow } from "electron";
import path from "path";
import crypto from "crypto";
import fs from "fs-extra";
import { safeHandle } from "./utils";
import { IpcContext } from "./types";
import { devLog, devError } from "../logger";
import { AccountService } from "../services/AccountService";
import { ConfigService } from "../services/ConfigService";
import {
  parsePayload,
  booleanSchema,
  logToMainSchema,
  quitChoiceSchema,
} from "./schemas";

export function registerMiscHandlers(
  getMainWindow: () => BrowserWindow | null,
  context: IpcContext,
  accountService: AccountService,
  configService: ConfigService,
) {
  safeHandle("select-account-image", async () => {
    const win = getMainWindow();
    if (!win) return null;
    const { canceled, filePaths } = await dialog.showOpenDialog(win, {
      properties: ["openFile"],
      filters: [
        { name: "Images", extensions: ["jpg", "png", "gif", "jpeg", "webp"] },
      ],
    });
    if (canceled || !filePaths[0]) return null;

    // Copy the selected image into userData/account-images/ so the sm-img
    // protocol can whitelist a single directory and block FS exfiltration.
    try {
      const sourcePath = filePaths[0];
      const ext = path.extname(sourcePath).toLowerCase() || ".png";
      const destDir = path.join(app.getPath("userData"), "account-images");
      await fs.ensureDir(destDir);
      const destPath = path.join(destDir, `${crypto.randomUUID()}${ext}`);
      await fs.copy(sourcePath, destPath);
      return destPath;
    } catch (err) {
      devError("select-account-image: copy failed:", err);
      return null;
    }
  });

  ipcMain.removeAllListeners("log-to-main");
  ipcMain.on("log-to-main", (_e, payload) => {
    try {
      const { level, args } = parsePayload(
        logToMainSchema,
        payload,
        "log-to-main",
      );
      const prefix = `[Renderer ${level.toUpperCase()}]`;
      devLog(`${prefix}`, ...args);
    } catch (err) {
      devError("log-to-main: invalid payload", err);
    }
  });

  safeHandle("get-status", async () => {
    const statusInfo = await context.getStatus();
    if (statusInfo.status === "Active" && statusInfo.accountId) {
      const accounts = await accountService.getAccounts();
      const acc = accounts.find((a) => a.id === statusInfo.accountId);
      if (acc) {
        statusInfo.accountName = acc.name;
      }
    }
    return statusInfo;
  });

  safeHandle("get-auto-start", () => context.getAutoStartStatus());
  safeHandle("set-auto-start", (_e, enable) => {
    const validated = parsePayload(booleanSchema, enable, "set-auto-start");
    context.setAutoStart(validated);
    return true;
  });

  safeHandle("confirm-quit", () => {
    app.quit();
  });

  safeHandle("minimize-to-tray", () => {
    getMainWindow()?.hide();
  });

  safeHandle("handle-quit-choice", async (_e, dataRaw: any) => {
    const { action, dontShowAgain } = parsePayload(
      quitChoiceSchema,
      dataRaw,
      "handle-quit-choice",
    );

    if (action === "quit") {
      (app as any).isQuitting = true;
      (global as any).isQuitting = true;
    }

    const win = getMainWindow();
    if (dontShowAgain) {
      const config = configService.getConfig();
      const newConfig = {
        ...config,
        showQuitModal: false,
        minimizeToTray: action === "minimize",
      };

      try {
        await configService.saveConfig(newConfig);
        if (action !== "quit" && win && !win.isDestroyed()) {
          void win.webContents.send("config-updated", newConfig);
        }
      } catch (err) {
        devError("Failed to save config during quit choice:", err);
      }
    }

    if (action === "quit") {
      if (win && !win.isDestroyed()) {
        win.close();
      }
      app.quit();
    } else {
      win?.hide();
    }
    return true;
  });

  safeHandle("close-app", () => {
    app.quit();
  });

  safeHandle("minimize-app", () => {
    getMainWindow()?.minimize();
  });

  safeHandle("restart-app", () => {
    app.relaunch();
    app.exit();
  });

  safeHandle("is-valorant-running", () => context.isValorantRunning());
}
