"""
Logging configuration
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """Setup application logging"""
    
    # Create handlers list
    handlers = [logging.StreamHandler(sys.stdout)]
    
    # Try to add file handler if possible
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Add file handler with rotation
        file_handler = RotatingFileHandler(
            "logs/app.log",
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        handlers.append(file_handler)
    except (PermissionError, OSError) as e:
        print(f"Warning: Cannot create log file, using console only: {e}")
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers
    )
    
    # Set specific log levels for different modules
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("google").setLevel(logging.WARNING)
    
    # Application logger
    logger = logging.getLogger("mini_asistente_qa")
    logger.setLevel(logging.INFO)
    
    return logger
