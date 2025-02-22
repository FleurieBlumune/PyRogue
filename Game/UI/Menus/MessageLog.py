"""Activity log system for tracking and displaying game events using pygame-gui."""
import pygame
import pygame_gui
from typing import List
from collections import deque
from Engine.Core.Events import EventManager, GameEventType
import logging

class ActivityLog:
    _instance = None
    MAX_MESSAGES = 100  # Maximum number of messages to store
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
            self.ui_manager = None
            self.text_box = None
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
        if self.text_box is not None:
            self.text_box.append_html_text(f"<br>{message}")
            # Scroll to bottom
            self.text_box.scroll_to_bottom()

    def initialize_ui(self, ui_manager: pygame_gui.UIManager, rect: pygame.Rect):
        """Initialize the UI components."""
        self.ui_manager = ui_manager
        
        # Create text box for messages
        self.text_box = pygame_gui.elements.UITextBox(
            html_text=f"<b>Activity Log ({len(self.messages)} messages)</b><br>",
            relative_rect=rect,
            manager=ui_manager,
            object_id="#message_log"
        )
        
        # Add existing messages
        for message in self.messages:
            self.text_box.append_html_text(f"<br>{message}")
        
        # Scroll to bottom
        self.text_box.scroll_to_bottom()

    def resize(self, rect: pygame.Rect):
        """Resize the message log."""
        if self.text_box is not None:
            self.text_box.kill()
            self.initialize_ui(self.ui_manager, rect) 