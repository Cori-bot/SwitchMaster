import path from "path";

/**
 * Vrai si `target` est un fichier strictement contenu dans `dir`
 * (protection anti path-traversal). Renvoie false pour le dossier lui-même
 * et pour tout chemin qui s'en échappe (`..`) ou sur un autre volume.
 */
export function isInsideDir(dir: string, target: string): boolean {
  const rel = path.relative(path.resolve(dir), path.resolve(target));
  return rel !== "" && !rel.startsWith("..") && !path.isAbsolute(rel);
}
