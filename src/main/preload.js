const { contextBridge, ipcRenderer } = require("electron");

// Canaux IPC autorisés, par direction. Toute tentative d'utiliser un canal hors
// de ces listes est rejetée : le renderer ne peut pas piloter des canaux
// internes/privilégiés arbitraires (défense en profondeur contre un XSS).
const INVOKE_CHANNELS = new Set([
  "get-security-status",
  "verify-pin",
  "set-pin",
  "disable-pin",
  "get-accounts",
  "get-account-credentials",
  "add-account",
  "update-account",
  "delete-account",
  "reorder-accounts",
  "fetch-account-stats",
  "get-config",
  "save-config",
  "select-riot-path",
  "auto-detect-paths",
  "switch-account",
  "launch-game",
  "select-account-image",
  "get-status",
  "get-auto-start",
  "set-auto-start",
  "handle-quit-choice",
  "confirm-quit",
  "minimize-to-tray",
  "close-app",
  "minimize-app",
  "restart-app",
  "is-valorant-running",
  "get-lcu-active-account",
  "check-updates",
  "simulate-update",
  "download-update",
  "install-update",
]);

const SEND_CHANNELS = new Set(["log-to-main"]);

const ON_CHANNELS = new Set([
  "config-updated",
  "accounts-updated",
  "status-updated",
  "riot-client-closed",
  "show-quit-modal",
  "update-status",
  "update-progress",
  "update-downloaded",
  "quick-connect-triggered",
  "login-success",
]);

// Expose a minimal, controlled IPC API to the renderer
contextBridge.exposeInMainWorld("ipc", {
  invoke: (channel, ...args) => {
    if (!INVOKE_CHANNELS.has(channel)) {
      return Promise.reject(new Error(`Blocked IPC invoke channel: ${channel}`));
    }
    return ipcRenderer.invoke(channel, ...args);
  },
  send: (channel, ...args) => {
    if (!SEND_CHANNELS.has(channel)) return;
    ipcRenderer.send(channel, ...args);
  },
  on: (channel, listener) => {
    if (!ON_CHANNELS.has(channel)) return () => {};
    const subscription = (event, ...data) => listener(event, ...data);
    ipcRenderer.on(channel, subscription);
    return () => ipcRenderer.removeListener(channel, subscription);
  },
  removeAllListeners: (channel) => {
    if (!ON_CHANNELS.has(channel)) return;
    ipcRenderer.removeAllListeners(channel);
  },
});

contextBridge.exposeInMainWorld("env", {
  isDev:
    process.env.NODE_ENV === "development" ||
    process.env.npm_lifecycle_event === "start",
});
