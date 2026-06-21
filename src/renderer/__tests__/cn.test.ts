import { describe, it, expect } from "vitest";
import { cn } from "../utils/cn";

describe("cn", () => {
  it("ignore les valeurs falsy et concatène", () => {
    expect(cn("text-white", false && "hidden", undefined, "font-bold")).toBe(
      "text-white font-bold",
    );
  });

  it("résout les conflits Tailwind (dernier gagnant)", () => {
    expect(cn("p-2", "p-4")).toBe("p-4");
    expect(cn("text-red-500", "text-blue-500")).toBe("text-blue-500");
  });
});
