"""Activity log system for tracking and displaying game events."""

from typing import List
from collections import deque
from Core.Events import EventManager, GameEventType
import logging

class ActivityLog:
    _instance = None
    MAX_MESSAGES = 20
    LINES_PER_PAGE = 5  # Number of lines to scroll for page up/down

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
        old_max = len(self.messages)
        self.messages.append(message)
        # If we were scrolled up, adjust offset to maintain position
        if self.scroll_offset > 0:
            self.scroll_offset = min(self.scroll_offset + 1, len(self.messages))
        self.logger.debug(f"Added message. Scroll offset: {self.scroll_offset}. Messages: {list(self.messages)}")

    def scroll(self, amount: int) -> None:
        """
        Scroll the message log by the given amount.
        Positive scrolls up (shows older messages), negative scrolls down.
        
        Args:
            amount (int): Number of lines to scroll. 
                         Positive values scroll up to show older messages.
                         Negative values scroll down to show newer messages.
        """
        # For page up/down, multiply by lines per page
        if abs(amount) >= 5:  # If amount is 5 or more, treat as page scroll
            amount = amount // abs(amount) * self.LINES_PER_PAGE
            
        max_scroll = len(self.messages)
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset + amount))
        self.logger.debug(f"Scrolled log to offset {self.scroll_offset}/{max_scroll}")

    def get_messages(self) -> List[str]:
        """Get all current messages with proper scroll indicators."""
        messages = list(self.messages)
        if not messages:
            return []

        max_scroll = len(messages)
        total_msg = f"Messages ({len(messages)})"
        
        # Add scroll indicators as needed with colors using ANSI-like markup
        if self.scroll_offset > 0:
            messages.append(f"<yellow>▼ {self.scroll_offset} newer messages below ▼</yellow>")
        if self.scroll_offset < max_scroll - 1:
            above_count = max_scroll - self.scroll_offset - self.MAX_MESSAGES
            if above_count > 0:
                messages.insert(0, f"<yellow>▲ {above_count} older messages above ▲</yellow>")
            
        # Insert message count at top
        messages.insert(0, f"<white>{total_msg}</white>")
            
        # Calculate visible range based on scroll position
        visible_start = max(0, max_scroll - self.MAX_MESSAGES - self.scroll_offset)
        visible_end = max_scroll - self.scroll_offset
        
        return messages[visible_start:visible_end]

    def get_display_text(self) -> str:
        """Get formatted text for display."""
        text = "\n".join(self.get_messages())
        return text