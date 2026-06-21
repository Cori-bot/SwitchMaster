import { app, BrowserWindow, protocol, net, session, ipcMain } from "electron";
import path from "path";
import { pathToFileURL } from "url";
import { devLog, devError } from "./logger";
import { isInsideDir } from "./utils/pathSafety";

import { ConfigService } from "./services/ConfigService";
import { SecurityService } from "./services/SecurityService";
import { AccountService } from "./services/AccountService";
import { RiotAutomationService } from "./services/RiotAutomationService";
import { SessionService } from "./services/SessionService";
import { SystemService } from "./services/SystemService";
import { StatsService } from "./services/StatsService";

// Capture globale des erreurs fatales (Production Stability)
process.on("uncaughtException", (err) => {
  devError("UNCAUGHT EXCEPTION:", err);
});

process.on("unhandledRejection", (reason, promise) => {
  devError("UNHANDLED REJECTION at:", promise, "reason:", reason);
});

// Register privileged schemes for custom protocols
protocol.registerSchemesAsPrivileged([
  {
    scheme: "sm-img",
    privileges: {
      secure: true,
      standard: true,
      supportFetchAPI: true,
      corsEnabled: true,
      stream: true,
    },
  },
]);

import { createWindow, updateTrayMenu } from "./window";
import { setupIpcHandlers } from "./ipc";
import { setupUpdater, handleUpdateCheck } from "./updater";

const isDev = process.env.NODE_ENV === "development" || !app.isPackaged;
let mainWindow: BrowserWindow | null = null;

const STATS_REFRESH_INTERVAL_MS = 120000;
const INITIAL_STATS_REFRESH_DELAY_MS = 5000;

// Track intervals and IPC listener channels for cleanup at quit time.
const trackedIntervals: NodeJS.Timeout[] = [];
const trackedIpcChannels: string[] = ["log-to-main"];

app.on("before-quit", () => {
  for (const id of trackedIntervals) {
    try {
      clearInterval(id);
    } catch {
      /* noop */
    }
  }
  trackedIntervals.length = 0;
  for (const channel of trackedIpcChannels) {
    try {
      ipcMain.removeAllListeners(channel);
    } catch {
      /* noop */
    }
  }
});

// Set App Name and UserData path before any complex logic
app.name = "switchmaster";
const userDataPath = path.join(app.getPath("appData"), "switchmaster");
app.setPath("userData", userDataPath);

// App Switches
app.commandLine.appendSwitch("disable-gpu-cache");
app.commandLine.appendSwitch("disable-gpu-shader-disk-cache");
app.commandLine.appendSwitch("disable-http-cache");
app.commandLine.appendSwitch("lang", "fr-FR");

import { LauncherFactory } from "./services/LauncherFactory";
import { LaunchGameData } from "./ipc/types";

// Instantiate Services
const configService = new ConfigService();
const securityService = new SecurityService(configService);
const statsService = new StatsService();
const accountService = new AccountService(securityService, statsService);
const riotAutomationService = new RiotAutomationService(
  configService,
  securityService,
);
const sessionService = new SessionService(
  accountService,
  riotAutomationService,
  configService,
);
const systemService = new SystemService();

const launcherFactory = new LauncherFactory([riotAutomationService]);

// Chargement synchrone de la config pour GPU

const initialConfig = configService.loadConfigSync();
if (!initialConfig.enableGPU) {
  app.disableHardwareAcceleration();
}

// Single Instance Lock - Appel immédiat au niveau racine
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  devLog("Une autre instance est déjà en cours d'exécution. Fermeture.");
  app.quit();
} else {
  initApp().catch((err) => {
    devError("Fatal error:", err);
    app.quit();
  });

  app.on("window-all-closed", () => {
    const config = configService.getConfig();
    if (process.platform !== "darwin" && !config.minimizeToTray) {
      app.quit();
    }
  });
}

