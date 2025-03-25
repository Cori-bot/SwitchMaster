"""
Switch confirmation dialog component for SwitchMaster
Dialog to confirm account switching and provide additional options
"""
import customtkinter as ctk
from ...utils.window_utils import center_window, set_dark_title_bar, set_window_icon


class SwitchConfirmationDialog:
    """
    Dialog for confirming account switch with additional options.
    """
    def __init__(self, parent, account, colors=None, logger=None, on_confirm_callback=None, game_id=None):
        """
        Initialize the switch confirmation dialog.
        
        Args:
            parent: Parent widget
            account (dict): Account information
            colors (dict): Color scheme dictionary
            logger: Logger instance
            on_confirm_callback: Callback function to run after confirming
            game_id (str): The ID of the game
        """
        self.parent = parent
        self.account = account
        self.colors = colors or {}
        self.logger = logger
        self.on_confirm_callback = on_confirm_callback
        self.game_id = game_id
        self.stay_logged_in = ctk.BooleanVar(value=False)
        self.launch_game = ctk.BooleanVar(value=False)
        
        # Create the dialog
        self.create_dialog()
        
    def create_dialog(self):
        """Create and show the dialog."""
        # Create dialog window
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Confirmation de changement de compte")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Set size and position
        center_window(self.dialog, 400, 370)
        
        # Configure appearance
        self.dialog.configure(fg_color=self.colors.get('bg_dark', "#1E1E1E"))
        
        # Keep on top temporarily and maintain icon
        self.dialog.attributes('-topmost', True)
        self.dialog.focus_force()
        
        def maintain_icon():
            if self.dialog.winfo_exists():
                set_window_icon(self.dialog)
                self.dialog.after(100, maintain_icon)
                
        maintain_icon()
        self.dialog.after(250, lambda: self.dialog.attributes('-topmost', False))
        set_dark_title_bar(self.dialog)
        
        # Content frame
        content_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text="Confirmer le changement de compte",
            font=("Arial", 18, "bold"),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        title_label.pack(pady=(0, 20))
        
        # Account info
        account_frame = ctk.CTkFrame(content_frame, fg_color=self.colors.get('bg_darker', "#181818"))
        account_frame.pack(fill='x', padx=10, pady=10)
        
        account_name_label = ctk.CTkLabel(
            account_frame,
            text=f"Compte: {self.account.get('username', 'Inconnu')}",
            font=("Arial", 14),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        account_name_label.pack(pady=(10, 10), padx=10)
        
        # Stay logged in option
        self.stay_logged_checkbox = ctk.CTkCheckBox(
            content_frame,
            text="Rester connecté après la connexion",
            variable=self.stay_logged_in,
            font=("Arial", 12),
            text_color=self.colors.get('text', "#FFFFFF"),
            fg_color=self.colors.get('accent', "#FF4655"),
            hover_color=self.colors.get('accent_hover', "#FF5F6D"),
        )
        self.stay_logged_checkbox.pack(pady=(15, 5), padx=10, anchor="w")
        
        # Launch game option
        self.launch_game_checkbox = ctk.CTkCheckBox(
            content_frame,
            text="Démarrer le jeu après la connexion",
            variable=self.launch_game,
            font=("Arial", 12),
            text_color=self.colors.get('text', "#FFFFFF"),
            fg_color=self.colors.get('accent', "#FF4655"),
            hover_color=self.colors.get('accent_hover', "#FF5F6D"),
        )
        self.launch_game_checkbox.pack(pady=(5, 5), padx=10, anchor="w")
        
        # Avertissement pour l'option "Rester connecté"
        warning_frame = ctk.CTkFrame(
            content_frame,
            fg_color=self.colors.get('bg_very_dark', "#0A0A0A"),
            corner_radius=6
        )
        warning_frame.pack(fill='x', padx=10, pady=(0, 15))
        
        warning_text = ctk.CTkLabel(
            warning_frame,
            text="⚠️ ATTENTION: Si vous restez connecté, vous ne pourrez plus\nchanger de compte avec SwitchMaster sans vous déconnecter\nmanuellement via le client Riot.",
            font=("Arial", 10),
            text_color="#FFA500",  # Orange pour l'avertissement
            justify="left"
        )
        warning_text.pack(pady=8, padx=8)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            fg_color=self.colors.get('button_secondary', "#2A2A2A"),
            hover_color=self.colors.get('button_secondary_hover', "#3A3A3A"),
            command=self.cancel
        )
        cancel_btn.pack(side='left', expand=True, padx=5)
        
        # Confirm button
        confirm_btn = ctk.CTkButton(
            buttons_frame,
            text="Confirmer",
            fg_color=self.colors.get('accent', "#FF4655"),
            hover_color=self.colors.get('accent_hover', "#FF5F6D"),
            command=self.confirm
        )
        confirm_btn.pack(side='right', expand=True, padx=5)
    
    def confirm(self):
        """Confirm the account switch."""
        # Afficher l'avertissement de freeze avant d'exécuter le callback
        self.show_freeze_warning()
    
    def show_freeze_warning(self):
        """Affiche un avertissement concernant le possible freeze de l'application."""
        # Détruire la boîte de dialogue actuelle
        self.dialog.destroy()
        
        # Créer une nouvelle boîte de dialogue d'avertissement
        warning_dialog = ctk.CTkToplevel(self.parent)
        warning_dialog.title("Avertissement - Possible freeze")
        warning_dialog.transient(self.parent)
        warning_dialog.grab_set()
        
        # Set size and position
        center_window(warning_dialog, 450, 250)
        
        # Configure appearance
        warning_dialog.configure(fg_color=self.colors.get('bg_dark', "#1E1E1E"))
        
        # Keep on top temporarily and maintain icon
        warning_dialog.attributes('-topmost', True)
        warning_dialog.focus_force()
        
        def maintain_icon():
            if warning_dialog.winfo_exists():
                set_window_icon(warning_dialog)
                warning_dialog.after(100, maintain_icon)
                
        maintain_icon()
        warning_dialog.after(250, lambda: warning_dialog.attributes('-topmost', False))
        set_dark_title_bar(warning_dialog)
        
        # Content frame
        content_frame = ctk.CTkFrame(warning_dialog, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Icône d'avertissement
        warning_label = ctk.CTkLabel(
            content_frame,
            text="⚠️",
            font=("Arial", 30, "bold"),
            text_color="#FFA500"  # Orange
        )
        warning_label.pack(pady=(0, 10))
        
        # Message d'avertissement
        message_label = ctk.CTkLabel(
            content_frame,
            text="L'application pourrait ne pas répondre pendant\nquelques secondes durant le changement de compte.",
            font=("Arial", 14),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        message_label.pack(pady=(0, 10))
        
        # Explication
        explanation_label = ctk.CTkLabel(
            content_frame,
            text="Cela est normal et dû au fait que le launcher Riot\ndoit être maintenu au premier plan pendant le processus.\nL'application reprendra son fonctionnement normalement ensuite.",
            font=("Arial", 12),
            text_color=self.colors.get('text_secondary', "#B0B0B0"),
            justify="left"
        )
        explanation_label.pack(pady=(0, 15))
        
        # Continuer button
        continue_btn = ctk.CTkButton(
            content_frame,
            text="Continuer",
            fg_color=self.colors.get('accent', "#FF4655"),
            hover_color=self.colors.get('accent_hover', "#FF5F6D"),
            command=lambda: self.proceed_with_switch(warning_dialog)
        )
        continue_btn.pack(pady=(10, 0))
    
    def proceed_with_switch(self, warning_dialog):
        """Procède au changement de compte après l'avertissement."""
        # Fermer la boîte de dialogue d'avertissement
        warning_dialog.destroy()
        
        # Exécuter le callback de confirmation avec les options sélectionnées
        if self.on_confirm_callback:
            launch_game_id = self.game_id if self.launch_game.get() else None
            self.on_confirm_callback(self.account, self.stay_logged_in.get(), launch_game_id)
    
    def cancel(self):
        """Cancel the account switch."""
        self.dialog.destroy()
    
    def show(self):
        """Show the dialog."""
        if not hasattr(self, 'dialog'):
            self.create_dialog() 