"""
Account management module for SwitchMaster
Handles loading, saving, and manipulating account information.
"""
import os
import json
from .encryption import PasswordEncryptor
from ..utils.logging import setup_logger


def get_config_path():
    """
    Gets the path to the accounts configuration file.
    
    Returns:
        str: Path to the accounts.json file
    """
    return os.path.join(os.getcwd(), "accounts.json")


class AccountManager:
    """
    Manages game accounts for Valorant and League of Legends.
    Handles loading, saving, adding, editing, and removing accounts.
    """
    def __init__(self, logger=None):
        """
        Initialize the Account Manager.
        
        Args:
            logger: Optional logger instance for logging events
        """
        self.logger = logger or setup_logger()
        self.password_manager = PasswordEncryptor(self.logger)
        self.accounts = {}
        self.load_accounts()
    
    def load_accounts(self):
        """
        Loads accounts from the configuration file.
        Initializes with empty account dictionaries if the file doesn't exist.
        """
        config_path = get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    self.accounts = json.load(f)
                
                if self.logger:
                    self.logger.info("Comptes chargés avec succès")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors du chargement des comptes: {str(e)}")
                self.accounts = {"valorant": {}, "league": {}}
        else:
            self.accounts = {"valorant": {}, "league": {}}
            self.save_accounts()
    
    def save_accounts(self):
        """
        Saves the accounts to the configuration file.
        """
        config_path = get_config_path()
        try:
            with open(config_path, "w") as f:
                json.dump(self.accounts, f, indent=4)
            
            if self.logger:
                self.logger.info("Comptes sauvegardés avec succès")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la sauvegarde des comptes: {str(e)}")
            return False
    
    def add_account(self, game_id, username, password, notes=""):
        """
        Add a new account for a game.
        
        Args:
            game_id (str): Game identifier
            username (str): Account username
            password (str): Account password
            notes (str): Optional notes about the account
            
        Returns:
            tuple: (success, message, account_num)
        """
        # Initialize structure if not exists
        if game_id not in self.accounts:
            self.accounts[game_id] = {}
            
        # Check if username already exists
        for acc_num, account in self.accounts[game_id].items():
            if account.get('username') == username:
                return False, f"Un compte avec le nom '{username}' existe déjà", None
                
        # Add account with incremented account number
        account_num = 1
        if self.accounts[game_id]:
            account_num = max(int(num) for num in self.accounts[game_id].keys()) + 1
            
        # Encrypt password
        encrypted_password = self.password_manager.encrypt(password)
        
        # Create account entry
        account = {
            'username': username,
            'password': encrypted_password,
            'notes': notes
        }
        
        # Add to accounts
        self.accounts[game_id][str(account_num)] = account
        
        # Save to file
        self.save_accounts()
        
        return True, f"Compte '{username}' ajouté avec succès", account_num
    
    def update_account(self, game_id, account_num, username, password, notes=""):
        """
        Update an existing account.
        
        Args:
            game_id (str): Game identifier
            account_num (int): Account number to update
            username (str): New username
            password (str): New password
            notes (str): New notes about the account
            
        Returns:
            tuple: (success, message)
        """
        # Check if game exists
        if game_id not in self.accounts:
            return False, f"Jeu '{game_id}' introuvable"
            
        # Find account by number
        account_str_num = str(account_num)
        if account_str_num not in self.accounts[game_id]:
            return False, f"Compte numéro {account_num} introuvable"
        
        # Check for duplicate username (only if username changed)
        if username != self.accounts[game_id][account_str_num].get('username'):
            for acc_id, acc in self.accounts[game_id].items():
                if acc.get('username') == username and acc_id != account_str_num:
                    return False, f"Un compte avec le nom '{username}' existe déjà"
        
        # Only update password if changed
        current_password = self.password_manager.decrypt(self.accounts[game_id][account_str_num]['password'])
        if password != current_password:
            self.accounts[game_id][account_str_num]['password'] = self.password_manager.encrypt(password)
                
        # Update other fields
        self.accounts[game_id][account_str_num]['username'] = username
        self.accounts[game_id][account_str_num]['notes'] = notes
                
        # Save to file
        self.save_accounts()
                
        return True, f"Compte '{username}' mis à jour avec succès"
    
    def delete_account(self, game_id, account_num):
        """
        Deletes an account and renumbers the remaining accounts.
        
        Args:
            game_id (str): Game identifier
            account_num (str): Account number to delete
            
        Returns:
            tuple: (success, message)
        """
        if account_num not in self.accounts.get(game_id, {}):
            return False, "Ce compte n'existe pas!"
        
        username = self.accounts[game_id][account_num]["username"]
        
        # Supprimer le compte
        del self.accounts[game_id][account_num]
        
        # Renuméroter les comptes restants
        new_accounts = {}
        for i, (_, account) in enumerate(sorted(self.accounts[game_id].items()), 1):
            new_accounts[str(i)] = account
        
        self.accounts[game_id] = new_accounts
        
        # Sauvegarder les changements
        if self.save_accounts():
            if self.logger:
                self.logger.info(f"Compte {username} supprimé avec succès pour {game_id}")
            return True, "Compte supprimé avec succès!"
        else:
            return False, "Erreur lors de la suppression du compte"
    
    def get_account(self, game_id, account_num):
        """
        Get account by number with decrypted password.
        
        Args:
            game_id (str): Game identifier
            account_num (int): Account number
            
        Returns:
            dict: Account data with decrypted password
        """
        # Check if game exists
        if game_id not in self.accounts:
            return None
            
        # Find account by number
        account_str_num = str(account_num)
        if account_str_num not in self.accounts[game_id]:
            return None
            
        # Create a copy to avoid modifying the original
        account_copy = self.accounts[game_id][account_str_num].copy()
        account_copy['num'] = account_num  # Add the account number
                
        # Decrypt password
        try:
            decrypted_password = self.password_manager.decrypt(account_copy.get('password', ''))
            account_copy['password'] = decrypted_password
        except Exception as e:
            self.logger.error(f"Erreur lors du déchiffrement du mot de passe: {e}")
            account_copy['password'] = ""
                    
        return account_copy
    
    def get_all_accounts(self, game_id):
        """
        Get all accounts for a game.
        
        Args:
            game_id (str): Game identifier
            
        Returns:
            list: List of account dictionaries with account numbers
        """
        if game_id not in self.accounts:
            return []
            
        accounts_list = []
        for num, account in self.accounts[game_id].items():
            account_with_num = account.copy()
            account_with_num['num'] = int(num)
            accounts_list.append(account_with_num)
            
        return accounts_list
    
    def get_accounts(self, game_id):
        """
        Get all accounts for a specific game.
        
        Args:
            game_id: ID of the game
            
        Returns:
            list: List of accounts for the game
        """
        if game_id not in self.accounts:
            return []
            
        accounts = []
        for account_id, account_data in self.accounts[game_id].items():
            account = {
                'id': account_id,
                'name': account_data.get('name', ''),
                'username': account_data.get('username', ''),
                'password': self.password_manager.decrypt(account_data.get('password', ''))
            }
            accounts.append(account)
            
        return accounts 