"""
Client finder module for SwitchMaster
Handles finding and managing game client paths.
"""
import os
import json
import psutil


class ClientFinder:
    """
    Finds and manages paths to Riot game clients.
    Handles saving and loading client paths.
    """
    def __init__(self, logger=None):
        """
        Initialize the Client Finder.
        
        Args:
            logger: Optional logger instance for logging events
        """
        self.logger = logger
        self.saved_paths = self.load_saved_paths()
        
        # Chemins standards pour les clients
        self.default_paths = {
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
    
    def load_saved_paths(self):
        """
        Loads saved client paths from configuration file.
        
        Returns:
            dict: Dictionary of saved paths
        """
        config_path = os.path.join(os.getcwd(), "client_paths.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    paths = json.load(f)
                
                if self.logger:
                    self.logger.info("Chemins des clients chargés avec succès")
                return paths
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors du chargement des chemins: {str(e)}")
                return {'riot': None, 'valorant': None, 'league': None}
        else:
            # Créer le fichier s'il n'existe pas
            default_paths = {'riot': None, 'valorant': None, 'league': None}
            with open(config_path, 'w') as f:
                json.dump(default_paths, f, indent=4)
            return default_paths
    
    def save_paths(self):
        """
        Saves client paths to configuration file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        config_path = os.path.join(os.getcwd(), "client_paths.json")
        try:
            with open(config_path, 'w') as f:
                json.dump(self.saved_paths, f, indent=4)
            
            if self.logger:
                self.logger.info("Chemins des clients sauvegardés avec succès")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la sauvegarde des chemins: {str(e)}")
            return False
    
    def search_client(self, client_type):
        """
        Searches for a specific client executable.
        
        Args:
            client_type (str): Type of client to search for ('riot', 'valorant', 'league')
            
        Returns:
            tuple: (success, path) - success is a boolean, path is the path if found or None
        """
        # Si déjà trouvé précédemment, vérifier qu'il existe toujours
        if self.saved_paths.get(client_type):
            if os.path.exists(self.saved_paths[client_type]):
                if self.logger:
                    self.logger.info(f"Client {client_type} déjà trouvé: {self.saved_paths[client_type]}")
                return True, self.saved_paths[client_type]
            else:
                # Le chemin sauvegardé n'existe plus
                self.saved_paths[client_type] = None
                self.save_paths()
        
        # Rechercher dans les chemins par défaut
        client_found = False
        client_path = None
        
        for path in self.default_paths[client_type]['paths']:
            if os.path.exists(path):
                self.saved_paths[client_type] = path
                self.save_paths()
                client_found = True
                client_path = path
                
                if self.logger:
                    self.logger.info(f"Client {client_type} trouvé: {path}")
                break
        
        return client_found, client_path
    
    def search_all_clients(self):
        """
        Searches for all client executables.
        
        Returns:
            dict: Dictionary of results with client types as keys and tuples (success, path) as values
        """
        results = {}
        for client_type in ['riot', 'valorant', 'league']:
            success, path = self.search_client(client_type)
            results[client_type] = (success, path)
        
        return results
    
    def find_all_clients(self):
        """
        Search for all clients and log results.
        This is the main method called from the UI.
        """
        if self.logger:
            self.logger.info("Recherche des clients en cours...")
            
        results = self.search_all_clients()
        
        # Log results
        for client_type, (success, path) in results.items():
            client_name = self.get_friendly_name(client_type)
            if success:
                if self.logger:
                    self.logger.info(f"✅ Client {client_name} trouvé : {path}")
            else:
                if self.logger:
                    self.logger.warning(f"❌ Client {client_name} non trouvé")
                    
        return results
    
    def set_client_path(self, client_type, path):
        """
        Sets a custom path for a client.
        
        Args:
            client_type (str): Type of client ('riot', 'valorant', 'league')
            path (str): Path to the client executable
            
        Returns:
            bool: True if the path is valid, False otherwise
        """
        if not path or not os.path.exists(path) or not path.endswith('.exe'):
            if self.logger:
                self.logger.error(f"Chemin invalide pour {client_type}: {path}")
            return False
        
        self.saved_paths[client_type] = path
        self.save_paths()
        
        if self.logger:
            self.logger.info(f"Chemin pour {client_type} défini manuellement: {path}")
        
        return True
    
    def get_client_path(self, client_type):
        """
        Gets the path for a specific client.
        
        Args:
            client_type (str): Type of client ('riot', 'valorant', 'league')
            
        Returns:
            str or None: Path to the client executable or None if not found
        """
        return self.saved_paths.get(client_type)
    
    def verify_client_running(self, process_name):
        """
        Verifies if a client is currently running.
        
        Args:
            process_name (str): Process name to check
            
        Returns:
            bool: True if the process is running, False otherwise
        """
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if process_name in proc.info['name']:
                        if self.logger:
                            self.logger.info(f"Processus {process_name} trouvé: PID {proc.pid}")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if self.logger:
                self.logger.warning(f"Processus {process_name} non trouvé")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la vérification du processus {process_name}: {str(e)}")
            return False
    
    def get_friendly_name(self, client_type):
        """
        Gets a user-friendly name for a client type.
        
        Args:
            client_type (str): Client type ('riot', 'valorant', 'league')
            
        Returns:
            str: User-friendly name for the client
        """
        return self.default_paths.get(client_type, {}).get('name', client_type.capitalize()) 