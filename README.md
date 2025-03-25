<p align="center">
  <img src="/images/logo.png" alt="Logo" title="a title" width="100"/>
</p>

# SwitchMaster

SwitchMaster est une application qui simplifie la gestion et le changement de comptes pour les jeux Riot Games (Valorant et League of Legends).

## Fonctionnalités

- 🎮 Détection automatique des clients de jeu
- 🔐 Stockage sécurisé des informations de compte avec chiffrement
- 🔄 Changement rapide entre plusieurs comptes
- 📝 Journalisation avancée pour suivre les actions
- ⚙️ Configuration personnalisable
- 🖥️ Interface utilisateur moderne et intuitive

## Prérequis

- Windows 10 ou 11
- Python 3.8 ou supérieur
- Riot Client installé (pour Valorant et/ou League of Legends)

## Installation

### À partir du code source

1. Clonez ce dépôt :
   ```
   git clone https://github.com/votre-username/SwitchMaster.git
   cd SwitchMaster
   ```

2. Installez les dépendances requises :
   ```
   pip install -r requirements.txt
   ```

3. Lancez l'application :
   ```
   python -m src.main
   ```

### Avec l'exécutable

1. Téléchargez la dernière version depuis la page [Releases](https://github.com/votre-username/SwitchMaster/releases)
2. Décompressez l'archive
3. Exécutez `SwitchMaster.exe`

## Guide d'utilisation

### Ajouter un compte

1. Lancez SwitchMaster
2. Cliquez sur le bouton "+" dans le cadre du jeu souhaité (Valorant ou League of Legends)
3. Entrez votre nom d'utilisateur et mot de passe Riot
4. Cliquez sur "Sauvegarder"

### Changer de compte

1. Cliquez sur "Trouver les clients" pour détecter les clients de jeu
2. Dans le cadre du jeu souhaité, cliquez sur "Switch" à côté du compte que vous souhaitez utiliser
3. Attendez que l'application effectue automatiquement le changement de compte

### Configuration

Cliquez sur "Paramètres" pour accéder aux options de configuration :

- **Général** : Thème et niveau de journalisation
- **Application** : Options de démarrage et mises à jour
- **Jeu** : Chemins personnalisés et comportement des clients

## Structure du projet

```
SwitchMaster/
├── src/                    # Code source principal
│   ├── core/               # Logique métier principale
│   │   ├── account_manager.py  # Gestion des comptes
│   │   ├── client_finder.py    # Détection des clients
│   │   ├── encryption.py       # Chiffrement des mots de passe
│   │   └── game_launcher.py    # Lancement des jeux
│   ├── ui/                 # Interface utilisateur
│   │   ├── components/     # Composants d'interface réutilisables
│   │   │   ├── account_card.py    # Carte de compte
│   │   │   ├── account_dialog.py  # Dialogue d'ajout/modification
│   │   │   ├── config_dialog.py   # Dialogue de configuration
│   │   │   ├── game_frame.py      # Cadre de jeu
│   │   │   ├── log_window.py      # Fenêtre de logs
│   │   │   └── title_bar.py       # Barre de titre personnalisée
│   │   ├── windows/        # Fenêtres de l'application
│   │   │   └── main_window.py     # Fenêtre principale
│   │   └── app.py          # Point d'entrée de l'interface
│   ├── utils/              # Utilitaires
│   │   ├── logging.py      # Journalisation
│   │   └── window_utils.py # Utilitaires pour les fenêtres
│   └── main.py             # Point d'entrée principal
├── assets/                 # Ressources (images, icônes)
├── requirements.txt        # Dépendances Python
└── README.md               # Documentation
```

## Sécurité

Les mots de passe sont chiffrés à l'aide de la bibliothèque `cryptography` avec une clé dérivée des informations système uniques. Les données sont stockées localement dans le dossier `.switchmaster` de votre répertoire utilisateur.

## Contribution

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer :

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout d'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Créez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Remerciements

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) pour les composants d'interface utilisateur
- [Riot Games](https://www.riotgames.com/) pour les jeux géniaux