async function initApp() {
  devLog("Démarrage de l'initialisation de l'application...");
  devLog("UserData Path:", userDataPath);

  try {
    // Set App User Model ID for Windows notifications
    if (process.platform === "win32") {
      app.setAppUserModelId("com.switchmaster.app");
    }
    devLog("Mode développement:", isDev);

    await configService.init();

    // Broadcast config updates
    configService.on("updated", (newConfig) => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send("config-updated", newConfig);
      }
    });

    await app.whenReady();

    // ---------- Security hardening ----------
    session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
      const csp = [
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: blob: sm-img:",
        "font-src 'self' data:",
        "connect-src 'self' https: wss:",
        "object-src 'none'",
        "base-uri 'self'",
        "frame-ancestors 'none'",
      ].join("; ");
      const responseHeaders = { ...(details.responseHeaders || {}) };
      for (const key of Object.keys(responseHeaders)) {
        if (key.toLowerCase() === "content-security-policy") {
          delete responseHeaders[key];
        }
      }
      responseHeaders["Content-Security-Policy"] = [csp];
      callback({ responseHeaders });
    });

    session.defaultSession.setPermissionRequestHandler((_wc, _p, cb) =>
      cb(false),
    );
    // ---------- /Security hardening ----------

    // Enregistrement du protocole sm-img pour les images locales.
    // Sécurité : ne sert QUE les fichiers contenus dans userData/account-images
    // (où select-account-image copie les images) afin d'empêcher tout
    // path traversal / exfiltration de fichiers système arbitraires.
    const accountImagesDir = path.join(
      app.getPath("userData"),
      "account-images",
    );
    protocol.handle("sm-img", (request) => {
      try {
        const parsedUrl = new URL(request.url);
        let decodedPath = decodeURIComponent(
          parsedUrl.hostname + parsedUrl.pathname,
        );

        if (process.platform === "win32" && decodedPath.startsWith("/")) {
          decodedPath = decodedPath.substring(1);
        }

        const absolutePath = path.resolve(decodedPath);
        if (!isInsideDir(accountImagesDir, absolutePath)) {
          devError(
            `[sm-img] Accès refusé (hors account-images): ${absolutePath}`,
          );
          return new Response("Forbidden", { status: 403 });
        }

        const fileUrl = pathToFileURL(absolutePath).toString();
        return net.fetch(fileUrl);
      } catch (e) {
        devError(`[sm-img] Erreur pour ${request.url}:`, e);
        return new Response("Not Found", { status: 404 });
      }
    });

    // Register IPC handlers ALWAYS BEFORE window creation
    const ipcContext = {
      launchGame: async (data: LaunchGameData) => {
        const service = launcherFactory.getService(data.launcherType || "riot");
        if (data.credentials) {
          await service.login(data.credentials);
        }

        if (data.autoLaunch !== false) {
          await service.launchGame(data.gameId);
        }
      },
      setAutoStart: (enable: boolean) =>
        systemService.setAutoStart(
          enable,
          configService.getConfig().startMinimized,
        ),
      getAutoStartStatus: () => systemService.getAutoStartStatus(),
      getStatus: async () => {
        const isRunning = await riotAutomationService.isRiotClientRunning();
        const lastAccountId = configService.getConfig().lastAccountId;
        if (isRunning && lastAccountId) {
          return { status: "Active", accountId: lastAccountId };
        }
        return { status: "Prêt" };
      },
      isValorantRunning: () => riotAutomationService.isValorantRunning(),
    };

    setupIpcHandlers(null, ipcContext, {
      configService,
      securityService,
      accountService,
      riotAutomationService,
      sessionService,
      systemService,
      statsService,
    });

    mainWindow = createWindow(isDev, configService);

    // Détection du mode de démarrage en arrière-plan
    const isAutoStartArg = process.argv.includes("--minimized");
    const os = require("os");
    const fs = require("fs");
    const uptime = os.uptime();
    const currentBootTime = Math.floor((Date.now() - uptime * 1000) / 60000);

    let lastBootTime = "";
    const bootFilePath = path.join(app.getPath("userData"), "last-boot.txt");
    try {
      if (fs.existsSync(bootFilePath)) {
        lastBootTime = fs.readFileSync(bootFilePath, "utf8");
      }
      fs.writeFileSync(bootFilePath, currentBootTime.toString());
    } catch (e) {
      devError("Erreur gestion boot time:", e);
    }

    const isNewSession = lastBootTime !== currentBootTime.toString();
    const isFirstRunOfSession = isNewSession && uptime < 300;
    const config = configService.getConfig();
    const isMinimized =
      config.startMinimized &&
      config.autoStart &&
      (isAutoStartArg || isFirstRunOfSession);

    // Gestion de la deuxième instance
    app.on("second-instance", (_event, commandLine) => {
      const isSecondInstanceAuto =
        commandLine.includes("--minimized") || commandLine.includes("--hidden");
      if (isMinimized && isSecondInstanceAuto && uptime < 600) return;

      if (mainWindow) {
        if (mainWindow.isMinimized()) mainWindow.restore();
        mainWindow.show();
        mainWindow.focus();
      }
    });

    if (!isMinimized) {
      if (mainWindow) {
        if (isDev) {
          mainWindow.show();
        } else {
          mainWindow.once("ready-to-show", () => {
            mainWindow?.show();
          });
          setTimeout(() => {
            if (mainWindow && !mainWindow.isVisible()) mainWindow.show();
          }, 1000);
        }
      }
    }

    const switchAccountTrigger = async (id: string) => {
      if (mainWindow) {
        mainWindow.webContents.send("quick-connect-triggered", id);
      }
      await updateTrayMenu(
        ipcContext.launchGame,
        switchAccountTrigger,
        configService,
        accountService,
      );
    };

    (global as any).refreshTray = () =>
      updateTrayMenu(
        ipcContext.launchGame,
        switchAccountTrigger,
        configService,
        accountService,
      );

    setupIpcHandlers(mainWindow, ipcContext, {
      configService,
      securityService,
      accountService,
      riotAutomationService,
      sessionService,
      systemService,
      statsService,
    });

    setupUpdater(mainWindow);
    await (global as any).refreshTray();

    const monitorIntervalId =
      riotAutomationService.monitorRiotProcess(mainWindow);
    if (monitorIntervalId) trackedIntervals.push(monitorIntervalId);

    const statsIntervalId = setInterval(
      () => accountService.refreshAllAccountStats(mainWindow),
      STATS_REFRESH_INTERVAL_MS,
    );
    trackedIntervals.push(statsIntervalId);
    setTimeout(
      () => accountService.refreshAllAccountStats(mainWindow),
      INITIAL_STATS_REFRESH_DELAY_MS,
    );

    handleUpdateCheck(mainWindow).catch((err) =>
      devError("Update check failed:", err),
    );
  } catch (err) {
    devError("App initialization failed:", err);
  }
}
