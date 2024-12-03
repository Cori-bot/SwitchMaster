# pylint: disable=import-error
# type: ignore
import customtkinter as ctk
import json
import os
from PIL import Image
from pathlib import Path
from ctypes import windll, byref, c_int, sizeof
import subprocess
import time
import pyautogui
import win32gui
import pyperclip
import sys
import win32process
import psutil
import win32con
import win32api
import platform
from time import sleep
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import hashlib
import secrets
import logging
from datetime import datetime

def get_config_path():
    return os.path.join(os.getcwd(), "accounts.json")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class PasswordManager:
    def __init__(self):
        # Utiliser un sel unique pour chaque installation
        self.salt = self.get_or_create_salt()
        # Dériver une clé à partir d'informations système uniques
        self.key = self.generate_key()
        self.cipher_suite = Fernet(self.key)

    def get_or_create_salt(self):
        """Récupère ou crée un sel unique"""
        salt_file = "salt.bin"
        if os.path.exists(salt_file):
            with open(salt_file, "rb") as f:
                return f.read()
        else:
            # Générer un nouveau sel
            salt = secrets.token_bytes(16)
            with open(salt_file, "wb") as f:
                f.write(salt)
            return salt

    def generate_key(self):
        """Génère une clé unique basée sur des informations système"""
        # Utiliser des informations système comme base pour la clé
        system_info = (
            getpass.getuser() +  # Nom d'utilisateur
            os.path.expanduser('~') +  # Chemin du dossier utilisateur
            platform.node()  # Nom de la machine
        ).encode()
        
        # Utiliser PBKDF2 pour dériver une clé
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(system_info))
        return key

    def encrypt_password(self, password):
        """Chiffre un mot de passe"""
        return self.cipher_suite.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password):
        """Déchiffre un mot de passe"""
        try:
            return self.cipher_suite.decrypt(encrypted_password.encode()).decode()
        except Exception:
            return None

