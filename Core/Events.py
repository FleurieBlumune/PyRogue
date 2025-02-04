import pygame
import logging
from enum import IntEnum
from collections import defaultdict

class GameEventType(IntEnum):
    PLAYER_MOVED = pygame.USEREVENT + 1
    ENTITY_MOVED = pygame.USEREVENT + 2
    PLAYER_TURN_ENDED = pygame.USEREVENT + 3
    CAMERA_MOVED = pygame.USEREVENT + 4
    GAME_QUIT = pygame.USEREVENT + 5
    EVENT_QUEUE_PROCESSED = pygame.USEREVENT + 6
    TURN_STARTED = pygame.USEREVENT + 6
    TURN_ENDED = pygame.USEREVENT + 7

class EventManager:
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
        """Subscribe to pygame event types or our GameEventType"""
        self.subscriptions[event_type].append(handler)
        self.logger.debug(f"Subscribed handler {handler.__name__} to event type {event_type}")

    def unsubscribe(self, event_type: int, handler: callable):
        if handler in self.subscriptions[event_type]:
            self.subscriptions[event_type].remove(handler)
            self.logger.debug(f"Unsubscribed handler {handler.__name__} from event type {event_type}")

    def process_events(self) -> bool:
        """Process all pending events and return True if any events were handled"""
        events_handled = False
        for event in pygame.event.get():
            self.logger.debug(f"Processing event: {event}")
            
            if event.type == GameEventType.GAME_QUIT:
                self.logger.info("Quit event received")
                if self.quit_handler:
                    self.quit_handler(event)
                else:
                    pygame.quit()
                    raise SystemExit
                    
            if event.type in self.subscriptions:
                events_handled = True
                for handler in self.subscriptions[event.type]:
                    self.logger.debug(f"Calling handler {handler.__name__} for event {event}")
                    handler(event)
        
        if events_handled:
            self.emit(GameEventType.EVENT_QUEUE_PROCESSED)
            
        return events_handled

    def emit(self, event_type: int, **kwargs):
        """Post events to Pygame's queue"""
        self.logger.debug(f"Emitting event type {event_type} with args {kwargs}")
        pygame.event.post(pygame.event.Event(event_type, kwargs))