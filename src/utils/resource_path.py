"""
Utilitaire pour résoudre les chemins des ressources dans l'application compilée et en développement.
"""
import os
import sys


def resource_path(relative_path):
    """
    Résout le chemin d'accès à une ressource, que l'application soit exécutée
    normalement ou empaquetée avec PyInstaller.
    
    Args:
        relative_path (str): Chemin relatif vers la ressource
        
    Returns:
        str: Chemin absolu vers la ressource
    """
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # En mode développement, on utilise le répertoire courant
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path) 