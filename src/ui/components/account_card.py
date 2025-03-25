"""
Account card component for SwitchMaster
Displays a single account with options to select, edit, or delete
"""
import customtkinter as ctk


class AccountCard:
    """
    Account card component for displaying a single account.
    Provides options to switch to the account, edit it, or delete it.
    """
    def __init__(self, parent, username, account_num, on_switch=None, on_edit=None):
        """
        Initialize the account card.
        
        Args:
            parent: Parent widget
            username (str): Account username to display
            account_num (str): Account number for identification
            on_switch: Callback when user clicks to switch to this account
            on_edit: Callback when user clicks to edit this account
        """
        self.parent = parent
        self.username = username
        self.account_num = account_num
        self.on_switch = on_switch
        self.on_edit = on_edit
        
        # Create the card
        self.frame = self.create_card()
    
    def create_card(self):
        """Create and return the account card widget."""
        # Main frame
        frame = ctk.CTkFrame(
            self.parent,
            corner_radius=10,
            fg_color="#242424",
            border_width=1,
            border_color="#333333"
        )
        
        # Add username
        username_label = ctk.CTkLabel(
            frame,
            text=self.username,
            font=("Arial", 14, "bold"),
            text_color="#FFFFFF"
        )
        username_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        # Account ID
        id_label = ctk.CTkLabel(
            frame,
            text=f"Account #{self.account_num}",
            font=("Arial", 10),
            text_color="#888888"
        )
        id_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))
        
        # Button frame
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")
        
        # Switch button
        switch_button = ctk.CTkButton(
            button_frame,
            text="Switch",
            font=("Arial", 12, "bold"),
            fg_color="#FF4655",
            hover_color="#FF5F6D",
            corner_radius=6,
            height=32,
            command=self._on_switch_click
        )
        switch_button.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        # Edit button
        edit_button = ctk.CTkButton(
            button_frame,
            text="Edit",
            font=("Arial", 12),
            fg_color="#333333",
            hover_color="#444444",
            corner_radius=6,
            height=32,
            command=self._on_edit_click
        )
        edit_button.pack(side="right", expand=True, fill="x", padx=(5, 0))
        
        return frame
    
    def _on_switch_click(self):
        """Handle switch button click."""
        if self.on_switch:
            self.on_switch(self.account_num)
    
    def _on_edit_click(self):
        """Handle edit button click."""
        if self.on_edit:
            self.on_edit(self.account_num)
    
    def pack(self, **kwargs):
        """Pack the frame with the given options."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame with the given options."""
        self.frame.grid(**kwargs)
    
    def place(self, **kwargs):
        """Place the frame with the given options."""
        self.frame.place(**kwargs)
    
    def destroy(self):
        """Destroy the frame."""
        self.frame.destroy() 