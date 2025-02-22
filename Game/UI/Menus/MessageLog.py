"""Activity log system for tracking and displaying game events using pygame-gui."""
import pygame
import pygame_gui
from pygame_gui.elements import UIWindow
from typing import List, Optional
from collections import deque
from Engine.Core.Events import EventManager, GameEventType
import logging
from datetime import datetime

class MessageLog(UIWindow):
    """
    Game message log that displays combat and other game events.
    Uses pygame-gui for rendering and supports HTML formatting.
    
    Attributes:
        MAX_MESSAGES (int): Maximum number of messages to store
        messages (deque): Queue of messages with maximum size
        ui_manager (pygame_gui.UIManager): The UI manager instance
        text_box (pygame_gui.elements.UITextBox): The text box element
    """
    
    MAX_MESSAGES = 100  # Maximum number of messages to store
    
    def __init__(self, ui_manager: pygame_gui.UIManager, rect: pygame.Rect):
        """
        Initialize the message log.
        
        Args:
            ui_manager: The pygame-gui UI manager
            rect: Rectangle defining the log's position and size
        """
        super().__init__(
            rect,
            ui_manager,
            window_display_title="Activity Log",
            object_id="#message_log",
            resizable=True,
            draggable=False
        )
        
        self.messages = deque(maxlen=self.MAX_MESSAGES)
        self.ui_manager = ui_manager
        self.text_box = None
        self.event_manager = EventManager.get_instance()
        self.logger = logging.getLogger(__name__)
        
        # Subscribe to game events
        self.event_manager.subscribe(GameEventType.COMBAT_ACTION, self._handle_combat)
        self.event_manager.subscribe(GameEventType.ENTITY_DIED, self._handle_death)
        
        # Initialize UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components."""
        # Create text box with initial header
        container_rect = pygame.Rect(0, 0, self.rect.width - 32, self.rect.height - 20)
        self.text_box = pygame_gui.elements.UITextBox(
            html_text=self._get_header(),
            relative_rect=container_rect,
            manager=self.ui_manager,
            container=self,
            object_id="#message_log_text"
        )
        
        # Add existing messages if any
        for message in self.messages:
            self._append_formatted_message(message)
            
        # Scroll to bottom
        if self.text_box is not None:
            self.text_box.scroll_position = len(self.text_box.html_text.split('\n')) * 10
    
    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handle window events, preventing dragging while allowing resizing.
        
        Args:
            event: The event to process
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return super().process_event(event)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return super().process_event(event)
        elif event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                return super().process_event(event)
                
        return False
        
    def _get_header(self) -> str:
        """Get the formatted header for the message log."""
        return (
            '<div style="background-color: #000000; padding: 5px; '
            'border-bottom: 1px solid #404040; margin-bottom: 5px; text-align: center;">'
            f'{len(self.messages)} Messages'
            '</div>'
        )
        
    def _format_message(self, message: str, message_type: str = "info") -> str:
        """
        Format a message with timestamp and type-specific styling.
        
        Args:
            message: The message to format
            message_type: Type of message for styling ("info", "combat", "death", etc.)
            
        Returns:
            str: HTML formatted message
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        return (
            f'<div class="message {message_type}">'
            f'<span class="timestamp">[{timestamp}]</span> '
            f'<span class="content">{message}</span>'
            f'</div>'
        )
        
    def _append_formatted_message(self, message: str, message_type: str = "info"):
        """Append a formatted message to the text box."""
        if self.text_box is not None:
            formatted = self._format_message(message, message_type)
            self.text_box.append_html_text(formatted)
            # Scroll to bottom
            self.text_box.scroll_position = len(self.text_box.html_text.split('\n')) * 10
            
    def add_message(self, message: str, message_type: str = "info"):
        """
        Add a new message to the log.
        
        Args:
            message: The message to add
            message_type: Type of message for styling
        """
        self.messages.append(message)
        self.logger.debug(f"Added message. Total messages: {len(self.messages)}")
        self._append_formatted_message(message, message_type)
        
        # Update message count in header
        if self.text_box is not None:
            old_header = self.text_box.html_text.split('\n')[0]
            new_header = self._get_header()
            self.text_box.html_text = self.text_box.html_text.replace(old_header, new_header)
            self.text_box.rebuild()
            
    def _handle_combat(self, event):
        """Handle combat events and create appropriate messages."""
        attacker = event.attacker.type.name
        defender = event.defender.type.name
        damage = event.damage
        message = f"{attacker} attacks {defender} for {damage} damage!"
        self.add_message(message, "combat")
            
    def _handle_death(self, event):
        """Handle entity death events."""
        entity = event.entity.type.name
        message = f"{entity} has been slain!"
        self.add_message(message, "death")
            
    def resize(self, rect: pygame.Rect):
        """
        Resize the message log.
        
        Args:
            rect: New rectangle defining position and size
        """
        # Store old dimensions
        old_width = self.rect.width
        old_height = self.rect.height
        
        # Update window dimensions
        super().set_dimensions(rect.size)
        
        # Update text box dimensions if it exists
        if self.text_box is not None:
            new_width = rect.width - 32  # Account for window borders
            new_height = rect.height - 20  # Account for title bar
            self.text_box.set_dimensions((new_width, new_height))
            
            # Trigger a rebuild of the text box to properly reflow text
            self.text_box.rebuild()
            
        # Notify the event manager about the resize
        self.event_manager.emit(
            GameEventType.WINDOW_RESIZED,
            old_width=old_width,
            old_height=old_height,
            new_width=rect.width,
            new_height=rect.height
        )
            
    def clear(self):
        """Clear all messages from the log."""
        self.messages.clear()
        if self.text_box is not None:
            self.text_box.html_text = self._get_header()
            self.text_box.rebuild()
            
    def get_visible_messages(self) -> List[str]:
        """Get the list of currently visible messages."""
        return list(self.messages) 