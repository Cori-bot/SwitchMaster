import { describe, it, expect, vi, beforeEach } from "vitest";
import { ipcMain } from "electron";
import { registerUpdateHandlers } from "../main/ipc/updateHandlers";
import * as updaterModule from "../main/updater";

// Mocks
vi.mock("electron", () => ({
  ipcMain: {
    handle: vi.fn(),
    removeHandler: vi.fn(),
    on: vi.fn(),
    removeAllListeners: vi.fn(),
  },
  dialog: { showOpenDialog: vi.fn() },
  app: { quit: vi.fn(), relaunch: vi.fn(), exit: vi.fn() as any },
  BrowserWindow: { getAllWindows: vi.fn() },
}));

vi.mock("../main/accounts", () => ({ loadAccountsMeta: vi.fn() }));
vi.mock("../main/config", () => ({ saveConfig: vi.fn(), getConfig: vi.fn() }));
vi.mock("../main/logger", () => ({ devLog: vi.fn(), devError: vi.fn() }));
vi.mock("../main/updater", () => ({
  handleUpdateCheck: vi.fn(),
  simulateUpdateCheck: vi.fn(),
  downloadUpdate: vi.fn(),
  installUpdate: vi.fn(),
}));

describe("updateHandlers check-updates coverage", () => {
  let registeredHandlers: Record<string, Function> = {};

  beforeEach(() => {
    vi.clearAllMocks();
    registeredHandlers = {};
    (ipcMain.handle as any).mockImplementation(
      (channel: string, handler: Function) => {
        registeredHandlers[channel] = handler;
      },
    );
  });

  it("calls handleUpdateCheck when window exists", async () => {
    const mockWindow = {} as any;
    registerUpdateHandlers(() => mockWindow);

    const handler = registeredHandlers["check-updates"];
    await handler({});

    expect(updaterModule.handleUpdateCheck).toHaveBeenCalledWith(
      mockWindow,
      true,
    );
  });

  it("does not call handleUpdateCheck when window missing", async () => {
    registerUpdateHandlers(() => null);

    const handler = registeredHandlers["check-updates"];
    await handler({});

    expect(updaterModule.handleUpdateCheck).not.toHaveBeenCalled();
  });
});
