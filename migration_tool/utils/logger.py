"""
Logging configuration for the application.
"""

import logging
from .config import LOG_FILE

def setup_logger() -> logging.Logger:
    """
    Sets up and returns the application logger.
    The logger writes to a file in the temporary directory.
    """
    logger = logging.getLogger("MigrationTool")
    
    # Check if handlers are already set up to avoid duplicate logs in interactive environments
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Create file handler
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler for debugging during development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

# Create a singleton logger instance to be imported by other modules
logger = setup_logger()
