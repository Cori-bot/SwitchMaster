# NEXT — SwitchMaster (roadmap post-v2.6)

> Mis à jour le 2026-06-21. Reprise de session : lis ce fichier, puis `AGENTS.md`.
> Roadmap complète : `~/.claude/plans/zesty-honking-llama.md` (Phases 0→6).
> Branche `main`, **7 commits d'avance sur origin (non poussés)**.

## 1. Avancement

- ✅ **Meta réalignée** (`b395827`) + version 2.6.0.
- ✅ **Phase 0 — correctifs critiques** (`ebc27c4`) : path-traversal `sm-img`, `<Suspense>`, palette Settings/Lock.
- ✅ **Phase 1 — parité designs** (`4a3d9c5`) : `pro` joignable + Settings partagés + recherche ; `modern` D&D + filtres + stubs câblés.
- ✅ **Phase 2 — DRY/conventions** (`4f7c53e`) : `cn()`, `useAccountModal` (dedup 3 designs), deps mortes retirées (marked/dompurify/chokidar/yaml), `contexts/` supprimé.
- ✅ **Phase 3 — perf** (`4904fdb`) : refresh stats gated sur visibilité, memo `cardStyle`. (Dashboard/AccountCard déjà memo ; backgroundThrottling/clearCache écartés car contre-productifs.)
- ✅ **Phase 4 — deps** (`62d03af`) : react 19.2.7, electron-updater 6.8.9, zod 4.4.3, tailwind 4.3.1 ; **framer-motion → motion 12.40** ; **lucide-react 1.21**. (Vite 8 / TS 6 volontairement écartés : majeurs risqués non demandés.)
- **État** : typecheck OK, **550 tests verts**, build prod OK (`SwitchMaster Setup 2.6.0.exe`).

## 2. Reste à faire

### Phase 5 — Stats & intégration Riot légitime ← _next, décision requise (clés API)_

- `RiotApiService` (RGAPI : rank LoL league-v4/summoner-v4, account-v1) — **nécessite une clé API utilisateur** (developer.riotgames.com).
- `HenrikService` (MMR/RR Valorant — clé gratuite HenrikDev).
- `LcuLocalService` (lockfile `%LOCALAPPDATA%/Riot Games/Riot Client/Config/lockfile`, REST local) — **opt-in, lecture seule, risque CGU moyen/élevé**.
- UI Settings pour saisir/chiffrer les clés ; cache + fallback gracieux ; remplacement progressif de tracker.gg dans `StatsService`.
- **Approche clés** : champ Settings où l'utilisateur colle sa clé (chiffrée via safeStorage), fallback tracker.gg si absente → pas de clé en dur, pas de blocage.

### Phase 6 — Nouvelles features (à prioriser)

Hotkeys globaux (Alt+1/2/3), launch après switch, tags/notes de compte, couleur d'accent, **multi-launcher** (câbler `SteamAdapter` en prod + IPC/UI ; puis Epic/EA/Battle.net/Ubisoft), **Discord RPC** (ré-implémentation propre opt-in). Plus tard : timeline rank, mode portable, rollback update, Windows Hello.

## 3. Décisions clés (rappel)

- État global = custom hooks. Tailwind v4 (`@tailwindcss/vite` + `@theme`). Animations `motion/react` en LazyMotion strict (`m`, jamais `motion.*`). Validation IPC zod obligatoire. pnpm strict, Node 20.
- **LCU local** : lecture seule + opt-in + détection compte connecté uniquement ; jamais d'automation/anti-cheat ; risque CGU à documenter.
- Commits sur `main`, non poussés (push uniquement sur demande). 1 phase ≈ 1 commit, typecheck+test verts avant chaque commit.
