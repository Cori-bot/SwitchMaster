# NEXT — SwitchMaster (roadmap post-v2.6)

> Mis à jour le 2026-06-21. Reprise de session : lis ce fichier, puis `AGENTS.md`.
> Roadmap complète : `~/.claude/plans/zesty-honking-llama.md` (Phases 0→6).
> Branche `main`, **10 commits d'avance sur origin (non poussés)**.

## 1. Avancement

- ✅ **Meta** (`b395827`) — docs réalignées, version 2.6.0.
- ✅ **Phase 0 — sécurité/bugs** (`ebc27c4`) — path-traversal `sm-img`, `<Suspense>`, palette Settings/Lock.
- ✅ **Phase 1 — parité designs** (`4a3d9c5`) — `pro` joignable + Settings partagés + recherche ; `modern` D&D + filtres + stubs.
- ✅ **Phase 2 — DRY/conventions** (`4f7c53e`) — `cn()`, `useAccountModal`, deps mortes retirées, `contexts/` supprimé.
- ✅ **Phase 3 — perf** (`4904fdb`) — refresh stats gated visibilité, memo `cardStyle`.
- ✅ **Phase 4 — deps** (`62d03af`) — react 19.2.7, electron-updater 6.8.9, zod 4.4.3, tailwind 4.3.1, **framer-motion → motion 12.40**, **lucide-react 1.21**. (Vite 8 / TS 6 écartés.)
- ✅ **Phase 5a — tracker.gg fiabilisé** (`fc0ec17`) — `StatsService` cache (TTL) + fallback dernière valeur + retry/backoff (skip 403/404/429).
- **État** : typecheck OK, **550 tests verts**, build prod OK (`SwitchMaster Setup 2.6.0.exe`).

## 2. Reste à faire

### Phase 5b — LCU local (opt-in, lecture seule) ← next

- Nouveau `src/main/services/LcuLocalService.ts` : lit le lockfile `%LOCALAPPDATA%/Riot Games/Riot Client/Config/lockfile` (via `process.env.LOCALAPPDATA`), parse `name:pid:port:password:protocol`, requête `https://127.0.0.1:{port}` (Basic `riot:password`, `rejectUnauthorized:false`) pour le compte/alias actif. `null` si client non lancé.
- Config : `enableLcuDetection?: boolean` (défaut **false**) dans `src/shared/types.ts`.
- IPC : handler `get-lcu-active-account` (gated sur le flag) + ajout à l'allowlist `INVOKE_CHANNELS` du preload.
- UI : toggle dans `Settings.tsx` + affichage read-only du compte détecté. **Avertir du risque CGU** (API non supportée par Riot).
- Tests : mock `fs-extra` + `https`.

### Phase 6 — Features (les 4 retenues, dans l'ordre)

- **6a — Tags/notes + couleur d'accent** : `Account.tags?: string[]`, `notes?: string`, `accentColor?: string` (+ schéma zod). UI `AddAccountModal`, affichage cartes (accent), recherche par tag dans `CommandPalette`.
- **6b — Hotkeys globaux** : `electron.globalShortcut` (Alt+1/2/3 → switch favoris/ordre) dans `main.ts`, nettoyés au quit ; config bindings. (Pas de nouvelle dep.)
- **6c — Launch jeu après switch** : config `autoLaunchAfterSwitch?: boolean` + câblage `App.handleSwitch`.
- **6d — Multi-launcher Steam** : câbler `SteamAdapter` (code mort actuel) via IPC (`captureProfile`/`restoreProfile`) + UI (launcherType `steam`). Gros morceau, à isoler.

> Différé (jugé non prioritaire/risqué) : Discord RPC propre, timeline rank, mode portable, rollback update, Windows Hello. `AccountCardBase` volontairement écarté (les 3 rendus de carte sont intentionnellement distincts — abstraction fuyante).

## 3. Décisions clés (rappel)

- État global = custom hooks. Tailwind v4 (`@tailwindcss/vite` + `@theme`). Animations `motion/react` en LazyMotion strict (`m`, jamais `motion.*`). Validation IPC zod obligatoire. pnpm strict, Node 20.
- **LCU local** : lecture seule + opt-in + détection compte connecté uniquement ; jamais d'automation/anti-cheat ; risque CGU à documenter.
- Commits sur `main`, **non poussés** (push uniquement sur demande). 1 phase ≈ 1 commit, typecheck+test verts avant chaque commit.
