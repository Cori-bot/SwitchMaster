import { describe, it, expect } from "vitest";
import path from "path";
import { isInsideDir } from "../main/utils/pathSafety";

describe("isInsideDir (garde anti path-traversal sm-img)", () => {
  const base = path.resolve("/data/switchmaster/account-images");

  it("autorise un fichier directement dans le dossier", () => {
    expect(isInsideDir(base, path.join(base, "abc.png"))).toBe(true);
  });

  it("autorise un fichier dans un sous-dossier", () => {
    expect(isInsideDir(base, path.join(base, "sub", "abc.png"))).toBe(true);
  });

  it("refuse une remontée de répertoire (..)", () => {
    expect(isInsideDir(base, path.join(base, "..", "..", "secret.txt"))).toBe(
      false,
    );
  });

  it("refuse un chemin système absolu", () => {
    expect(isInsideDir(base, "C:/Windows/System32/config/SAM")).toBe(false);
    expect(isInsideDir(base, "/etc/passwd")).toBe(false);
  });

  it("refuse le dossier lui-même", () => {
    expect(isInsideDir(base, base)).toBe(false);
  });

  it("refuse un dossier voisin au préfixe identique", () => {
    expect(isInsideDir(base, base + "-evil/leak.png")).toBe(false);
  });
});
