import { describe, it, expect, vi, beforeEach } from "vitest";
import * as cp from "child_process";
import fs from "fs-extra";
import path from "path";
import { SteamAdapter } from "../main/services/launchers/SteamAdapter";

vi.mock("child_process", () => {
  const exec = vi.fn();
  const spawn = vi.fn();
  return { exec, spawn, default: { exec, spawn } };
});

vi.mock("fs-extra", () => {
  const m = {
    pathExists: vi.fn(),
    ensureDir: vi.fn().mockResolvedValue(undefined),
    copy: vi.fn().mockResolvedValue(undefined),
    readdir: vi.fn(),
  };
  return { ...m, default: m };
});

vi.mock("electron", () => ({
  app: {
    getPath: vi.fn().mockReturnValue("USER"),
  },
}));

vi.mock("../main/logger", () => ({
  devDebug: vi.fn(),
  devError: vi.fn(),
}));

const STEAM_PATH = "C:\\Program Files (x86)\\Steam";

function mockExecOk(stdout = "") {
  (cp.exec as any).mockImplementation((_cmd: string, cb: any) => {
    if (typeof cb === "function") cb(null, { stdout, stderr: "" });
    return { on: vi.fn() };
  });
}

function mockExecFail() {
  (cp.exec as any).mockImplementation((_cmd: string, cb: any) => {
    if (typeof cb === "function") cb(new Error("fail"));
    return { on: vi.fn() };
  });
}

describe("SteamAdapter", () => {
  let adapter: SteamAdapter;

  beforeEach(() => {
    vi.clearAllMocks();
    adapter = new SteamAdapter();
    // Default: registry probe fails, fall back to default install dir.
    mockExecFail();
    (fs.pathExists as any).mockImplementation(async (p: string) => {
      // Default Steam path exists; nothing else.
      return p === STEAM_PATH;
    });
    (fs.readdir as any).mockResolvedValue([
      "ssfn1234567890",
      "ssfn0987654321",
      "config",
      "steam.exe",
    ]);
  });

  it("has the expected id and displayName", () => {
    expect(adapter.id).toBe("steam");
    expect(adapter.displayName).toBe("Steam");
  });

  it("isInstalled returns true when default path exists", async () => {
    expect(await adapter.isInstalled()).toBe(true);
  });

  it("isInstalled returns false when nothing exists", async () => {
    (fs.pathExists as any).mockResolvedValue(false);
    expect(await adapter.isInstalled()).toBe(false);
  });

  it("killProcesses calls taskkill for steam.exe", async () => {
    mockExecOk();
    await adapter.killProcesses();
    expect(cp.exec).toHaveBeenCalled();
    const calledWith = (cp.exec as any).mock.calls[0][0] as string;
    expect(calledWith).toContain("taskkill");
    expect(calledWith).toContain("steam.exe");
  });

  it("killProcesses swallows errors when no process is running", async () => {
    mockExecFail();
    await expect(adapter.killProcesses()).resolves.toBeUndefined();
  });

  it("captureProfile copies loginusers.vdf, config.vdf, and ssfn* files", async () => {
    (fs.pathExists as any).mockImplementation(async (p: string) => {
      if (p === STEAM_PATH) return true;
      if (p.endsWith("loginusers.vdf")) return true;
      if (p.endsWith("config.vdf")) return true;
      return false;
    });

    await adapter.captureProfile("acc1");

    const profileDir = path.join("USER", "profiles", "steam", "acc1");
    expect(fs.ensureDir).toHaveBeenCalledWith(profileDir);

    const copyCalls = (fs.copy as any).mock.calls.map((c: any[]) => [
      c[0],
      c[1],
    ]);
    const sources = copyCalls.map((c: string[]) => c[0]);
    const dests = copyCalls.map((c: string[]) => c[1]);

    expect(sources.some((s: string) => s.endsWith("loginusers.vdf"))).toBe(
      true,
    );
    expect(sources.some((s: string) => s.endsWith("config.vdf"))).toBe(true);
    expect(sources.some((s: string) => s.endsWith("ssfn1234567890"))).toBe(
      true,
    );
    expect(dests.some((d: string) => d.includes(profileDir))).toBe(true);
  });

  it("restoreProfile copies vdf and ssfn files back and sets AutoLoginUser", async () => {
    const profileDir = path.join("USER", "profiles", "steam", "acc1");
    (fs.pathExists as any).mockImplementation(async (p: string) => {
      if (p === STEAM_PATH) return true;
      if (p === profileDir) return true;
      if (p.endsWith("loginusers.vdf")) return true;
      if (p.endsWith("config.vdf")) return true;
      return false;
    });

    const execCalls: string[] = [];
    (cp.exec as any).mockImplementation((cmd: string, cb: any) => {
      execCalls.push(cmd);
      if (typeof cb === "function") cb(null, { stdout: "", stderr: "" });
      return { on: vi.fn() };
    });

    await adapter.restoreProfile("acc1");

    const copyCalls = (fs.copy as any).mock.calls.map((c: any[]) => c[0]);
    expect(copyCalls.some((s: string) => s.endsWith("loginusers.vdf"))).toBe(
      true,
    );
    expect(copyCalls.some((s: string) => s.endsWith("config.vdf"))).toBe(true);
    expect(copyCalls.some((s: string) => s.endsWith("ssfn1234567890"))).toBe(
      true,
    );

    expect(execCalls.some((c) => c.includes("AutoLoginUser"))).toBe(true);
    expect(execCalls.some((c) => c.includes("acc1"))).toBe(true);
  });

  it("restoreProfile throws if snapshot is missing", async () => {
    (fs.pathExists as any).mockImplementation(async (p: string) => {
      return p === STEAM_PATH;
    });
    await expect(adapter.restoreProfile("missing")).rejects.toThrow(
      /snapshot not found/i,
    );
  });

  it("launchClient spawns steam.exe", async () => {
    (fs.pathExists as any).mockImplementation(async (p: string) => {
      if (p === STEAM_PATH) return true;
      if (p.endsWith("steam.exe")) return true;
      return false;
    });
    (cp.spawn as any).mockReturnValue({ unref: vi.fn() });

    await adapter.launchClient();
    expect(cp.spawn).toHaveBeenCalled();
    const spawnArgs = (cp.spawn as any).mock.calls[0];
    expect(spawnArgs[0]).toContain("steam.exe");
  });
});
