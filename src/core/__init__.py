"""
SwitchMaster Core Module
Contains core business logic for account management, game client detection and game launching
"""
from .account_manager import AccountManager
from .client_finder import ClientFinder
from .encryption import PasswordEncryptor
from .game_launcher import GameLauncher

__all__ = ['AccountManager', 'ClientFinder', 'PasswordEncryptor', 'GameLauncher'] 