"""
Main Menu class for handling menu display and interaction.
"""

from typing import Optional, Any, Dict, Set, Tuple, List
import pygame
from Menu.MenuItem import MenuItem
from Menu.MenuTypes import MenuItemType  # Add direct import for consistency
import re

class Menu:
    # Track occupied screen regions across all menus
    _reserved_regions: Set[str] = set()
    
    # Define colors for markup and UI elements
    COLORS = {
        'white': (255, 255, 255),
        'yellow': (255, 255, 0),
        'gray': (200, 200, 200),
        'scrollbar_track': (40, 40, 40),
        'scrollbar_handle': (100, 100, 100),
        'scrollbar_handle_hover': (150, 150, 150),
        'scrollbar_handle_drag': (200, 200, 200)
    }
    
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
        
        # Register this menu's region
        Menu._reserved_regions.add(position)
        
        self.dragging_scrollbar = False
        self.scrollbar_hover = False
        self.scrollbar_rect = None
        self.scrollbar_track_rect = None
        
    def __del__(self):
        """Clean up by removing this menu's region when destroyed."""
        Menu._reserved_regions.discard(self.position)
        
    @classmethod
    def get_reserved_height(cls, position: str) -> int:
        """Get the height reserved by menus in a given position."""
        if position == "top-left" and "top-left" in cls._reserved_regions:
            return 30  # HUD bar height
        return 0

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
        # Update scrollbar hover state
        if self.scrollbar_rect and event.type == pygame.MOUSEMOTION:
            self.scrollbar_hover = self.scrollbar_rect.collidepoint(event.pos)

        # Handle scrollbar dragging in activity log
        if self.position == "right":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if click was on scrollbar
                if self.scrollbar_rect and self.scrollbar_rect.collidepoint(event.pos):
                    self.dragging_scrollbar = True
                    return None
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_scrollbar = False
            elif event.type == pygame.MOUSEMOTION and self.dragging_scrollbar:
                # Calculate new scroll position based on mouse position
                if self.scrollbar_rect and len(self.items) > 0:
                    item = self.items[0]  # Activity log is always first item
                    if hasattr(item.value_getter, 'scroll'):
                        # Calculate relative position in scroll area
                        total_height = self.scrollbar_track_rect.height
                        relative_y = event.pos[1] - self.scrollbar_track_rect.top
                        scroll_ratio = max(0, min(1, relative_y / total_height))
                        # Convert to message index
                        max_scroll = len(item.value_getter.messages)
                        new_scroll = int(max_scroll * scroll_ratio)
                        # Update scroll position
                        current_scroll = item.value_getter.scroll_offset
                        if new_scroll != current_scroll:
                            item.value_getter.scroll(new_scroll - current_scroll)
                        return None

        # Handle activity log scrolling if this is the activity log menu
        if self.position == "right" and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                item = self.items[self.selected_index]
                if item.type == MenuItemType.LOG and hasattr(item.value_getter, 'scroll'):
                    scroll_direction = 1 if event.key == pygame.K_UP else -1
                    # Check for shift modifier for page scrolling
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        scroll_amount = scroll_direction * 5  # Page scroll
                    else:
                        scroll_amount = scroll_direction  # Line scroll
                    item.value_getter.scroll(scroll_amount)
                return None
            elif event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                item = self.items[self.selected_index]
                if item.type == MenuItemType.LOG and hasattr(item.value_getter, 'scroll'):
                    scroll_amount = 5 if event.key == pygame.K_PAGEUP else -5
                    item.value_getter.scroll(scroll_amount)
                return None

        # Handle regular menu input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.position != "right":
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif event.key == pygame.K_DOWN and self.position != "right":
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
        elif self.position == "right":
            self._render_right(screen, width, height)
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
            
    def _render_right(self, screen: pygame.Surface, width: int, height: int) -> None:
        """
        Render a right-aligned menu for logs and similar content.
        
        Args:
            screen: The surface to render to
            width: Screen width
            height: Screen height
        """
        padding = 10
        log_width = width // 3  # Take up 1/3 of the screen width instead of 1/4
        x = width - log_width - padding
        
        # Adjust starting y position based on other menus
        y = padding + self.get_reserved_height("top-left")  # Account for HUD height if present
        
        # Draw semi-transparent background from adjusted y position
        log_height = height - 2 * padding - y
        log_surface = pygame.Surface((log_width, log_height))
        log_surface.fill((0, 0, 0))
        log_surface.set_alpha(180)
        screen.blit(log_surface, (x, y))
        
        # Calculate maximum y position for text
        max_y = y + log_height - padding
        
        # Draw title if present
        if self.title:
            title_surface = self.font_small.render(self.title, True, (255, 255, 255))
            title_rect = title_surface.get_rect(midtop=(x + log_width//2, y + padding))
            screen.blit(title_surface, title_rect)
            y = title_rect.bottom + padding
        
        # Draw log items with word wrapping
        wrap_width = log_width - 2 * padding - 12  # Account for scrollbar width + padding
        
        for item in self.items:
            display_text = item.get_display_text()
            # Split text into lines
            lines = display_text.split('\n')
            total_lines = len(lines)
            
            # Draw scrollbar if we have scrollable content
            if total_lines > 0 and hasattr(item.value_getter, 'scroll_offset'):
                scrollbar_width = 8
                content_height = total_lines * self.font_small.get_linesize()
                
                if content_height > log_height:
                    # Calculate scrollbar dimensions and position
                    scrollbar_height = max(40, log_height * (log_height / content_height))
                    max_scroll = len(item.value_getter.messages)
                    scroll_progress = item.value_getter.scroll_offset / max_scroll if max_scroll > 0 else 0
                    scrollbar_y = y + (log_height - scrollbar_height) * scroll_progress
                    
                    # Store scrollbar rects for hit detection
                    self.scrollbar_track_rect = pygame.Rect(
                        x + log_width - scrollbar_width - padding, y,
                        scrollbar_width, log_height
                    )
                    self.scrollbar_rect = pygame.Rect(
                        x + log_width - scrollbar_width - padding, scrollbar_y,
                        scrollbar_width, scrollbar_height
                    )
                    
                    # Draw scrollbar track with rounded corners
                    track_color = self.COLORS['scrollbar_track']
                    pygame.draw.rect(screen, track_color, self.scrollbar_track_rect, 
                                   border_radius=4)
                    
                    # Draw scrollbar handle with hover/drag effects and rounded corners
                    if self.dragging_scrollbar:
                        handle_color = self.COLORS['scrollbar_handle_drag']
                    elif self.scrollbar_hover:
                        handle_color = self.COLORS['scrollbar_handle_hover']
                    else:
                        handle_color = self.COLORS['scrollbar_handle']
                        
                    # Draw handle with a slight glow effect when dragging
                    if self.dragging_scrollbar:
                        glow_rect = self.scrollbar_rect.inflate(4, 4)
                        pygame.draw.rect(screen, (handle_color[0]//2, handle_color[1]//2, handle_color[2]//2), 
                                       glow_rect, border_radius=6)
                    
                    pygame.draw.rect(screen, handle_color, self.scrollbar_rect, 
                                   border_radius=4)
            
            # Draw messages
            for line in lines:
                new_y = self._render_wrapped_text(screen, line, x + padding, y, wrap_width, max_y)
                if new_y == y:  # Couldn't render more text
                    break
                y = new_y + 5  # Add spacing between lines
                if y >= max_y:
                    break
                
    def _render_wrapped_text(self, screen: pygame.Surface, text: str, x: int, y: int, max_width: int, max_y: int) -> int:
        """
        Render text with word wrapping, respecting maximum height and color markup.
        
        Args:
            screen: Surface to render to
            text: Text to render (may include color markup)
            x: Starting x position
            y: Starting y position
            max_width: Maximum width in pixels for text
            max_y: Maximum y position to render text

        Returns:
            int: The new y position after rendering all wrapped lines, or original y if couldn't render
        """
        if y >= max_y:
            return y

        # Parse color markup
        color = self.COLORS['gray']  # Default color
        markup_pattern = r'<(\w+)>(.*?)</\w+>'
        match = re.match(markup_pattern, text)
        if match:
            color_name, text = match.groups()
            color = self.COLORS.get(color_name, color)

        words = text.split(' ')
        if not words:
            return y
            
        # Handle lines one at a time
        line = []
        for word in words:
            # Try adding one more word
            line.append(word)
            # Get size if we render this line
            fw, fh = self.font_small.size(' '.join(line))
            if fw > max_width:
                # Line would be too wide
                if len(line) > 1:
                    # Remove the last word and render the line
                    line.pop()
                    # Check if we can fit this line
                    if y + fh > max_y:
                        return y
                    surf = self.font_small.render(' '.join(line), True, color)
                    screen.blit(surf, (x, y))
                    y += surf.get_height()
                    # Start a new line with the word that didn't fit
                    line = [word]
                else:
                    # Single word is too long, need to force wrap it
                    # Check if we can fit this word
                    if y + fh > max_y:
                        return y
                    surf = self.font_small.render(word, True, color)
                    screen.blit(surf, (x, y))
                    y += surf.get_height()
                    line = []
        
        # Render any remaining words
        if line:
            surf = self.font_small.render(' '.join(line), True, color)
            # Check if we can fit the last line
            if y + surf.get_height() <= max_y:
                screen.blit(surf, (x, y))
                y += surf.get_height()
            
        return y