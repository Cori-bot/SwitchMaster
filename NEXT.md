# NEXT — SwitchMaster v2.6 → roadmap post-v2.6

> Mis à jour le 2026-06-21. Reprise de session : lis ce fichier en premier, puis `AGENTS.md`.
> Roadmap complète approuvée : `~/.claude/plans/zesty-honking-llama.md` (Phases 0→6).

## 1. État courant

**Fait / marche :**

- v2.6 finalisée. Designs interchangeables (`classic`/`modern`/`pro`, registry lazy), command palette `Ctrl/Cmd+K`, sécurité durcie (zod IPC, PIN timing-safe, CSP, sandbox), abstraction launchers (`SteamAdapter` testé). Tests verts, CI Windows (Node 20, pnpm 9).
- **Docs/meta réalignées** (commit `b395827`) : `AGENTS.md`, `.claude/CLAUDE.md`, `README.md`, `package.json` (→ 2.6.0), `.claude/settings.json`, `.gitignore`, `NEXT.md`.
- **✅ Phase 0 — correctifs critiques (commit `ebc27c4`)** :
  - Sécurité : `sm-img` restreint à `userData/account-images` (anti path-traversal) + helper testé `isInsideDir` (`src/main/utils/pathSafety.ts`).
  - `<Suspense>` ajouté autour des designs lazy (`App.tsx`).
  - Command palette : « Settings » câblé (signal global `openSettingsSignal` → designs), « Lock » verrouille vraiment (ou propose de définir un PIN) via `useSecurity.lock`.
  - `ClassicLayout` réagit au signal d'ouverture des réglages.
  - Tests : `pathSafety.test.ts` + 2 cas `CommandPalette` (Settings/Lock). **536 tests verts.**

**Reste / points d'attention (non encore traités) :**

- [ ] **LauncherAdapter = code mort runtime** (`SteamAdapter`/`getAdapter`/`captureProfile`…) → câbler (Phase 6) ou marquer « expérimental ».
- [ ] **Designs non à parité** : `pro` injoignable depuis l'UI + sans page Settings ; `modern` sans drag&drop, filtres incomplets, stubs (`GameView.handleChangePath`, backgrounds par défaut, toggle autoUpdate). → **Phase 1**.
- [ ] **Deps déclarées non importées** : `marked`, `dompurify`, `chokidar`, `yaml` (à retirer) ; `clsx`/`tailwind-merge` (à activer via util `cn()`). → **Phase 2**.
- [ ] **`src/renderer/contexts/`** : dossier vide → suppression (Phase 2).
- [ ] **Perf** : `backgroundThrottling`, fuite mémoire webview auth, stats liées à la visibilité, re-renders. → **Phase 3**.
- [ ] **Deps majeurs** : `framer-motion → motion`, `lucide-react` v1. → **Phase 4**.
- [ ] **Stats** : migrer tracker.gg → RGAPI + HenrikDev + LCU local (opt-in, lecture seule, risque CGU à documenter). → **Phase 5**.
- [ ] **Discord RPC** : ré-implémentation propre (Phase 6). Distribution non signée (mémoire `distribution-signing-pending`).

## 2. Décisions clés

- **Périmètre validé** : tout, phasé sur plusieurs sessions ; modern + pro **à parité** avec classic ; stats via **RGAPI + HenrikDev + LCU local** ; **upgrades majeurs inclus**.
- **LCU local** = lecture seule + opt-in + détection du compte connecté uniquement ; jamais d'automation/anti-cheat ; risque CGU moyen/élevé à documenter.
- État global = custom hooks (pas de Context). Tailwind v4 (`@tailwindcss/vite` + `@theme`, pas de `tailwind.config.js`). framer-motion en LazyMotion strict (`m`, jamais `motion.*`). Validation IPC zod obligatoire. pnpm strict, Node 20.
- L'allowlist Bash de `.claude/settings.json` n'a pas pu être posée auto (garde-fou anti-auto-permission) → via `/update-config` si besoin.

## 3. Prochaine étape — Phase 1 (parité des designs)

Référence = `classic`. Voir le plan pour le détail. Grandes lignes :

- **1A pro** : ajouter `pro` aux sélecteurs (`src/renderer/components/Settings.tsx`, `src/renderer/designs/modern/pages/SettingsPage.tsx`) ; page Settings pour pro (réutiliser un composant partagé) ; consommer `openSettingsSignal` dans `ProLayout` ; câbler la recherche du `TopBar` pro.
- **1B modern** : drag&drop `@dnd-kit` (réutiliser `designs/pro/AccountList.tsx`) → `actions.reorderAccounts` ; finir les filtres par launcher ; câbler les stubs ; consommer `openSettingsSignal` dans `ModernLayout`.
- **1C tests** : composants modern + pro + test de bascule de design.

## 4. Checklist phases restantes

- [ ] **Phase 1** — parité designs (modern + pro = classic) ← _next_
- [ ] **Phase 2** — réutilisation & conventions (cn(), hooks partagés, rankFormatter, AccountCardBase, nettoyage deps mortes + `contexts/`)
- [ ] **Phase 3** — performance (backgroundThrottling, webview destroy, stats/visibilité, re-renders)
- [ ] **Phase 4** — dépendances (patches sûrs + majeurs : motion, lucide v1)
- [ ] **Phase 5** — stats Riot légitimes (RGAPI + HenrikDev + LCU local opt-in)
- [ ] **Phase 6** — nouvelles features (hotkeys, launch après switch, tags, multi-launcher, Discord RPC…)
