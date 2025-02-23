"""
Pause menu implementation.
"""

import pygame
import logging
from Engine.UI.MenuSystem.Menu import Menu
from Engine.UI.MenuSystem.MenuTypes import MenuID
from Game.UI.Menus.MenuConfigs import MENU_CONFIGS

logger = logging.getLogger(__name__)

class PauseMenu(Menu):
    """
    Implements a simple pause menu that can be toggled with ESC.
    """
    
    # Color constants
    BACKGROUND_COLOR = (0, 0, 0, 128)  # Semi-transparent black
    TEXT_COLOR = (255, 255, 255)
    SELECTED_COLOR = (100, 100, 255)
    
    def __init__(self, window_surface: pygame.Surface):
        """
        Initialize the pause menu.
        
        Args:
            window_surface: The main game window surface
        """
        config = MENU_CONFIGS[MenuID.PAUSE]
        super().__init__(
            title=config["Title"],
            font_large=pygame.font.Font(None, 48),
            font_small=pygame.font.Font(None, 36),
            position="center"
        )
        
        self.window_surface = window_surface
        self.config = config
        self.is_visible = False
        
        # Menu state
        self.selected_item = 0
        self.menu_items = self.config["Items"]
        
        # Update dimensions based on window size
        self.update_dimensions()
        
    def update_dimensions(self):
        """Update menu dimensions based on window size."""
        screen_width = self.window_surface.get_width()
        screen_height = self.window_surface.get_height()
        self._update_dimensions_from_size(screen_width, screen_height)
        
    def _update_dimensions_from_size(self, width: int, height: int):
        """Update dimensions based on provided width and height."""
        self.window_width = width
        self.window_height = height
        
        # Calculate vertical centering
        total_items = len(self.menu_items)
        total_height = 60 + (total_items * 50)  # Title (48px) + spacing (12px) + (items * spacing)
        center_y = height // 2
        
        # Calculate positions relative to center
        self.title_y = center_y - (total_height // 2)
        self.first_item_y = self.title_y + 60  # Title height + spacing
        self.item_spacing = 50

    def show(self):
        """Show the pause menu."""
        self.is_visible = True
        self.selected_item = 0
    
    def hide(self):
        """Hide the pause menu."""
        self.is_visible = False
    
    def toggle(self):
        """Toggle the visibility of the pause menu."""
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def handle_event(self, event: pygame.event.Event) -> tuple[bool, str]:
        """
        Handle pygame events for the pause menu.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            tuple[bool, str]: (event_handled, action_to_take)
                action_to_take can be: "", "RESUME", "QUIT"
        """
        # If menu is not visible, only handle ESC to show it
        if not self.is_visible:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.show()
                return True, ""
            return False, ""
        
        # Handle window resize
        if event.type == pygame.VIDEORESIZE:
            self.update_dimensions()
            return True, ""
        
        # If menu is visible, handle navigation and actions
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True, "RESUME"
            elif event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                return True, ""
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                return True, ""
            elif event.key == pygame.K_RETURN:
                action = self.menu_items[self.selected_item]["Action"]
                if action == "ResumeGame":
                    self.hide()
                    return True, "RESUME"
                elif action == "QuitToMain":
                    return True, "QUIT"
                
        return False, ""

    def render(self, screen: pygame.Surface, width: int, height: int) -> None:
        """
        Render the pause menu.
        
        Args:
            screen: The surface to render to
            width: Screen width
            height: Screen height
        """
        if not self.is_visible:
            return
            
        # Update dimensions based on current screen size
        self._update_dimensions_from_size(width, height)
            
        # Create overlay surface
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill(self.BACKGROUND_COLOR)
        screen.blit(overlay, (0, 0))
        
        # Draw title
        title_surface = self.font_large.render(self.config["Title"], True, self.TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(width // 2, self.title_y))
        screen.blit(title_surface, title_rect)
        
        # Draw menu items
        for i, item in enumerate(self.menu_items):
            color = self.SELECTED_COLOR if i == self.selected_item else self.TEXT_COLOR
            text_surface = self.font_small.render(item["Text"], True, color)
            text_rect = text_surface.get_rect(center=(width // 2, self.first_item_y + i * self.item_spacing))
            screen.blit(text_surface, text_rect) 