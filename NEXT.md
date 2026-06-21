# NEXT — SwitchMaster

> Mis à jour le 2026-06-21. Roadmap post-v2.6 (`~/.claude/plans/zesty-honking-llama.md`) : **Phases 0→6 TERMINÉES.**
> Branche `main`, **14 commits d'avance sur origin (non poussés — push sur demande)**.
> État : typecheck OK, **558 tests verts**, build prod OK (`SwitchMaster Setup 2.6.0.exe`).

## 1. Fait (roadmap complète)

- ✅ **Meta** (`b395827`) — docs réalignées, v2.6.0.
- ✅ **P0 sécurité/bugs** (`ebc27c4`) — path-traversal `sm-img`, `<Suspense>`, palette Settings/Lock.
- ✅ **P1 parité designs** (`4a3d9c5`) — pro joignable + Settings partagés + recherche ; modern D&D + filtres + stubs.
- ✅ **P2 DRY** (`4f7c53e`) — `cn()`, `useAccountModal`, deps mortes retirées, `contexts/` supprimé.
- ✅ **P3 perf** (`4904fdb`) — refresh stats gated visibilité, memo.
- ✅ **P4 deps** (`62d03af`) — minors sûrs + `motion` 12.40 + `lucide` v1.
- ✅ **P5 stats Riot** (`fc0ec17`, `538747c`) — tracker.gg fiabilisé (cache/retry) + LCU local opt-in (lecture seule).
- ✅ **P6 features** :
  - `2e71970` — tags/notes/couleur d'accent par compte (+ recherche palette).
  - `6a1a9e0` — hotkeys globaux Alt+1/2/3 (opt-in) + clarification launch-après-switch.
  - `acddf22` — multi-launcher Steam (capture/restore) câblé en prod + UI Settings.

## 2. Suites possibles (non planifiées, optionnelles)

- [ ] Étendre tags/couleur d'accent aux designs **modern** et **pro** (appliqués pour l'instant au design **classic**).
- [ ] Polir l'UI Steam (renommer/supprimer un profil, mapper un profil à un compte, lancement depuis le dashboard) ; implémenter `UbisoftAdapter`/`BattleNetAdapter` sur le même modèle.
- [ ] **Discord Rich Presence** propre (vrai client ID, opt-in) — retiré en v2.6.
- [ ] Deps majeures différées : **Vite 8**, **TypeScript 6** (à évaluer, breaking changes).
- [ ] Distribution signée (mémoire `distribution-signing-pending`).
- [ ] Idées veille : timeline de rang, mode portable, rollback d'update, Windows Hello.

> Écartés à dessein : `AccountCardBase` (les 3 rendus de carte sont volontairement distincts — abstraction fuyante) ; `backgroundThrottling:false` et `clearCache()` webview (contre-productifs ici).

## 3. Décisions clés (rappel)

- État global = custom hooks. Tailwind v4 (`@tailwindcss/vite` + `@theme`). Animations `motion/react` LazyMotion strict (`m`). Validation IPC zod obligatoire. pnpm strict, Node 20.
- **LCU local** : lecture seule + opt-in ; jamais d'automation/anti-cheat ; risque CGU documenté dans l'UI.
- **Steam** : ids de profil validés (zod) + sanitizés (anti-injection chemin/registre).
- Commits sur `main`, **non poussés**. 1 chantier ≈ 1 commit, typecheck+test verts avant chaque commit.
