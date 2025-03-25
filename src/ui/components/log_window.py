"""
Log window component for SwitchMaster
Displays application logs in a dedicated window
"""
import customtkinter as ctk
from datetime import datetime
from ...utils.window_utils import center_window, set_dark_title_bar, set_window_icon


class LogWindow(ctk.CTkToplevel):
    """Fenêtre de logs."""
    def __init__(self, parent, title="Logs", colors=None, logger=None):
        super().__init__(parent)
        self.title(title)
        self.colors = colors or {}
        self.logger = logger
        
        # Configure window
        self.geometry("800x600")
        self.minsize(600, 400)
        self.configure(fg_color=self.colors.get('bg_dark', "#1E1E1E"))
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        # Content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text="Logs de l'application",
            font=("Arial", 18, "bold"),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        title_label.pack(pady=(0, 15))
        
        # Log text widget (read-only)
        self.log_text = ctk.CTkTextbox(
            content_frame,
            fg_color=self.colors.get('bg_very_dark', "#131313"),
            text_color=self.colors.get('text', "#FFFFFF"),
            font=("Consolas", 12),
            corner_radius=6,
            wrap="word"
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Button frame
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(fill='x', pady=(15, 0))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            button_frame,
            text="Rafraîchir",
            font=("Arial", 12, "bold"),
            fg_color=self.colors.get('button', "#3391D4"),
            hover_color=self.colors.get('button_hover', "#40A9FF"),
            width=100,
            command=self.update_logs
        )
        refresh_btn.pack(side='left', padx=5)
        
        # Close button
        self.close_btn = ctk.CTkButton(
            button_frame,
            text="Fermer",
            font=("Arial", 12, "bold"),
            fg_color=self.colors.get('accent', "#FF4655"),
            hover_color=self.colors.get('accent_hover', "#FF5F6D"),
            width=100,
            command=self.destroy  # Par défaut, on détruit juste la fenêtre
        )
        self.close_btn.pack(side='right', padx=5)
        
        # Load initial logs
        self.update_logs()
    
    def bind_close_button(self, callback):
        """Bind a callback to the close button."""
        self.close_btn.configure(command=callback)
    
    def update_logs(self):
        """Update the log display."""
        # Enable temporarily to insert text
        self.log_text.configure(state="normal")
        self.log_text.delete('1.0', 'end')
        try:
            with open("switchmaster.log", 'r', encoding='utf-8') as f:
                # Lire les 1000 dernières lignes pour éviter de surcharger
                lines = f.readlines()[-1000:]
                self.log_text.insert('end', ''.join(lines))
            self.log_text.see('end')  # Scroll to end
        except Exception as e:
            self.log_text.insert('end', f"Erreur lors de la lecture des logs : {str(e)}")
        # Set back to read-only
        self.log_text.configure(state="disabled")

    def show(self):
        """Show the log window or bring to front if already open."""
        if self.window is None:
            self.create_window()
        elif not self.window.winfo_exists():
            self.create_window()
        else:
            self.window.focus_force()
            self.window.lift()
    
    def create_window(self):
        """Create the log window."""
        # Create window
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title(self.title)
        self.window.transient(self.parent)
        
        # Set size and position
        center_window(self.window, self.width, self.height)
        
        # Configure appearance
        self.window.configure(fg_color=self.colors.get('bg_dark', "#1E1E1E"))
        set_window_icon(self.window)
        set_dark_title_bar(self.window)
        
        # Main frame
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill='x', pady=(0, 15))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=self.title,
            font=("Arial", 18, "bold"),
            text_color=self.colors.get('text', "#FFFFFF")
        )
        title_label.pack(side='left')
        
        # Button frame
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side='right')
        
        # Clear button
        clear_button = ctk.CTkButton(
            button_frame,
            text="Effacer",
            font=("Arial", 12),
            fg_color=self.colors.get('button', "#444444"),
            hover_color=self.colors.get('button_hover', "#555555"),
            corner_radius=6,
            width=80,
            height=30,
            command=self.clear_logs
        )
        clear_button.pack(side='left', padx=(0, 10))
        
        # Export button
        export_button = ctk.CTkButton(
            button_frame,
            text="Exporter",
            font=("Arial", 12),
            fg_color=self.colors.get('button', "#444444"),
            hover_color=self.colors.get('button_hover', "#555555"),
            corner_radius=6,
            width=80,
            height=30,
            command=self.export_logs
        )
        export_button.pack(side='left')
        
        # Textbox frame
        text_frame = ctk.CTkFrame(main_frame)
        text_frame.pack(fill='both', expand=True)
        
        # Log text widget
        self.log_text = ctk.CTkTextbox(
            text_frame,
            font=("Consolas", 12),
            fg_color=self.colors.get('bg_very_dark', "#131313"),
            text_color=self.colors.get('text', "#FFFFFF"),
            corner_radius=6,
            wrap="word"
        )
        self.log_text.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Add any pending logs
        for timestamp, level, message in self.pending_logs:
            self._display_log(timestamp, level, message)
        self.pending_logs = []
        
        # Auto-scroll to bottom when new content is added
        self.log_text.configure(state='disabled')
        
        # Close button
        close_button = ctk.CTkButton(
            main_frame,
            text="Fermer",
            font=("Arial", 12, "bold"),
            fg_color=self.colors.get('accent', "#FF4655"),
            hover_color=self.colors.get('accent_hover', "#FF5F6D"),
            corner_radius=6,
            height=35,
            command=self.window.destroy
        )
        close_button.pack(pady=(15, 0))
    
    def add_log(self, timestamp, level, message):
        """
        Add a log entry to the window.
        
        Args:
            timestamp: Log timestamp (datetime object or string)
            level (str): Log level (INFO, WARNING, etc.)
            message (str): Log message
        """
        if self.window is None or not self.window.winfo_exists():
            # Store log for when window is opened
            self.pending_logs.append((timestamp, level, message))
            return
        
        self._display_log(timestamp, level, message)
    
    def _display_log(self, timestamp, level, message):
        """Internal method to display a log in the text widget."""
        if self.log_text is None:
            return
            
        # Enable editing temporarily
        self.log_text.configure(state='normal')
        
        # Format timestamp if it's a datetime object
        if isinstance(timestamp, datetime):
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        # Get color for log level
        level_color = {
            "DEBUG": "#808080",  # Gray
            "INFO": "#3391D4",   # Blue
            "SUCCESS": "#28A745", # Green
            "WARNING": "#FFC107", # Yellow
            "ERROR": "#DC3545",  # Red
            "CRITICAL": "#9C27B0" # Purple
        }.get(level.upper(), "#FFFFFF")
        
        # Format and insert timestamp
        self.log_text.insert('end', f"[{timestamp}] ", "timestamp")
        self.log_text.tag_configure("timestamp", foreground="#808080")
        
        # Format and insert level
        self.log_text.insert('end', f"[{level.upper()}] ", "level")
        self.log_text.tag_configure("level", foreground=level_color, font=("Consolas", 12, "bold"))
        
        # Format and insert message with emojis
        self.log_text.insert('end', f"{message}\n", "message")
        self.log_text.tag_configure("message", foreground=self.colors.get('text', "#FFFFFF"))
        
        # Disable editing and scroll to end
        self.log_text.configure(state='disabled')
        self.log_text.see('end')
    
    def clear_logs(self):
        """Clear all logs from the window."""
        if self.log_text:
            self.log_text.configure(state='normal')
            self.log_text.delete('1.0', 'end')
            self.log_text.configure(state='disabled')
    
    def export_logs(self):
        """Export logs to a file."""
        if not self.log_text:
            return
            
        try:
            from tkinter import filedialog
            import os
            
            # Get current date and time for filename
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"switchmaster_logs_{now}.txt"
            
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if file_path:
                # Get log content
                log_content = self.log_text.get('1.0', 'end')
                
                # Save to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                # Show success message
                from tkinter import messagebox
                messagebox.showinfo(
                    "Export Successful", 
                    f"Logs exported successfully to:\n{os.path.basename(file_path)}"
                )
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}") 