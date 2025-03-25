"""
Window utilities module for SwitchMaster
Provides helper functions for window management and styling.
"""
import os
import sys
import ctypes
from PIL import Image, ImageDraw, ImageTk
import customtkinter as ctk


def resource_path(relative_path):
    """
    Get absolute path to resource, works for development and for PyInstaller.
    
    Args:
        relative_path (str): Relative path to the resource
        
    Returns:
        str: Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def center_window(window, width=None, height=None):
    """
    Center a window on the screen.
    
    Args:
        window: The window to center
        width (int, optional): The width of the window
        height (int, optional): The height of the window
    """
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()
        
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")


def set_dark_title_bar(window):
    """
    Apply dark mode to the title bar on Windows.
    
    Args:
        window: The window to apply dark mode to
        
    Returns:
        bool: True if successful, False otherwise
    """
    if sys.platform == "win32":
        window.update()
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
        get_parent = ctypes.windll.user32.GetParent
        hwnd = get_parent(window.winfo_id())
        rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
        value = 2
        value = ctypes.c_int(value)
        set_window_attribute(hwnd, rendering_policy, ctypes.byref(value), ctypes.sizeof(value))
        return True
    else:
        return False


def set_window_icon(window):
    """Set the window icon."""
    try:
        # Importer resource_path si ce n'est pas déjà fait
        # Cette fonction doit être dans ce module
        icon_path = resource_path(os.path.join("assets", "images", "logo.ico"))
        
        try:
            window.iconbitmap(icon_path)
        except:
            # Essayer avec le format PNG si le ICO ne fonctionne pas
            icon_path_png = resource_path(os.path.join("assets", "images", "logo.png"))
            if os.path.exists(icon_path_png):
                # Utiliser le PNG comme alternative
                icon_image = Image.open(icon_path_png)
                window.iconphoto(True, ImageTk.PhotoImage(icon_image))
            else:
                # Si tout échoue, utiliser une icône par défaut
                pass
    except Exception as e:
        # Ignorer l'erreur, ce n'est pas critique
        pass


def set_icon(window, icon_path):
    """
    Set icon for window (wrapper for set_window_icon).
    
    Args:
        window: The window to set the icon for
        icon_path (str): Path to the icon file
    """
    set_window_icon(window)


def make_window_draggable(window, draggable_frame=None):
    """
    Make a window draggable from a specific frame.
    
    Args:
        window: Window to make draggable
        draggable_frame: Frame to use for dragging (defaults to window)
    """
    frame = draggable_frame or window
    frame._drag_start_x = 0
    frame._drag_start_y = 0
    
    def start_drag(event):
        frame._drag_start_x = event.x
        frame._drag_start_y = event.y
        
    def do_drag(event):
        if frame._drag_start_x != 0 and frame._drag_start_y != 0:
            dx = event.x - frame._drag_start_x
            dy = event.y - frame._drag_start_y
            x = window.winfo_x() + dx
            y = window.winfo_y() + dy
            window.geometry(f"+{x}+{y}")
            
    def stop_drag(event):
        frame._drag_start_x = 0
        frame._drag_start_y = 0
        
    frame.bind("<Button-1>", start_drag)
    frame.bind("<B1-Motion>", do_drag)
    frame.bind("<ButtonRelease-1>", stop_drag)


def create_rounded_rectangle(width, height, radius, fill):
    """Create a rounded rectangle image."""
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw rounded rectangle
    draw.rounded_rectangle(
        [(0, 0), (width-1, height-1)],
        radius=radius,
        fill=fill
    )
    
    return image


def setup_window_appearance(window, title="SwitchMaster", icon_path=None, width=800, height=600):
    """
    Setup common window appearance settings.
    
    Args:
        window: The window to configure
        title (str): The window title
        icon_path (str, optional): Path to the window icon
        width (int): Window width
        height (int): Window height
    """
    # Set window title
    window.title(title)
    
    # Set window size and position
    center_window(window, width, height)
    
    # Configure window appearance
    window.configure(bg="#1E1E1E")
    
    # Set dark title bar
    set_dark_title_bar(window)
    
    # Set window icon
    if icon_path:
        set_window_icon(window)


def create_color_scheme(theme="dark_blue"):
    """
    Create a color scheme for the application.
    
    Args:
        theme (str): The base theme to use
        
    Returns:
        dict: Dictionary of colors
    """
    if theme == "dark_blue":
        return {
            'bg_dark': "#1E1E1E",
            'bg_light': "#2D2D2D",
            'accent': "#FF4655",  # Rouge Valorant
            'accent_hover': "#FF5F6D",
            'button': "#3391D4",  # Bleu vif
            'button_hover': "#40A9FF",
            'text': "#FFFFFF",
            'text_secondary': "#A0A0A0",
            'border': "#333333"
        }
    elif theme == "valorant":
        return {
            'bg_dark': "#0F1923",
            'bg_light': "#1F2731",
            'accent': "#FF4655",
            'accent_hover': "#FF5F6D",
            'button': "#FF4655",
            'button_hover': "#FF5F6D",
            'text': "#FFFFFF",
            'text_secondary': "#A7B4C1",
            'border': "#364049"
        }
    else:
        # Default theme
        return {
            'bg_dark': "#1E1E1E",
            'bg_light': "#2D2D2D",
            'accent': "#FF4655",
            'accent_hover': "#FF5F6D",
            'button': "#3391D4",
            'button_hover': "#40A9FF",
            'text': "#FFFFFF",
            'text_secondary': "#A0A0A0",
            'border': "#333333"
        }


def configure_ctk_theme():
    """Configure the CustomTkinter theme for the application."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue") 