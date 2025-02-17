"""
Main entry point for the game.
"""

import sys
import traceback
from Engine.Core.GameLoop import GameLoop
from Engine.Core.LogConfig import setup_logging, log_system_info
import logging

def main():
    """Initialize and run the game."""
    try:
        # Set up logging first thing
        logger = setup_logging()
        
        # Log system information for debugging
        log_system_info()
        
        # Create and run game loop
        logger.info("Initializing game loop")
        game = GameLoop()
        logger.info("Starting game loop")
        game.run()
        logger.info("Game loop ended normally")
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.critical(f"Fatal error in main loop: {e}", exc_info=True)
        raise  # Re-raise to trigger sys.excepthook
    finally:
        logging.shutdown()

if __name__ == "__main__":
    main()