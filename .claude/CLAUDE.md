# SwitchMaster v2

Switcher de comptes multi-launchers (Riot Games en priorité), application Electron de bureau (Windows).

Stack : Electron 42, React 19, TypeScript 5.9, Vite 7, Vitest 4, Tailwind v4 (`@tailwindcss/vite`), electron-updater, zod
Commands : `pnpm dev`, `pnpm build`, `pnpm test`, `pnpm test:coverage`, `pnpm typecheck`, `pnpm release`
Package manager : pnpm (strict — jamais npm/yarn). Node 20 (figé par la CI).

## Structure

```
src/main/                 — Electron main process
  services/               — logique métier (Account, Config, Security, Session, Stats, System, RiotAutomation, LauncherFactory, launchers/SteamAdapter)
  ipc/                    — handlers par domaine + schemas.ts (zod), utils.ts (safeHandle/parsePayload), types.ts
  interfaces/             — ILauncherService.ts (contrats ILauncherService & LauncherAdapter)
  valorant-api/           — auth Riot OAuth webview (riotWebviewAuth, riotAuthService)
src/renderer/             — React (designs/ {classic,modern,pro} via registry lazy, components/, hooks/, constants/, styles/, utils/)
src/shared/               — types.ts + validation.ts (zod), partagés main/renderer
src/__tests__/            — tests Vitest du main process
src/renderer/__tests__/   — tests Vitest du renderer
src/assets/               — assets statiques (jeux, launchers, branding)
src/scripts/              — scripts PowerShell (automate_login.ps1, detect_games.ps1)
```

## Conventions

- État global : custom hooks (`useConfig`, `useAccountManager`, `useAccounts`, `useSecurity`, `useNotifications`, `useAppIpc`) — PAS de React Context (le dossier `contexts/` est vide).
- UI multi-designs : registry lazy (`src/renderer/designs/registry.ts`), design actif via `config.activeDesignModule` (`classic` | `modern` | `pro`). Tokens de design dans `src/renderer/styles/tokens.css` (`--sm-*`).
- Tailwind v4 : configuré via le plugin `@tailwindcss/vite` + `@theme` dans le CSS — aucun `tailwind.config.js`.
- Animations : framer-motion en mode `LazyMotion` + composant `m` (`import { LazyMotion, domAnimation, m }`) — jamais `motion.*` (strict mode).
- Command palette : `Ctrl/Cmd+K` via `cmdk` (`src/renderer/components/CommandPalette.tsx`).
- Drag & drop (design `pro`) : `@dnd-kit/core` + `sortable` + `utilities`.
- Validation IPC : `zod` (`src/main/ipc/schemas.ts`) + comptes (`src/shared/validation.ts`).
- Sécurité : preload `contextBridge` avec allowlists de canaux, CSP stricte, PIN HMAC-SHA256 timing-safe + anti-brute-force, chiffrement via `safeStorage` (DPAPI).
- Auto-updates : electron-updater (`src/main/updater.ts`).
- Logging : `devLog`/`devError` (`src/main/logger.ts`), electron-log. Coverage : `@vitest/coverage-v8`. Icônes : `lucide-react`.

> Discord RPC a été retiré en v2.6 (placeholder client ID) — aucune dépendance discord, aucun code Discord dans le projet.

Conventions de code détaillées (style, IPC, tests, règles agents) : voir `AGENTS.md` à la racine.
