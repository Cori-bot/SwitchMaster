# NEXT — SwitchMaster

> Mis à jour le 2026-06-21. Roadmap post-v2.6 + retours terrain traités. Tout poussé sur `origin/main`.
> État : typecheck OK, **553 tests verts**, build prod OK (`SwitchMaster Setup 2.6.0.exe`).

## 1. Fait au dernier tour (retours terrain)

- ✅ **Bugs** (`3bef9f4`) : « Actif: undefined » corrigé à la source (`getStatus` enrichi) ; icônes de rang via SVG locaux (la CSP bloquait tracker.gg).
- ✅ **Suppressions** (`3bef9f4`) : designs **pro + modern** retirés (classic seul, rendu direct, sélecteur retiré) ; **hotkeys Alt** retirés ; `@dnd-kit` retiré.
- ✅ **Finition classic** (`2af53cb`) : recherche + tri (Dashboard) ; feedback de switch (`switchingId` → spinner « Connexion… ») ; notifications d'erreur de switch (`switchError`).

## 2. Reste à faire

### ❌ Riot login session-swap — RETIRÉ (`af5e6db`) : incompatible avec le RSO actuel

Testé en conditions réelles : la capture fonctionnait, mais Riot **rejette la session restaurée** (`riot-login: Failed to authenticate with persisted login state` / `400 No RSO authorization` → page de login). Cause confirmée (logs Riot Client + recherche web TcNo / RiotSwitcher / valapidocs-techchrism) : les cookies RSO « Rester connecté » sont **rotatifs / à usage unique** (le `ssid` tourne à chaque ré-auth ; durée ~1 semaine) → un fichier de session copié devient périmé immédiatement. Même TcNo a des issues 2026 non résolues (#440/#510). Le file-swap n'est PAS une méthode de login fiable pour le Riot Client actuel.

**Décision validée : connexion Riot = frappe du mot de passe automatisée**, fiabilisée : focus de fenêtre robuste (Win32 `SetForegroundWindow` + restore + vérif, re-focus par champ) dans `automate_login.ps1`, presse-papier (indépendant AZERTY/IME), et **kill complet** de tous les process Riot avant relance (gardé du travail session-swap).

### Finition classic — reste

- [ ] **« Dernière utilisation »** par compte : poser `lastUsed` (timestamp) côté `AccountService.switchAccount` + afficher « il y a X » sur la carte (skeletons stats déjà présents).

### Plus tard (demande explicite : « on le fera plus tard »)

- [ ] **Système launcher unifié** : UI commune pour Steam (déjà câblé) + autres launchers (Epic/EA/Battle.net/Ubisoft) — gestion des profils capturés, mapping profil↔compte, lancement depuis le dashboard. Aujourd'hui Steam est exposé via Settings (capture/restore) mais pas intégré au flux de comptes.

### Divers / différé

- [ ] Deps majeures : Vite 8, TypeScript 6 (à évaluer).
- [ ] Distribution signée (mémoire `distribution-signing-pending`).

## 3. Décisions clés (rappel)

- **Un seul design : classic.** État global = custom hooks. Tailwind v4. Animations `motion/react` LazyMotion strict (`m`). Validation IPC zod. pnpm strict, Node 20.
- Login Riot : **frappe du mot de passe automatisée** (session-swap retiré, incompatible RSO 2026 — cookies rotatifs). Jamais d'automation anti-cheat.
- Commits sur `main`, poussés sur `origin` au fil de l'eau. 1 chantier ≈ 1 commit, typecheck+test verts avant chaque commit.
