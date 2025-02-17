"""
Main Menu class for handling menu display and interaction.
"""

from typing import Optional, Any, Dict, Set, Tuple, List
import pygame
from .MenuItem import MenuItem
from .MenuTypes import MenuItemType
import re
import logging
from Game.UI.Menus.MessageLog import ActivityLog

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
        self.logger = logging.getLogger(__name__)
        
        # Initialize state variables
        self.dragging_scrollbar = False
        self.scrollbar_hover = False
        self.scrollbar_rect = None
        self.scrollbar_track_rect = None
        self.resizing = False
        self.padding = 10  # Default padding
        
        # Initialize log width for right-positioned menus
        if position == "right":
            # Get screen size for initial width calculation
            display_info = pygame.display.Info()
            screen_width = display_info.current_w
            self.log_width = min(screen_width // 3, 400)  # Cap initial width
        else:
            self.log_width = None
            
        self.last_screen_width = None
        self.on_resize = None
        self.on_resize_end = None
        
        # Register this menu's region
        Menu._reserved_regions.add(position)
        
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


    def update_log_width(self, new_width: int) -> None:
        """
        Update the message log width and notify resize listeners.
        
        Args:
            new_width (int): New width for the log in pixels
        """
        try:
            if new_width != self.log_width:
                old_width = self.log_width
                self.log_width = new_width
                self.logger.debug(f"Resized message log from {old_width} to {new_width}")
                
                # Calculate new wrap width considering padding and scrollbar offset
                new_wrap_width = max(50, self.log_width - 2 * self.padding - 12)  # Ensure minimum width
                
                # Update ActivityLog wrap parameters
                activity_log = ActivityLog.get_instance()
                if activity_log:
                    activity_log.set_wrap_params(new_wrap_width, self.font_small)
                
                # Notify about the resize
                if self.on_resize:
                    try:
                        self.on_resize(new_width)
                    except Exception as e:
                        self.logger.error(f"Error in resize callback: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error updating log width: {e}")
            # Try to recover by resetting to a safe width
            self.log_width = 200
            if self.on_resize:
                self.on_resize(200)

    def handle_input(self, event: pygame.event.Event) -> Optional[Any]:
        """
        Handle input events for the menu.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            Optional[Any]: Result from menu item activation if any
        """
        # If this is the activity log menu (position 'right'), check for resize handle interactions
        if self.position == "right":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(self, '_resize_handle_rect') and self._resize_handle_rect.collidepoint(event.pos):
                    self.resizing = True
                    self.logger.debug("Started resizing message log")
                    return None
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.resizing:
                    self.resizing = False
                    self.logger.debug("Finished resizing message log")
                    # Notify that resizing has ended
                    if self.on_resize_end:
                        self.on_resize_end()
                    return None
            # We should make this a public method and call it from the GameLoop
            # That way when we resize the window, the message log will resize with it
            elif event.type == pygame.MOUSEMOTION and self.resizing:
                # Calculate new log width based on mouse position
                # Right edge remains fixed at (self.last_screen_width - self.padding)
                new_log_width = self.last_screen_width - self.padding - event.pos[0]
                # Clamp the new log width between a minimum and a fraction of the screen width
                new_log_width = max(100, min(new_log_width, int(self.last_screen_width * 0.8)))
                self.update_log_width(new_log_width)
                return None
        
        # Existing code: Update scrollbar hover state
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
                        total_height = self.scrollbar_track_rect.height
                        relative_y = event.pos[1] - self.scrollbar_track_rect.top
                        scroll_ratio = max(0, min(1, relative_y / total_height))
                        max_scroll = len(item.value_getter.messages)
                        new_scroll = int(max_scroll * scroll_ratio)
                        current_scroll = item.value_getter.scroll_offset
                        if new_scroll != current_scroll:
                            item.value_getter.scroll(new_scroll - current_scroll)
                        return None

        # Handle activity log scrolling with keyboard
        if self.position == "right" and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                item = self.items[self.selected_index]
                if item.type == MenuItemType.LOG and hasattr(item.value_getter, 'scroll'):
                    scroll_direction = 1 if event.key == pygame.K_UP else -1
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        scroll_amount = scroll_direction * 5
                    else:
                        scroll_amount = scroll_direction
                    item.value_getter.scroll(scroll_amount)
                return None
            elif event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                item = self.items[self.selected_index]
                if item.type == MenuItemType.LOG and hasattr(item.value_getter, 'scroll'):
                    scroll_amount = 5 if event.key == pygame.K_PAGEUP else -5
                    item.value_getter.scroll(scroll_amount)
                return None

        # Handle regular menu input for non-log menus
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
        try:
            padding = 10
            self.last_screen_width = width
            self.padding = padding
            
            # Initialize or adjust log width based on screen size
            if not hasattr(self, 'log_width') or self.log_width is None:
                self.log_width = min(width // 3, 400)  # Cap initial width
            elif self.log_width > width - 2 * padding:
                # Adjust if log is too wide for new screen size
                self.log_width = width // 3
            
            x = width - self.log_width - padding
            y = padding + self.get_reserved_height("top-left")
            log_height = height - 2 * padding - y
            
            # Create rectangles for log area and resize handle
            self._log_rect = pygame.Rect(x, y, self.log_width, log_height)
            handle_width = 8
            self._resize_handle_rect = pygame.Rect(x, y, handle_width, log_height)
            
            # Draw semi-transparent background
            log_surface = pygame.Surface((self.log_width, log_height))
            log_surface.fill((0, 0, 0))
            log_surface.set_alpha(180)
            screen.blit(log_surface, (x, y))
            
            # Draw resize handle
            handle_color = (200, 200, 200) if getattr(self, 'resizing', False) else (150, 150, 150)
            pygame.draw.rect(screen, handle_color, self._resize_handle_rect)
            
            # Draw title if present
            title_y = y + padding
            if self.title:
                title_surface = self.font_small.render(self.title, True, (255, 255, 255))
                title_rect = title_surface.get_rect(midtop=(x + self.log_width//2, y + padding))
                screen.blit(title_surface, title_rect)
                title_y = title_rect.bottom + padding
            
            # Calculate text area
            wrap_width = max(50, self.log_width - 2 * padding - 12)  # Ensure minimum wrap width
            
            # Draw log items
            current_y = title_y
            for item in self.items:
                if item.type == MenuItemType.LOG:
                    try:
                        # Get the formatted text from the menu item
                        text = item.get_display_text()
                        if not text:
                            continue
                            
                        # Split into lines and handle color markup
                        lines = text.splitlines()
                        for line in lines:
                            if current_y >= self._log_rect.bottom - padding:
                                break
                                
                            # Handle color markup
                            color = self.COLORS['gray']  # Default color
                            markup_pattern = r'<(\w+)>(.*?)</\w+>'
                            match = re.match(markup_pattern, line)
                            if match:
                                color_name, line = match.groups()
                                color = self.COLORS.get(color_name, color)
                                
                            # Render the line
                            text_surface = self.font_small.render(line, True, color)
                            screen.blit(text_surface, (x + padding + handle_width, current_y))
                            current_y += self.font_small.get_height() + 2  # Small spacing between lines
                            
                    except Exception as e:
                        self.logger.error(f"Error rendering log message: {e}", exc_info=True)
                else:
                    # Render non-log items normally
                    if current_y >= self._log_rect.bottom - padding:
                        break
                    try:
                        text = item.get_display_text()
                        text_surface = self.font_small.render(text, True, (255, 255, 255))
                        screen.blit(text_surface, (x + padding + handle_width, current_y))
                        current_y += self.font_small.get_height() + 5
                    except Exception as e:
                        self.logger.error(f"Error rendering menu item: {e}", exc_info=True)
                
        except Exception as e:
            self.logger.error(f"Error rendering right menu: {e}", exc_info=True)
            # Draw error message if rendering fails
            error_text = "Error rendering menu"
            error_surface = self.font_small.render(error_text, True, (255, 0, 0))
            screen.blit(error_surface, (width - 200, 10))

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

    def set_resize_callback(self, callback, end_callback=None):
        """
        Set the callbacks for resize events.
        
        Args:
            callback: Called during resizing with the new width
            end_callback: Called when resizing ends
        """
        self.on_resize = callback
        self.on_resize_end = end_callback

    def handle_window_resize(self, new_width: int, new_height: int) -> None:
        """
        Handle window resize events by adjusting menu dimensions.
        
        Args:
            new_width (int): New window width in pixels
            new_height (int): New window height in pixels
        """
        try:
            self.logger.debug(f"Menu handling window resize: {new_width}x{new_height}, position={self.position}")
            if self.position == "right":
                # Calculate new log width based on screen width
                new_log_width = int(new_width / 3)  # Keep log at 1/3 of screen width
                
                self.logger.debug(f"Current log width: {self.log_width}, New target width: {new_log_width}")
                
                # Only update if there's a significant change
                if abs(self.log_width - new_log_width) > 10:
                    self.logger.debug("Significant width change detected, updating...")
                    # Use the existing resize callback to ensure consistent behavior
                    if self.on_resize:
                        self.logger.debug("Using resize callback")
                        self.on_resize(new_log_width)
                    else:
                        self.logger.debug("No resize callback, using direct update")
                        # Fallback if no callback is set
                        self.update_log_width(new_log_width)
                    
                    self.logger.debug(f"Window resize adjusted log width to {new_log_width}")
                else:
                    self.logger.debug("Change too small, skipping update")
                    
        except Exception as e:
            self.logger.error(f"Error handling window resize: {e}", exc_info=True)