import time
import subprocess
import pyautogui
import psutil
import win32gui
import win32con
import win32process
import threading
from queue import Queue
from typing import Optional, Tuple, Callable

class GameLauncher:
    def __init__(self, logger=None):
        self.logger = logger
        # Configurer pyautogui pour être plus sûr
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5  # Pause entre chaque action
        self.operation_queue = Queue()
        self.current_operation = None
        
    def _run_in_thread(self, target: Callable, *args, **kwargs):
        """
        Exécute une fonction dans un thread séparé.
        
        Args:
            target: Fonction à exécuter
            *args: Arguments positionnels
            **kwargs: Arguments nommés
        """
        def thread_wrapper():
            try:
                result = target(*args, **kwargs)
                self.operation_queue.put(("success", result))
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur dans le thread: {e}")
                self.operation_queue.put(("error", str(e)))
            
        thread = threading.Thread(target=thread_wrapper)
        thread.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête
        thread.start()
        return thread
            
    def _wait_for_window(self, window_title: str, timeout: int = 30) -> Optional[int]:
        """
        Attend qu'une fenêtre avec le titre spécifié apparaisse.
        
        Args:
            window_title: Titre de la fenêtre à attendre
            timeout: Temps maximum d'attente en secondes
            
        Returns:
            Handle de la fenêtre si trouvée, None sinon
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                hwnd = win32gui.FindWindow(None, window_title)
                if hwnd != 0:
                    return hwnd
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Erreur lors de la recherche de la fenêtre: {e}")
            time.sleep(0.5)
        return None
        
    def _is_process_running(self, process_name: str) -> bool:
        """Vérifie si un processus est en cours d'exécution."""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
        
    def _safe_type(self, text: str, interval: float = 0.1):
        """
        Tape du texte de manière sûre avec des délais.
        
        Args:
            text: Texte à taper
            interval: Intervalle entre chaque caractère
        """
        try:
            pyautogui.write(text, interval=interval)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la saisie du texte: {e}")
            raise
            
    def _safe_hotkey(self, *args):
        """
        Exécute un raccourci clavier de manière sûre.
        
        Args:
            *args: Touches à presser
        """
        try:
            pyautogui.hotkey(*args)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de l'exécution du raccourci: {e}")
            raise
            
    def _focus_window(self, hwnd: int):
        """
        Met le focus sur une fenêtre de manière sûre.
        
        Args:
            hwnd: Handle de la fenêtre
        """
        try:
            if win32gui.IsIconic(hwnd):  # Si la fenêtre est minimisée
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)  # Attendre que le focus soit effectif
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la mise au premier plan: {e}")
            raise
            
    def launch_game(self, game_name: str, username: str, password: str, callback: Callable = None) -> None:
        """
        Lance le jeu et se connecte avec les identifiants fournis (de manière asynchrone).
        
        Args:
            game_name: Nom du jeu à lancer
            username: Nom d'utilisateur
            password: Mot de passe
            callback: Fonction à appeler quand l'opération est terminée
        """
        def launch_operation():
            try:
                # Vérifier si le client est déjà en cours d'exécution
                if self._is_process_running("RiotClientServices.exe"):
                    if self.logger:
                        self.logger.warning("Le client Riot est déjà en cours d'exécution")
                    return False
                    
                # Lancer le client Riot
                subprocess.Popen([
                    "C:/Riot Games/Riot Client/RiotClientServices.exe",
                    "--launch-product=valorant",
                    "--launch-patchline=live"
                ])
                
                # Attendre que la fenêtre du client apparaisse
                client_hwnd = self._wait_for_window("Riot Client")
                if not client_hwnd:
                    if self.logger:
                        self.logger.error("La fenêtre du client Riot n'a pas été trouvée")
                    return False
                    
                # Mettre le focus sur la fenêtre
                self._focus_window(client_hwnd)
                time.sleep(1)  # Attendre que la fenêtre soit prête
                
                # Saisir les identifiants
                self._safe_type(username)
                self._safe_hotkey('tab')
                time.sleep(0.5)
                self._safe_type(password)
                self._safe_hotkey('enter')
                
                if self.logger:
                    self.logger.info(f"Connexion réussie pour {game_name}")
                return True
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors du lancement du jeu: {e}")
                return False
        
        # Lancer l'opération dans un thread séparé
        self.current_operation = self._run_in_thread(launch_operation)
        
        # Si un callback est fourni, vérifier périodiquement la fin de l'opération
        if callback:
            def check_completion():
                if not self.operation_queue.empty():
                    status, result = self.operation_queue.get()
                    callback(result)
                    return
                
                # Vérifier toutes les 100ms
                threading.Timer(0.1, check_completion).start()
            
            check_completion()
            
    def close_game(self, game_name: str, callback: Callable = None) -> None:
        """
        Ferme le jeu spécifié (de manière asynchrone).
        
        Args:
            game_name: Nom du jeu à fermer
            callback: Fonction à appeler quand l'opération est terminée
        """
        def close_operation():
            try:
                # Fermer tous les processus liés au jeu
                processes_to_kill = ["RiotClientServices.exe", "VALORANT.exe", "LeagueClient.exe"]
                
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name'] in processes_to_kill:
                            proc.terminate()
                            proc.wait(timeout=5)  # Attendre la fin du processus
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        if self.logger:
                            self.logger.warning(f"Impossible de terminer le processus {proc.info['name']}")
                        
                if self.logger:
                    self.logger.info(f"Fermeture réussie de {game_name}")
                return True
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de la fermeture du jeu: {e}")
                return False
        
        # Lancer l'opération dans un thread séparé
        self.current_operation = self._run_in_thread(close_operation)
        
        # Si un callback est fourni, vérifier périodiquement la fin de l'opération
        if callback:
            def check_completion():
                if not self.operation_queue.empty():
                    status, result = self.operation_queue.get()
                    callback(result)
                    return
                
                # Vérifier toutes les 100ms
                threading.Timer(0.1, check_completion).start()
            
            check_completion() 