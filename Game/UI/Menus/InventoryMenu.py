"""
Inventory menu implementation for managing cards and deck building.
Uses pure Pygame for rendering.
"""

import pygame
from Engine.UI.MenuSystem.MenuTypes import MenuID, MenuItemType
from Game.Content.Cards.CardLoader import CardLoader
from Game.UI.Menus.MenuConfigs import MENU_CONFIGS

class InventoryMenu:
    """
    Implements the inventory menu system for managing cards and deck building.
    This menu is toggled with the 'I' key and can be closed with ESC.
    """
    
    # Color constants
    BACKGROUND_COLOR = (20, 20, 20, 200)  # Dark semi-transparent
    PANEL_COLOR = (40, 40, 40)
    TEXT_COLOR = (255, 255, 255)
    SELECTED_COLOR = (60, 60, 100)
    BORDER_COLOR = (80, 80, 80)
    
    # Rarity colors
    RARITY_COLORS = {
        'COMMON': (200, 200, 200),    # White
        'UNCOMMON': (0, 200, 0),      # Green
        'RARE': (0, 100, 255),        # Blue
        'LEGENDARY': (255, 215, 0)     # Gold
    }

    def __init__(self, window_surface: pygame.Surface):
        """
        Initialize the inventory menu.
        
        Args:
            window_surface: The main game window surface
        """
        self.window_surface = window_surface
        self.config = MENU_CONFIGS[MenuID.INVENTORY]
        self.is_visible = False
        self.card_loader = CardLoader()
        
        # Calculate window dimensions
        self.window_width = 800
        self.window_height = 600
        self.window_x = (window_surface.get_width() - self.window_width) // 2
        self.window_y = (window_surface.get_height() - self.window_height) // 2
        
        # Create surfaces
        self.window = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        self.left_panel = pygame.Surface((350, 480))
        self.right_panel = pygame.Surface((350, 480))
        self.bottom_panel = pygame.Surface((780, 90))
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 36)
        self.card_font = pygame.font.Font(None, 24)
        self.detail_font = pygame.font.Font(None, 20)
        
        # Track selected items
        self.selected_card = None
        self.selected_panel = 'left'  # 'left' or 'right'
        self.scroll_offset = {'left': 0, 'right': 0}
        
        # Card data
        self.available_cards = []  # Will be populated by refresh_cards
        self.deck_cards = []       # Will be populated by refresh_cards
        
    def draw(self):
        """Draw the inventory menu if visible."""
        if not self.is_visible:
            return
            
        # Draw semi-transparent background
        self.window.fill(self.BACKGROUND_COLOR)
        
        # Draw panels
        self._draw_panel(self.left_panel, (10, 10), "Available Cards")
        self._draw_panel(self.right_panel, (440, 10), "Current Deck")
        self._draw_panel(self.bottom_panel, (10, 500), "Card Details")
        
        # Draw to main surface
        self.window_surface.blit(self.window, (self.window_x, self.window_y))
        
    def _draw_panel(self, panel: pygame.Surface, pos: tuple, title: str):
        """Draw a panel with title and border."""
        # Fill panel background
        panel.fill(self.PANEL_COLOR)
        pygame.draw.rect(panel, self.BORDER_COLOR, panel.get_rect(), 2)
        
        # Draw title
        title_surface = self.title_font.render(title, True, self.TEXT_COLOR)
        panel.blit(title_surface, (10, 5))
        
        # Blit panel to window
        self.window.blit(panel, pos)
        
    def show(self):
        """Show the inventory menu."""
        self.is_visible = True
        self.refresh_cards()
        
    def hide(self):
        """Hide the inventory menu."""
        self.is_visible = False
        
    def toggle(self):
        """Toggle the visibility of the inventory menu."""
        if self.is_visible:
            self.hide()
        else:
            self.show()
            
    def refresh_cards(self):
        """Refresh the card displays in both panels."""
        # TODO: Load actual card data from CardLoader
        pass
        
    def handle_event(self, event: pygame.event.Event):
        """
        Handle pygame events for the inventory menu.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        if not self.is_visible:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                self.toggle()
                return True
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
            elif event.key == pygame.K_TAB:
                self.selected_panel = 'right' if self.selected_panel == 'left' else 'left'
                return True
            elif event.key in (pygame.K_UP, pygame.K_DOWN):
                self._handle_vertical_navigation(event.key)
                return True
            elif event.key == pygame.K_RETURN:
                self._handle_card_action()
                return True
                
        return False
        
    def _handle_vertical_navigation(self, key):
        """Handle up/down navigation in card lists."""
        cards = self.available_cards if self.selected_panel == 'left' else self.deck_cards
        if not cards:
            return
            
        current_index = cards.index(self.selected_card) if self.selected_card in cards else -1
        if key == pygame.K_UP:
            current_index = max(0, current_index - 1)
        else:  # pygame.K_DOWN
            current_index = min(len(cards) - 1, current_index + 1)
        
        self.selected_card = cards[current_index]
        
    def _handle_card_action(self):
        """Handle card selection/deselection when Enter is pressed."""
        if not self.selected_card:
            return
            
        if self.selected_panel == 'left':
            # Add card to deck if not at maximum
            if len(self.deck_cards) < 20:  # Maximum deck size
                self.deck_cards.append(self.selected_card)
        else:
            # Remove card from deck
            if self.selected_card in self.deck_cards:
                self.deck_cards.remove(self.selected_card)
                
        self.refresh_cards() 