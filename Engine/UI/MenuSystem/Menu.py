"""
Base menu class that handles common menu functionality.
"""

import pygame
import pygame_gui
import logging
from typing import List, Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

class Menu:
    """
    Base menu class that provides common menu functionality.
    
    This class handles:
    - Basic menu item management
    - Keyboard navigation
    - Selection highlighting
    - Common event processing
    
    Attributes:
        ui_manager (pygame_gui.UIManager): The UI manager for this menu
        menu_items (list): List of selectable menu items
        selected_index (int): Currently selected menu item index
        width (int): Current menu width
        height (int): Current menu height
    """
    
    def __init__(self, width: int, height: int, theme_path: str):
        """
        Initialize the menu.
        
        Args:
            width (int): Initial menu width
            height (int): Initial menu height
            theme_path (str): Path to the UI theme file
        """
        self.width = width
        self.height = height
        self.ui_manager = pygame_gui.UIManager((width, height), theme_path)
        
        # Initialize menu state
        self.menu_items: List[pygame_gui.core.UIElement] = []
        self.selected_index = 0
        
        # Initialize UI elements
        self._init_gui_elements()
        
    def _init_gui_elements(self):
        """
        Initialize GUI elements. Override in subclasses.
        
        This method should:
        1. Clear existing elements
        2. Create new UI elements
        3. Add elements to menu_items list
        4. Call _update_selection()
        """
        self.ui_manager.clear_and_reset()
        self.menu_items = []
        self.selected_index = 0
        
    def _update_selection(self):
        """Update the visual state of the selected menu item."""
        for i, item in enumerate(self.menu_items):
            if i == self.selected_index:
                # Simulate hover state for the selected item
                item.hovered = True
                if isinstance(item, pygame_gui.elements.UIButton):
                    item.select()
                elif isinstance(item, pygame_gui.elements.UIDropDownMenu):
                    # Custom highlight for dropdown using theme colors
                    item.background_colour = self.ui_manager.get_theme().get_colour('selected_bg')
                    item.text_colour = self.ui_manager.get_theme().get_colour('selected_text')
                    item.border_colour = self.ui_manager.get_theme().get_colour('selected_border')
                    item.rebuild()
            else:
                item.hovered = False
                if isinstance(item, pygame_gui.elements.UIButton):
                    item.unselect()
                elif isinstance(item, pygame_gui.elements.UIDropDownMenu):
                    # Reset dropdown colors using theme colors
                    item.background_colour = self.ui_manager.get_theme().get_colour('normal_bg')
                    item.text_colour = self.ui_manager.get_theme().get_colour('normal_text')
                    item.border_colour = self.ui_manager.get_theme().get_colour('normal_border')
                    item.rebuild()
    
    def _handle_keyboard_navigation(self, event: pygame.event.Event) -> Optional[Tuple[bool, Dict[str, Any]]]:
        """
        Handle keyboard navigation of menu items.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            Optional[Tuple[bool, Dict[str, Any]]]: Menu-specific return value if any
        """
        if event.type == pygame.KEYDOWN:
            # Safety check - if no menu items, can't navigate
            if not self.menu_items:
                return None
                
            old_index = self.selected_index
            # Ensure selected_index is within bounds
            self.selected_index = min(self.selected_index, len(self.menu_items) - 1)
            
            # Handle navigation keys
            if event.key in (pygame.K_UP, pygame.K_KP8):
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            elif event.key in (pygame.K_DOWN, pygame.K_KP2):
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self._handle_selection()
            
            # Update selection if changed
            if old_index != self.selected_index:
                self._update_selection()
                
        return None
    
    def _handle_selection(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Handle selection of the current menu item. Override in subclasses.
        
        Returns:
            Tuple[bool, Dict[str, Any]]: (should_exit, menu_specific_data)
        """
        return False, {}
    
    def handle_input(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Handle all input events.
        
        Returns:
            Tuple[bool, Dict[str, Any]]: (should_exit, menu_specific_data)
        """
        time_delta = pygame.time.Clock().tick(60)/1000.0

        for event in pygame.event.get():
            logger.debug(f"DEBUG: UI Event - {event}")
            if event.type == pygame.QUIT:
                return True, {}
            
            # Handle keyboard navigation
            result = self._handle_keyboard_navigation(event)
            if result is not None:
                return result
            
            # Let UI manager process events
            self.ui_manager.process_events(event)
            
        self.ui_manager.update(time_delta)
        return False, {}
    
    def render(self, screen: pygame.Surface):
        """
        Render the menu.
        
        Args:
            screen: The surface to render to
        """
        screen.fill((0, 0, 0))  # Default background
        self.ui_manager.draw_ui(screen)
        pygame.display.flip() 