"""Activity log system for tracking and displaying game events."""

from typing import List
from collections import deque
from Core.Events import EventManager, GameEventType
from Core.GlyphProvider import GlyphProvider
import logging

class ActivityLog:
    _instance = None
    MAX_MESSAGES = 100  # Increased to store more message history
    LINES_PER_PAGE = 5  # Number of lines to scroll for page up/down
    VISIBLE_MESSAGES = 20  # Number of messages to show at once

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
            self.scroll_offset = 0  # Number of lines scrolled up from bottom
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
        # Adjust scroll offset to maintain position when viewing history
        if self.scroll_offset > 0:
            self.scroll_offset += 1
        self.logger.debug(f"Added message. Scroll offset: {self.scroll_offset}. Total messages: {len(self.messages)}")

    def scroll(self, amount: int) -> None:
        """
        Scroll the message log by the given amount.
        Positive scrolls up (shows older messages), negative scrolls down.
        """
        # For page up/down, multiply by lines per page
        if abs(amount) >= 5:  # If amount is 5 or more, treat as page scroll
            amount = amount // abs(amount) * self.LINES_PER_PAGE

        # Calculate maximum scroll based on message count
        max_scroll = max(0, len(self.messages) - self.VISIBLE_MESSAGES)
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset + amount))
        self.logger.debug(f"Scrolled log to offset {self.scroll_offset}/{max_scroll}")

    def get_messages(self) -> List[str]:
        """Get all current messages with proper scroll indicators."""
        messages = list(self.messages)
        if not messages:
            return []

        # Calculate total messages and visible range
        total_messages = len(messages)
        max_scroll = max(0, total_messages - self.VISIBLE_MESSAGES)
        start_idx = max(0, total_messages - self.VISIBLE_MESSAGES - self.scroll_offset)
        end_idx = total_messages - self.scroll_offset

        glyphs = GlyphProvider.get_instance()
        
        # Add scroll indicators and message count
        result = []
        result.append(f"<white>Messages ({total_messages})</white>")

        # Show indicator for messages above
        if start_idx > 0:
            result.append(f"<yellow>{glyphs.get('ARROW_UP')}</yellow>")  # Use Unicode by default

        # Add visible messages
        result.extend(messages[start_idx:end_idx])

        # Show indicator for messages below
        remaining_below = self.scroll_offset
        if remaining_below > 0:
            result.append(f"<yellow>{glyphs.get('ARROW_DOWN')}</yellow>")  # Use Unicode by default

        return result

    def get_display_text(self) -> str:
        """Get formatted text for display."""
        text = "\n".join(self.get_messages())
        return text