"""
Main application window for SwitchMaster
Implements the main application window and UI components
"""
import customtkinter as ctk
import os
from PIL import Image
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Callable

# Import UI components
from ..components.game_frame import GameFrame
from ..components.log_window import LogWindow
from ..components.config_dialog import ConfigDialog
from ...utils.window_utils import (
    center_window,
    set_window_icon,
    resource_path,
    create_rounded_rectangle,
    set_dark_title_bar
)


class ThreadManager:
    """Gestionnaire de threads pour l'application."""
    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, Any] = {}
        self.queue = queue.Queue()
        self.running = True
        
        # Démarrer le thread de surveillance
        self.monitor_thread = threading.Thread(target=self._monitor_tasks, daemon=True)
        self.monitor_thread.start()
    
    def submit_task(self, name: str, func: Callable, *args, **kwargs) -> None:
        """Soumet une tâche à exécuter."""
        future = self.executor.submit(func, *args, **kwargs)
        self.tasks[name] = {
            'future': future,
            'start_time': threading.Event(),
            'completed': threading.Event()
        }
        self.tasks[name]['start_time'].set()
    
    def _monitor_tasks(self):
        """Surveille l'état des tâches."""
        while self.running:
            try:
                # Vérifier les tâches terminées
                completed_tasks = []
                for name, task in self.tasks.items():
                    if task['future'].done():
                        completed_tasks.append(name)
                        task['completed'].set()
                
                # Nettoyer les tâches terminées
                for name in completed_tasks:
                    del self.tasks[name]
                
                # Attendre un peu avant la prochaine vérification
                threading.Event().wait(0.1)
            except Exception as e:
                print(f"Erreur dans le moniteur de tâches: {e}")
    
    def shutdown(self):
        """Arrête le gestionnaire de threads."""
        self.running = False
        self.executor.shutdown(wait=True)

