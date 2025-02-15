"""Activity log system for tracking and displaying game events."""

from typing import List
from collections import deque
from Core.Events import EventManager, GameEventType
import logging

class ActivityLog:
    _instance = None
    MAX_MESSAGES = 20  # Increased from 10 since we can show more with word wrapping

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ActivityLog, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.messages = deque(maxlen=self.MAX_MESSAGES)
            self.event_manager = EventManager.get_instance()
            self.event_manager.subscribe(GameEventType.COMBAT_ACTION, self._handle_combat)
            self.event_manager.subscribe(GameEventType.ENTITY_DIED, self._handle_death)
            self.logger = logging.getLogger(__name__)
            self._initialized = True

    @staticmethod
    def get_instance():
        if ActivityLog._instance is None:
            ActivityLog()
        return ActivityLog._instance

    def _handle_combat(self, event):
        """Handle combat events and create appropriate messages."""
        attacker = event.attacker.type.name
        defender = event.defender.type.name
        damage = event.damage
        message = f"{attacker} attacks {defender} for {damage} damage!"
        self.logger.debug(f"Adding combat message: {message}")
        self.add_message(message)

    def _handle_death(self, event):
        """Handle entity death events."""
        entity = event.entity.type.name
        message = f"{entity} has been slain!"
        self.logger.debug(f"Adding death message: {message}")
        self.add_message(message)

    def add_message(self, message: str):
        """Add a new message to the log."""
        self.messages.append(message)
        self.logger.debug(f"Current messages after add: {list(self.messages)}")

    def get_messages(self) -> List[str]:
        """Get all current messages."""
        messages = list(self.messages)
        return messages

    def get_display_text(self) -> str:
        """Get formatted text for display."""
        text = "\n".join(self.get_messages())
        return text