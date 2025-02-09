"""
Event management system for the game.
Provides a centralized event handling mechanism using a singleton pattern.
"""

import pygame
import logging
from enum import IntEnum

class GameEventType(IntEnum):
    """Game-specific event types extending pygame's event system"""
    PLAYER_MOVED = pygame.USEREVENT + 1
    ENTITY_MOVED = pygame.USEREVENT + 2
    PLAYER_TURN_ENDED = pygame.USEREVENT + 3
    CAMERA_MOVED = pygame.USEREVENT + 4
    GAME_QUIT = pygame.USEREVENT + 5
    TURN_STARTED = pygame.USEREVENT + 6
    TURN_ENDED = pygame.USEREVENT + 7
    ENTITY_TURN = pygame.USEREVENT + 8
    COMBAT_ACTION = pygame.USEREVENT + 9
    ENTITY_DIED = pygame.USEREVENT + 10

class EventManager:
    """Singleton event manager that handles both pygame and custom game events."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            logging.basicConfig(level=logging.DEBUG)
            self.logger = logging.getLogger(__name__)
            self.subscriptions = {}
            self.quit_handler = None
            self._initialized = True
            self.logger.debug("EventManager initialized")

    @staticmethod
    def get_instance():
        if EventManager._instance is None:
            EventManager()
        return EventManager._instance

    def subscribe(self, event_type: int, handler: callable):
        """Subscribe to an event type with a handler function"""
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []
        self.subscriptions[event_type].append(handler)
        self.logger.debug(f"Subscribed {handler.__name__} to {event_type}")
        self.logger.debug(f"Current subscribers for {event_type}: {[h.__name__ for h in self.subscriptions[event_type]]}")

    def unsubscribe(self, event_type: int, handler: callable):
        """Remove a handler's subscription to an event type"""
        if event_type in self.subscriptions and handler in self.subscriptions[event_type]:
            self.subscriptions[event_type].remove(handler)
            self.logger.debug(f"Unsubscribed {handler.__name__} from {event_type}")

    def process_events(self):
        """Process all pending events"""
        for event in pygame.event.get():
            self.logger.debug(f"Processing event: {event}")
            
            if event.type == pygame.QUIT:
                if self.quit_handler:
                    self.quit_handler(event)
                else:
                    pygame.quit()
                    raise SystemExit
            
            if event.type in self.subscriptions:
                for handler in self.subscriptions[event.type]:
                    try:
                        self.logger.debug(f"Calling handler {handler.__name__} for {event}")
                        handler(event)
                    except Exception as e:
                        self.logger.error(f"Error in handler {handler.__name__}: {e}")

    def emit(self, event_type: int, **kwargs):
        """Emit a new event"""
        self.logger.debug(f"Emitting event {event_type} with {kwargs}")
        event = pygame.event.Event(event_type, kwargs)
        
        # Process ENTITY_TURN events immediately to ensure proper turn order
        if event_type == GameEventType.ENTITY_TURN and event_type in self.subscriptions:
            self.logger.debug("Processing ENTITY_TURN event immediately")
            for handler in self.subscriptions[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error in immediate handler {handler.__name__}: {e}")
            return
            
        try:
            pygame.event.post(event)
        except Exception as e:
            self.logger.error(f"Error posting event {event_type}: {e}")