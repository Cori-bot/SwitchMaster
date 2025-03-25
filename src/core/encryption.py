"""
Encryption module for SwitchMaster
Handles password encryption and decryption using Fernet
"""
import os
import base64
import uuid
import hashlib
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordEncryptor:
    """Handles password encryption and decryption using Fernet."""
    
    def __init__(self, logger=None):
        """Initialize the password encryptor."""
        self.logger = logger
        self.key = self._generate_key()
        self.cipher_suite = Fernet(self.key)
    
    def _get_machine_id(self):
        """
        Get a stable unique machine identifier.
        
        Returns:
            str: Unique machine identifier
        """
        # Try to get machine UUID which is stable across reboots
        try:
            # For Windows
            if os.name == 'nt':
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Cryptography")
                value, _ = winreg.QueryValueEx(key, "MachineGuid")
                return value
            
            # For Linux
            elif os.path.exists('/etc/machine-id'):
                with open('/etc/machine-id', 'r') as f:
                    return f.read().strip()
            
            # For macOS
            elif os.path.exists('/Library/Preferences/SystemConfiguration/com.apple.computer.plist'):
                import plistlib
                with open('/Library/Preferences/SystemConfiguration/com.apple.computer.plist', 'rb') as f:
                    plist = plistlib.load(f)
                    return plist.get('LocalHostName', '')
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Impossible de récupérer l'ID machine: {str(e)}")
        
        # Fallback: Use a hash of system information
        system_info = [
            os.name,
            os.getenv('COMPUTERNAME', ''),
            os.getenv('USERNAME', ''),
            os.getenv('PROCESSOR_IDENTIFIER', ''),
            str(Path.home())
        ]
        
        # Create a stable ID from system info
        return hashlib.sha256(''.join([str(i) for i in system_info]).encode()).hexdigest()
    
    def _generate_key(self):
        """
        Generate a key for encryption using machine-specific information.
        
        Returns:
            bytes: The generated key
        """
        # Get a unique machine identifier
        machine_id = self._get_machine_id()
        
        # Use a fixed app-specific salt combined with machine ID
        salt = (machine_id + 'SwitchMaster-Salt-v1').encode()
        
        # Generate a key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        # Derive key using a constant passphrase - security comes from the machine-specific salt
        key = base64.urlsafe_b64encode(kdf.derive(b"SwitchMaster-Static-Key"))
        
        return key
    
    def encrypt(self, password):
        """
        Encrypt a password.
        
        Args:
            password (str): The password to encrypt
            
        Returns:
            str: The encrypted password
        """
        if not password:
            return ""
        
        try:
            # Convert password to bytes and encrypt
            password_bytes = password.encode()
            encrypted_password = self.cipher_suite.encrypt(password_bytes)
            
            # Convert to base64 for storage
            return base64.urlsafe_b64encode(encrypted_password).decode()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors du chiffrement: {str(e)}")
            return ""
    
    def decrypt(self, encrypted_password):
        """
        Decrypt a password.
        
        Args:
            encrypted_password (str): The encrypted password to decrypt
            
        Returns:
            str: The decrypted password
        """
        if not encrypted_password:
            return ""
        
        try:
            # Convert from base64 and decrypt
            if self.logger:
                self.logger.debug(f"Tentative de déchiffrement (longueur: {len(encrypted_password)})")
            
            # Some basic validation to ensure we're working with a properly formatted string
            if not isinstance(encrypted_password, str):
                if self.logger:
                    self.logger.error(f"Le mot de passe chiffré n'est pas une chaîne de caractères: {type(encrypted_password)}")
                return ""
                
            try:
                encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur de décodage base64: {str(e)}")
                return ""
                
            try:
                decrypted_password = self.cipher_suite.decrypt(encrypted_bytes)
                return decrypted_password.decode()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur de déchiffrement Fernet: {str(e)}")
                return ""
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors du déchiffrement: {str(e)}")
            return "" 