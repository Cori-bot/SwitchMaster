/// <reference types="vite/client" />
// Icônes de rang servies depuis les assets locaux (bundlés) plutôt que depuis
// des URLs externes (tracker.gg) — ces dernières sont bloquées par la CSP
// (img-src 'self' data: blob: sm-img:).

const leagueGlob = import.meta.glob(
  "../../assets/games/league-of-legends/*.svg",
  { eager: true, query: "?url", import: "default" },
) as Record<string, string>;

const valorantGlob = import.meta.glob("../../assets/games/valorant/*.svg", {
  eager: true,
  query: "?url",
  import: "default",
}) as Record<string, string>;

function indexByName(glob: Record<string, string>): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [p, url] of Object.entries(glob)) {
    const name = p
      .split("/")
      .pop()!
      .replace(/\.svg$/, "");
    out[name] = url;
  }
  return out;
}

const LEAGUE = indexByName(leagueGlob);
const VALORANT = indexByName(valorantGlob);

/**
 * Résout l'URL de l'icône de rang locale.
 * - League : tier (premier mot) -> `silver.svg`, etc.
 * - Valorant : `diamond 1` -> `diamond_1.svg`, `radiant` -> `radiant.svg`.
 * Renvoie null si aucun asset ne correspond (ex: Valorant Unranked).
 */
export function getRankIconUrl(
  gameType: "league" | "valorant",
  rank?: string | null,
): string | null {
  if (!rank) return null;
  const lower = rank.toLowerCase().trim();

  if (gameType === "league") {
    if (lower === "unranked") return LEAGUE["unranked"] ?? null;
    const tier = lower.split(" ")[0];
    return LEAGUE[tier] ?? LEAGUE["unranked"] ?? null;
  }

  const key = lower.replace(/\s+/g, "_");
  return VALORANT[key] ?? null;
}
