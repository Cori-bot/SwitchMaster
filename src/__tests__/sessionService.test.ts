import { describe, it, expect, vi, beforeEach } from "vitest";
import { SessionService } from "../main/services/SessionService";

describe("SessionService", () => {
  let service: SessionService;
  let mockAcc: any;
  let mockAuto: any;
  let mockCfg: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockAcc = {
      getCredentials: vi
        .fn()
        .mockResolvedValue({ username: "u", password: "p" }),
    };
    mockAuto = {
      killProcesses: vi.fn(),
      launchClient: vi.fn(),
      login: vi.fn(),
      loginLegacy: vi.fn(),
    };
    mockCfg = {
      getConfig: vi.fn().mockReturnValue({ riotPath: "R" }),
      saveConfig: vi.fn(),
    };
    service = new SessionService(mockAcc, mockAuto, mockCfg);
  });

  it("switchAccount success (Line 23-53)", async () => {
    expect(await service.switchAccount("id")).toBe(true);
    expect(mockAuto.launchClient).toHaveBeenCalled();
  });

  it("switchAccount launches the client (path resolution déléguée à launchClient)", async () => {
    mockCfg.getConfig.mockReturnValue({ riotPath: "C:\\Riot" });
    await service.switchAccount("id");
    // SessionService ne construit plus le chemin de l'exe : launchClient()
    // lit lui-même le chemin via configService.getRiotPath(). Il est donc
    // appelé sans argument.
    expect(mockAuto.launchClient).toHaveBeenCalledWith();
  });

  it("switchAccount calls loginLegacy with credentials", async () => {
    await service.switchAccount("id");
    expect(mockAuto.loginLegacy).toHaveBeenCalledWith("u", "p");
  });

  it("switchAccount handles error (Line 55)", async () => {
    mockAcc.getCredentials.mockRejectedValue(new Error("FAIL"));
    await expect(service.switchAccount("id")).rejects.toThrow();
  });
});
