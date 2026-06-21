import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Compose des classes Tailwind conditionnelles et résout les conflits
 * (la dernière classe gagnante l'emporte). Combine clsx + tailwind-merge.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
