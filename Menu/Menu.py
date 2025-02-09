"""
Main Menu class for handling menu display and interaction.
"""

from typing import Optional, Any
import pygame
from Menu.MenuItem import MenuItem

class Menu:
    """
    A menu that can display and handle interaction with multiple menu items.
    
    Attributes:
        title (str): The menu's title
        items (list[MenuItem]): List of menu items
        selected_index (int): Index of currently selected item
        font_large (pygame.font.Font): Font for title text
        font_small (pygame.font.Font): Font for menu items
        position (str): Position indicator for special menus like HUD
    """
    
    def __init__(self, 
                 title: str,
                 font_large: pygame.font.Font,
                 font_small: pygame.font.Font,
                 position: str = "center"):
        """
        Initialize a new menu.
        
        Args:
            title: The menu's title
            font_large: Font for title text
            font_small: Font for menu items
            position: Position indicator for special menus like HUD
        """
        self.title = title
        self.items: list[MenuItem] = []
        self.selected_index = 0
        self.font_large = font_large
        self.font_small = font_small
        self.position = position
        
    def add_item(self, item: MenuItem) -> None:
        """Add a menu item to the menu."""
        self.items.append(item)
        
    def handle_input(self, event: pygame.event.Event) -> Optional[Any]:
        """
        Handle input events for the menu.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            Optional[Any]: Result from menu item activation if any
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
            elif event.key == pygame.K_RETURN:
                return self.items[self.selected_index].activate()
            elif event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                item = self.items[self.selected_index]
                if event.key == pygame.K_RIGHT:
                    item.next_value()
                else:
                    item.previous_value()
                if item.callback:
                    return item.callback()
        return None
        
    def render(self, screen: pygame.Surface, width: int, height: int) -> None:
        """
        Render the menu to the screen.
        
        Args:
            screen: The surface to render to
            width: Screen width
            height: Screen height
        """
        if self.position == "top-left":
            self._render_hud(screen, width)
        else:
            self._render_centered(screen, width, height)
            
    def _render_centered(self, screen: pygame.Surface, width: int, height: int) -> None:
        """Render a centered menu with title."""
        # Draw title
        if self.title:
            title_surface = self.font_large.render(self.title, True, (255, 255, 255))
            title_rect = title_surface.get_rect(center=(width // 2, height // 4))
            screen.blit(title_surface, title_rect)
        
        # Draw menu items starting from vertical center
        start_y = height // 2
        for i, item in enumerate(self.items):
            color = (255, 255, 0) if i == self.selected_index else (200, 200, 200)
            text_surface = self.font_small.render(item.get_display_text(), True, color)
            pos = (width // 2, start_y + i * 40)
            rect = text_surface.get_rect(center=pos)
            screen.blit(text_surface, rect)
            
    def _render_hud(self, screen: pygame.Surface, width: int) -> None:
        """
        Render HUD-style menu in top-left corner with background bar.
        
        Args:
            screen: The surface to render to
            width: Screen width
        """
        # Calculate HUD dimensions
        padding = 10
        bar_height = 30  # Height of the black background bar
        
        # Draw black background bar across the screen
        bar_surface = pygame.Surface((width, bar_height))
        bar_surface.fill((0, 0, 0))
        bar_surface.set_alpha(200)  # Make it slightly transparent
        screen.blit(bar_surface, (0, 0))
        
        # Draw HUD items
        x = padding
        y = (bar_height - self.font_small.get_height()) // 2  # Center text vertically in bar
        
        for item in self.items:
            text_surface = self.font_small.render(item.get_display_text(), True, (255, 255, 255))
            screen.blit(text_surface, (x, y))
            x += text_surface.get_width() + padding  # Space items horizontally 