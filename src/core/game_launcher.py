"""
Game launcher module for SwitchMaster
Handles launching games and automating login processes.
"""
import subprocess
import time
import pyautogui
import win32gui
import win32con
import win32process
import pyperclip
import psutil
from time import sleep
import os


class GameLauncher:
    """
    Handles game launching and account switching automation.
    Manages the interaction with Riot clients for automatic login.
    """
    def __init__(self, logger=None):
        """
        Initialize the Game Launcher.
        
        Args:
            logger: Optional logger instance for logging events
        """
        self.logger = logger
    
    def kill_processes(self, process_names):
        """
        Kills specified processes.
        
        Args:
            process_names (list): List of process names to kill
            
        Returns:
            bool: True if all processes were successfully killed or not found
        """
        success = True
        
        if self.logger:
            self.logger.info("Début de la fermeture des clients...")
        
        for process_name in process_names:
            process_killed = False
            
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if process_name.lower() in proc.info['name'].lower():
                            pid = proc.info['pid']
                            proc.kill()
                            process_killed = True
                            
                            if self.logger:
                                self.logger.info(f"Processus '{process_name}' (PID {pid}) arrêté avec succès")
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        if self.logger:
                            self.logger.error(f"Erreur lors de l'arrêt du processus '{process_name}': {str(e)}")
                        success = False
                
                if not process_killed and self.logger:
                    self.logger.warning(f"Processus '{process_name}' non trouvé")
                    
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur inattendue lors de l'arrêt de '{process_name}': {str(e)}")
                success = False
        
        if self.logger:
            self.logger.info("Fermeture des clients terminée.")
        
        return success
    
    def find_riot_window(self):
        """
        Finds the Riot client window.
        
        Returns:
            int or None: Window handle if found, None otherwise
        """
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
        
        if hwnd_list and self.logger:
            self.logger.info(f"Fenêtre Riot trouvée: {hwnd_list[0]}")
        
        return hwnd_list[0] if hwnd_list else None
    
    def force_window_focus(self, hwnd):
        """
        Forces focus on a window.
        
        Args:
            hwnd (int): Window handle
            
        Returns:
            bool: True if focus was obtained, False otherwise
        """
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
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la mise au premier plan de la fenêtre: {str(e)}")
            return False
    
    def ensure_window_focus(self, riot_window):
        """
        Ensures that the Riot window has focus with verification.
        
        Args:
            riot_window (int): Riot window handle
            
        Returns:
            bool: True if focus was obtained, False otherwise
        """
        max_attempts = 5
        for _ in range(max_attempts):
            try:
                # Vérifier que la fenêtre existe toujours
                if not win32gui.IsWindow(riot_window):
                    if self.logger:
                        self.logger.error("La fenêtre n'existe plus")
                    return False
                    
                # Vérifier que le processus est toujours en cours
                if not self.verify_riot_client_running():
                    if self.logger:
                        self.logger.error("Le client Riot n'est plus en cours d'exécution")
                    return False
                    
                # Vérifier le focus actuel
                current_focus = win32gui.GetForegroundWindow()
                if current_focus == riot_window:
                    return True
                    
                # Tenter de forcer le focus
                if self.force_window_focus(riot_window):
                    sleep(0.2)  # Attendre que le focus soit effectif
                    return win32gui.GetForegroundWindow() == riot_window
                    
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de la vérification du focus: {str(e)}")
            sleep(0.1)
        
        if self.logger:
            self.logger.error("Impossible d'obtenir le focus après plusieurs tentatives")
        return False
    
    def verify_riot_client_running(self):
        """
        Verifies if the Riot client is running.
        
        Returns:
            bool: True if running, False otherwise
        """
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if "RiotClientServices" in proc.info['name']:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la vérification du client Riot: {str(e)}")
            return False
    
    def launch_game(self, riot_client_path, game_id):
        """
        Launch a game using the Riot client.
        
        Args:
            riot_client_path (str): Path to the Riot client executable
            game_id (str): ID of the game to launch ('league' or 'valorant')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not riot_client_path or not os.path.exists(riot_client_path):
                if self.logger:
                    self.logger.error(f"Client Riot non trouvé à: {riot_client_path}")
                return False
                
            # Normalize game ID
            if game_id == "league":
                product = "league_of_legends"
            elif game_id == "valorant":
                product = "valorant"
            else:
                product = game_id
                
            launch_cmd = [
                riot_client_path,
                f"--launch-product={product}",
                "--launch-patchline=live"
            ]
            
            if self.logger:
                self.logger.info(f"Lancement du jeu: {product}")
                self.logger.info(f"Commande: {' '.join(launch_cmd)}")
                
            # Launch the game
            subprocess.Popen(launch_cmd)
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors du lancement du jeu: {str(e)}")
            return False
    
    def switch_account(self, riot_client_path, account, stay_logged_in=False, launch_game_id=None):
        """
        Switches to a different account by automating the login process.
        
        Args:
            riot_client_path (str): Path to the Riot client executable
            account (dict): Account information with username and password
            stay_logged_in (bool): Whether to stay logged in after authentication
            launch_game_id (str, optional): Game ID to launch after login
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Log for debugging (sanitize password by only showing length)
            if self.logger:
                # Safe password logging without revealing the actual password
                login_mode = "AVEC 'Rester connecté'" if stay_logged_in else "SANS 'Rester connecté'"
                game_launch_info = f" et lancement de {launch_game_id}" if launch_game_id else ""
                self.logger.info(f"Tentative de connexion {login_mode}{game_launch_info} pour le compte: {account.get('username', 'Unknown')}")
                self.logger.info(f"Longueur du mot de passe: {len(str(account.get('password', '')))}")
                
            # Fermer les clients existants
            processes_to_kill = [
                "RiotClientServices.exe",
                "RiotClientUx.exe",
                "LeagueClient.exe",
                "VALORANT.exe"
            ]
            
            self.kill_processes(processes_to_kill)
            
            time.sleep(2)
            
            # Lancer le client Riot
            if self.logger:
                self.logger.info(f"Lancement du client Riot depuis : {riot_client_path}")
            
            subprocess.Popen([riot_client_path])
            
            # Attendre que la fenêtre apparaisse
            max_attempts = 40
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
                                if self.force_window_focus(riot_window):
                                    break
                            except Exception as e:
                                if self.logger:
                                    self.logger.error(f"Erreur lors de la mise au premier plan: {str(e)}")
                                continue
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Erreur lors de la recherche de la fenêtre: {str(e)}")
                        if attempt == max_attempts - 1:
                            if self.logger:
                                self.logger.error("Impossible de trouver la fenêtre du client Riot")
                            return False
                        continue
                
                if not riot_window:
                    if self.logger:
                        self.logger.error("Fenêtre Riot non trouvée après plusieurs tentatives")
                    return False
                
                time.sleep(1.5)  # Attendre que l'interface soit complètement chargée
                
                try:
                    old_clipboard = pyperclip.paste()
                except Exception:
                    old_clipboard = ""
                
                try:
                    # Vérifier l'état initial
                    if not self.verify_riot_client_running():
                        if self.logger:
                            self.logger.error("Le client Riot n'est pas en cours d'exécution")
                        return False
                        
                    # Saisir le nom d'utilisateur
                    for attempt in range(3):
                        if not self.ensure_window_focus(riot_window):
                            if attempt == 2:
                                if self.logger:
                                    self.logger.error("Impossible de maintenir le focus sur la fenêtre Riot")
                                return False
                            continue
                            
                        try:
                            # Sauvegarder et vérifier le presse-papier
                            pyperclip.copy(account['username'])
                            if pyperclip.paste() != account['username']:
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
                        except Exception as e:
                            if self.logger:
                                self.logger.error(f"Erreur lors de la saisie du nom d'utilisateur: {str(e)}")
                            if attempt == 2:
                                raise
                            continue
                    
                    # Saisir le mot de passe avec les mêmes vérifications
                    for attempt in range(3):
                        if not self.ensure_window_focus(riot_window):
                            if attempt == 2:
                                if self.logger:
                                    self.logger.error("Impossible de maintenir le focus sur la fenêtre Riot")
                                return False
                            continue
                            
                        try:
                            # Ensure password is a string
                            password = str(account.get('password', ''))
                            
                            # Check if password is empty
                            if not password:
                                if self.logger:
                                    self.logger.error("Erreur: Mot de passe vide")
                                return False
                            
                            # Clear clipboard and copy password
                            pyperclip.copy('')
                            time.sleep(0.1)
                            
                            # Try to copy the password and verify it was copied correctly
                            pyperclip.copy(password)
                            clipboard_content = pyperclip.paste()
                            
                            if clipboard_content != password:
                                if self.logger:
                                    self.logger.error(f"Erreur de copie dans le presse-papier: longueur attendue={len(password)}, obtenue={len(clipboard_content)}")
                                if attempt == 2:
                                    return False
                                continue
                                
                            pyautogui.hotkey('ctrl', 'a')
                            time.sleep(0.2)
                            
                            if not self.ensure_window_focus(riot_window):
                                continue
                                
                            pyautogui.hotkey('ctrl', 'v')
                            time.sleep(0.3)
                            
                            if not self.ensure_window_focus(riot_window):
                                continue
                                
                            # Si l'option "Rester connecté" est active, ne pas appuyer sur Enter ici
                            # car nous allons faire une séquence différente
                            if not stay_logged_in:
                                pyautogui.press('enter')
                            else:
                                if self.logger:
                                    self.logger.info("Option 'Rester connecté' activée, exécution de la séquence")
                                
                                # Presser 6 fois Tab pour naviguer au bouton "Rester connecté"
                                for i in range(6):
                                    pyautogui.press('tab')
                                    time.sleep(0.15)
                                
                                # Presser Entrée pour activer le bouton
                                pyautogui.press('enter')
                                time.sleep(0.2)
                                
                                # Presser Tab une fois pour aller au bouton de confirmation
                                pyautogui.press('tab')
                                time.sleep(0.15)
                                
                                # Presser Entrée à nouveau pour confirmer
                                pyautogui.press('enter')
                                
                                if self.logger:
                                    self.logger.info("Séquence 'Rester connecté' exécutée")
                            
                            break
                        except Exception as e:
                            if self.logger:
                                self.logger.error(f"Erreur lors de la saisie du mot de passe: {str(e)}")
                            if attempt == 2:
                                raise
                            continue
                            
                finally:
                    try:
                        # Nettoyer le presse-papier de manière sécurisée
                        pyperclip.copy(" " * 100)  # Effacer avec des espaces
                        pyperclip.copy(old_clipboard)
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Erreur lors du nettoyage du presse-papier: {str(e)}")
                
                time.sleep(3)
                
                # Vérifier s'il y a des messages d'erreur
                try:
                    error_messages = []
                    win32gui.EnumWindows(
                        lambda hwnd, ctx: ctx.append(win32gui.GetWindowText(hwnd)) 
                        if "Erreur" in win32gui.GetWindowText(hwnd) else None, 
                        error_messages
                    )
                    
                    if any("refusé" in msg.lower() for msg in error_messages):
                        if self.logger:
                            self.logger.warning("Une vérification par e-mail est nécessaire")
                        return (False, "email_verification")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Erreur lors de la vérification des messages d'erreur: {str(e)}")
                
                # Signaler le succès du changement de compte
                if self.logger:
                    login_mode = "AVEC 'Rester connecté' activé" if stay_logged_in else "SANS 'Rester connecté'"
                    self.logger.info(f"✅ Connexion réussie au compte {account.get('username', 'Unknown')} {login_mode}")
                
                # Launch game if requested
                if launch_game_id:
                    time.sleep(1)  # Petit délai avant de lancer le jeu
                    game_launched = self.launch_game(riot_client_path, launch_game_id)
                    if game_launched and self.logger:
                        self.logger.info(f"✅ Processus complet terminé: Compte connecté et jeu {launch_game_id} lancé")
                else:
                    # Processus terminé (sans lancement de jeu)
                    if self.logger:
                        self.logger.info(f"✅ Processus complet terminé: Compte connecté")
                
                return True
                
            finally:
                pyautogui.FAILSAFE = True
                
        except Exception as e:
            error_msg = f"Erreur lors de la connexion : {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False 