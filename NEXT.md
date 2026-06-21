# NEXT — SwitchMaster v2.6

> Mis à jour le 2026-06-21. Reprise de session : lis ce fichier en premier, puis `AGENTS.md`.

## 1. État courant

**Fait / marche :**

- v2.6 finalisée (commits `9bfa8da..d5fc629` sur `main`). Avant le commit de réalignement doc, `main` == `origin/main`.
- Système de **designs interchangeables** : `classic`, `modern`, `pro` via un registry lazy (`src/renderer/designs/registry.ts`), design actif piloté par `config.activeDesignModule` (défaut main-process = `modern`, fallback runtime = `classic`).
- Design `pro` : liste de comptes réordonnable en **drag & drop** (`@dnd-kit`).
- **Perf** : code-splitting par design + vendor chunks (`vite.config.ts`), animations en `LazyMotion + m`.
- **Command palette** `Ctrl/Cmd+K` (`cmdk`, `src/renderer/components/CommandPalette.tsx`).
- **Sécurité durcie** : validation IPC zod (`src/main/ipc/schemas.ts`), PIN HMAC-SHA256 timing-safe + anti-brute-force, CSP stricte, `sandbox:true`, allowlists preload, permissions refusées par défaut, `safeStorage` (DPAPI).
- **Abstraction launchers** : interfaces `ILauncherService` + `LauncherAdapter`, `LauncherFactory`, `SteamAdapter` (implémenté + 9 tests).
- Tests verts, typecheck OK. CI Windows (Node 20, pnpm 9) : install → typecheck → test.
- **Docs/meta réalignées** sur le code réel (ce commit) : `AGENTS.md`, `.claude/CLAUDE.md`, `README.md`, `package.json` (→ 2.6.0), `.claude/settings.json`, `.gitignore`, ce `NEXT.md`.

**Reste / points d'attention (issus de l'analyse v2.6) :**

- [ ] **LauncherAdapter = code mort runtime** : `SteamAdapter` / `getAdapter` / `captureProfile` / `restoreProfile` ne sont appelés par aucun code de prod (uniquement les tests). À câbler (IPC + UI + `SessionService`) ou marquer explicitement « expérimental ».
- [ ] **Design `pro` injoignable depuis l'UI** : les sélecteurs (classic `Settings.tsx`, modern `SettingsPage.tsx`) n'offrent que `classic`/`modern`. `pro` n'est sélectionnable qu'en éditant la config.
- [ ] **Pas de `<Suspense>`** autour des designs lazy dans `App.tsx` (React 19) — masqué par les tests (chunks résolus en eager). À vérifier en build de prod / chargement lent.
- [ ] **Command palette** : l'item « Settings » est un no-op (`onOpenSettings` non passée à `<CommandPalette>` dans `App.tsx`) ; le libellé « Lock » ouvre en fait le modal de définition de PIN (`openSecurityModal('set')`).
- [ ] **Deps déclarées mais jamais importées** : `marked`, `dompurify`, `chokidar`, `yaml`, `clsx`, `tailwind-merge`. À retirer après vérif, ou à utiliser (ex. util `cn()` avec clsx+tailwind-merge).
- [ ] **`src/renderer/contexts/`** : dossier vide (mort) — candidat à suppression.
- [ ] **`sm-img` protocol** (`src/main/main.ts`) : sert n'importe quel fichier local sans garde anti-path-traversal. À restreindre.
- [ ] **Discord RPC** : retiré en v2.6 (client ID placeholder). À ré-implémenter proprement si souhaité.
- [ ] Distribution non signée (mémoire `distribution-signing-pending`) ; stats via `tracker.gg` fragile (mémoire `stats-api-tracker-gg`).

## 2. Décisions clés

- **État global = custom hooks**, PAS de React Context (`contexts/` vide).
- **Tailwind v4** via plugin `@tailwindcss/vite` + `@theme` dans le CSS — aucun `tailwind.config.js`. Tokens dans `src/renderer/styles/tokens.css` (`--sm-*`).
- **framer-motion en LazyMotion strict** : importer `m`, jamais `motion.*`.
- **Validation IPC obligatoire** côté main via zod avant tout traitement.
- **pnpm strict** (jamais npm/yarn). **Node 20** (figé CI).
- **Version 2.6.0** (bump effectué dans ce commit).

## 3. Fichiers modifiés (commit de réalignement)

- `package.json` — version 2.5.1 → 2.6.0
- `AGENTS.md` — Electron 42, état via hooks, `designs/` (au lieu de layouts/contexts), Tailwind v4, LazyMotion, Node 20, liste services/ipc
- `.claude/CLAUDE.md` — structure réelle, retrait de Discord RPC, ajout cmdk/dnd-kit/zod/electron-log
- `README.md` — badge version 2.6.0, fonctionnalités (Cmd+K, designs, sécurité)
- `.claude/settings.json` — NOUVEAU : hook SessionStart (pointe vers AGENTS.md/NEXT.md)
- `.gitignore` — ignore `.claude-session.tmp` et `.claude/settings.local.json`
- `NEXT.md` — NOUVEAU (ce fichier)

## 4. Tâches restantes (checklist priorisée)

1. [ ] Câbler ou marquer « expérimental » l'abstraction LauncherAdapter/SteamAdapter.
2. [ ] Exposer le design `pro` dans les sélecteurs (ou retirer du type).
3. [ ] Ajouter un `<Suspense fallback>` autour de `<CurrentDesign>` dans `App.tsx`.
4. [ ] Corriger l'item « Settings » de la command palette (passer `onOpenSettings`).
5. [ ] Décider du sort des deps inutilisées (`marked`, `dompurify`, `chokidar`, `yaml`, `clsx`, `tailwind-merge`).
6. [ ] Supprimer `src/renderer/contexts/` si confirmé vide.
7. [ ] Sécuriser le handler de protocole `sm-img` (anti-path-traversal).

---

> Note : ce `NEXT.md` documente l'état post-v2.6. Une initiative plus large (audit complet, finition design, perf, veille concurrentielle, nouvelles features) est en cours de cadrage — voir le plan associé.
