"""
Generic popup menu implementation using pygame-gui.
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow
from typing import List, Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PopupMenu(UIWindow):
    """
    A generic popup menu that can be used to display a list of options.
    
    Attributes:
        options (List[str]): List of options to display
        callback (Callable[[str], None]): Function to call when an option is selected
        selected_index (int): Currently selected option index
        option_buttons (List[pygame_gui.elements.UIButton]): List of option buttons
        on_close (Callable[[], None]): Function to call when popup is closed
    """
    
    def __init__(self, 
                 rect: pygame.Rect,
                 options: List[str],
                 callback: Callable[[str], None],
                 manager: pygame_gui.UIManager,
                 on_close: Callable[[], None],
                 window_title: str = "Select an Option",
                 object_id: Optional[str] = None):
        """
        Initialize the popup menu.
        
        Args:
            rect: The rectangle defining the popup's position and size
            options: List of options to display
            callback: Function to call when an option is selected
            manager: The UI manager
            on_close: Function to call when popup is closed
            window_title: Title of the popup window
            object_id: Optional object ID for theming
        """
        super().__init__(rect, manager, 
                        window_title,
                        object_id=object_id,
                        resizable=False)
                        
        self.options = options
        self.callback = callback
        self.on_close = on_close
        self.selected_index = 0
        self.option_buttons = []
        
        # Create container for options
        self.options_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((0, 0), (rect.width - 32, rect.height - 50)),
            manager=manager,
            container=self,
            anchors={'left': 'left',
                    'right': 'right',
                    'top': 'top',
                    'bottom': 'bottom'}
        )
        
        # Create buttons for each option
        button_height = 30
        for i, option in enumerate(options):
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((0, i * (button_height + 5)), 
                                        (rect.width - 50, button_height)),
                text=option,
                manager=manager,
                container=self.options_container,
                object_id=f"#option_button_{i}"
            )
            self.option_buttons.append(button)
            
        # Update initial selection
        self._update_selection()
        
    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handle events for the popup menu.
        
        Args:
            event: The event to process
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        handled = super().process_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_KP8):
                self.selected_index = (self.selected_index - 1) % len(self.options)
                self._update_selection()
                return True
            elif event.key in (pygame.K_DOWN, pygame.K_KP2):
                self.selected_index = (self.selected_index + 1) % len(self.options)
                self._update_selection()
                return True
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._handle_selection()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.close()
                return True
                
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element in self.option_buttons:
                    self.selected_index = self.option_buttons.index(event.ui_element)
                    self._handle_selection()
                    return True
                    
        return handled
        
    def _update_selection(self):
        """Update the visual state of the selected option."""
        for i, button in enumerate(self.option_buttons):
            if i == self.selected_index:
                button.select()
            else:
                button.unselect()
                
    def _handle_selection(self):
        """Handle selection of the current option."""
        if 0 <= self.selected_index < len(self.options):
            selected_option = self.options[self.selected_index]
            self.callback(selected_option)
            self.close()
            
    def close(self):
        """Close the popup and notify the parent."""
        self.kill()
        self.on_close() 