"""
Centralized logging configuration for all modules
"""
import logging
import logging.handlers
import os
from pathlib import Path

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / "invoiceai.log"


def get_logger(module_name: str) -> logging.Logger:
    """
    Get a configured logger for a module.
    
    Args:
        module_name: Name of the module (__name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(module_name)
    
    # Only add handlers if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler with color-like formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotating backup
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                LOG_FILE,
                maxBytes=10_000_000,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not set up file logging: {e}")
    
    return logger
