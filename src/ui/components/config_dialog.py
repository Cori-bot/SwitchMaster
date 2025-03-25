"""
Configuration dialog component for SwitchMaster
Dialog for managing application settings
"""
import customtkinter as ctk
from tkinter import messagebox
from ...utils.window_utils import center_window, set_dark_title_bar, set_window_icon
import json
import os


class ConfigDialog:
    """
    Dialog for application configuration.
    Handles viewing and modifying application settings.
    """
    def __init__(self, parent, title="Configuration", colors=None, 
                 config_path=None, on_save_callback=None, logger=None):
        """
        Initialize the configuration dialog.
        
        Args:
            parent: Parent widget
            title (str): Dialog title
            colors (dict): Color scheme dictionary
            config_path (str): Path to the configuration file
            on_save_callback: Callback function to run after saving
            logger: Logger instance
        """
        self.parent = parent
        self.title = title
        self.colors = colors or {}
        self.config_path = config_path
        self.on_save_callback = on_save_callback
        self.logger = logger
        
        # Default configuration values
        self.default_config = {
            "general": {
                "theme": "dark",
                "log_level": "INFO"
            },
            "app": {
                "start_minimized": False,
                "auto_run_on_startup": False,
                "check_updates": True
            },
            "game": {
                "auto_close_launcher": True,
                "close_client_on_switch": False,
                "valorant_path": "",
                "league_path": ""
            }
        }
        
        # Load current configuration
        self.config = self.load_config()
        
        # Create the dialog
        self.dialog = None
        self.create_dialog()
    
    def load_config(self):
        """Load configuration from file or return defaults."""
        config = self.default_config.copy()
        
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    saved_config = json.load(f)
                
                # Update default config with saved values
                for section in config:
                    if section in saved_config:
                        for key in config[section]:
                            if key in saved_config[section]:
                                config[section][key] = saved_config[section][key]
                                
                if self.logger:
                    self.logger.info(f"✅ Configuration loaded from {self.config_path}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"❌ Failed to load configuration: {str(e)}")
        
        return config
    
    def save_config(self):
        """Save configuration to file."""
        if not self.config_path:
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            if self.logger:
                self.logger.info(f"✅ Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to save configuration: {str(e)}")
            return False
    
    def create_dialog(self):
        """Create and show the dialog."""
        # Create dialog window
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Set size and position
        center_window(self.dialog, 500, 550)
        
        # Configure appearance
        self.dialog.configure(fg_color=self.colors.get('bg_dark', "#1E1E1E"))
        set_window_icon(self.dialog)
        set_dark_title_bar(self.dialog)
        
        # Keep on top temporarily
        self.dialog.attributes('-topmost', True)
        self.dialog.focus_force()
        self.dialog.after(250, lambda: self.dialog.attributes('-topmost', False))
        
        # Content frame
        content_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text=self.title,
            font=("Arial", 20, "bold"),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        title_label.pack(pady=(0, 20))
        
        # Tabview for different sections
        tabview = ctk.CTkTabview(
            content_frame,
            fg_color=self.colors.get('bg_light', "#2D2D2D"),
            segmented_button_fg_color=self.colors.get('bg_dark', "#1E1E1E"),
            segmented_button_selected_color=self.colors.get('accent', "#FF4655"),
            segmented_button_selected_hover_color=self.colors.get('accent_hover', "#FF5F6D"),
            segmented_button_unselected_color=self.colors.get('bg_dark', "#1E1E1E"),
            segmented_button_unselected_hover_color=self.colors.get('bg_very_dark', "#131313")
        )
        tabview.pack(fill='both', expand=True)
        
        # Create tabs
        general_tab = tabview.add("Général")
        app_tab = tabview.add("Application")
        game_tab = tabview.add("Jeu")
        
        # Set active tab
        tabview.set("Général")
        
        # General tab content
        self.create_general_tab(general_tab)
        
        # App tab content
        self.create_app_tab(app_tab)
        
        # Game tab content
        self.create_game_tab(game_tab)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            font=("Arial", 14),
            fg_color=self.colors.get('bg_light', "#2D2D2D"),
            hover_color=self.colors.get('bg_very_light', "#3D3D3D"),
            height=40,
            corner_radius=8,
            command=self.dialog.destroy
        )
        cancel_btn.pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        # Save button
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Sauvegarder",
            font=("Arial", 14, "bold"),
            fg_color=self.colors.get('accent', "#FF4655"),
            hover_color=self.colors.get('accent_hover', "#FF5F6D"),
            height=40,
            corner_radius=8,
            command=self.save_settings
        )
        save_btn.pack(side='right', fill='x', expand=True)
    
    def create_general_tab(self, parent):
        """Create the general settings tab."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Theme selection
        theme_label = ctk.CTkLabel(
            frame,
            text="Thème:",
            font=("Arial", 12, "bold"),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        theme_label.pack(anchor='w', pady=(0, 5))
        
        self.theme_var = ctk.StringVar(value=self.config["general"]["theme"])
        theme_dropdown = ctk.CTkComboBox(
            frame,
            values=["dark", "light"],
            variable=self.theme_var,
            height=35,
            fg_color=self.colors.get('bg_dark', "#1E1E1E"),
            border_color=self.colors.get('border', "#333333"),
            button_color=self.colors.get('bg_very_dark', "#131313"),
            button_hover_color=self.colors.get('bg_dark', "#1E1E1E"),
            dropdown_fg_color=self.colors.get('bg_dark', "#1E1E1E"),
            dropdown_hover_color=self.colors.get('bg_light', "#2D2D2D")
        )
        theme_dropdown.pack(fill='x', pady=(0, 20))
        
        # Log level selection
        log_level_label = ctk.CTkLabel(
            frame,
            text="Niveau de journalisation:",
            font=("Arial", 12, "bold"),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        log_level_label.pack(anchor='w', pady=(0, 5))
        
        self.log_level_var = ctk.StringVar(value=self.config["general"]["log_level"])
        log_level_dropdown = ctk.CTkComboBox(
            frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            variable=self.log_level_var,
            height=35,
            fg_color=self.colors.get('bg_dark', "#1E1E1E"),
            border_color=self.colors.get('border', "#333333"),
            button_color=self.colors.get('bg_very_dark', "#131313"),
            button_hover_color=self.colors.get('bg_dark', "#1E1E1E"),
            dropdown_fg_color=self.colors.get('bg_dark', "#1E1E1E"),
            dropdown_hover_color=self.colors.get('bg_light', "#2D2D2D")
        )
        log_level_dropdown.pack(fill='x', pady=(0, 20))
    
    def create_app_tab(self, parent):
        """Create the application settings tab."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Start minimized
        self.start_minimized_var = ctk.BooleanVar(value=self.config["app"]["start_minimized"])
        start_minimized_switch = ctk.CTkSwitch(
            frame,
            text="Démarrer minimisé",
            font=("Arial", 12),
            variable=self.start_minimized_var,
            progress_color=self.colors.get('accent', "#FF4655"),
            button_color=self.colors.get('bg_very_light', "#3D3D3D"),
            button_hover_color=self.colors.get('bg_light', "#2D2D2D")
        )
        start_minimized_switch.pack(anchor='w', pady=(0, 15))
        
        # Auto run on startup
        self.auto_run_var = ctk.BooleanVar(value=self.config["app"]["auto_run_on_startup"])
        auto_run_switch = ctk.CTkSwitch(
            frame,
            text="Lancer au démarrage",
            font=("Arial", 12),
            variable=self.auto_run_var,
            progress_color=self.colors.get('accent', "#FF4655"),
            button_color=self.colors.get('bg_very_light', "#3D3D3D"),
            button_hover_color=self.colors.get('bg_light', "#2D2D2D")
        )
        auto_run_switch.pack(anchor='w', pady=(0, 15))
        
        # Check for updates
        self.check_updates_var = ctk.BooleanVar(value=self.config["app"]["check_updates"])
        check_updates_switch = ctk.CTkSwitch(
            frame,
            text="Vérifier les mises à jour",
            font=("Arial", 12),
            variable=self.check_updates_var,
            progress_color=self.colors.get('accent', "#FF4655"),
            button_color=self.colors.get('bg_very_light', "#3D3D3D"),
            button_hover_color=self.colors.get('bg_light', "#2D2D2D")
        )
        check_updates_switch.pack(anchor='w', pady=(0, 15))
    
    def create_game_tab(self, parent):
        """Create the game settings tab."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Auto close launcher
        self.auto_close_launcher_var = ctk.BooleanVar(value=self.config["game"]["auto_close_launcher"])
        auto_close_launcher_switch = ctk.CTkSwitch(
            frame,
            text="Fermer automatiquement le launcher",
            font=("Arial", 12),
            variable=self.auto_close_launcher_var,
            progress_color=self.colors.get('accent', "#FF4655"),
            button_color=self.colors.get('bg_very_light', "#3D3D3D"),
            button_hover_color=self.colors.get('bg_light', "#2D2D2D")
        )
        auto_close_launcher_switch.pack(anchor='w', pady=(0, 15))
        
        # Close client on switch
        self.close_client_var = ctk.BooleanVar(value=self.config["game"]["close_client_on_switch"])
        close_client_switch = ctk.CTkSwitch(
            frame,
            text="Fermer le jeu lors du changement de compte",
            font=("Arial", 12),
            variable=self.close_client_var,
            progress_color=self.colors.get('accent', "#FF4655"),
            button_color=self.colors.get('bg_very_light', "#3D3D3D"),
            button_hover_color=self.colors.get('bg_light', "#2D2D2D")
        )
        close_client_switch.pack(anchor='w', pady=(0, 20))
        
        # Valorant path
        valorant_label = ctk.CTkLabel(
            frame,
            text="Chemin Valorant (optionnel):",
            font=("Arial", 12, "bold"),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        valorant_label.pack(anchor='w', pady=(0, 5))
        
        # Frame for path input and browse button
        valorant_path_frame = ctk.CTkFrame(frame, fg_color="transparent")
        valorant_path_frame.pack(fill='x', pady=(0, 20))
        
        self.valorant_path_var = ctk.StringVar(value=self.config["game"]["valorant_path"])
        valorant_path_entry = ctk.CTkEntry(
            valorant_path_frame,
            textvariable=self.valorant_path_var,
            height=35,
            placeholder_text="Laisser vide pour la détection automatique",
            corner_radius=8,
            border_width=2,
            border_color=self.colors.get('border', "#333333")
        )
        valorant_path_entry.pack(side='left', fill='x', expand=True)
        
        browse_valorant_btn = ctk.CTkButton(
            valorant_path_frame,
            text="Parcourir",
            width=80,
            height=35,
            corner_radius=8,
            fg_color=self.colors.get('bg_light', "#2D2D2D"),
            hover_color=self.colors.get('button', "#3391D4"),
            command=lambda: self.browse_path(self.valorant_path_var)
        )
        browse_valorant_btn.pack(side='right', padx=(5, 0))
        
        # League path
        league_label = ctk.CTkLabel(
            frame,
            text="Chemin League of Legends (optionnel):",
            font=("Arial", 12, "bold"),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        league_label.pack(anchor='w', pady=(0, 5))
        
        # Frame for path input and browse button
        league_path_frame = ctk.CTkFrame(frame, fg_color="transparent")
        league_path_frame.pack(fill='x')
        
        self.league_path_var = ctk.StringVar(value=self.config["game"]["league_path"])
        league_path_entry = ctk.CTkEntry(
            league_path_frame,
            textvariable=self.league_path_var,
            height=35,
            placeholder_text="Laisser vide pour la détection automatique",
            corner_radius=8,
            border_width=2,
            border_color=self.colors.get('border', "#333333")
        )
        league_path_entry.pack(side='left', fill='x', expand=True)
        
        browse_league_btn = ctk.CTkButton(
            league_path_frame,
            text="Parcourir",
            width=80,
            height=35,
            corner_radius=8,
            fg_color=self.colors.get('bg_light', "#2D2D2D"),
            hover_color=self.colors.get('button', "#3391D4"),
            command=lambda: self.browse_path(self.league_path_var)
        )
        browse_league_btn.pack(side='right', padx=(5, 0))
    
    def browse_path(self, path_var):
        """Open file browser and set selected path."""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            filetypes=[
                ("Executable files", "*.exe"),
                ("All files", "*.*")
            ],
            title="Select executable"
        )
        
        if path:
            path_var.set(path)
    
    def save_settings(self):
        """Save all settings to the configuration."""
        # Update configuration from UI values
        self.config["general"]["theme"] = self.theme_var.get()
        self.config["general"]["log_level"] = self.log_level_var.get()
        
        self.config["app"]["start_minimized"] = self.start_minimized_var.get()
        self.config["app"]["auto_run_on_startup"] = self.auto_run_var.get()
        self.config["app"]["check_updates"] = self.check_updates_var.get()
        
        self.config["game"]["auto_close_launcher"] = self.auto_close_launcher_var.get()
        self.config["game"]["close_client_on_switch"] = self.close_client_var.get()
        self.config["game"]["valorant_path"] = self.valorant_path_var.get()
        self.config["game"]["league_path"] = self.league_path_var.get()
        
        # Save to file
        if self.save_config():
            if self.on_save_callback:
                self.on_save_callback(self.config)
            self.dialog.destroy()
            messagebox.showinfo("Succès", "Configuration sauvegardée avec succès")
        else:
            messagebox.showerror("Erreur", "Impossible de sauvegarder la configuration") 