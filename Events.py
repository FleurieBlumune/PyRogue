from enum import Enum, auto
from typing import Any, Callable, Dict, List
from dataclasses import dataclass

class EventType(Enum):
    PLAYER_MOVED = auto()
    ENTITY_MOVED = auto()
    PLAYER_TURN_ENDED = auto()
    CAMERA_MOVED = auto()
    GAME_QUIT = auto()

@dataclass
class Event:
    type: EventType
    data: Dict[str, Any] = None

class EventManager:
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable[[Event], None]]] = {}
        
    def subscribe(self, event_type: EventType, listener: Callable[[Event], None]) -> None:
        """Subscribe a listener to an event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
    
    def unsubscribe(self, event_type: EventType, listener: Callable[[Event], None]) -> None:
        """Unsubscribe a listener from an event type."""
        if event_type in self._listeners and listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)
    
    def emit(self, event: Event) -> None:
        """Emit an event to all subscribed listeners."""
        if event.type in self._listeners:
            for listener in self._listeners[event.type]:
                listener(event)
