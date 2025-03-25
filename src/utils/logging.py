"""
Logging utility module for SwitchMaster
Provides custom logging configuration with emoji formatting.
"""
import logging
import os
from datetime import datetime


class Logger:
    """Custom logger for SwitchMaster with emoji formatting and file logging."""
    
    def __init__(self, app_name="SwitchMaster", log_file="switchmaster.log", 
                 console_level="INFO", file_level="DEBUG", enable_console=False):
        """
        Initialize the logger with custom configuration.
        
        Args:
            app_name (str): Name of the application/logger
            log_file (str): Path to log file
            console_level (str): Logging level for console output
            file_level (str): Logging level for file output
            enable_console (bool): Whether to enable console output
        """
        self.app_name = app_name
        self.log_file = log_file
        self.enable_console = enable_console
        
        # Convert string levels to logging levels
        self.console_level = self._get_log_level(console_level)
        self.file_level = self._get_log_level(file_level)
        
        # Create logger
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(min(self.console_level, self.file_level))
        
        # Remove any existing handlers
        self.logger.handlers = []
        
        # Setup handlers
        if self.enable_console:
            self._setup_console_handler()
        self._setup_file_handler()
        
        # Initialize callbacks list
        self.callbacks = []
        
        # Reference à la fenêtre principale (sera définie plus tard)
        self.main_window = None
        
        # Start with an info message
        self.info(f"Logger initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def set_main_window(self, main_window):
        """
        Définit une référence à la fenêtre principale pour permettre les mises à jour de statut.
        
        Args:
            main_window: Référence à la fenêtre principale
        """
        self.main_window = main_window
    
    def get_main_window(self):
        """
        Retourne la référence à la fenêtre principale.
        
        Returns:
            La référence à la fenêtre principale ou None si elle n'est pas définie
        """
        return self.main_window
    
    def _get_log_level(self, level_name):
        """Convert a level name string to a logging level."""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(level_name.upper(), logging.INFO)
    
    def _setup_console_handler(self):
        """Set up a console handler for the logger."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.console_level)
        
        # Create formatter with emoji support
        formatter = self._create_formatter("%(emoji)s %(message)s")
        console_handler.setFormatter(formatter)
        
        # Add the handler to the logger
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Set up a file handler for the logger."""
        # Create file handler
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(self.file_level)
        
        # Create formatter with emoji support
        formatter = self._create_formatter("%(asctime)s [%(levelname)s] %(emoji)s %(message)s")
        file_handler.setFormatter(formatter)
        
        # Add the handler to the logger
        self.logger.addHandler(file_handler)
    
    def _create_formatter(self, format_str):
        """Create a custom formatter with emoji support."""
        class EmojiFormatter(logging.Formatter):
            def format(self, record):
                # Add emoji based on log level
                emojis = {
                    "DEBUG": "🔍",
                    "INFO": "ℹ️",
                    "SUCCESS": "✅",
                    "WARNING": "⚠️",
                    "ERROR": "❌",
                    "CRITICAL": "🚨"
                }
                record.emoji = emojis.get(record.levelname, "")
                return super().format(record)
        
        return EmojiFormatter(format_str)
    
    def register_callback(self, callback):
        """
        Register a callback function to receive log messages.
        Callback should accept three parameters: timestamp, level, message
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def unregister_callback(self, callback):
        """Remove a previously registered callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def set_level(self, level):
        """Set the logging level."""
        log_level = self._get_log_level(level)
        self.logger.setLevel(log_level)
        for handler in self.logger.handlers:
            handler.setLevel(log_level)
    
    def _notify_callbacks(self, level, message):
        """Notify all registered callbacks about a new log message."""
        timestamp = datetime.now()
        for callback in self.callbacks:
            try:
                callback(timestamp, level, message)
            except Exception as e:
                print(f"Error in log callback: {str(e)}")
    
    def debug(self, message):
        """Log a debug message."""
        self.logger.debug(message)
        self._notify_callbacks("DEBUG", message)
    
    def info(self, message):
        """Log an info message."""
        self.logger.info(message)
        self._notify_callbacks("INFO", message)
    
    def success(self, message):
        """Log a success message (using custom level)."""
        # Create a custom level for success if it doesn't exist
        if not hasattr(logging, "SUCCESS"):
            logging.SUCCESS = 25  # between INFO and WARNING
            logging.addLevelName(logging.SUCCESS, "SUCCESS")
        
        # Log at SUCCESS level
        self.logger.log(logging.SUCCESS, message)
        self._notify_callbacks("SUCCESS", message)
    
    def warning(self, message):
        """Log a warning message."""
        self.logger.warning(message)
        self._notify_callbacks("WARNING", message)
    
    def error(self, message):
        """Log an error message."""
        self.logger.error(message)
        self._notify_callbacks("ERROR", message)
    
    def critical(self, message):
        """Log a critical message."""
        self.logger.critical(message)
        self._notify_callbacks("CRITICAL", message)


def get_logger(name="SwitchMaster"):
    """
    Get an existing logger by name, or create one if it doesn't exist.
    
    Args:
        name (str): Name of the logger
        
    Returns:
        logging.Logger: The requested logger
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up
    if not logger.handlers:
        logger = Logger(name)
    
    return logger


def setup_logger(name="SwitchMaster", log_file="switchmaster.log", level=logging.INFO):
    """
    Set up logger with file handler and emoji formatting.
    
    Args:
        name (str): Logger name
        log_file (str): Log file path
        level (int): Logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    class EmojiFormatter(logging.Formatter):
        def format(self, record):
            # Add emoji based on log level
            emojis = {
                "DEBUG": "🔍",
                "INFO": "ℹ️",
                "SUCCESS": "✅",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "CRITICAL": "🚨"
            }
            record.emoji = emojis.get(record.levelname, "")
            return super().format(record)
    
    formatter = EmojiFormatter('%(asctime)s - %(emoji)s %(levelname)s - %(message)s')
    
    # Create file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Add SUCCESS level
    if not hasattr(logging, "SUCCESS"):
        logging.SUCCESS = 25  # Between INFO and WARNING
        logging.addLevelName(logging.SUCCESS, 'SUCCESS')
    
    # Add success method
    def success(self, message, *args, **kwargs):
        self.log(logging.SUCCESS, message, *args, **kwargs)
    
    if not hasattr(logging.Logger, 'success'):
        logging.Logger.success = success
    
    # Log the logger initialization
    logger.info(f"Logger initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return logger 