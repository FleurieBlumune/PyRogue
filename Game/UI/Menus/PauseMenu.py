"""
Pause menu implementation.
"""

import pygame
from Engine.UI.MenuSystem.MenuTypes import MenuID
from Game.UI.Menus.MenuConfigs import MENU_CONFIGS

class PauseMenu:
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
        self.window_surface = window_surface
        self.config = MENU_CONFIGS[MenuID.PAUSE]
        self.is_visible = False
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 48)
        self.menu_font = pygame.font.Font(None, 36)
        
        # Menu state
        self.selected_item = 0
        self.menu_items = self.config["Items"]
        
        # Create overlay surface
        self.overlay = pygame.Surface(window_surface.get_size(), pygame.SRCALPHA)
        
    def draw(self):
        """Draw the pause menu if visible."""
        if not self.is_visible:
            return
            
        # Draw semi-transparent overlay
        self.overlay.fill(self.BACKGROUND_COLOR)
        self.window_surface.blit(self.overlay, (0, 0))
        
        # Draw title
        title_surface = self.title_font.render(self.config["Title"], True, self.TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(self.window_surface.get_width() // 2, 200))
        self.window_surface.blit(title_surface, title_rect)
        
        # Draw menu items
        for i, item in enumerate(self.menu_items):
            color = self.SELECTED_COLOR if i == self.selected_item else self.TEXT_COLOR
            text_surface = self.menu_font.render(item["Text"], True, color)
            text_rect = text_surface.get_rect(center=(self.window_surface.get_width() // 2, 300 + i * 50))
            self.window_surface.blit(text_surface, text_rect)
    
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