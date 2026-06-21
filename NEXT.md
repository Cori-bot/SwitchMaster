# NEXT — SwitchMaster

> Mis à jour le 2026-06-21. Roadmap post-v2.6 + retours terrain traités. Tout poussé sur `origin/main`.
> État : typecheck OK, **559 tests verts**, build prod OK (`SwitchMaster Setup 2.6.0.exe`).

## 1. Fait au dernier tour (retours terrain)

- ✅ **Bugs** (`3bef9f4`) : « Actif: undefined » corrigé à la source (`getStatus` enrichi) ; icônes de rang via SVG locaux (la CSP bloquait tracker.gg).
- ✅ **Suppressions** (`3bef9f4`) : designs **pro + modern** retirés (classic seul, rendu direct, sélecteur retiré) ; **hotkeys Alt** retirés ; `@dnd-kit` retiré.
- ✅ **Finition classic** (`2af53cb`) : recherche + tri (Dashboard) ; feedback de switch (`switchingId` → spinner « Connexion… ») ; notifications d'erreur de switch (`switchError`).

## 2. Reste à faire

### ✅ Riot login session-swap — IMPLÉMENTÉ (`b2a80e3`), À TESTER EN CONDITIONS RÉELLES

- `src/main/services/riot/RiotSessionService.ts` : capture/restore des fichiers de session Riot Client (`Data/RiotGamesPrivateSettings.yaml` + `Config/RiotClientSettings.yaml`) avec **backup** avant restauration ; intégré au flux `launch-game` (main.ts) avec **fallback frappe clavier** en cas d'échec ; opt-in `enableRiotSessionSwap` (défaut off) ; IPC `riot-capture-session`/`riot-has-session` (zod + allowlist) ; toggle Settings + item « Capturer la session » dans le menu ⋮ de la carte ; tests fs-extra.
- **À VÉRIFIER en vrai** (je ne peux pas sans ton client Riot) :
  1. Connecte-toi à un compte, active le toggle (Paramètres → « Connexion Riot par session »), capture la session (menu ⋮ de la carte).
  2. Bascule sur un autre compte, recapture, puis reswitch → doit relancer en **auto-login sans taper le mot de passe**.
  3. Si ça ne logue pas : ajuster la liste `RIOT_SESSION_FILES` dans `RiotSessionService.ts` (les fichiers de session ont pu bouger). Le **backup** (`userData/profiles/riot/__backup__`) permet de revenir en arrière.
  4. Expiration (~72 h) → doit retomber sur la frappe clavier (fallback).

### Finition classic — reste

- [ ] **« Dernière utilisation »** par compte : poser `lastUsed` (timestamp) côté `AccountService.switchAccount` + afficher « il y a X » sur la carte (skeletons stats déjà présents).

### Plus tard (demande explicite : « on le fera plus tard »)

- [ ] **Système launcher unifié** : UI commune pour Steam (déjà câblé) + autres launchers (Epic/EA/Battle.net/Ubisoft) — gestion des profils capturés, mapping profil↔compte, lancement depuis le dashboard. Aujourd'hui Steam est exposé via Settings (capture/restore) mais pas intégré au flux de comptes.

### Divers / différé

- [ ] Deps majeures : Vite 8, TypeScript 6 (à évaluer).
- [ ] Distribution signée (mémoire `distribution-signing-pending`).

## 3. Décisions clés (rappel)

- **Un seul design : classic.** État global = custom hooks. Tailwind v4. Animations `motion/react` LazyMotion strict (`m`). Validation IPC zod. pnpm strict, Node 20.
- Login Riot : **session-swap opt-in + fallback frappe** (validé). Jamais d'automation anti-cheat.
- Commits sur `main`, **non poussés** (push sur demande). 1 chantier ≈ 1 commit, typecheck+test verts avant chaque commit.
