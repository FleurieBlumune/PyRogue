"""
Event management system for the game.
Provides a centralized event handling mechanism using a singleton pattern.
Handles both pygame events and custom game events.
"""

import pygame
import logging
from enum import IntEnum
from collections import defaultdict

class GameEventType(IntEnum):
    """Enumeration of custom game events extending pygame's event system."""
    PLAYER_MOVED = pygame.USEREVENT + 1
    ENTITY_MOVED = pygame.USEREVENT + 2
    PLAYER_TURN_ENDED = pygame.USEREVENT + 3
    CAMERA_MOVED = pygame.USEREVENT + 4
    GAME_QUIT = pygame.USEREVENT + 5
    EVENT_QUEUE_PROCESSED = pygame.USEREVENT + 6
    TURN_STARTED = pygame.USEREVENT + 6
    TURN_ENDED = pygame.USEREVENT + 7

class EventManager:
    """
    Singleton event manager that handles both pygame and custom game events.
    
    Provides methods for:
    - Subscribing/unsubscribing to events
    - Processing events from the queue
    - Emitting new events
    
    Attributes:
        subscriptions (defaultdict): Maps event types to lists of handler functions
        quit_handler (callable): Special handler for quit events
        logger (Logger): Logger instance for debugging event flow
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.subscriptions = defaultdict(list)
            self.quit_handler = None
            logging.basicConfig(level=logging.DEBUG)
            self.logger = logging.getLogger(__name__)
            self._initialized = True

    @staticmethod
    def get_instance():
        """Get or create the EventManager instance"""
        if EventManager._instance is None:
            EventManager()
        return EventManager._instance

    def subscribe(self, event_type: int, handler: callable):
        """
        Subscribe a handler function to an event type.

        Args:
            event_type (int): The type of event to subscribe to
            handler (callable): The function to call when event occurs
        """
        self.subscriptions[event_type].append(handler)
        self.logger.debug(f"Subscribed handler {handler.__name__} to event type {event_type}")

    def unsubscribe(self, event_type: int, handler: callable):
        if handler in self.subscriptions[event_type]:
            self.subscriptions[event_type].remove(handler)
            self.logger.debug(f"Unsubscribed handler {handler.__name__} from event type {event_type}")

    def process_events(self) -> bool:
        """
        Process all pending events in the queue.

        Returns:
            bool: True if any events were handled, False otherwise
        """
        events_handled = False
        for event in pygame.event.get():
            self.logger.debug(f"Processing event: {event}, type: {event.type}")
            
            if event.type == pygame.QUIT:
                self.logger.info("Quit event received")
                if self.quit_handler:
                    self.quit_handler(event)
                else:
                    pygame.quit()
                    raise SystemExit
                    
            if event.type in self.subscriptions:
                events_handled = True
                for handler in self.subscriptions[event.type]:
                    try:
                        self.logger.debug(f"Calling handler {handler.__name__} for event {event}")
                        handler(event)
                    except Exception as e:
                        self.logger.error(f"Error in event handler {handler.__name__}: {e}")
        
        return events_handled

    def emit(self, event_type: int, **kwargs):
        """Post events to Pygame's queue"""
        self.logger.debug(f"Emitting event type {event_type} with args {kwargs}")
        try:
            pygame.event.post(pygame.event.Event(event_type, kwargs))
        except Exception as e:
            self.logger.error(f"Error posting event {event_type}: {e}")