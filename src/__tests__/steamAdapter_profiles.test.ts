import { describe, it, expect, vi, beforeEach } from "vitest";
import fs from "fs-extra";
import { SteamAdapter } from "../main/services/launchers/SteamAdapter";

vi.mock("fs-extra");
vi.mock("electron", () => ({
  app: { getPath: () => "C:/userData" },
}));

describe("SteamAdapter.listProfiles", () => {
  const adapter = new SteamAdapter();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("liste les sous-dossiers de profils capturés", async () => {
    (fs.readdir as unknown as ReturnType<typeof vi.fn>).mockResolvedValue([
      "acc1",
      "acc2",
    ]);
    (fs.stat as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      isDirectory: () => true,
    });
    expect(await adapter.listProfiles()).toEqual(["acc1", "acc2"]);
  });

  it("ignore les entrées qui ne sont pas des dossiers", async () => {
    (fs.readdir as unknown as ReturnType<typeof vi.fn>).mockResolvedValue([
      "acc1",
      "stray.txt",
    ]);
    (fs.stat as unknown as ReturnType<typeof vi.fn>).mockImplementation(
      (p: string) => ({
        isDirectory: () => !p.endsWith(".txt"),
      }),
    );
    expect(await adapter.listProfiles()).toEqual(["acc1"]);
  });

  it("renvoie [] si le dossier de profils n'existe pas", async () => {
    (fs.readdir as unknown as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error("ENOENT"),
    );
    expect(await adapter.listProfiles()).toEqual([]);
  });
});
