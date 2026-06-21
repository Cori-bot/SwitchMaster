import { describe, it, expect, vi, beforeEach } from "vitest";
import fs from "fs-extra";
import { RiotSessionService } from "../main/services/riot/RiotSessionService";

vi.mock("fs-extra");
vi.mock("electron", () => ({
  app: { getPath: () => "C:/userData" },
}));

const mock = (fn: unknown) => fn as ReturnType<typeof vi.fn>;

describe("RiotSessionService (session-swap, expérimental)", () => {
  const svc = new RiotSessionService();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("hasSession = false sans snapshot", async () => {
    mock(fs.pathExists).mockResolvedValue(false);
    expect(await svc.hasSession("a1")).toBe(false);
  });

  it("hasSession = true si le fichier clé existe", async () => {
    mock(fs.pathExists).mockResolvedValue(true);
    expect(await svc.hasSession("a1")).toBe(true);
  });

  it("captureSession = no-client si aucun fichier de session", async () => {
    mock(fs.pathExists).mockResolvedValue(false);
    expect(await svc.captureSession("a1")).toBe("no-client");
    expect(fs.copy).not.toHaveBeenCalled();
  });

  it("captureSession = no-session si persist null (Rester connecté off)", async () => {
    mock(fs.pathExists).mockResolvedValue(true);
    mock(fs.readFile).mockResolvedValue("riot-login:\n    persist: null\n");
    mock(fs.ensureDir).mockResolvedValue(undefined);
    mock(fs.copy).mockResolvedValue(undefined);
    expect(await svc.captureSession("a1")).toBe("no-session");
  });

  it("captureSession = ok si une session persistée existe", async () => {
    mock(fs.pathExists).mockResolvedValue(true);
    mock(fs.readFile).mockResolvedValue("riot-login:\n    persist: true\n");
    mock(fs.ensureDir).mockResolvedValue(undefined);
    mock(fs.copy).mockResolvedValue(undefined);
    expect(await svc.captureSession("a1")).toBe("ok");
    expect(fs.copy).toHaveBeenCalled();
  });

  it("restoreSession lève une erreur sans snapshot", async () => {
    mock(fs.pathExists).mockResolvedValue(false);
    await expect(svc.restoreSession("a1")).rejects.toThrow();
  });

  it("restoreSession backup puis restaure quand un snapshot existe", async () => {
    mock(fs.pathExists).mockResolvedValue(true);
    mock(fs.ensureDir).mockResolvedValue(undefined);
    mock(fs.copy).mockResolvedValue(undefined);
    await svc.restoreSession("a1");
    // backup (fichiers courants) + restauration (snapshot) -> plusieurs copies
    expect(mock(fs.copy).mock.calls.length).toBeGreaterThanOrEqual(2);
  });
});
