"""Activity log system for tracking and displaying game events."""
import pygame
from typing import List
from collections import deque
from Engine.Core.Events import EventManager, GameEventType
from Engine.Core.Utils.GlyphProvider import GlyphProvider
import logging
import re

class ActivityLog:
    _instance = None
    MAX_MESSAGES = 100  # Maximum number of messages to store
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
            self.wrap_width = None
            self.font = None
            self._wrapped_lines = []
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
        self.logger.debug(f"Added message. Total messages: {len(self.messages)}")
        if self.wrap_width is not None and self.font is not None:
            self.reflow_messages()

    def scroll(self, amount: int) -> None:
        """
        Scroll the message log by the given amount.
        Positive scrolls up (shows older messages), negative scrolls down.
        """
        # Convert large scroll amounts to page up/down
        if abs(amount) >= 5:
            amount = (amount // abs(amount)) * self.LINES_PER_PAGE

        # Calculate total lines available for scrolling
        total_lines = len(self._wrapped_lines) if self._wrapped_lines else len(self.messages)
        
        # Calculate maximum possible scroll offset
        max_scroll = max(0, total_lines - self.VISIBLE_MESSAGES)
        
        # Update scroll offset within bounds
        new_offset = self.scroll_offset + amount
        self.scroll_offset = max(0, min(max_scroll, new_offset))
        
        self.logger.debug(f"Scrolled log to offset {self.scroll_offset}/{max_scroll} (amount={amount}, total_lines={total_lines})")

    def get_messages(self) -> List[str]:
        """Get all current messages with proper scroll indicators."""
        messages_to_display = self._wrapped_lines if self._wrapped_lines else list(self.messages)
        if not messages_to_display:
            return ["<white>Messages (0)</white>"]

        total_lines = len(messages_to_display)
        max_scroll = max(0, total_lines - self.VISIBLE_MESSAGES)
        start_idx = max(0, total_lines - self.VISIBLE_MESSAGES - self.scroll_offset)
        end_idx = total_lines - self.scroll_offset

        glyphs = GlyphProvider()
        result = []
        result.append(f"<white>Messages ({len(self.messages)})</white>")

        # Show up arrow if there are messages above
        if start_idx > 0:
            result.append(f"<yellow>{glyphs.get('ARROW_UP')}</yellow>")

        # Add visible messages
        result.extend(messages_to_display[start_idx:end_idx])

        # Show down arrow if there are messages below
        if self.scroll_offset > 0:
            result.append(f"<yellow>{glyphs.get('ARROW_DOWN')}</yellow>")

        return result

    def get_display_text(self) -> str:
        """Get formatted text for display."""
        return "\n".join(self.get_messages())

    def set_wrap_params(self, wrap_width: int, font: 'pygame.font.Font') -> None:
        """Set text wrapping parameters and reflow messages."""
        if wrap_width != self.wrap_width or font != self.font:
            self.logger.debug(f"Setting wrap width to {wrap_width}")
            self.wrap_width = wrap_width
            self.font = font
            self.reflow_messages()

    def reflow_messages(self) -> None:
        """Reflow all messages with current wrap parameters."""
        if self.wrap_width is None or self.font is None:
            self._wrapped_lines = []
            return

        try:
            new_lines = []
            for message in self.messages:
                for line in message.splitlines():
                    wrapped = self._wrap_text(line, self.font, self.wrap_width)
                    if wrapped:
                        new_lines.extend(wrapped)
                    else:
                        new_lines.append("")
            
            # Adjust scroll offset if necessary to maintain relative position
            if self._wrapped_lines:
                old_total = len(self._wrapped_lines)
                new_total = len(new_lines)
                if old_total != new_total and self.scroll_offset > 0:
                    # Adjust scroll offset proportionally
                    self.scroll_offset = min(
                        self.scroll_offset,
                        max(0, new_total - self.VISIBLE_MESSAGES)
                    )
            
            self._wrapped_lines = new_lines
            self.logger.debug(f"Reflowed {len(self.messages)} messages into {len(new_lines)} lines")
        except Exception as e:
            self.logger.error(f"Error reflowing messages: {e}", exc_info=True)

    def _wrap_text(self, text: str, font: 'pygame.font.Font', wrap_width: int) -> list:
        """Wrap text to fit within the given width."""
        try:
            # Handle color markup
            markup_pattern = r'<(\w+)>(.*?)</\w+>'
            match = re.match(markup_pattern, text)
            if match:
                color, text = match.groups()  # Extract both color and text from markup

            words = text.split()
            if not words:
                return [""]

            lines = []
            current_line = words[0]
            for word in words[1:]:
                test_line = current_line + " " + word
                if font.size(test_line)[0] <= wrap_width:
                    current_line = test_line
                else:
                    # Reapply color markup to wrapped lines if it existed
                    if match:
                        lines.append(f"<{color}>{current_line}</{color}>")
                    else:
                        lines.append(current_line)
                    current_line = word

            # Don't forget to add the last line with proper markup
            if match:
                lines.append(f"<{color}>{current_line}</{color}>")
            else:
                lines.append(current_line)
            return lines
        except Exception as e:
            self.logger.error(f"Error wrapping text: {e}", exc_info=True)
            return [text]  # Return original text if wrapping fails 