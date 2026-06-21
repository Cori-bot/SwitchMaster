# SwitchMaster 2.6.0

Une grosse mise à jour centrée sur la **fiabilité de la connexion Riot**, des **comptes plus riches**, une **sécurité renforcée** et de meilleures **performances**.

> Application de bureau Windows pour basculer entre vos comptes Riot (League of Legends / Valorant) en un clic.

---

## ✨ Nouveautés

- **Connexion Riot vraiment fiable.** La saisie automatique des identifiants a été durcie : la fenêtre du client Riot est ramenée au premier plan de façon robuste (plusieurs tentatives, restauration si réduite) et la frappe passe par le presse-papier — compatible **AZERTY / claviers spéciaux**.
- **Diagnostic de connexion en temps réel.** SwitchMaster lit désormais les **logs du client Riot** pour connaître le **vrai résultat** d'une connexion et l'afficher clairement :
  - ✅ Connexion réussie / session restaurée
  - ❌ Identifiants incorrects, **trop de tentatives** (rate-limit), compte suspendu
  - 🧩 **Captcha** ou **2FA** requis → « connecte-toi manuellement cette fois »

  Fini le doute : une notification précise remplace les échecs silencieux.

- **Palette de commandes (`Ctrl/Cmd + K`).** Recherchez un compte, basculez, ouvrez les réglages… au clavier, instantanément.
- **Comptes enrichis.** Ajoutez des **tags**, des **notes** et une **couleur d'accent** par compte. Tags recherchables (y compris dans la palette).
- **Recherche & tri** dans le tableau de bord (par nom, Riot ID, tag ; tri manuel / A-Z / favoris d'abord).
- **Retour visuel de bascule** : indicateur « Connexion… » et notifications d'erreur pendant un switch.
- **Stats plus fiables** : mise en cache, nouvelles tentatives automatiques et conservation du dernier rang connu en cas de coupure réseau ; icônes de rang locales.
- **Steam (expérimental)** : capture/restauration de profils Steam, en option dans les réglages.

## 🔐 Sécurité

- Verrouillage par **PIN** durci : hachage **HMAC-SHA256** à comparaison à temps constant + protection anti-force brute.
- **Chiffrement des identifiants** via le coffre Windows (DPAPI / `safeStorage`).
- Communication interne (IPC) **validée** (zod) avec listes blanches de canaux, **CSP stricte** et garde contre l'accès à des fichiers hors du dossier des images de compte.

## ⚡ Performance

- Démarrage et mémoire allégés : chargement différé, séparation des bundles, animations optimisées.
- Le rafraîchissement des stats **et** la surveillance du client Riot se mettent en pause quand l'app est **réduite dans la barre des tâches** (économie CPU).
- Moins de rendus inutiles dans l'interface.

## 🛠️ Corrections & améliorations

- Statut « Actif » affichant correctement le **nom du compte** connecté.
- Menu déroulant de tri lisible en thème sombre.
- Nombreux correctifs de stabilité et de robustesse (gestion d'erreurs, cycle de vie de la fenêtre, plateau système).

## 📦 Technique

- Mises à jour majeures : **React 19**, **Electron 42**, **Vite 7**, **Tailwind v4**, **zod 4**, `motion`, `lucide-react` v1.
- **Mises à jour automatiques** intégrées (electron-updater).

## ⬇️ Installation

Téléchargez **`SwitchMaster Setup 2.6.0.exe`** ci-dessous et lancez-le. Les mises à jour suivantes s'installeront automatiquement.

> Windows peut afficher un avertissement SmartScreen tant que l'application n'est pas signée par un certificat reconnu : cliquez sur « Informations complémentaires » → « Exécuter quand même ».
