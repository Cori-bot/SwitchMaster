# NEXT — SwitchMaster

> Mis à jour le 2026-06-21. Roadmap post-v2.6 : Phases 0→6 terminées + retours terrain traités.
> Branche `main` — **2 commits locaux non poussés** (`3bef9f4`, `2af53cb`).
> État : typecheck OK, **553 tests verts**, build prod OK (`SwitchMaster Setup 2.6.0.exe`).

## 1. Fait au dernier tour (retours terrain)

- ✅ **Bugs** (`3bef9f4`) : « Actif: undefined » corrigé à la source (`getStatus` enrichi) ; icônes de rang via SVG locaux (la CSP bloquait tracker.gg).
- ✅ **Suppressions** (`3bef9f4`) : designs **pro + modern** retirés (classic seul, rendu direct, sélecteur retiré) ; **hotkeys Alt** retirés ; `@dnd-kit` retiré.
- ✅ **Finition classic** (`2af53cb`) : recherche + tri (Dashboard) ; feedback de switch (`switchingId` → spinner « Connexion… ») ; notifications d'erreur de switch (`switchError`).

## 2. Reste à faire

### 🎯 Riot login « vraiment automatique » — session-swap (gros morceau, à tester en vrai)

> **Pourquoi pas livré tout de suite** : ça lit/écrit les fichiers de session du Riot Client ; non vérifiable sans un vrai client (risque de casser le login si chemins/format faux). À faire en **opt-in, off par défaut, avec backup** pour ne jamais casser le setup actuel.

Plan d'exécution (modèle TcNo, intégré à l'abstraction `LauncherAdapter` existante) :

1. **`src/main/services/riot/RiotSessionService.ts`** (lecture/écriture, opt-in) :
   - Chemins à capturer/restaurer : `%LOCALAPPDATA%\Riot Games\Riot Client\Data\RiotGamesPrivateSettings.yaml` (identité/session persistée) + `Config\RiotClientSettings.yaml`.
   - `captureSession(accountId)` : kill Riot Client → copier ces fichiers vers `userData/profiles/riot/<accountId>/` (read-only, sûr).
   - `restoreSession(accountId)` : **backup** des fichiers actuels → restaurer le snapshot du compte → relancer le Riot Client (auto-login).
   - `hasSession(accountId)` : snapshot existe ?
2. **`SessionService.switchAccount`** : si session-swap activé ET snapshot présent → `restoreSession` ; sinon **fallback** sur l'automation frappe actuelle (RiotAutomationService).
3. **Config** : `enableRiotSessionSwap?: boolean` (défaut false) dans `src/shared/types.ts`.
4. **IPC + allowlist** : `riot-capture-session` (gated), `riot-has-session`.
5. **UI** (Settings + carte) : toggle « Connexion par session (expérimental) » + bouton « Capturer la session » par compte + badge « session prête ». Avertir : session ~72 h (peut expirer → fallback frappe), peut casser sur grosse maj Riot.
6. **Sécurité/sanitisation** : valider `accountId` (zod) comme pour Steam ; backup avant toute écriture.
7. **Tests** : capture/restore (mock fs-extra) ; fallback quand pas de snapshot.

Sources : TcNo-Acc-Switcher (wiki Riot), hextechdocs. Vanguard NON concerné (fichiers launcher).

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
