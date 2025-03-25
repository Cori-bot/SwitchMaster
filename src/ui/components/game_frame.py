"""
Game frame component for SwitchMaster
Implements a frame for managing game accounts and launching games
"""
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from ...utils.window_utils import resource_path, create_rounded_rectangle
from ..components.account_dialog import AccountDialog
from ..components.switch_confirmation_dialog import SwitchConfirmationDialog
from ...utils.resource_path import resource_path

class GameFrame(ctk.CTkFrame):
    """
    Frame for managing game accounts and launching games.
    """
    def __init__(self, 
                 parent=None,
                 game_name=None,
                 account_manager=None,
                 client_finder=None,
                 game_launcher=None,
                 logger=None,
                 colors=None,
                 images=None):
        """
        Initialize the game frame.
        
        Args:
            parent: Parent widget
            game_name: Name of the game
            account_manager: Account manager instance
            client_finder: Client finder instance
            game_launcher: Game launcher instance
            logger: Logger instance
            colors: Color scheme dictionary
            images: Dictionary of loaded images
        """
        super().__init__(parent, fg_color=colors.get('bg_darker', '#1A1A1A'))
        
        self.game_name = game_name
        self.account_manager = account_manager
        self.client_finder = client_finder
        self.game_launcher = game_launcher
        self.logger = logger
        self.colors = colors or {}
        self.images = images or {}
        
        self.accounts = []
        self.selected_account = None
        
        # Load game logo
        self.load_game_logo()
        
        self.create_game_frame()
        self.load_accounts()
        
    def load_game_logo(self):
        """Load the game logo."""
        game_id = self._normalize_game_id()
        logo_path = resource_path(os.path.join("assets", "images", f"{game_id}.png"))
        
        try:
            if os.path.exists(logo_path):
                # Charger et redimensionner l'image
                image = Image.open(logo_path)
                image = image.resize((24, 24), Image.Resampling.LANCZOS)
                self.game_logo = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=(24, 24)
                )
            else:
                if self.logger:
                    self.logger.warning(f"Logo non trouvé: {logo_path}")
                self.game_logo = None
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors du chargement du logo {game_id}: {str(e)}")
            self.game_logo = None
        
    def _normalize_game_id(self):
        """Normalize game name for use as an ID."""
        return self.game_name.lower().replace(' ', '_').replace('league_of_legends', 'league')
        
    def create_game_frame(self):
        """Create the game frame UI."""
        # Game header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill='x', padx=10, pady=5)
        
        # Game logo
        if self.game_logo:
            logo_label = ctk.CTkLabel(
                header_frame,
                text="",
                image=self.game_logo
            )
            logo_label.pack(side='left', padx=5)
        
        # Game title
        title_label = ctk.CTkLabel(
            header_frame,
            text=self.game_name,
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors.get('text', '#FFFFFF')
        )
        title_label.pack(side='left', padx=5)
        
        # Accounts list frame
        accounts_frame = ctk.CTkFrame(self, fg_color="transparent")
        accounts_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Accounts list
        self.accounts_list = ctk.CTkScrollableFrame(
            accounts_frame,
            fg_color=self.colors.get('bg_dark', '#1E1E1E'),
            corner_radius=10
        )
        self.accounts_list.pack(fill='both', expand=True)
        
        # Add account button
        add_btn = ctk.CTkButton(
            self,
            text="Add Account",
            image=self.images.get('add'),
            compound="left",
            command=self.add_account,
            fg_color=self.colors.get('button', '#3391D4'),
            hover_color=self.colors.get('button_hover', '#4BA3E3')
        )
        add_btn.pack(side='bottom', fill='x', padx=10, pady=10)
        
    def load_accounts(self):
        """Load accounts for the game."""
        self.logger.info(f"Loading accounts for {self.game_name}")
        
        # Clear existing account buttons
        for widget in self.accounts_list.winfo_children():
            widget.destroy()
            
        # Get accounts for this game
        game_id = self._normalize_game_id()
        accounts = self.account_manager.get_all_accounts(game_id)
        
        if not accounts:
            label = ctk.CTkLabel(
                self.accounts_list,
                text="Aucun compte trouvé",
                text_color=self.colors.get('text_secondary', "#A0A0A0"),
                font=("Arial", 12)
            )
            label.pack(pady=20)
            return
            
        # Create buttons for each account
        for i, account in enumerate(accounts):
            account_frame = ctk.CTkFrame(
                self.accounts_list,
                fg_color=self.colors.get('bg_light', "#2D2D2D"),
                corner_radius=8
            )
            account_frame.pack(fill="x", pady=5, padx=10)
            
            # Account details
            details_frame = ctk.CTkFrame(
                account_frame,
                fg_color="transparent"
            )
            details_frame.pack(fill="x", expand=True, side="left", padx=10, pady=5)
            
            # Username
            username_label = ctk.CTkLabel(
                details_frame,
                text=account.get('username', 'Unknown'),
                font=("Arial", 12, "bold"),
                text_color=self.colors.get('text', "#FFFFFF")
            )
            username_label.pack(anchor="w")
            
            # Notes (if any)
            if account.get('notes'):
                notes_label = ctk.CTkLabel(
                    details_frame,
                    text=account.get('notes', ''),
                    font=("Arial", 10),
                    text_color=self.colors.get('text_secondary', "#A0A0A0")
                )
                notes_label.pack(anchor="w")
            
            # Buttons
            buttons_frame = ctk.CTkFrame(
                account_frame,
                fg_color="transparent"
            )
            buttons_frame.pack(side="right", padx=5)
            
            # Edit button
            edit_btn = ctk.CTkButton(
                buttons_frame,
                text="Edit",
                font=("Arial", 11),
                width=60,
                height=25,
                corner_radius=5,
                fg_color=self.colors.get('bg_dark', "#1E1E1E"),
                hover_color=self.colors.get('accent', "#FF4655"),
                command=lambda acc=account: self.edit_account(acc.get('num'))
            )
            edit_btn.pack(side="right", padx=5)
            
            # Switch button
            switch_btn = ctk.CTkButton(
                buttons_frame,
                text="Switch",
                font=("Arial", 11),
                width=60,
                height=25,
                corner_radius=5,
                fg_color=self.colors.get('button', "#3391D4"),
                hover_color=self.colors.get('button_hover', "#40A9FF"),
                command=lambda acc=account: self.switch_account(acc)
            )
            switch_btn.pack(side="right", padx=5)
            
    def add_account(self):
        """Open the add account dialog."""
        dialog = AccountDialog(
            parent=self.winfo_toplevel(),
            title=f"Add Account",
            game_id=self._normalize_game_id(),
            account_manager=self.account_manager,
            logger=self.logger,
            on_save_callback=self._on_account_saved,
            colors=self.colors
        )
        dialog.show()
    
    def edit_account(self, account_num):
        """Open the edit account dialog."""
        account = self.account_manager.get_account(self._normalize_game_id(), account_num)
        if account:
            dialog = AccountDialog(
                parent=self.winfo_toplevel(),
                title=f"Edit Account",
                game_id=self._normalize_game_id(),
                account_manager=self.account_manager,
                account_num=account_num,
                account=account,
                logger=self.logger,
                on_save_callback=self._on_account_saved,
                allow_delete=True,
                colors=self.colors
            )
            dialog.show()
    
    def _on_account_saved(self, account_num, account_data):
        """Callback for when an account is saved."""
        game_id = self._normalize_game_id()
        if account_num is not None:  # Editing existing account
            self.account_manager.update_account(
                game_id, 
                account_num, 
                account_data["username"], 
                account_data["password"],
                account_data.get("notes", "")
            )
        else:  # Adding new account
            self.account_manager.add_account(
                game_id,
                account_data["username"],
                account_data["password"],
                account_data.get("notes", "")
            )
        self.load_accounts()
        
    def switch_account(self, account):
        """Switch to the selected account."""
        if not self.game_launcher:
            return
            
        self.selected_account = account
        game_id = self._normalize_game_id()
        
        # Afficher le dialogue de confirmation
        dialog = SwitchConfirmationDialog(
            parent=self.winfo_toplevel(),
            account=account,
            colors=self.colors,
            logger=self.logger,
            on_confirm_callback=self._perform_account_switch,
            game_id=game_id
        )
        dialog.show()
        
    def _perform_account_switch(self, account, stay_logged_in, launch_game_id=None):
        """
        Effectue réellement le changement de compte après confirmation.
        
        Args:
            account (dict): Informations du compte
            stay_logged_in (bool): Option pour rester connecté
            launch_game_id (str, optional): ID du jeu à lancer après la connexion
        """
        game_id = self._normalize_game_id()
        username = account.get('username', 'Unknown')
        main_window = None
        
        # Mise à jour du statut si le logger est disponible
        if hasattr(self, 'logger') and self.logger:
            # Log indicating the account switch and stay logged in option
            login_info = f"avec 'Rester connecté' activé" if stay_logged_in else "sans 'Rester connecté'"
            game_launch_info = f" et lancement du jeu" if launch_game_id else ""
            self.logger.info(f"✨ Changement vers le compte {username} ({login_info}{game_launch_info})...")
            
            # Si nous avons accès à la fenêtre principale à travers le logger
            if hasattr(self.logger, 'get_main_window'):
                main_window = self.logger.get_main_window()
                if main_window:
                    activity_msg = f"Changement de compte: {username}"
                    if launch_game_id:
                        activity_msg += f" et lancement de {launch_game_id}"
                    main_window.start_activity(activity_msg)
        
        # Ensure account has the decrypted password correctly set
        if self.account_manager:
            # Retrieve a fresh copy of the account with properly decrypted password
            fresh_account = self.account_manager.get_account(game_id, account['num'])
            if fresh_account:
                if self.logger:
                    self.logger.info(f"Utilisation du compte: {fresh_account.get('username')}")
                account_to_use = fresh_account
            else:
                account_to_use = account
                if self.logger:
                    self.logger.warning(f"Impossible de rafraîchir le compte, utilisation des données existantes")
        else:
            account_to_use = account
        
        result = False
        
        # Always use the Riot client path, not the game client path
        if self.client_finder:
            # Get the Riot client path directly
            riot_client_path = self.client_finder.get_client_path('riot')
            
            if riot_client_path and os.path.exists(riot_client_path):
                if self.logger:
                    self.logger.info(f"Utilisation du client Riot: {riot_client_path}")
                result = self.game_launcher.switch_account(riot_client_path, account_to_use, stay_logged_in, launch_game_id)
            else:
                if self.logger:
                    self.logger.error("Client Riot non trouvé. Recherche en cours...")
                # Try to find the Riot client
                success, path = self.client_finder.search_client('riot')
                if success:
                    result = self.game_launcher.switch_account(path, account_to_use, stay_logged_in, launch_game_id)
                else:
                    if self.logger:
                        self.logger.error("Impossible de trouver le client Riot")
        
        # Mise à jour de l'activité pour indiquer qu'elle est terminée
        if main_window:
            # Short delay to ensure all operations are complete
            self.after(2000, lambda: main_window.end_activity(
                f"Compte {username} connecté" + (" et jeu lancé" if launch_game_id else ""), 
                "SUCCESS" if result else "ERROR"
            ))
        
        return result 