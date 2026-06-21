<img src="https://img.shields.io/badge/Status-Beta-orange" height="28">
<img src="https://img.shields.io/badge/Version-2.6.0-blue" height="28">
<img src="https://img.shields.io/badge/License-ISC-white" height="28">

# SwitchMaster

SwitchMaster est un gestionnaire de comptes multi-plateforme pour les jeux Riot Games (Valorant, League of Legends). Il permet de basculer rapidement entre vos différents comptes sans avoir à ressaisir vos identifiants à chaque fois.

## 🚀 Fonctionnalités

- **Bascule rapide** : Changez de compte Riot en un clic.
- **Command palette** : Toutes les actions à portée de clavier via `Ctrl/Cmd+K`.
- **Sécurité** : Identifiants chiffrés via le coffre de l'OS (DPAPI/Keychain), verrouillage optionnel par code PIN, validation IPC stricte (zod) et CSP.
- **Statistiques** : Affichage automatique de votre rang pour chaque compte.
- **Designs personnalisables** : Plusieurs interfaces au choix (classic, modern), thème sombre et images de compte personnalisées.
- **Tray Icon** : Accès rapide depuis la barre des tâches.
- **Mises à jour automatiques** : via electron-updater.

## 🛠️ Installation

1. Téléchargez la dernière version dans l'onglet [Releases](https://github.com/Cori-bot/SwitchMaster-v2/releases).
2. Lancez l'installeur `SwitchMaster Setup.exe`.
3. Suivez les instructions à l'écran.

## 👩‍💻 Développement

```bash
pnpm install      # installer les dépendances (pnpm requis)
pnpm dev          # lancer Electron + Vite en mode dev
pnpm test         # tests Vitest
pnpm typecheck    # vérification TypeScript
pnpm build        # build de production
```

Conventions de code et architecture détaillées : voir [AGENTS.md](./AGENTS.md).

## 📄 Licence

Ce projet est sous licence ISC.
