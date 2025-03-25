"""
SwitchMaster Utils Module
Contains utility functions and classes for logging, window management, and other helper functions
"""
from .logging import Logger
from .window_utils import (
    center_window, set_dark_title_bar, set_window_icon, 
    make_window_draggable, set_icon, resource_path,
    create_rounded_rectangle, setup_window_appearance
)

__all__ = [
    'Logger', 
    'center_window', 'set_dark_title_bar', 'set_window_icon',
    'make_window_draggable', 'set_icon', 'resource_path',
    'create_rounded_rectangle', 'setup_window_appearance'
] 