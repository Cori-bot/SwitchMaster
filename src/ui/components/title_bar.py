"""
Title bar component for SwitchMaster
Custom title bar with minimize, maximize, and close buttons
"""
import customtkinter as ctk
from PIL import Image
from ...utils.window_utils import resource_path


class TitleBar:
    """
    Custom title bar component for SwitchMaster.
    Provides draggable title bar with application controls.
    """
    def __init__(self, parent, title="SwitchMaster", close_command=None, 
                 maximize_command=None, minimize_command=None, 
                 colors=None, images=None, 
                 start_move_callback=None, on_move_callback=None):
        """
        Initialize the title bar.
        
        Args:
            parent: Parent widget
            title (str): Window title
            close_command: Callback for close button
            maximize_command: Callback for maximize button
            minimize_command: Callback for minimize button
            colors (dict): Color scheme dictionary
            images (dict): Dictionary of loaded images
            start_move_callback: Callback for starting drag
            on_move_callback: Callback for dragging
        """
        self.parent = parent
        self.title = title
        self.colors = colors or {}
        self.images = images or {}
        
        # Create icon images if not provided
        if 'minimize' not in self.images:
            self.images['minimize'] = "─"
        if 'maximize' not in self.images:
            self.images['maximize'] = "□"
        if 'close' not in self.images:
            self.images['close'] = "✕"
        
        # Callbacks
        self.close_command = close_command
        self.maximize_command = maximize_command
        self.minimize_command = minimize_command
        self.start_move_callback = start_move_callback
        self.on_move_callback = on_move_callback
        
        # Create the title bar
        self.create_title_bar()
    
    def create_title_bar(self):
        """
        Create the title bar UI.
        
        Returns:
            ctk.CTkFrame: The title bar frame
        """
        # Title bar frame
        title_bar = ctk.CTkFrame(
            self.parent,
            fg_color=self.colors.get('bg_darker', '#1A1A1A'),
            height=40
        )
        title_bar.pack(fill='x', side='top')
        
        # Make sure the frame keeps its height
        title_bar.pack_propagate(False)
        
        # Logo and title container
        title_container = ctk.CTkFrame(title_bar, fg_color="transparent")
        title_container.pack(side='left', fill='y')
        
        # App logo
        if 'app_logo' in self.images:
            logo_label = ctk.CTkLabel(
                title_container,
                text="",
                image=self.images['app_logo']
            )
            logo_label.pack(side='left', padx=10)
        
        # Window title
        title_label = ctk.CTkLabel(
            title_container,
            text=self.title,
            font=("Segoe UI", 12),
            text_color=self.colors.get('text', '#FFFFFF')
        )
        title_label.pack(side='left', padx=10)
        
        # Window controls container
        controls = ctk.CTkFrame(title_bar, fg_color="transparent")
        controls.pack(side='right', fill='y')
        
        # Minimize button
        if self.minimize_command:
            min_btn = ctk.CTkButton(
                controls,
                text="—",
                width=45,
                height=30,
                command=self.minimize_command,
                fg_color="transparent",
                hover_color=self.colors.get('button_hover', '#2A2A2A'),
                font=("Segoe UI", 10)
            )
            min_btn.pack(side='left')
        
        # Maximize button
        if self.maximize_command:
            max_btn = ctk.CTkButton(
                controls,
                text="□",
                width=45,
                height=30,
                command=self.maximize_command,
                fg_color="transparent",
                hover_color=self.colors.get('button_hover', '#2A2A2A'),
                font=("Segoe UI", 10)
            )
            max_btn.pack(side='left')
        
        # Close button
        if self.close_command:
            close_btn = ctk.CTkButton(
                controls,
                text="✕",
                width=45,
                height=30,
                command=self.close_command,
                fg_color="transparent",
                hover_color=self.colors.get('close_hover', '#E81123'),
                font=("Segoe UI", 10)
            )
            close_btn.pack(side='left')
        
        # Bind move events
        if self.start_move_callback and self.on_move_callback:
            title_bar.bind("<Button-1>", self.start_move_callback)
            title_bar.bind("<B1-Motion>", self.on_move_callback)
            title_container.bind("<Button-1>", self.start_move_callback)
            title_container.bind("<B1-Motion>", self.on_move_callback)
        
        return title_bar
    
    def _start_move(self, event):
        """
        Handle start of window drag.
        
        Args:
            event: Mouse event
        """
        if self.start_move_callback:
            self.start_move_callback(event)
    
    def _on_move(self, event):
        """
        Handle window dragging.
        
        Args:
            event: Mouse event
        """
        if self.on_move_callback:
            self.on_move_callback(event) 