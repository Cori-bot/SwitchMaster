import { describe, it, expect, vi, beforeEach } from "vitest";
import fs from "fs-extra";
import { LcuLocalService } from "../main/services/LcuLocalService";

vi.mock("fs-extra");

describe("LcuLocalService (lecture seule, opt-in)", () => {
  const svc = new LcuLocalService();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("parse le lockfile (name:pid:port:password:protocol)", async () => {
    (fs.readFile as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(
      "Riot Client:1234:52000:secretpw:https",
    );
    expect(await svc.readLockfile()).toEqual({
      port: 52000,
      password: "secretpw",
      protocol: "https",
    });
  });

  it("renvoie null si le lockfile est absent (client non lancé)", async () => {
    (fs.readFile as unknown as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error("ENOENT"),
    );
    expect(await svc.readLockfile()).toBeNull();
    expect(await svc.isRiotClientRunning()).toBe(false);
    expect(await svc.getActiveAccount()).toBeNull();
  });

  it("renvoie null si le lockfile est malformé", async () => {
    (fs.readFile as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(
      "garbage",
    );
    expect(await svc.readLockfile()).toBeNull();
  });

  it("isRiotClientRunning = true quand le lockfile est présent", async () => {
    (fs.readFile as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(
      "Riot Client:1:52000:pw:https",
    );
    expect(await svc.isRiotClientRunning()).toBe(true);
  });
});