class SwitchMaster:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("SwitchMaster")
        self.center_window(self.window, 1200, 600)
        
        # Garder la fenêtre au premier plan au démarrage
        self.window.attributes('-topmost', True)
        self.window.focus_force()
        
        # Désactiver le topmost après quelques secondes
        self.window.after(250, lambda: self.window.attributes('-topmost', False))
        
        # Définir les couleurs en premier
        self.colors = {
            'bg_dark': "#1E1E1E",
            'bg_light': "#2D2D2D",
            'accent': "#FF4655",  # Rouge Valorant
            'accent_hover': "#FF5F6D",
            'button': "#3391D4",  # Bleu vif
            'button_hover': "#40A9FF",
            'text': "#FFFFFF",
            'text_secondary': "#A0A0A0",
            'border': "#333333"
        }
        
        # Définir l'icône de la fenêtre (barre des tâches)
        icon_path = resource_path("images/logo.ico")
        if os.path.exists(icon_path):
            self.window.iconbitmap(icon_path)
        elif os.path.exists('images/logo.png'):
            try:
                # Convertir PNG en ICO
                icon = Image.open('images/logo.png')
                # Redimensionner à 32x32 pour une meilleure compatibilité
                icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
                icon.save('images/logo.ico')
                self.window.iconbitmap('images/logo.ico')
            except Exception as e:
                print(f"Erreur lors de la conversion de l'icône: {e}")
        
        # Configuration de la fenêtre principale
        self.window.configure(fg_color=self.colors['bg_dark'])
        
        # Création du conteneur principal avec coins arrondis
        self.main_container = ctk.CTkFrame(
            self.window,
            fg_color=self.colors['bg_dark'],
            corner_radius=15
        )
        self.main_container.pack(fill='both', expand=True, padx=2, pady=2)
        
        # État de la fenêtre
        self.is_maximized = False
        self.normal_size = {"width": 1000, "height": 500}
        
        # Configuration du thème
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Charger les icônes
        self.icons = {
            'settings': ctk.CTkImage(
                Image.open(resource_path('images/roue.png')),
                size=(20, 20)  # Ajustez la taille selon vos besoins
            ),
        }
        
        # Charger les images
        self.images = {}
        self.load_images()
        
        # Charger les comptes
        self.config_file = "accounts.json"
        self.load_accounts()
        
        # Création du contenu principal
        self.create_main_content()
        
        # Ajouter ces variables
        self.minimized = False
        self.withdrawn = False
        self.iconified = False
        
        # Appliquer le thème sombre aux fenêtres Windows
        if os.name == 'nt':
            try:
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                set_window_attribute = windll.dwmapi.DwmSetWindowAttribute
                get_parent = windll.user32.GetParent
                
                def set_dark_title_bar(window):
                    window.update()
                    hwnd = window.winfo_id()
                    value = c_int(2)
                    set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(value), sizeof(value))
                
                # Appliquer à la fenêtre principale
                set_dark_title_bar(self.window)
                
                # Sauvegarder la fonction pour l'utiliser sur les dialogues
                self.set_dark_title_bar = set_dark_title_bar
                
            except Exception as e:
                print(f"Erreur lors de l'application du thème sombre: {e}")
        self.riot_client_path = None
        self.password_manager = PasswordManager()
        self.load_accounts()  # Charger les comptes avec les mots de passe chiffrés
        
        # Configuration des logs
        self.setup_logging()

    def setup_logging(self):
        """Configure le système de logs"""
        log_file = "switchmaster.log"
        
        # Définir les formats avec emojis
        log_formats = {
            'INFO': '✅',
            'WARNING': '🚧',
            'ERROR': '❌',
            'DEBUG': 'ℹ️'
        }
        
        class EmojiFormatter(logging.Formatter):
            def format(self, record):
                emoji = log_formats.get(record.levelname, '')
                record.emoji = emoji
                return super().format(record)
        
        # Configuration du logger avec le format personnalisé
        formatter = EmojiFormatter('%(asctime)s - %(emoji)s %(levelname)s - %(message)s')
        
        # Gestionnaire de fichier uniquement (plus de console)
        file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
        file_handler.setFormatter(formatter)
        
        # Configuration du logger
        logger = logging.getLogger('SwitchMaster')
        logger.setLevel(logging.INFO)
        
        # Supprimer les anciens handlers s'ils existent
        logger.handlers = []
        
        # Ajouter uniquement le gestionnaire de fichier
        logger.addHandler(file_handler)
        
        self.logger = logger
        
        # Log le lancement de l'application
        self.logger.info(f"Lancement de l'application")

    def kill_process(self, process_name):
        """Tue un processus et log le résultat"""
        try:
            # Obtenir la liste des processus correspondants
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        pid = proc.info['pid']
                        proc.kill()
                        self.logger.info(f"Processus '{process_name}' (PID {pid}) arrêté avec succès")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.error(f"Erreur lors de l'arrêt du processus '{process_name}': {str(e)}")
            
            self.logger.warning(f"Processus '{process_name}' non trouvé")
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de l'arrêt de '{process_name}': {str(e)}")
            return False

    def setup_window(self):
        if os.name == 'nt':  # Windows
            try:
                from ctypes import windll
                hwnd = self.window.winfo_id()
                
                # Styles Windows
                GWL_STYLE = -16
                GWL_EXSTYLE = -20
                WS_EX_APPWINDOW = 0x00040000
                WS_MINIMIZEBOX = 0x00020000
                WS_MAXIMIZEBOX = 0x00010000
                WS_SYSMENU = 0x00080000
                WS_CAPTION = 0x00C00000
                
                # Obtenir le style actuel
                style = windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
                
                # Enlever la barre de titre Windows mais garder les fonctionnalités
                style = style & ~WS_CAPTION  # Enlever la barre de titre
                style = style | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU  # Garder les fonctionnalités
                
                # Appliquer le style
                windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
                
                # S'assurer que la fenêtre apparaît dans la barre des tâches
                style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                style = style | WS_EX_APPWINDOW
                windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
                
                # Forcer la mise à jour de l'apparence
                windll.user32.SetWindowPos(
                    hwnd, 0, 0, 0, 0, 0,
                    0x0002 | 0x0004 | 0x0020  # SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED
                )
                
                self.window.attributes('-alpha', 1.0)
                
            except ImportError:
                print("Module ctypes non disponible")
                self.window.attributes('-alpha', 1.0)
        else:
            self.window.attributes('-alpha', 1.0)

    def load_images(self):
        image_files = {
            'logo': 'images/logo.png',
            'valorant': 'images/valorant.png',
            'lol': 'images/lol.png'
        }
        
        for key, filename in image_files.items():
            path = Path(resource_path(filename))
            if path.exists():
                self.images[key] = ctk.CTkImage(
                    Image.open(path),
                    size=(25, 25)
                )

    def create_title_bar(self):
        # Création de la barre de titre
        title_bar = ctk.CTkFrame(
            self.main_container, 
            height=35, 
            fg_color=self.colors['bg_light'],
            corner_radius=10
        )
        title_bar.pack(fill='x', padx=5, pady=5)
        title_bar.pack_propagate(False)

        # Container pour le logo et le titre (côté gauche)
        left_container = ctk.CTkFrame(title_bar, fg_color="transparent")
        left_container.pack(side='left', fill='y')

        # Logo
        if 'logo' in self.images:
            logo_label = ctk.CTkLabel(
                left_container,
                text="",
                image=self.images['logo'],
                width=20
            )
            logo_label.pack(side='left', padx=(10, 5))

        # Titre
        title_label = ctk.CTkLabel(
            left_container,
            text="SwitchMaster",
            font=("Arial", 12, "bold"),
            text_color=self.colors['text']
        )
        title_label.pack(side='left', padx=5)

        # Container pour les boutons (côté droit)
        button_container = ctk.CTkFrame(title_bar, fg_color="transparent")
        button_container.pack(side='right', fill='y')

        # Boutons de contrôle avec style minimaliste
        button_style = {
            'width': 35,
            'height': 25,
            'corner_radius': 5,
            'fg_color': "transparent",
            'font': ("Arial", 13),
            'text_color': self.colors['text']
        }

        # Bouton fermer (style spécial pour le bouton fermer)
        close_style = button_style.copy()  # Copier le style de base
        close_style['hover_color'] = "#FF4444"  # Ajouter la couleur de survol spécifique
        
        close_btn = ctk.CTkButton(
            button_container,
            text=self.icons['close'],
            command=self.window.quit,
            **close_style
        )
        close_btn.pack(side='right', padx=(0, 5))

        # Style pour les autres boutons
        normal_style = button_style.copy()
        normal_style['hover_color'] = self.colors['bg_dark']

        # Bouton maximiser
        maximize_btn = ctk.CTkButton(
            button_container,
            text=self.icons['maximize'],
            command=self.toggle_maximize,
            **normal_style
        )
        maximize_btn.pack(side='right', padx=2)

        # Bouton minimiser
        minimize_btn = ctk.CTkButton(
            button_container,
            text=self.icons['minimize'],
            command=self.minimize_window,  # Utiliser la nouvelle méthode
            **normal_style
        )
        minimize_btn.pack(side='right', padx=2)

        # Rendre la fenêtre déplaçable
        for widget in [title_bar, left_container, title_label]:
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<B1-Motion>", self.on_move)
            widget.bind("<Double-Button-1>", lambda e: self.toggle_maximize())

    def create_main_content(self):
        # Frame principal avec coins arrondis
        main_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors['bg_dark'],
            corner_radius=15
        )
        main_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))

        # Bouton de recherche des clients en haut
        find_clients_btn = ctk.CTkButton(
            main_frame,
            text="Rechercher les clients",
            font=("Arial", 13, "bold"),
            fg_color=self.colors['bg_light'],
            hover_color=self.colors['accent'],
            height=45,
            corner_radius=10,
            command=self.find_riot_client
        )
        find_clients_btn.pack(pady=(10, 20), padx=20)

        # Container pour les jeux
        games_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        games_frame.pack(fill='both', expand=True, padx=10)
        
        # Configurer la grille pour avoir deux colonnes de même taille
        games_frame.grid_columnconfigure((0, 1), weight=1, uniform="column")
        
        # Calculer la largeur pour chaque colonne (la moitié de la largeur totale moins les paddings)
        column_width = (1200 - 60) // 2  # 1200 est la largeur totale, 60 pour les paddings
        
        # Frame Valorant avec largeur fixe
        valorant_frame = self.create_game_frame(games_frame, "VALORANT")
        valorant_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        valorant_frame.configure(width=column_width)

        # Frame League of Legends avec largeur fixe
        league_frame = self.create_game_frame(games_frame, "LEAGUE OF LEGENDS")
        league_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        league_frame.configure(width=column_width)

        # Bouton pour voir les logs en bas de la fenêtre
        logs_btn = ctk.CTkButton(
            main_frame,
            text="Voir les logs",
            font=("Arial", 12),
            fg_color=self.colors['bg_light'],
            hover_color=self.colors['button'],
            height=30,
            corner_radius=8,
            command=self.show_logs
        )
        logs_btn.pack(pady=(10, 20))

    def create_game_frame(self, parent, game_name):
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_light'],
            corner_radius=15,
            border_width=1,
            border_color=self.colors['border']
        )
        
        # Container pour le titre avec logo
        title_container = ctk.CTkFrame(frame, fg_color="transparent")
        title_container.pack(pady=(20, 15), padx=20, fill='x')
        
        # Logo du jeu
        game_id = game_name.lower().replace(" ", "")
        if game_id == "leagueoflegends":
            game_id = "lol"
        
        if game_id in self.images:
            logo_label = ctk.CTkLabel(
                title_container,
                text="",
                image=self.images[game_id],
                width=35
            )
            logo_label.pack(side='left', padx=10)
        
        # Titre du jeu centré
        title = ctk.CTkLabel(
            title_container,
            text=game_name,
            font=("Arial", 24, "bold"),
            text_color=self.colors['accent'] if game_id == "valorant" else "#C79C41"
        )
        title.pack(expand=True)

        # Container principal qui prendra toute la hauteur disponible
        main_container = ctk.CTkFrame(frame, fg_color="transparent")
        main_container.pack(fill='both', expand=True, padx=25)

        # Container pour les boutons de compte
        account_buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        account_buttons_frame.pack(fill='x', pady=(25, 15))
        
        # Charger les comptes existants
        game_id = "league" if game_id == "lol" else game_id
        if game_id in self.accounts:
            for num, account in self.accounts[game_id].items():
                # Container pour le bouton de compte et le bouton d'édition
                account_container = ctk.CTkFrame(account_buttons_frame, fg_color="transparent")
                account_container.pack(pady=5, fill='x')
                
                # Bouton du compte
                account_btn = ctk.CTkButton(
                    account_container,
                    text=account['username'],
                    fg_color=self.colors['button'],
                    hover_color=self.colors['button_hover'],
                    height=35,
                    corner_radius=8,
                    command=lambda g=game_id, n=num: self.switch_account(g, n)
                )
                account_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))
                
                # Bouton d'édition
                edit_btn = ctk.CTkButton(
                    account_container,
                    text="",
                    image=self.icons['settings'],
                    width=35,
                    height=35,
                    corner_radius=8,
                    fg_color=self.colors['bg_dark'],
                    hover_color=self.colors['accent'],
                    command=lambda g=game_id, n=num, f=account_buttons_frame: 
                        self.edit_account(g, n, f)
                )
                edit_btn.pack(side='right')

        # Frame pour le bouton ajouter (en bas)
        add_button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        add_button_frame.pack(side='bottom', fill='x', pady=(0, 15))

        # Bouton configurer
        config_btn = ctk.CTkButton(
            add_button_frame,
            text=f"Ajouter un compte",
            font=("Arial", 13, "bold"),
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            height=45,
            corner_radius=10,
            command=lambda: self.show_config_dialog(game_id, account_buttons_frame)
        )
        config_btn.pack(fill='x')

        return frame

    def show_config_dialog(self, game, account_buttons_frame):
        dialog = ctk.CTk()
        dialog.title(f"Configuration {game.upper()}")
        self.center_window(dialog, 400, 450)
        dialog.configure(fg_color=self.colors['bg_dark'])
        
        # Définir l'icône de la fenêtre
        icon_path = resource_path("images/logo.ico")
        if os.path.exists(icon_path):
            dialog.iconbitmap(icon_path)
        elif os.path.exists('images/logo.png'):
            try:
                if not os.path.exists('images/logo.ico'):
                    icon = Image.open('images/logo.png')
                    icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
                    icon.save('images/logo.ico')
                dialog.iconbitmap('images/logo.ico')
            except Exception as e:
                print(f"Erreur lors de l'application de l'icône: {e}")

        # Contenu principal
        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=30, pady=30)  # Padding augmenté

        # Titre
        title_label = ctk.CTkLabel(
            content_frame,
            text="Ajouter un compte",
            font=("Arial", 20, "bold"),
            text_color=self.colors['text']
        )
        title_label.pack(pady=(0, 30))

        # Frame pour les champs de saisie
        fields_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        fields_frame.pack(fill='x', padx=20)

        # Nom d'utilisateur
        username_label = ctk.CTkLabel(
            fields_frame,
            text="Nom d'utilisateur:",
            font=("Arial", 12),
            text_color=self.colors['text_secondary']
        )
        username_label.pack(anchor='w', pady=(0, 5))
        
        username = ctk.CTkEntry(
            fields_frame,
            height=45,
            placeholder_text="Entrez votre nom d'utilisateur",
            font=("Arial", 13),
            corner_radius=8,
            border_width=2,
            border_color=self.colors['border']
        )
        username.pack(fill='x', pady=(0, 20))

        # Mot de passe
        password_label = ctk.CTkLabel(
            fields_frame,
            text="Mot de passe:",
            font=("Arial", 12),
            text_color=self.colors['text_secondary']
        )
        password_label.pack(anchor='w', pady=(0, 5))
        
        password = ctk.CTkEntry(
            fields_frame,
            height=45,
            placeholder_text="Entrez votre mot de passe",
            font=("Arial", 13),
            corner_radius=8,
            border_width=2,
            border_color=self.colors['border'],
            show="•"
        )
        password.pack(fill='x', pady=(0, 30))

        # Bouton de sauvegarde
        save_btn = ctk.CTkButton(
            fields_frame,
            text="Sauvegarder",
            font=("Arial", 14, "bold"),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            height=45,
            corner_radius=8,
            command=lambda: self.save_account(game, username.get(), password.get(), dialog, account_buttons_frame)
        )
        save_btn.pack(fill='x', pady=(10, 0))

        # Appliquer le thème sombre
        if hasattr(self, 'set_dark_title_bar'):
            self.set_dark_title_bar(dialog)

        # Lancer la fenêtre
        dialog.mainloop()

    def load_accounts(self):
        config_path = get_config_path()
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.accounts = json.load(f)
        else:
            self.accounts = {"valorant": {}, "league": {}}
            with open(config_path, "w") as f:
                json.dump(self.accounts, f, indent=4)

    def save_account(self, game, username, password, dialog, account_buttons_frame):
        if not username or not password:
            self.show_error("Veuillez remplir tous les champs!")
            return

        game_id = "league" if game in ["leagueoflegends", "lol"] else game

        if game_id not in self.accounts:
            self.accounts[game_id] = {}

        account_num = len(self.accounts[game_id]) + 1
        
        # Chiffrer le mot de passe avant de le sauvegarder
        encrypted_password = self.password_manager.encrypt_password(password)
        
        self.accounts[game_id][str(account_num)] = {
            "username": username,
            "password": encrypted_password
        }

        with open(get_config_path(), "w") as f:
            json.dump(self.accounts, f, indent=4)

        # Container pour le bouton de compte et le bouton d'édition
        account_container = ctk.CTkFrame(account_buttons_frame, fg_color="transparent")
        account_container.pack(pady=5, fill='x')
        
        # Bouton du compte
        account_btn = ctk.CTkButton(
            account_container,
            text=username,
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            height=35,
            corner_radius=8,
            command=lambda: self.switch_account(game_id, account_num)
        )
        account_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        # Bouton d'édition
        edit_btn = ctk.CTkButton(
            account_container,
            text="",
            image=self.icons['settings'],
            width=35,
            height=35,
            corner_radius=8,
            fg_color=self.colors['bg_dark'],
            hover_color=self.colors['accent'],
            command=lambda: self.edit_account(game_id, account_num, account_buttons_frame)
        )
        edit_btn.pack(side='right')

        # Fermer proprement la fenêtre
        dialog.after(100, dialog.destroy)
        dialog.quit()
        
        # Afficher le message de succès
        self.show_info("Compte enregistré avec succès!")

    def switch_account(self, game, account_num):
        if str(account_num) not in self.accounts[game]:
            self.show_error("Ce compte n'est pas configuré!")
            return

        account = self.accounts[game][str(account_num)]
        
        # Déchiffrer le mot de passe au moment de l'utilisation
        decrypted_password = self.password_manager.decrypt_password(account['password'])
        if not decrypted_password:
            self.show_error("Impossible de déchiffrer le mot de passe!")
            return

        # Créer un dictionnaire temporaire avec le mot de passe déchiffré
        temp_account = {
            "username": account['username'],
            "password": decrypted_password
        }

        riot_client_path = "C:/Riot Games/Riot Client/RiotClientServices.exe"
        
        try:
            # Fermer les clients existants
            self.logger.info("Début de la fermeture des clients...")
            
            processes_to_kill = [
                "RiotClientServices.exe",
                "RiotClientUx.exe",
                "LeagueClient.exe",
                "VALORANT.exe"
            ]
            
            for process in processes_to_kill:
                self.kill_process(process)
            
            self.logger.info("Fermeture des clients terminée.")
            
            time.sleep(2)
            
            # Lancer le client Riot
            self.logger.info(f"Lancement du client Riot depuis : {riot_client_path}")
            subprocess.Popen([riot_client_path])
            
            # Attendre que la fenêtre apparaisse
            max_attempts = 40  # Augmenter le nombre de tentatives
            riot_window = None
            
            # Désactiver temporairement le failsafe de pyautogui
            pyautogui.FAILSAFE = False
            
            try:
                # Boucle d'attente avec gestion des erreurs
                for attempt in range(max_attempts):
                    time.sleep(0.5)
                    try:
                        riot_window = self.find_riot_window()
                        if riot_window:
                            try:
                                # Forcer la restauration et le focus de la fenêtre
                                win32gui.ShowWindow(riot_window, 9)  # SW_RESTORE
                                win32gui.SetForegroundWindow(riot_window)
                                
                                # Attendre que la fenêtre soit active
                                for _ in range(10):  # Essayer plusieurs fois
                                    time.sleep(0.2)
                                    if win32gui.GetForegroundWindow() == riot_window:
                                        break
                                else:
                                    continue  # Si le focus n'est pas obtenu, continuer la boucle
                                
                                # Si on arrive ici, la fenêtre est bien au premier plan
                                break
                                
                            except Exception:
                                continue
                    except Exception:
                        if attempt == max_attempts - 1:
                            self.show_error("Impossible de trouver la fenêtre du client Riot")
                            return
                        continue
                
                if riot_window:
                    time.sleep(1.5)  # Attendre que l'interface soit complètement chargée
                    
                    try:
                        old_clipboard = pyperclip.paste()
                    except Exception:
                        old_clipboard = ""
                    
                    try:
                        # Vérifier l'état initial
                        if not self.verify_riot_client_running():
                            self.show_error("Le client Riot n'est pas en cours d'exécution")
                            return
                            
                        # Saisir le nom d'utilisateur
                        for attempt in range(3):
                            if not self.ensure_window_focus(riot_window):
                                if attempt == 2:
                                    self.show_error("Impossible de maintenir le focus sur la fenêtre Riot")
                                    return
                                continue
                                
                            try:
                                # Sauvegarder et vérifier le presse-papier
                                pyperclip.copy(temp_account['username'])
                                if pyperclip.paste() != temp_account['username']:
                                    continue
                                    
                                pyautogui.hotkey('ctrl', 'a')
                                time.sleep(0.2)
                                
                                if not self.ensure_window_focus(riot_window):
                                    continue
                                    
                                pyautogui.hotkey('ctrl', 'v')
                                time.sleep(0.3)
                                
                                if not self.ensure_window_focus(riot_window):
                                    continue
                                    
                                pyautogui.press('tab')
                                time.sleep(0.3)
                                break
                            except Exception:
                                if attempt == 2:
                                    raise
                                continue
                        
                        # Saisir le mot de passe avec les mêmes vérifications
                        for attempt in range(3):
                            if not self.ensure_window_focus(riot_window):
                                if attempt == 2:
                                    self.show_error("Impossible de maintenir le focus sur la fenêtre Riot")
                                    return
                                continue
                                
                            try:
                                pyperclip.copy(temp_account['password'])
                                if pyperclip.paste() != temp_account['password']:
                                    continue
                                    
                                pyautogui.hotkey('ctrl', 'a')
                                time.sleep(0.2)
                                
                                if not self.ensure_window_focus(riot_window):
                                    continue
                                    
                                pyautogui.hotkey('ctrl', 'v')
                                time.sleep(0.3)
                                
                                if not self.ensure_window_focus(riot_window):
                                    continue
                                    
                                pyautogui.press('enter')
                                break
                            except Exception:
                                if attempt == 2:
                                    raise
                                continue
                            
                    finally:
                        try:
                            # Nettoyer le presse-papier de manière sécurisée
                            pyperclip.copy(" " * 100)  # Effacer avec des espaces
                            pyperclip.copy(old_clipboard)
                        except Exception:
                            pass
                    
                    time.sleep(3)
                    
                    try:
                        error_messages = []
                        win32gui.EnumWindows(
                            lambda hwnd, ctx: ctx.append(win32gui.GetWindowText(hwnd)) 
                            if "Erreur" in win32gui.GetWindowText(hwnd) else None, 
                            error_messages
                        )
                        
                        if any("refusé" in msg.lower() for msg in error_messages):
                            self.show_info("Une vérification par e-mail est nécessaire")
                            self.show_email_options()
                    except Exception:
                        pass
                    
            finally:
                pyautogui.FAILSAFE = True
                
        except Exception as e:
            error_msg = f"Erreur lors de la connexion : {str(e)}"
            self.logger.error(error_msg)
            self.show_error(error_msg)
                

    def show_error(self, message):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Erreur")
        self.center_window(dialog, 300, 200)
        dialog.configure(fg_color=self.colors['bg_dark'])
        dialog.transient(self.window)
        dialog.grab_set()

        # Définir l'icône de la fenêtre
        icon_path = resource_path("images/logo.ico")
        if os.path.exists(icon_path):
            dialog.iconbitmap(icon_path)
        elif os.path.exists('images/logo.png'):
            try:
                if not os.path.exists('images/logo.ico'):
                    icon = Image.open('images/logo.png')
                    icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
                    icon.save('images/logo.ico')
                dialog.iconbitmap('images/logo.ico')
            except Exception as e:
                print(f"Erreur lors de l'application de l'icône: {e}")

        # Centrer la fenêtre
        dialog.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - 300) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 200) // 2
        dialog.geometry(f"+{x}+{y}")

        # Message directement dans la fenêtre
        label = ctk.CTkLabel(
            dialog,
            text=message,
            font=("Arial", 12),
            wraplength=250
        )
        label.pack(pady=30)

        # Bouton OK
        btn = ctk.CTkButton(
            dialog,
            text="OK",
            font=("Arial", 12, "bold"),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            height=35,
            corner_radius=8,
            command=dialog.destroy
        )
        btn.pack(pady=(0, 20), padx=50)

        # Appliquer le thème sombre à la barre de titre
        if hasattr(self, 'set_dark_title_bar'):
            self.set_dark_title_bar(dialog)

    def show_info(self, message):
        dialog = ctk.CTk()
        dialog.title("Information")
        
        # Vérifier si c'est un message de vérification email
        show_email_buttons = "vérification par e-mail" in message.lower()
        height = 350 if show_email_buttons else 200
        
        self.center_window(dialog, 450, height)
        dialog.configure(fg_color=self.colors['bg_dark'])
        
        icon_path = resource_path("images/logo.ico")
        if os.path.exists(icon_path):
            dialog.iconbitmap(icon_path)

        # Contenu
        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Message
        label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=("Arial", 12),
            wraplength=350,
            text_color=self.colors['text']
        )
        label.pack(pady=(10, 20))

        # Boutons de messagerie seulement si c'est un message de vérification email
        if show_email_buttons:
            email_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            email_frame.pack(fill='x', pady=(0, 10))

            email_clients = {
                "Gmail": "https://gmail.com",
                "Outlook": "https://outlook.live.com",
                "Windows Mail": "ms-outlook:",
                "Yahoo Mail": "https://mail.yahoo.com"
            }           



            def open_email_client(client):
                import webbrowser
                if client == "Windows Mail":
                    os.system("start ms-outlook:")
                else:
                    webbrowser.open(email_clients[client])

            for client in email_clients:
                btn = ctk.CTkButton(
                    email_frame,
                    text=client,
                    font=("Arial", 12, "bold"),
                    fg_color=self.colors['button'],
                    hover_color=self.colors['button_hover'],
                    height=35,
                    corner_radius=8,
                    command=lambda c=client: open_email_client(c)
                )
                btn.pack(fill='x', pady=5)

        # Bouton OK
        def close_dialog():
            dialog.after(100, dialog.destroy)
            dialog.quit()

        ok_btn = ctk.CTkButton(
            content_frame,
            text="OK",
            font=("Arial", 12, "bold"),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            height=35,
            corner_radius=8,
            command=close_dialog
        )
        ok_btn.pack(pady=(10, 0), padx=50)

        if hasattr(self, 'set_dark_title_bar'):
            self.set_dark_title_bar(dialog)

        dialog.mainloop()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")

    def toggle_maximize(self):
        if not self.is_maximized:
            # Sauvegarder la position et taille actuelles
            self.normal_pos = self.window.geometry().split('+')[1:]
            self.normal_size = {
                "width": self.window.winfo_width(),
                "height": self.window.winfo_height()
            }
            
            # Maximiser
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            self.window.geometry(f"{screen_width}x{screen_height}+0+0")
            self.is_maximized = True
        else:
            # Restaurer
            width = self.normal_size["width"]
            height = self.normal_size["height"]
            x = self.normal_pos[0]
            y = self.normal_pos[1]
            self.window.geometry(f"{width}x{height}+{x}+{y}")
            self.is_maximized = False

    def run(self):
        self.window.mainloop()

    def edit_account(self, game, account_num, account_buttons_frame):
        if str(account_num) not in self.accounts[game]:
            self.show_error("Ce compte n'existe pas!")
            return

        account = self.accounts[game][str(account_num)]
        
        # Déchiffrer le mot de passe pour l'affichage
        decrypted_password = self.password_manager.decrypt_password(account['password'])
        if not decrypted_password:
            self.show_error("Impossible de déchiffrer le mot de passe!")
            return

        dialog = ctk.CTkToplevel(self.window)
        dialog.title(f"Édition du compte {account['username']}")
        self.center_window(dialog, 400, 300)
        dialog.configure(fg_color=self.colors['bg_dark'])
        
        # Garder la fenêtre au premier plan
        dialog.attributes('-topmost', True)
        dialog.focus_force()
        
        # Désactiver le topmost après quelques secondes
        dialog.after(250, lambda: dialog.attributes('-topmost', False))
        
        # Définir l'icône de la fenêtre
        self.set_dialog_icon(dialog)
        
        # Titre
        title_label = ctk.CTkLabel(
            dialog,
            text="Modifier le compte",
            font=("Arial", 20, "bold"),
            text_color=self.colors['text']
        )
        title_label.pack(pady=20)
        
        # Frame pour les champs
        fields_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        fields_frame.pack(fill='x', padx=20)
        
        # Nom d'utilisateur
        username_label = ctk.CTkLabel(fields_frame, text="Nom d'utilisateur:", anchor='w')
        username_label.pack(fill='x', pady=(0, 5))
        
        username_entry = ctk.CTkEntry(fields_frame)
        username_entry.insert(0, account['username'])
        username_entry.pack(fill='x', pady=(0, 15))
        
        # Mot de passe
        password_label = ctk.CTkLabel(fields_frame, text="Mot de passe:", anchor='w')
        password_label.pack(fill='x', pady=(0, 5))
        
        # Frame pour le mot de passe et le bouton voir
        password_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        password_frame.pack(fill='x', pady=(0, 15))
        
        password_entry = ctk.CTkEntry(password_frame, show="*")
        password_entry.insert(0, decrypted_password)  # Utiliser le mot de passe déchiffré
        password_entry.pack(side='left', fill='x', expand=True)
        
        # Variable pour suivre l'état du mot de passe
        password_visible = False
        
        def toggle_password():
            nonlocal password_visible
            password_visible = not password_visible
            password_entry.configure(show="" if password_visible else "*")
        
        show_password_btn = ctk.CTkButton(
            password_frame,
            text="👁",
            width=35,
            command=toggle_password
        )
        show_password_btn.pack(side='right', padx=(5, 0))
        
        # Frame pour les boutons
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        # Bouton Supprimer
        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="Supprimer",
            fg_color="#FF4444",
            hover_color="#FF6666",
            command=lambda: self.delete_account(game, account_num, dialog, account_buttons_frame)
        )
        delete_btn.pack(side='left', expand=True, padx=5)
        
        # Bouton Sauvegarder
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Sauvegarder",
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            command=lambda: self.update_account(
                game,
                account_num,
                username_entry.get(),
                password_entry.get(),
                dialog,
                account_buttons_frame
            )
        )
        save_btn.pack(side='right', expand=True, padx=5)

    def update_account(self, game, account_num, username, password, dialog, account_buttons_frame):
        if not username or not password:
            self.show_error("Veuillez remplir tous les champs!")
            return

        # Vérifiez que le compte existe
        if str(account_num) in self.accounts[game]:
            # Chiffrer le nouveau mot de passe
            encrypted_password = self.password_manager.encrypt_password(password)
            
            self.accounts[game][str(account_num)] = {
                "username": username,
                "password": encrypted_password  # Sauvegarder le mot de passe chiffré
            }

            with open(get_config_path(), "w") as f:
                json.dump(self.accounts, f, indent=4)

            # Fermer proprement la fenêtre
            dialog.after(100, dialog.destroy)
            dialog.quit()

            self.refresh_accounts(game, account_buttons_frame)
            self.show_info("Compte mis à jour avec succès!")
            
            # Log la modification
            self.logger.info(f"Compte {username} modifié avec succès")
        else:
            self.show_error("Compte non trouvé.")

    def delete_account(self, game, account_num, dialog, account_buttons_frame):
        if str(account_num) in self.accounts[game]:
            del self.accounts[game][str(account_num)]
            
            # Renuméroter les comptes restants
            new_accounts = {}
            for i, (_, account) in enumerate(sorted(self.accounts[game].items()), 1):
                new_accounts[str(i)] = account
            self.accounts[game] = new_accounts

            with open(get_config_path(), "w") as f:
                json.dump(self.accounts, f, indent=4)

            # Fermer proprement la fenêtre
            dialog.after(100, dialog.destroy)
            dialog.quit()

            self.refresh_accounts(game, account_buttons_frame)
            self.show_info("Compte supprimé avec succès!")
        else:
            self.show_error("Compte non trouvé.")

    def refresh_accounts(self, game, account_buttons_frame):
        # Effacer tous les widgets existants
        for widget in account_buttons_frame.winfo_children():
            widget.destroy()
        
        # Recréer les boutons de compte
        if game in self.accounts:
            for num, account in self.accounts[game].items():
                account_container = ctk.CTkFrame(account_buttons_frame, fg_color="transparent")
                account_container.pack(pady=5, padx=20, fill='x')
                
                account_btn = ctk.CTkButton(
                    account_container,
                    text=account['username'],
                    fg_color=self.colors['button'],
                    hover_color=self.colors['button_hover'],
                    height=35,
                    corner_radius=8,
                    command=lambda g=game, n=num: self.switch_account(g, n)
                )
                account_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))
                
                edit_btn = ctk.CTkButton(
                    account_container,
                    text="",  # Texte vide car on utilise une image
                    image=self.icons['settings'],
                    width=35,
                    height=35,
                    corner_radius=8,
                    fg_color=self.colors['bg_dark'],
                    hover_color=self.colors['accent'],
                    command=lambda g=game, n=num, f=account_buttons_frame: 
                        self.edit_account(g, n, f)
                )
                edit_btn.pack(side='right')

    def minimize_window(self):
        if not self.minimized:
            self.window.wm_iconify()
            self.minimized = True
        else:
            self.window.deiconify()
            self.minimized = False

    def on_unmap(self, event):
        if not self.minimized:
            self.minimize_window()

    def set_dialog_icon(self, dialog):
        """Méthode utilitaire pour définir l'icône des fenêtres de dialogue"""
        icon_path = resource_path("images/logo.ico")
        if os.path.exists(icon_path):
            dialog.iconbitmap(icon_path)
        elif os.path.exists('images/logo.png'):
            try:
                if not os.path.exists('images/logo.ico'):
                    icon = Image.open('images/logo.png')
                    icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
                    icon.save('images/logo.ico')
                dialog.iconbitmap('images/logo.ico')
            except Exception as e:
                print(f"Erreur lors de l'application de l'icône: {e}")

    def center_window(self, window, width, height):
        """Centre une fenêtre sur l'écran"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def load_saved_paths(self):
        """Charge les chemins sauvegardés au démarrage"""
        config_path = os.path.join(os.getcwd(), "client_paths.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        else:
            # Créer le fichier s'il n'existe pas
            default_paths = {'riot': None, 'valorant': None, 'league': None}
            with open(config_path, 'w') as f:
                json.dump(default_paths, f, indent=4)
            return default_paths
        return {'riot': None, 'valorant': None, 'league': None}

    def find_riot_client(self):
        """Trouve les chemins d'installation des clients"""
        # Ajouter une variable de classe pour sauvegarder les chemins
        if not hasattr(self, 'saved_paths'):
            self.saved_paths = self.load_saved_paths()

        paths = {
            'riot': {'name': "Client Riot"},
            'valorant': {'name': "VALORANT"},
            'league': {'name': "League of Legends"}
        }

        dialog = ctk.CTk()
        dialog.title("Recherche des clients")
        self.center_window(dialog, 500, 500)
        dialog.configure(fg_color=self.colors['bg_dark'])

        # Définir l'icône de la fenêtre
        self.set_dialog_icon(dialog)

        # Contenu
        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=30, pady=30)

        # Titre
        title_label = ctk.CTkLabel(
            content_frame,
            text="Rechercher les clients",
            font=("Arial", 20, "bold"),
            text_color=self.colors['text']
        )
        title_label.pack(pady=(0, 10))

        # Nouveau bouton "Rechercher tout"
        search_all_btn = ctk.CTkButton(
            content_frame,
            text="Rechercher automatiquement tous les clients",
            font=("Arial", 13, "bold"),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            height=45,
            corner_radius=10,
            command=lambda: self.search_all_clients(buttons, paths)
        )
        search_all_btn.pack(fill='x', pady=(0, 20))

        # Séparateur
        separator = ctk.CTkFrame(
            content_frame,
            height=2,
            fg_color=self.colors['border']
        )
        separator.pack(fill='x', pady=(0, 20))

        # Variable pour suivre si au moins un client a été trouvé
        clients_found = {'riot': False, 'valorant': False, 'league': False}

        # Boutons de recherche avec retour visuel
        buttons = {}
        for client_type in ['riot', 'valorant', 'league']:
            def create_search_command(ctype):
                def command():
                    # Si le client est déjà trouvé, désactiver le bouton
                    if self.saved_paths.get(ctype):
                        return

                    success = self.search_client(ctype)
                    if success:
                        buttons[ctype].configure(
                            fg_color=self.colors['accent'],
                            text=f"✓ {paths[ctype]['name']} trouvé",
                            state="disabled",
                            hover_color=self.colors['accent']
                        )
                    else:
                        buttons[ctype].configure(
                            fg_color="#FF4444",
                            text=f"✗ {paths[ctype]['name']} non trouvé"
                        )
                return command

            buttons[client_type] = ctk.CTkButton(
                content_frame,
                text=f"Rechercher {paths[client_type]['name']}",
                font=("Arial", 13, "bold"),
                fg_color=self.colors['button'],
                hover_color=self.colors['button_hover'],
                height=45,
                corner_radius=10,
                command=create_search_command(client_type)
            )
            
            # Si le client est déjà trouvé, configurer le bouton comme désactivé
            if self.saved_paths.get(client_type):
                buttons[client_type].configure(
                    fg_color=self.colors['accent'],
                    text=f"✓ {paths[client_type]['name']} trouvé",
                    state="disabled",
                    hover_color=self.colors['accent']
                )
            
            buttons[client_type].pack(fill='x', pady=10)

        # Fonction pour fermer proprement la fenêtre
        def close_window():
            dialog.quit()  # Arrête la boucle mainloop
            dialog.after(100, dialog.destroy)  # Détruit la fenêtre après un court délai

        # Bouton Fermer modifié
        close_btn = ctk.CTkButton(
            content_frame,
            text="Fermer",
            font=("Arial", 13, "bold"),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            height=45,
            corner_radius=10,
            command=close_window  # Utilise la nouvelle fonction
        )
        close_btn.pack(fill='x', pady=(20, 10))

        # Appliquer le thème sombre
        if hasattr(self, 'set_dark_title_bar'):
            self.set_dark_title_bar(dialog)

        dialog.mainloop()

    def show_question(self, message):
        dialog = ctk.CTk()
        dialog.title("Question")
        self.center_window(dialog, 400, 200)
        dialog.configure(fg_color=self.colors['bg_dark'])
        
        icon_path = resource_path("images/logo.ico")
        if os.path.exists(icon_path):
            dialog.iconbitmap(icon_path)

        result = [False]  # Pour stocker la réponse

        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=("Arial", 12),
            wraplength=350,
            text_color=self.colors['text']
        )
        label.pack(pady=(10, 20))

        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(fill='x', pady=(0, 10))

        def on_response(value):
            result[0] = value
            dialog.quit()  # Arrête la boucle mainloop
            dialog.after(100, dialog.destroy)  # Détruit la fenêtre après un court délai

        # Bouton Non
        no_btn = ctk.CTkButton(
            buttons_frame,
            text="Non",
            font=("Arial", 12, "bold"),
            fg_color=self.colors['bg_light'],
            hover_color=self.colors['bg_dark'],
            height=35,
            corner_radius=8,
            command=lambda: on_response(False)
        )
        no_btn.pack(side='left', padx=5, expand=True)

        # Bouton Oui
        yes_btn = ctk.CTkButton(
            buttons_frame,
            text="Oui",
            font=("Arial", 12, "bold"),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            height=35,
            corner_radius=8,
            command=lambda: on_response(True)
        )
        yes_btn.pack(side='right', padx=5, expand=True)

        if hasattr(self, 'set_dark_title_bar'):
            self.set_dark_title_bar(dialog)

        dialog.mainloop()
        return result[0]

    def show_email_options(self):
        dialog = ctk.CTk()
        dialog.title("Vérification e-mail")
        self.center_window(dialog, 400, 300)
        dialog.configure(fg_color=self.colors['bg_dark'])
        
        icon_path = resource_path("images/logo.ico")
        if os.path.exists(icon_path):
            dialog.iconbitmap(icon_path)

        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=30, pady=30)

        # Message
        label = ctk.CTkLabel(
            content_frame,
            text="Une vérification par e-mail est nécessaire.\nChoisissez votre client de messagerie :",
            font=("Arial", 12),
            wraplength=350,
            text_color=self.colors['text']
        )
        label.pack(pady=(0, 20))

        # Dictionnaire des clients e-mail avec leurs URLs/commandes
        email_clients = {
            "Gmail": "https://gmail.com",
            "Outlook": "https://outlook.live.com",
            "Windows Mail": "ms-outlook:",
            "Yahoo Mail": "https://mail.yahoo.com"
        }

        # Fonction pour ouvrir le client e-mail
        def open_email_client(client):
            import webbrowser
            if client == "Windows Mail":
                os.system("start ms-outlook:")
            else:
                webbrowser.open(email_clients[client])
            dialog.destroy()
            dialog.quit()

        # Créer les boutons pour chaque client e-mail
        for client in email_clients:
            btn = ctk.CTkButton(
                content_frame,
                text=client,
                font=("Arial", 13, "bold"),
                fg_color=self.colors['button'],
                hover_color=self.colors['button_hover'],
                height=40,
                corner_radius=8,
                command=lambda c=client: open_email_client(c)
            )
            btn.pack(fill='x', pady=5)

        if hasattr(self, 'set_dark_title_bar'):
            self.set_dark_title_bar(dialog)

        dialog.mainloop()

    def find_riot_window(self):
        """Trouve la fenêtre du client Riot de manière fiable avec vérifications supplémentaires"""
        def enum_window_callback(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if "Riot Client" in window_title or "Riot Games" in window_title:
                    try:
                        # Vérifier si la fenêtre est réellement visible et non minimisée
                        placement = win32gui.GetWindowPlacement(hwnd)
                        if placement[1] != 2:  # 2 = SW_SHOWMINIMIZED
                            # Vérifier que le processus appartient bien à Riot
                            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                            try:
                                process = psutil.Process(process_id)
                                if "Riot" in process.name() and process.is_running():
                                    # Vérifier que la fenêtre est accessible
                                    if win32gui.IsWindowEnabled(hwnd):
                                        result.append(hwnd)
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                    except Exception:
                        pass
        hwnd_list = []
        win32gui.EnumWindows(enum_window_callback, hwnd_list)
        return hwnd_list[0] if hwnd_list else None

    def verify_riot_client_running(self):
        """Vérifie si le client Riot est en cours d'exécution"""
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if "RiotClientServices" in proc.info['name']:
                        self.logger.info(f"Client Riot trouvé : PID {proc.pid}")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            self.logger.warning("Client Riot non trouvé")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification du client Riot : {str(e)}")
            return False

    def force_window_focus(self, hwnd):
        """Force le focus sur une fenêtre avec plusieurs méthodes"""
        try:
            # Restaurer la fenêtre si elle est minimisée
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # Activer la fenêtre
            win32gui.SetForegroundWindow(hwnd)
            
            # Forcer le focus avec différentes méthodes
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetActiveWindow(hwnd)
            
            # Vérifier que le focus a été obtenu
            return win32gui.GetForegroundWindow() == hwnd
        except Exception:
            return False

    def ensure_window_focus(self, riot_window):
        """S'assure que la fenêtre Riot est au premier plan avec vérifications"""
        max_attempts = 5
        for _ in range(max_attempts):
            try:
                # Vérifier que la fenêtre existe toujours
                if not win32gui.IsWindow(riot_window):
                    return False
                    
                # Vérifier que le processus est toujours en cours
                if not self.verify_riot_client_running():
                    return False
                    
                # Vérifier le focus actuel
                current_focus = win32gui.GetForegroundWindow()
                if current_focus == riot_window:
                    return True
                    
                # Tenter de forcer le focus
                if self.force_window_focus(riot_window):
                    sleep(0.2)  # Attendre que le focus soit effectif
                    return win32gui.GetForegroundWindow() == riot_window
                    
            except Exception:
                pass
            sleep(0.1)
        return False

    def search_all_clients(self, buttons, paths):
        """Recherche automatiquement tous les clients"""
        for client_type in ['riot', 'valorant', 'league']:
            # Ne rechercher que si le client n'est pas déjà trouvé
            if not self.saved_paths.get(client_type):
                success = self.search_client(client_type)
                if success:
                    buttons[client_type].configure(
                        fg_color=self.colors['accent'],
                        text=f"✓ {paths[client_type]['name']} trouvé",
                        state="disabled",
                        hover_color=self.colors['accent']
                    )
                else:
                    buttons[client_type].configure(
                        fg_color="#FF4444",
                        text=f"✗ {paths[client_type]['name']} non trouvé"
                    )

    def search_client(self, client_type):
        """Recherche un client spécifique"""
        paths = {
            'riot': {
                'name': "Client Riot",
                'paths': [
                    "C:/Riot Games/Riot Client/RiotClientServices.exe",
                    "C:/Program Files/Riot Games/Riot Client/RiotClientServices.exe",
                    "C:/Program Files (x86)/Riot Games/Riot Client/RiotClientServices.exe",
                ]
            },
            'valorant': {
                'name': "VALORANT",
                'paths': [
                    "C:/Riot Games/VALORANT/VALORANT.exe",
                    "C:/Program Files/Riot Games/VALORANT/VALORANT.exe",
                    "C:/Program Files (x86)/Riot Games/VALORANT/VALORANT.exe",
                    "C:/Riot Games/VALORANT/live/VALORANT.exe"
                ]
            },
            'league': {
                'name': "League of Legends",
                'paths': [
                    "C:/Riot Games/League of Legends/LeagueClient.exe",
                    "C:/Program Files/Riot Games/League of Legends/LeagueClient.exe",
                    "C:/Program Files (x86)/Riot Games/League of Legends/LeagueClient.exe",
                ]
            }
        }

        # Si déjà trouvé précédemment, utiliser le chemin sauvegardé
        if self.saved_paths.get(client_type):
            if os.path.exists(self.saved_paths[client_type]):
                if client_type == 'riot':
                    self.riot_client_path = self.saved_paths[client_type]
                return True
            else:
                self.saved_paths[client_type] = None
                self.save_paths()

        client_found = False
        for path in paths[client_type]['paths']:
            if os.path.exists(path):
                if client_type == 'riot':
                    self.riot_client_path = path
                self.saved_paths[client_type] = path
                self.save_paths()
                client_found = True
                break
        
        if not client_found:
            result = self.show_question(
                f"{paths[client_type]['name']} non trouvé.\nVoulez-vous sélectionner le chemin manuellement ?"
            )
            if result:
                selected_path = self.browse_path(client_type) or self.manual_path_input(client_type, paths[client_type]['name'])
                if selected_path:
                    self.saved_paths[client_type] = selected_path
                    self.save_paths()
                    client_found = True
                else:
                    self.show_error(f"Aucun chemin valide fourni pour {paths[client_type]['name']}")
            else:
                self.show_error(f"{paths[client_type]['name']} non trouvé et sélection manuelle annulée")
        
        return client_found

    def browse_path(self, client_type):
        """Ouvre une boîte de dialogue pour sélectionner un fichier"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title=f"Sélectionner {client_type}",
            filetypes=[("Executable", "*.exe")],
            initialdir="C:/Riot Games"
        )
        if file_path:
            if client_type == 'riot':
                self.riot_client_path = file_path
            return file_path
        return None

    def manual_path_input(self, client_type, client_name):
        """Affiche une boîte de dialogue pour saisir manuellement le chemin"""
        dialog = ctk.CTkInputDialog(
            text=f"Entrez le chemin complet vers {client_name} :",
            title="Saisie manuelle du chemin"
        )
        path = dialog.get_input()
        if path and os.path.exists(path) and path.endswith('.exe'):
            if client_type == 'riot':
                self.riot_client_path = path
            return path
        return None

    def save_paths(self):
        """Sauvegarde les chemins trouvés"""
        config_path = os.path.join(os.getcwd(), "client_paths.json")
        with open(config_path, 'w') as f:
            json.dump(self.saved_paths, f, indent=4)

    def show_logs(self):
        """Affiche la fenêtre des logs"""
        log_window = ctk.CTkToplevel(self.window)
        log_window.title("Logs de l'application")
        self.center_window(log_window, 800, 600)
        log_window.configure(fg_color=self.colors['bg_dark'])
        
        # Garder la fenêtre au premier plan
        log_window.attributes('-topmost', True)
        log_window.focus_force()
        
        # Désactiver le topmost après quelques secondes
        log_window.after(2000, lambda: log_window.attributes('-topmost', False))
        
        # Définir l'icône de la fenêtre (barre des tâches)
        icon_path = resource_path("images/logo.ico")
        if os.path.exists(icon_path):
            log_window.iconbitmap(icon_path)
        elif os.path.exists('images/logo.png'):
            try:
                # Convertir PNG en ICO
                icon = Image.open('images/logo.png')
                # Redimensionner à 32x32 pour une meilleure compatibilité
                icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
                icon.save('images/logo.ico')
                log_window.iconbitmap('images/logo.ico')
            except Exception as e:
                print(f"Erreur lors de la conversion de l'icône: {e}")
        
        # Logo en haut de la fenêtre
        if 'logo' in self.images:  # Utiliser l'image déjà chargée
            logo_label = ctk.CTkLabel(
                log_window,
                text="",
                image=self.images['logo']
            )
            logo_label.pack(pady=(10, 0))
            
            # Titre avec le logo
            title_label = ctk.CTkLabel(
                log_window,
                text="Logs de l'application",
                font=("Arial", 16, "bold"),
                text_color=self.colors['text']
            )
            title_label.pack(pady=(5, 10))
        
        # Frame principal
        main_frame = ctk.CTkFrame(log_window, fg_color="transparent")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Zone de texte pour les logs (lecture seule)
        log_text = ctk.CTkTextbox(
            main_frame,
            fg_color=self.colors['bg_light'],
            text_color=self.colors['text'],
            font=("Consolas", 12),
            wrap="none",
            state="disabled"  # Rend le textbox en lecture seule
        )
        log_text.pack(fill='both', expand=True)
        
        # Fonction pour rafraîchir les logs
        def refresh_logs():
            # Activer temporairement pour insérer le texte
            log_text.configure(state="normal")
            log_text.delete('1.0', 'end')
            try:
                with open("switchmaster.log", 'r', encoding='utf-8') as f:
                    log_text.insert('end', f.read())
                log_text.see('end')  # Défiler jusqu'à la fin
            except Exception as e:
                log_text.insert('end', f"Erreur lors de la lecture des logs : {str(e)}")
            # Remettre en lecture seule
            log_text.configure(state="disabled")
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Bouton rafraîchir
        refresh_btn = ctk.CTkButton(
            button_frame,
            text="Rafraîchir",
            font=("Arial", 12, "bold"),
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            width=100,
            command=refresh_logs
        )
        refresh_btn.pack(side='left', padx=5)
        
        # Bouton fermer
        close_btn = ctk.CTkButton(
            button_frame,
            text="Fermer",
            font=("Arial", 12, "bold"),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            width=100,
            command=log_window.destroy
        )
        close_btn.pack(side='right', padx=5)
        
        # Charger les logs initiaux
        refresh_logs()

if __name__ == "__main__":
    app = SwitchMaster()
    app.run() 