"""
Main application entry point for SwitchMaster
Initializes all components and starts the application
"""
import os
import sys
import customtkinter as ctk
from PIL import Image

# Import components
from .windows.main_window import MainWindow
from ..core.account_manager import AccountManager
from ..core.client_finder import ClientFinder
from ..core.game_launcher import GameLauncher
from ..core.encryption import PasswordEncryptor
from ..utils.logging import Logger
from ..utils.window_utils import resource_path, set_icon, setup_window_appearance


class Application:
    """
    Main application class for SwitchMaster.
    Initializes all components and starts the application.
    """
    def __init__(self):
        """Initialize the application."""
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize components
        self.logger = Logger(
            app_name="SwitchMaster", 
            log_file="switchmaster.log",
            enable_console=False  # Désactiver l'affichage des logs dans le terminal
        )
        self.account_manager = AccountManager(self.logger)
        self.client_finder = ClientFinder(self.logger)
        self.game_launcher = GameLauncher(self.logger)
        
        # Load resources
        self.colors = self.load_colors()
        self.images = self.load_images()
        
        # Create main window
        self.main_window = MainWindow(
            account_manager=self.account_manager,
            client_finder=self.client_finder,
            game_launcher=self.game_launcher,
            logger=self.logger,
            colors=self.colors,
            images=self.images
        )
        
    def load_colors(self):
        """Load color scheme."""
        return {
            'bg_dark': '#1E1E1E',
            'bg_darker': '#141414',
            'bg_very_dark': '#0A0A0A',
            'text': '#FFFFFF',
            'text_secondary': '#A0A0A0',
            'accent': '#FF4655',
            'button': '#3391D4',
            'button_hover': '#4BA3E3',
            'button_secondary': '#2A2A2A',
            'button_secondary_hover': '#3A3A3A',
            'close_hover': '#E81123',
            'border': '#333333'
        }
        
    def load_images(self):
        """Load application images."""
        images = {}
        image_dir = os.path.join("assets", "images")
        
        # Image specifications
        image_specs = {
            'logo': ('logo.png', (32, 32)),
            'valorant': ('valorant.png', (24, 24)),
            'league': ('league.png', (24, 24)),
            'settings': ('settings.png', (16, 16)),
            'refresh': ('refresh.png', (16, 16)),
            'add': ('add.png', (16, 16)),
            'logs': ('logs.png', (16, 16))
        }
        
        # Load each image
        for name, (filename, size) in image_specs.items():
            try:
                path = os.path.join(image_dir, filename)
                if os.path.exists(path):
                    image = Image.open(path)
                    if size:
                        image = image.resize(size, Image.Resampling.LANCZOS)
                    images[name] = ctk.CTkImage(
                        light_image=image,
                        dark_image=image,
                        size=size
                    )
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement de {filename}: {str(e)}")
        
        return images
    
    def set_application_icon(self, window):
        """Set the application icon."""
        try:
            icon_path = resource_path(os.path.join('assets', 'images', 'logo.png'))
            if os.path.exists(icon_path):
                set_icon(window, icon_path)
            else:
                self.logger.warning(f"❌ Icon not found: {icon_path}")
        except Exception as e:
            self.logger.error(f"❌ Error setting application icon: {str(e)}")
    
    def run(self):
        """Run the application."""
        try:
            # Set icon and appearance
            self.set_application_icon(self.main_window.window)
            
            # Log startup
            self.logger.info("✅ SwitchMaster démarré avec succès")
            
            # Run main loop
            self.main_window.run()
            
        except Exception as e:
            self.logger.critical(f"❌ Erreur fatale lors du démarrage: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            sys.exit(1)


def main():
    """Entry point for the application."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main() 