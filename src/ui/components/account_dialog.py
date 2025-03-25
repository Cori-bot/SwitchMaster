"""
Account dialog component for SwitchMaster
Dialog for adding, editing, and deleting accounts
"""
import customtkinter as ctk
from tkinter import messagebox
from ...utils.window_utils import center_window, set_dark_title_bar, set_window_icon


class AccountDialog:
    """
    Dialog for account management.
    Handles adding, editing and deleting accounts.
    """
    def __init__(self, parent, title, game_id, account_manager, colors=None, 
                 logger=None, on_save_callback=None, account_num=None, 
                 account=None, allow_delete=False):
        """
        Initialize the account dialog.
        
        Args:
            parent: Parent widget
            title (str): Dialog title
            game_id (str): Game identifier ('valorant' or 'league')
            account_manager: Account manager instance
            colors (dict): Color scheme dictionary
            logger: Logger instance
            on_save_callback: Callback function to run after saving
            account_num (str, optional): Account number when editing
            account (dict, optional): Account data when editing
            allow_delete (bool): Whether to show delete button
        """
        self.parent = parent
        self.title = title
        self.game_id = game_id
        self.account_manager = account_manager
        self.colors = colors or {}
        self.logger = logger
        self.on_save_callback = on_save_callback
        self.account_num = account_num
        self.account = account
        self.allow_delete = allow_delete
        self.password_visible = False
        
        # Create the dialog
        self.create_dialog()
        
    def create_dialog(self):
        """Create and show the dialog."""
        # Create dialog window
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Set size and position
        center_window(self.dialog, 400, 450)
        
        # Configure appearance
        self.dialog.configure(fg_color=self.colors.get('bg_dark', "#1E1E1E"))
        
        # Keep on top temporarily and maintain icon
        self.dialog.attributes('-topmost', True)
        self.dialog.focus_force()
        
        def maintain_icon():
            if self.dialog.winfo_exists():
                set_window_icon(self.dialog)
                self.dialog.after(100, maintain_icon)
                
        maintain_icon()
        self.dialog.after(250, lambda: self.dialog.attributes('-topmost', False))
        set_dark_title_bar(self.dialog)
        
        # Content frame
        content_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text=self.title,
            font=("Arial", 20, "bold"),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        title_label.pack(pady=(0, 20))
        
        # Fields frame
        fields_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        fields_frame.pack(fill='x')
        
        # Username field
        username_label = ctk.CTkLabel(
            fields_frame,
            text="Nom d'utilisateur:",
            font=("Arial", 12),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        username_label.pack(anchor='w', pady=(10, 0))
        
        self.username_entry = ctk.CTkEntry(
            fields_frame,
            width=300,
            placeholder_text="Entrez votre nom d'utilisateur"
        )
        self.username_entry.pack(pady=(5, 10), fill="x")
        
        # Password field
        password_label = ctk.CTkLabel(
            fields_frame,
            text="Mot de passe:",
            font=("Arial", 12),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        password_label.pack(anchor='w', pady=(10, 0))
        
        password_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        password_frame.pack(pady=(5, 10), fill="x")
        
        self.password_entry = ctk.CTkEntry(
            password_frame,
            width=270,
            placeholder_text="Entrez votre mot de passe",
            show="•"
        )
        self.password_entry.pack(side="left", fill="x", expand=True)
        
        toggle_btn = ctk.CTkButton(
            password_frame,
            text="👁",
            width=30,
            height=30,
            corner_radius=8,
            fg_color="#333333",
            hover_color="#444444",
            command=self.toggle_password
        )
        toggle_btn.pack(side="right", padx=(5, 0))
        
        # Notes field
        notes_label = ctk.CTkLabel(
            fields_frame,
            text="Notes:",
            font=("Arial", 12),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        notes_label.pack(anchor='w', pady=(10, 0))
        
        self.notes_entry = ctk.CTkTextbox(
            fields_frame,
            width=300,
            height=80,
            fg_color="#242424",
            corner_radius=6
        )
        self.notes_entry.pack(pady=(5, 10), fill="x")
        
        # Fill fields if editing
        if self.account:
            self.username_entry.insert(0, self.account.get('username', ''))
            self.password_entry.insert(0, self.account.get('password', ''))
            if 'notes' in self.account:
                self.notes_entry.insert("1.0", self.account.get('notes', ''))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        # Delete button (only show when editing)
        if self.allow_delete:
            delete_btn = ctk.CTkButton(
                buttons_frame,
                text="Delete",
                fg_color="#FF4444",
                hover_color="#FF6666",
                command=self.delete_account
            )
            delete_btn.pack(side='left', expand=True, padx=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Sauvegarder",
            fg_color=self.colors.get('accent', "#FF4655"),
            hover_color=self.colors.get('accent_hover', "#FF5F6D"),
            command=self.save_account
        )
        
        if self.allow_delete:
            save_btn.pack(side='right', expand=True, padx=5)
        else:
            save_btn.pack(side='right', expand=True, padx=5)
    
    def toggle_password(self):
        """Toggle password visibility."""
        self.password_visible = not self.password_visible
        self.password_entry.configure(show="" if self.password_visible else "•")
    
    def save_account(self):
        """Save the account information."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        notes = self.notes_entry.get("1.0", "end-1c").strip()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Le nom d'utilisateur et le mot de passe sont obligatoires.")
            return
            
        # Create account data dict
        account_data = {
            "username": username,
            "password": password,
            "notes": notes
        }
        
        # Call save callback
        if self.on_save_callback:
            self.on_save_callback(self.account_num, account_data)
            
        self.dialog.destroy()
    
    def delete_account(self):
        """Delete the account."""
        if not self.account_num:
            return
            
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer le compte {self.account.get('username', '')}?"):
            success, message = self.account_manager.delete_account(
                self.game_id,
                self.account_num
            )
            
            if success:
                if self.on_save_callback:
                    self.on_save_callback()
                self.dialog.destroy()
                messagebox.showinfo("Succès", message)
            else:
                messagebox.showerror("Erreur", message)

    def show(self):
        """Show the dialog."""
        if not hasattr(self, 'dialog'):
            self.create_dialog() 