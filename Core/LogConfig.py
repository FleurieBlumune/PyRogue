"""
Centralized logging configuration for the game.

This module sets up logging with the following features:
- File and console output
- Timestamps and source information
- Exception tracking
- Different log levels for different components
"""

import logging
import logging.handlers
import sys
import os
import traceback
from pathlib import Path
from datetime import datetime
import pygame

def setup_logging(log_level=logging.DEBUG):
    """
    Set up logging configuration for the entire application.
    
    Args:
        log_level: The base logging level to use
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create a new log file for each session with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"pyrogue_{timestamp}.log"
    
    # Create formatters with more detailed information
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)-8s | %(name)-20s | %(message)s'
    )
    
    # Set up file handler with immediate flush and UTF-8 encoding
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        delay=False,  # Open the file immediately
        encoding='utf-8'  # Force UTF-8 encoding
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Set up console handler with UTF-8 encoding
    # Use sys.stdout.reconfigure() to ensure UTF-8 encoding
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific levels for different modules
    logging.getLogger('pygame').setLevel(logging.DEBUG)
    logging.getLogger('Core').setLevel(logging.DEBUG)
    logging.getLogger('Menu').setLevel(logging.DEBUG)
    logging.getLogger('Zone').setLevel(logging.INFO)
    logging.getLogger('Entity').setLevel(logging.INFO)
    
    # Set up exception hook
    sys.excepthook = handle_exception
    
    # Log initial startup message
    root_logger.info(f"Starting new session, logging to {log_file}")
    
    return root_logger

def log_system_info():
    """Log system information for debugging purposes."""
    logger = logging.getLogger(__name__)
    
    try:
        import platform
        
        logger.info("System Information:")
        logger.info(f"OS: {platform.system()} {platform.release()}")
        logger.info(f"Python: {sys.version}")
        
        # Only try to get pygame info if display is initialized
        if pygame.display.get_init():
            logger.info(f"Pygame: {pygame.version.ver}")
            logger.info(f"Display Driver: {pygame.display.get_driver()}")
            logger.info(f"Display Info: {pygame.display.Info().__dict__}")
            logger.info(f"Available display modes: {pygame.display.list_modes()}")
        else:
            logger.info("Pygame display not yet initialized")
            
    except Exception as e:
        logger.error(f"Error collecting system info: {e}", exc_info=True)

def log_display_state():
    """Log current state of the pygame display system."""
    logger = logging.getLogger(__name__)
    
    try:
        if not pygame.display.get_init():
            logger.warning("Display system not initialized")
            return
            
        logger.debug("=== Display State ===")
        
        # Get current display surface size
        surface = pygame.display.get_surface()
        if surface:
            current_mode = surface.get_size()
            logger.debug(f"Current surface size: {current_mode}")
            logger.debug(f"Surface flags: {surface.get_flags()}")
        else:
            logger.debug("No active display surface")
            
        logger.debug(f"Display driver: {pygame.display.get_driver()}")
        
        # Get display info
        try:
            info = pygame.display.Info()
            info_dict = {
                'width': info.current_w,
                'height': info.current_h,
                'hw_available': bool(info.hw),
                'wm_available': bool(info.wm),
                'video_mem': getattr(info, 'video_mem', 'unknown')
            }
            logger.debug(f"Display info: {info_dict}")
        except Exception as e:
            logger.warning(f"Could not get display info: {e}")
        
        # Get available fullscreen modes
        try:
            modes = pygame.display.list_modes()
            if modes:
                logger.debug(f"Available fullscreen modes: {modes}")
            else:
                logger.debug("No fullscreen modes reported")
        except Exception as e:
            logger.debug(f"Could not get available display modes: {e}")
            
        logger.debug("===================")
        
    except Exception as e:
        logger.error(f"Error getting display state: {e}", exc_info=True)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions with detailed pygame state logging."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Call the default handler for KeyboardInterrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    logger = logging.getLogger(__name__)
    
    # Get the full stack trace
    stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Log with critical level
    logger.critical(f"Uncaught exception: {exc_type.__name__}: {exc_value}")
    logger.critical(f"Stack trace:\n{stack_trace}")
    
    # Try to get additional pygame info if available
    try:
        if pygame.display.get_init():
            surface = pygame.display.get_surface()
            if surface:
                logger.critical(f"Active display surface size: {surface.get_size()}")
                logger.critical(f"Surface flags: {surface.get_flags()}")
            
            info = pygame.display.Info()
            info_dict = {
                'width': info.current_w,
                'height': info.current_h,
                'hw_available': bool(info.hw),
                'wm_available': bool(info.wm)
            }
            logger.critical(f"Display info at crash: {info_dict}")
            logger.critical(f"Display driver: {pygame.display.get_driver()}")
    except Exception as e:
        logger.critical(f"Could not get pygame display info at crash: {e}")
        
    # Log with critical level
    logger.critical(f"Uncaught exception: {exc_type.__name__}: {exc_value}")
    logger.critical(f"Stack trace:\n{stack_trace}")
    
    # Try to get additional pygame info if available
    try:
        if pygame.display.get_init():
            display_info = pygame.display.Info()
            logger.critical(f"Pygame display info at crash:\n{display_info.__dict__}")
            logger.critical(f"Current display mode: {pygame.display.get_mode()}")
            logger.critical(f"Display driver: {pygame.display.get_driver()}")
    except:
        logger.critical("Could not get pygame display info at crash") 