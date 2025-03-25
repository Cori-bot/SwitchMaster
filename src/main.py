"""
Main entry point for SwitchMaster application.
"""
import sys
import os
import traceback

# Add parent directory to path for development
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Handle uncaught exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions and log them."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Default behavior for keyboard interrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    # Log the error
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Try to log to file
    try:
        log_dir = os.path.join(os.path.expanduser("~"), ".switchmaster", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        from datetime import datetime
        log_file = os.path.join(log_dir, f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        with open(log_file, 'w') as f:
            f.write(f"SwitchMaster Crash Report\n")
            f.write(f"========================\n\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Error Type: {exc_type.__name__}\n")
            f.write(f"Error Message: {exc_value}\n\n")
            f.write(f"Traceback:\n{error_msg}\n")
            
        print(f"Crash log saved to: {log_file}")
    except:
        # If we can't log to file, just print
        pass
        
    # Show error to user
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "SwitchMaster Error",
            f"Une erreur s'est produite:\n\n{exc_value}\n\n"
            f"Veuillez consulter les logs pour plus de détails."
        )
        root.destroy()
    except:
        # If we can't show a message box, just print
        print(f"ERROR: {exc_type.__name__}: {exc_value}")
        print(error_msg)
    
    sys.exit(1)

# Set the exception handler
sys.excepthook = handle_exception

def main():
    """Main entry point for the application."""
    try:
        # Import the application
        from src.ui.app import Application
        
        # Create and run the application
        app = Application()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 