class MainWindow:
    """
    Main application window for SwitchMaster.
    """
    def __init__(self, 
                 parent=None,
                 account_manager=None,
                 client_finder=None, 
                 game_launcher=None,
                 logger=None,
                 colors=None,
                 images=None):
        """
        Initialize the main window.
        
        Args:
            parent: Parent widget
            account_manager: Account manager instance
            client_finder: Client finder instance
            game_launcher: Game launcher instance
            logger: Logger instance
            colors: Color scheme dictionary
            images: Dictionary of loaded images
        """
        self.parent = parent
        self.account_manager = account_manager
        self.client_finder = client_finder
        self.game_launcher = game_launcher
        self.logger = logger
        self.colors = colors or {}
        self.images = images or {}
        
        # Gestionnaire de threads
        self.thread_manager = ThreadManager()
        
        # File d'attente pour les mises à jour d'interface
        self.ui_queue = queue.Queue()
        
        # Cache pour les fenêtres
        self._window_cache = {}
        
        # Initialize window
        self.window = ctk.CTk()
        self.window.title("SwitchMaster")
        self.window.geometry("1200x600")
        self.window.minsize(800, 500)
        
        # Configure window appearance
        self.window.configure(fg_color=self.colors['bg_dark'])
        set_window_icon(self.window)
        
        # Position window in center of screen
        center_window(self.window, 1200, 600)
        
        # Main content frame
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(fill='both', expand=True)
        
        self.setup_ui()
        
        # Register callback for log events
        if self.logger:
            self.logger.register_callback(self.log_message)
            if hasattr(self.logger, 'set_main_window'):
                self.logger.set_main_window(self)
        
        # Log window - initialiser à None
        self.log_window = None
        
        # Démarrer le thread de mise à jour de l'interface
        self._start_ui_update_thread()
    
    def _start_ui_update_thread(self):
        """Démarre le thread de mise à jour de l'interface."""
        def update_ui():
            while True:
                try:
                    # Récupérer la prochaine mise à jour
                    update_func = self.ui_queue.get()
                    # Exécuter la mise à jour dans le thread principal
                    self.window.after(0, update_func)
                except queue.Empty:
                    continue
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Erreur dans la mise à jour de l'interface: {e}")
        
        # Démarrer le thread
        ui_thread = threading.Thread(target=update_ui, daemon=True)
        ui_thread.start()
    
    def update_ui_safe(self, func: Callable):
        """Met à jour l'interface de manière thread-safe."""
        self.ui_queue.put(func)
    
    def _get_cached_window(self, key, window_class):
        """Récupère une fenêtre du cache ou en crée une nouvelle."""
        if key not in self._window_cache:
            # Créer une nouvelle instance de la fenêtre
            self._window_cache[key] = window_class(
                self.window,
                title="Logs de l'application",
                colors=self.colors,
                logger=self.logger
            )
        return self._window_cache[key]
    
    def _cleanup_window_cache(self):
        """Nettoie le cache des fenêtres."""
        for window in self._window_cache.values():
            if hasattr(window, 'destroy'):
                window.destroy()
        self._window_cache.clear()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Create main content
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
    
    def create_main_content(self):
        """Create the main content area."""
        # Main content frame
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Top buttons frame with center alignment
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        # Center container for buttons
        center_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        center_container.pack(expand=True)
        
        # Find clients button
        find_clients_btn = ctk.CTkButton(
            center_container,
            text="Find Clients",
            image=self.images.get('refresh'),
            compound="left",
            command=self.find_clients,
            fg_color=self.colors.get('button', '#3391D4'),
            hover_color=self.colors.get('button_hover', '#4BA3E3')
        )
        find_clients_btn.pack(side='left', padx=5)
        
        # View logs button
        view_logs_btn = ctk.CTkButton(
            center_container,
            text="View Logs",
            image=self.images.get('logs'),
            compound="left",
            command=self.show_logs,
            fg_color=self.colors.get('button', '#3391D4'),
            hover_color=self.colors.get('button_hover', '#4BA3E3')
        )
        view_logs_btn.pack(side='left', padx=5)
        
        # Games frame
        games_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        games_frame.pack(fill='both', expand=True)
        
        # Valorant frame
        valorant_frame = GameFrame(
            parent=games_frame,
            game_name="Valorant",
            account_manager=self.account_manager,
            client_finder=self.client_finder,
            game_launcher=self.game_launcher,
            logger=self.logger,
            colors=self.colors,
            images=self.images
        )
        valorant_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # League of Legends frame
        league_frame = GameFrame(
            parent=games_frame,
            game_name="League of Legends",
            account_manager=self.account_manager,
            client_finder=self.client_finder,
            game_launcher=self.game_launcher,
            logger=self.logger,
            colors=self.colors,
            images=self.images
        )
        league_frame.pack(side='left', fill='both', expand=True, padx=5)
    
    def create_status_bar(self):
        """Create the status bar."""
        status_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors.get('bg_very_dark', '#131313'))
        status_frame.pack(fill='x', side='bottom')
        
        # Ajout d'une icône d'état
        self.status_icon_label = ctk.CTkLabel(
            status_frame,
            text="●",  # Point comme indicateur d'état
            text_color="#4CAF50",  # Vert pour "Ready"
            font=("Arial", 14)
        )
        self.status_icon_label.pack(side='left', padx=(10, 0), pady=5)
        
        # Texte de statut principal
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            text_color=self.colors.get('text_secondary', '#A0A0A0')
        )
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Ajout d'un compteur d'activités pour les processus en cours
        self.activity_counter_frame = ctk.CTkFrame(
            status_frame,
            fg_color="transparent"
        )
        self.activity_counter_frame.pack(side='right', padx=10, pady=5)
        
        # Label pour les activités en cours
        self.activity_label = ctk.CTkLabel(
            self.activity_counter_frame,
            text="",
            text_color=self.colors.get('accent', '#FF4655')
        )
        self.activity_label.pack(side='right')
        
        # Label pour le compte total d'activités
        self.total_activity_label = ctk.CTkLabel(
            self.activity_counter_frame,
            text="",
            text_color=self.colors.get('text_secondary', '#A0A0A0')
        )
        self.total_activity_label.pack(side='right', padx=(0, 10))
        
        # Initialiser les compteurs d'activités
        self.activity_count = 0  # Activités en cours
        self.total_activity_count = 0  # Nombre total d'activités exécutées
        self.last_activity = "Ready"  # Dernière activité exécutée
    
    def update_status(self, message, level="INFO"):
        """
        Met à jour la barre d'état avec un nouveau message.
        
        Args:
            message (str): Message à afficher
            level (str): Niveau du message (INFO, WARNING, ERROR, SUCCESS)
        """
        if not hasattr(self, 'status_label'):
            return
            
        # Définir la couleur en fonction du niveau
        if level.upper() == "ERROR" or level.upper() == "CRITICAL":
            icon_color = "#FF5252"  # Rouge pour erreur
            message = f"Erreur: {message}"
        elif level.upper() == "WARNING":
            icon_color = "#FFC107"  # Jaune pour avertissement
            message = f"Attention: {message}"
        elif level.upper() == "SUCCESS":
            icon_color = "#4CAF50"  # Vert pour succès
        else:
            icon_color = "#2196F3"  # Bleu pour info
        
        # Stocker le message comme dernière activité si ce n'est pas un message d'erreur
        if level.upper() not in ["ERROR", "CRITICAL", "WARNING"]:
            self.last_activity = message
            
        # Mettre à jour l'icône et le texte
        self.status_icon_label.configure(text_color=icon_color)
        self.status_label.configure(text=message)
    
    def reset_status(self):
        """Réinitialise le statut pour montrer la dernière activité exécutée."""
        if self.activity_count == 0:
            self.status_icon_label.configure(text_color="#4CAF50")
            # Afficher la dernière activité au lieu de "Ready"
            self.status_label.configure(text=self.last_activity)
    
    def start_activity(self, description=""):
        """
        Indique qu'une nouvelle activité a commencé.
        
        Args:
            description (str): Description de l'activité
        """
        # Vérifier si on n'a pas dépassé une limite raisonnable
        if self.activity_count >= 10:  # Limite de sécurité
            self.logger.warning("Trop d'activités en cours, réinitialisation du compteur")
            self.activity_count = 0
            self.end_activity("Réinitialisation du compteur d'activités", "WARNING")
            return
            
        self.activity_count += 1
        
        # Mettre à jour le compteur d'activités en cours
        if self.activity_count > 0:
            self.activity_label.configure(text=f"Activités en cours: {self.activity_count}")
            
        # Mettre à jour le statut si une description est fournie
        if description:
            self.update_status(description, "INFO")
            
        # Planifier une vérification de sécurité après 30 secondes
        self.window.after(30000, self._check_activity_timeout)
    
    def _check_activity_timeout(self):
        """Vérifie si une activité est bloquée depuis trop longtemps."""
        if self.activity_count > 0:
            self.logger.warning("Activité bloquée détectée, réinitialisation du compteur")
            self.activity_count = 0
            self.end_activity("Réinitialisation du compteur d'activités", "WARNING")
    
    def end_activity(self, result_message="", level="INFO"):
        """
        Indique qu'une activité est terminée.
        
        Args:
            result_message (str): Message de résultat à afficher
            level (str): Niveau du message
        """
        self.activity_count = max(0, self.activity_count - 1)
        
        # Incrémenter le compteur total d'activités terminées
        self.total_activity_count += 1
        
        # Mettre à jour le compteur d'activités en cours
        if self.activity_count > 0:
            self.activity_label.configure(text=f"Activités en cours: {self.activity_count}")
        else:
            self.activity_label.configure(text="")
        
        # Mettre à jour le compteur total d'activités
        self.total_activity_label.configure(text=f"Total exécuté: {self.total_activity_count}")
            
        # Afficher le message de résultat si fourni
        if result_message:
            self.update_status(result_message, level)
            # Stocker ce message comme dernière activité exécutée si c'est un succès
            if level.upper() == "SUCCESS":
                self.last_activity = result_message
        else:
            self.reset_status()
    
    def toggle_maximize(self):
        """Toggle window maximization."""
        if self.window.state() == 'zoomed':
            self.window.state('normal')
        else:
            self.window.state('zoomed')
    
    def find_clients(self):
        """Open a dialog to find game clients."""
        # Commencer une activité de recherche de clients
        self.start_activity("Recherche des clients de jeu...")
        
        # Create dialog window
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Recherche des clients")
        center_window(dialog, 500, 500)
        dialog.configure(fg_color=self.colors.get('bg_dark', "#1E1E1E"))
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Ensure focus and visibility
        dialog.attributes('-topmost', True)
        dialog.focus_force()
        
        # Maintain icon - reapply every 100ms
        def maintain_icon():
            if dialog.winfo_exists():
                set_window_icon(dialog)
                dialog.after(100, maintain_icon)
                
        maintain_icon()
        dialog.after(250, lambda: dialog.attributes('-topmost', False))
        
        # Apply dark title bar
        set_dark_title_bar(dialog)
        
        # Content frame
        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text="Rechercher les clients",
            font=("Arial", 20, "bold"),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        title_label.pack(pady=(0, 10))
        
        # Dictionary for client info and buttons
        client_info = {
            'riot': {'name': "Client Riot", 'button': None, 'path_label': None},
            'valorant': {'name': "VALORANT", 'button': None, 'path_label': None},
            'league': {'name': "League of Legends", 'button': None, 'path_label': None}
        }
        
        # Search all button
        search_all_btn = ctk.CTkButton(
            content_frame,
            text="Rechercher automatiquement tous les clients",
            font=("Arial", 13, "bold"),
            fg_color=self.colors.get('accent', "#FF4655"),
            hover_color=self.colors.get('accent_hover', "#FF5F6D"),
            height=45,
            corner_radius=10,
            command=lambda: self._search_all_clients(client_info)
        )
        search_all_btn.pack(fill='x', pady=(0, 20))
        
        # Separator
        separator = ctk.CTkFrame(
            content_frame,
            height=2,
            fg_color=self.colors.get('border', "#333333")
        )
        separator.pack(fill='x', pady=(0, 20))
        
        # Buttons for each client
        for client_type in client_info:
            def create_search_command(ctype):
                def command():
                    # If client already found, disable button
                    if self.client_finder.get_client_path(ctype):
                        return
                    
                    # Start individual search activity
                    self.start_activity(f"Recherche du client {client_info[ctype]['name']}...")
                    
                    success, path = self.client_finder.search_client(ctype)
                    if success:
                        client_info[ctype]['button'].configure(
                            fg_color='#4CAF50',
                            hover_color='#4CAF50',
                            text=f"✅ {client_info[ctype]['name']} trouvé",
                            state="disabled"
                        )
                        # End activity with success
                        self.end_activity(f"Client {client_info[ctype]['name']} trouvé", "SUCCESS")
                    else:
                        client_info[ctype]['button'].configure(
                            fg_color='#FF9800',
                            hover_color='#FFA726',
                            text=f"⚠️ {client_info[ctype]['name']} non trouvé"
                        )
                        # End activity with warning
                        self.end_activity(f"Client {client_info[ctype]['name']} non trouvé", "WARNING")
                        # Show manual input options
                        self._show_manual_input_options(ctype, client_info[ctype]['name'], client_info)
                return command
            
            button = ctk.CTkButton(
                content_frame,
                text=f"Rechercher {client_info[client_type]['name']}",
                font=("Arial", 13, "bold"),
                fg_color=self.colors.get('accent', "#FF4655"),
                hover_color=self.colors.get('accent_hover', "#FF5F6D"),
                height=45,
                corner_radius=10,
                command=create_search_command(client_type)
            )
            
            # Configure button if client already found
            if self.client_finder.get_client_path(client_type):
                button.configure(
                    fg_color='#4CAF50',
                    hover_color='#4CAF50',
                    text=f"✅ {client_info[client_type]['name']} trouvé",
                    state="disabled"
                )
            
            button.pack(fill='x', pady=10)
            client_info[client_type]['button'] = button
        
        # Create a custom close command to properly end the activity
        def close_dialog():
            # Ensure the activity is ended
            self.end_activity("Fenêtre de recherche des clients fermée", "INFO")
            dialog.destroy()
        
        # Close button
        close_btn = ctk.CTkButton(
            content_frame,
            text="Fermer",
            font=("Arial", 13, "bold"),
            fg_color=self.colors.get('accent', "#FF4655"),
            hover_color=self.colors.get('accent_hover', "#FF5F6D"),
            height=45,
            corner_radius=10,
            command=close_dialog
        )
        close_btn.pack(fill='x', pady=(20, 10))
        
        # Also track dialog closure with the window manager (X button)
        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
    
    def _search_all_clients(self, client_info):
        """Search for all clients."""
        # Commencer une activité de recherche
        activity_desc = "Recherche de tous les clients de jeu..."
        self.start_activity(activity_desc)
        
        def search_task():
            try:
                # Perform search
                client_results = self.client_finder.find_all_clients()
                
                # Display results
                for client_type, (success, path) in client_results.items():
                    if client_type in client_info and client_info[client_type]['button']:
                        if success:
                            # Client found - update button
                            self.update_ui_safe(lambda ct=client_type: client_info[ct]['button'].configure(
                                fg_color='#4CAF50',
                                hover_color='#4CAF50',
                                text=f"✅ {client_info[ct]['name']} trouvé",
                                state="disabled"
                            ))
                        else:
                            # Client not found
                            self.update_ui_safe(lambda ct=client_type: client_info[ct]['button'].configure(
                                fg_color='#FF9800',
                                hover_color='#FFA726',
                                text=f"⚠️ {client_info[ct]['name']} non trouvé"
                            ))
                
                # Terminer l'activité
                self.update_ui_safe(lambda: self.end_activity("Recherche des clients terminée", "SUCCESS"))
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de la recherche des clients: {e}")
                self.update_ui_safe(lambda: self.end_activity("Erreur lors de la recherche des clients", "ERROR"))
        
        # Soumettre la tâche au gestionnaire de threads
        self.thread_manager.submit_task("search_all_clients", search_task)
    
    def _show_manual_input_options(self, client_type, client_name, client_info):
        """Show dialog for manual client path selection."""
        from tkinter import messagebox, filedialog
        
        # Start an activity for manual client selection
        self.start_activity(f"Sélection manuelle du client {client_name}...")
        
        def manual_input_task():
            try:
                def show_confirmation():
                    return messagebox.askyesno(
                        "Client non trouvé",
                        f"{client_name} non trouvé.\nVoulez-vous sélectionner le chemin manuellement ?",
                        parent=self.window
                    )
                
                # Demander confirmation dans le thread principal
                result = self.window.after(0, show_confirmation)
                if not result:
                    self.update_ui_safe(lambda: self.end_activity(f"Sélection manuelle du client {client_name} annulée", "INFO"))
                    return
                
                def show_file_dialog():
                    return filedialog.askopenfilename(
                        title=f"Sélectionner {client_name}",
                        filetypes=[("Executable", "*.exe")],
                        initialdir="C:/Riot Games"
                    )
                
                # Ouvrir le sélecteur de fichier dans le thread principal
                file_path = self.window.after(0, show_file_dialog)
                
                if file_path and file_path.endswith('.exe'):
                    success = self.client_finder.set_client_path(client_type, file_path)
                    if success:
                        self.update_ui_safe(lambda: client_info[client_type]['button'].configure(
                            fg_color='#4CAF50',
                            hover_color='#4CAF50',
                            text=f"✅ {client_name} trouvé",
                            state="disabled"
                        ))
                        self.update_ui_safe(lambda: self.end_activity(f"Client {client_name} configuré manuellement", "SUCCESS"))
                        return
                    else:
                        self.update_ui_safe(lambda: self.end_activity(f"Échec de la configuration du client {client_name}", "ERROR"))
                        self.update_ui_safe(lambda: messagebox.showerror(
                            "Erreur",
                            f"Impossible de configurer le chemin pour {client_name}",
                            parent=self.window
                        ))
                        return
                
                # Si on arrive ici, la sélection a été annulée ou est invalide
                self.update_ui_safe(lambda: self.end_activity(f"Sélection du client {client_name} annulée", "WARNING"))
                self.update_ui_safe(lambda: messagebox.showerror(
                    "Erreur",
                    f"Aucun chemin valide fourni pour {client_name}",
                    parent=self.window
                ))
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de la sélection manuelle du client: {e}")
                self.update_ui_safe(lambda: self.end_activity(f"Erreur lors de la sélection du client {client_name}", "ERROR"))
        
        # Soumettre la tâche au gestionnaire de threads
        self.thread_manager.submit_task(f"manual_input_{client_type}", manual_input_task)
    
    def show_logs(self):
        """Show the log window."""
        # Start an activity for viewing logs
        self.start_activity("Consultation des logs...")
        
        def create_log_window():
            try:
                # Créer la fenêtre de logs dans le thread principal
                def create_window():
                    if self.log_window is None or not self.log_window.winfo_exists():
                        self.log_window = LogWindow(
                            self.window,
                            title="Logs de SwitchMaster",
                            colors=self.colors,
                            logger=self.logger
                        )
                        
                        # Function to close the window and end the activity
                        def close_log_window():
                            self.end_activity("Fenêtre des logs fermée", "INFO")
                            self.log_window.destroy()
                            self.log_window = None
                        
                        # Handle window close via X button and close button
                        self.log_window.protocol("WM_DELETE_WINDOW", close_log_window)
                        self.log_window.bind_close_button(close_log_window)
                    
                    # S'assurer que la fenêtre est visible
                    self.log_window.lift()
                    self.log_window.focus_force()
                    
                    # Ensure focus and visibility
                    self.log_window.attributes('-topmost', True)
                    self.log_window.after(250, lambda: self.log_window.attributes('-topmost', False))
                    
                    # Apply dark title bar and icon
                    set_dark_title_bar(self.log_window)
                    set_window_icon(self.log_window)
                    
                    # Maintain icon - reapply every 100ms
                    def maintain_icon():
                        if self.log_window and self.log_window.winfo_exists():
                            set_window_icon(self.log_window)
                            self.log_window.after(100, maintain_icon)
                    maintain_icon()
                
                # Créer la fenêtre dans le thread principal
                self.update_ui_safe(create_window)
                
                # Charger les logs de manière asynchrone
                def load_logs():
                    try:
                        if self.log_window and self.log_window.winfo_exists():
                            self.update_ui_safe(lambda: self.log_window.update_logs())
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Erreur lors du chargement des logs: {e}")
                
                # Soumettre la tâche de chargement des logs
                self.thread_manager.submit_task("load_logs", load_logs)
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de la création de la fenêtre de logs: {e}")
                self.end_activity("Erreur lors de l'affichage des logs", "ERROR")
        
        # Soumettre la tâche au gestionnaire de threads
        self.thread_manager.submit_task("create_log_window", create_log_window)
    
    def log_message(self, timestamp, level, message):
        """Handle log messages from the logger."""
        def update_log():
            try:
                # Mettre à jour la barre d'état pour tous les niveaux de logs
                level_str = level.upper() if level else "INFO"
                
                # Filtrer certains messages trop fréquents pour la barre d'état
                if "DEBUG" not in level_str and not message.startswith("✅ SwitchMaster démarré"):
                    # Convertir certains niveaux spéciaux
                    status_level = level_str
                    if "ERROR" in level_str or "CRITICAL" in level_str:
                        status_level = "ERROR"
                    elif "WARNING" in level_str:
                        status_level = "WARNING"
                    elif "INFO" in level_str:
                        if any(success_keyword in message for success_keyword in 
                              ["trouvé", "réussi", "succès", "sauvegardé", "chargé"]):
                            status_level = "SUCCESS"
                        else:
                            status_level = "INFO"
                    
                    # Afficher le message dans la barre d'état
                    self.update_status(message, status_level)
                    
                    # Mettre à jour la fenêtre de logs si elle existe
                    if hasattr(self, 'log_window') and self.log_window and self.log_window.winfo_exists():
                        self.log_window.update_logs()
            
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de la mise à jour des logs: {e}")
        
        # Mettre à jour l'interface de manière thread-safe
        self.update_ui_safe(update_log)
    
    def show_config(self):
        """Show the configuration dialog."""
        def create_config_dialog():
            try:
                config_path = os.path.join(os.path.expanduser("~"), ".switchmaster", "config.json")
                
                def show_dialog():
                    ConfigDialog(
                        self.window,
                        title="Configuration",
                        colors=self.colors,
                        config_path=config_path,
                        on_save_callback=self.apply_config,
                        logger=self.logger
                    )
                
                self.update_ui_safe(show_dialog)
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de l'affichage de la configuration: {e}")
        
        # Soumettre la tâche au gestionnaire de threads
        self.thread_manager.submit_task("show_config", create_config_dialog)
    
    def apply_config(self, config):
        """Apply configuration changes."""
        def apply_config_task():
            try:
                # Apply theme in UI thread
                self.update_ui_safe(lambda: ctk.set_appearance_mode(config["general"]["theme"]))
                
                # Apply log level
                if self.logger and hasattr(self.logger, 'set_level'):
                    self.logger.set_level(config["general"]["log_level"])
                
                # Apply client paths
                if self.client_finder:
                    if config["game"]["valorant_path"]:
                        self.client_finder.valorant_paths = [config["game"]["valorant_path"]]
                    
                    if config["game"]["league_path"]:
                        self.client_finder.league_paths = [config["game"]["league_path"]]
                
                self.update_ui_safe(lambda: self.update_status("Configuration appliquée avec succès", "SUCCESS"))
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de l'application de la configuration: {e}")
                self.update_ui_safe(lambda: self.update_status("Erreur lors de l'application de la configuration", "ERROR"))
        
        # Soumettre la tâche au gestionnaire de threads
        self.thread_manager.submit_task("apply_config", apply_config_task)
    
    def run(self):
        """Run the main window."""
        try:
            # Initialiser les compteurs d'activités au démarrage
            self.activity_count = 0
            self.total_activity_count = 0
            self.last_activity = "Ready"
            
            # Mettre à jour les labels
            if hasattr(self, 'activity_label'):
                self.activity_label.configure(text="")
            if hasattr(self, 'total_activity_label'):
                self.total_activity_label.configure(text="")
            if hasattr(self, 'status_label'):
                self.status_label.configure(text="Ready")
            
            # Planifier les tâches périodiques
            self._schedule_cleanup()
            
            # Démarrer la boucle principale
            self.window.mainloop()
            
        finally:
            # Nettoyage à la fermeture
            self.thread_manager.shutdown()
    
    def _schedule_cleanup(self):
        """Planifie le nettoyage périodique des ressources."""
        # Nettoyer le cache des fenêtres toutes les 5 minutes
        self.window.after(300000, self._cleanup_window_cache)
        
        # Vérifier les activités bloquées toutes les minute
        self.window.after(60000, self._check_activity_timeout)
        
        # Réinitialiser les compteurs si nécessaire
        self.window.after(3600000, self._reset_counters)  # Toutes les heures
    
    def _reset_counters(self):
        """Réinitialise les compteurs si nécessaire."""
        if self.activity_count > 0:
            self.logger.warning("Réinitialisation des compteurs d'activités")
            self.activity_count = 0
            self.end_activity("Réinitialisation des compteurs", "WARNING")
        
        # Planifier la prochaine réinitialisation
        self.window.after(3600000, self._reset_counters)
    
    def show(self):
        """Show the window."""
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
    
    def switch_account(self, account_name: str):
        """Switch to the specified account."""
        try:
            # Get account info
            account = self.account_manager.get_account(account_name)
            if not account:
                self.update_status(f"Compte {account_name} non trouvé", "ERROR")
                return
            
            # Start activity
            self.start_activity(f"Changement de compte vers {account_name}")
            
            def switch_account_task():
                try:
                    # Close current game
                    def on_game_closed(success: bool):
                        if not success:
                            self.update_ui_safe(lambda: self.update_status("Erreur lors de la fermeture du jeu", "ERROR"))
                            self.update_ui_safe(lambda: self.end_activity("Échec du changement de compte", "ERROR"))
                            return
                        
                        # Launch game with new account
                        def on_game_launched(success: bool):
                            if success:
                                self.update_ui_safe(lambda: self.update_status(f"Connecté au compte {account_name}", "SUCCESS"))
                                self.update_ui_safe(lambda: self.end_activity(f"Changement de compte vers {account_name} réussi", "SUCCESS"))
                            else:
                                self.update_ui_safe(lambda: self.update_status("Erreur lors du lancement du jeu", "ERROR"))
                                self.update_ui_safe(lambda: self.end_activity("Échec du changement de compte", "ERROR"))
                        
                        # Launch game with callback
                        self.game_launcher.launch_game(
                            "VALORANT",
                            account.username,
                            account.get_password(),
                            callback=on_game_launched
                        )
                    
                    # Close game with callback
                    self.game_launcher.close_game("VALORANT", callback=on_game_closed)
                    
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Erreur dans le thread de changement de compte: {e}")
                    self.update_ui_safe(lambda: self.update_status("Erreur lors du changement de compte", "ERROR"))
                    self.update_ui_safe(lambda: self.end_activity("Échec du changement de compte", "ERROR"))
            
            # Soumettre la tâche au gestionnaire de threads
            self.thread_manager.submit_task(
                f"switch_account_{account_name}",
                switch_account_task
            )
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors du changement de compte: {e}")
            self.update_status("Erreur lors du changement de compte", "ERROR")
            self.end_activity("Échec du changement de compte", "ERROR") 