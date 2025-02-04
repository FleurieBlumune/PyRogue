"""
Turn-based game management system.
Handles the sequencing and processing of game turns.
"""

import logging
from Core.Events import EventManager, GameEventType

class TurnManager:
    """
    Singleton manager for turn-based game progression.
    
    Coordinates the sequence of turns and notifies the system when turns begin/end.
    Uses the event system to communicate turn state changes.
    
    Attributes:
        event_manager (EventManager): Reference to the game's event management system
        current_turn (int): The current turn number
        logger (Logger): Logger instance for debugging turn progression
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TurnManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.event_manager = EventManager.get_instance()
            self.current_turn = 0
            logging.basicConfig(level=logging.DEBUG)
            self.logger = logging.getLogger(__name__)
            self._initialized = True

    @staticmethod
    def get_instance():
        if TurnManager._instance is None:
            TurnManager()
        return TurnManager._instance

    def start_turn(self):
        """
        Begin processing a new turn.
        
        Increments the turn counter, processes any pending events,
        and emits a TURN_ENDED event when processing is complete.
        """
        self.current_turn += 1
        self.logger.debug(f"Starting turn {self.current_turn}")
        
        # Signal turn start
        self.event_manager.emit(GameEventType.TURN_STARTED, turn_number=self.current_turn)
        
        # Process any immediate events
        self.event_manager.process_events()
        
        # Signal turn end
        self.logger.debug(f"Ending turn {self.current_turn}")
        self.event_manager.emit(GameEventType.TURN_ENDED, turn_number=self.current_turn)
