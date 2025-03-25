"""
Image utilities for SwitchMaster
Provides functions for loading and managing images
"""
import os
from PIL import Image, ImageDraw

def create_icon(size, color, symbol=None):
    """
    Create a simple icon with optional symbol.
    
    Args:
        size (tuple): Icon size (width, height)
        color (str): Icon color in hex format
        symbol (str, optional): Symbol to draw on icon
        
    Returns:
        PIL.Image: Created icon
    """
    # Create base image
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw symbol if provided
    if symbol:
        # Calculate text size and position
        font_size = min(size) - 4
        x = size[0] // 2
        y = size[1] // 2
        
        # Draw centered text
        draw.text(
            (x, y),
            symbol,
            fill=color,
            anchor="mm",
            font=None,
            font_size=font_size
        )
    
    return image

def load_images(base_path):
    """
    Load all required images.
    
    Args:
        base_path (str): Base path for image files
        
    Returns:
        dict: Dictionary of loaded images
    """
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
    
    # Load images
    images = {}
    for name, (filename, size) in image_specs.items():
        path = os.path.join(base_path, filename)
        try:
            if os.path.exists(path):
                image = Image.open(path)
                if size:
                    image = image.resize(size, Image.Resampling.LANCZOS)
                images[name] = image
        except Exception as e:
            print(f"Erreur lors du chargement de {filename}: {str(e)}")
    
    return images 