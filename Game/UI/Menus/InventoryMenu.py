"""
Inventory menu implementation for managing cards and deck building.
"""

import pygame
import logging
from Engine.UI.MenuSystem.MenuTypes import MenuID, MenuItemType
from Game.Content.Cards.CardLoader import CardLoader
from Game.Content.Cards.InventoryManager import InventoryManager
from Game.Content.Cards.DeckManager import DeckManager
from Game.UI.Menus.MenuConfigs import MENU_CONFIGS

logger = logging.getLogger(__name__)

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
    
    # Rarity symbols (will be overridden if Unicode not supported)
    RARITY_SYMBOLS = {
        'COMMON': '◆',      # Diamond
        'UNCOMMON': '◆',    # Diamond
        'RARE': '◆',        # Diamond
        'LEGENDARY': '★'    # Star
    }

    def __init__(self, window_surface: pygame.Surface, deck_manager: DeckManager = None):
        """
        Initialize the inventory menu.
        
        Args:
            window_surface: The main game window surface
            deck_manager: Optional DeckManager instance. If None, a new one will be created.
        """
        self.window_surface = window_surface
        self.config = MENU_CONFIGS[MenuID.INVENTORY]
        self.is_visible = False
        
        # Initialize dimensions
        self.update_dimensions()
        
        # Create surfaces
        self.create_surfaces()
        
        # Initialize fonts using Segoe UI Symbol
        self.init_fonts()
        
        # Track selected items
        self.selected_card = None
        self.selected_panel = 'left'  # 'left' or 'right'
        self.scroll_offset = {'left': 0, 'right': 0}
        
        # Initialize managers
        self.inventory = InventoryManager.get_instance()
        self.deck_manager = deck_manager or DeckManager()
        
        # Card data
        self.available_cards = []  # Will be populated by refresh_cards
        self.deck_cards = []       # Will be populated by refresh_cards
        
        # Test Unicode support by checking if the font can render the symbols
        try:
            test_surface = self.card_font.render('◆★', True, (255, 255, 255))
            test_rect = test_surface.get_rect()
            self.unicode_supported = test_rect.width > 0
        except:
            self.unicode_supported = False
            self.RARITY_SYMBOLS = {
                'COMMON': '*',      # Asterisk
                'UNCOMMON': '+',    # Plus
                'RARE': '#',        # Hash
                'LEGENDARY': '@'    # Star
            }

    def update_dimensions(self):
        """Update menu dimensions based on window size."""
        screen_width = self.window_surface.get_width()
        screen_height = self.window_surface.get_height()
        
        # Calculate proportional sizes (80% of screen width, 90% of screen height)
        self.window_width = min(int(screen_width * 0.8), 1200)  # Cap at 1200px
        self.window_height = min(int(screen_height * 0.9), 800)  # Cap at 800px
        
        # Center the window
        self.window_x = (screen_width - self.window_width) // 2
        self.window_y = (screen_height - self.window_height) // 2
        
        # Calculate panel sizes
        self.panel_width = (self.window_width - 30) // 2  # 15px padding on sides
        self.panel_height = self.window_height - 120  # Space for bottom panel
        self.bottom_panel_height = 90

    def create_surfaces(self):
        """Create or recreate all surfaces with current dimensions."""
        self.window = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        self.left_panel = pygame.Surface((self.panel_width, self.panel_height))
        self.right_panel = pygame.Surface((self.panel_width, self.panel_height))
        self.bottom_panel = pygame.Surface((self.window_width - 20, self.bottom_panel_height))

    def init_fonts(self):
        """Initialize fonts with appropriate sizes based on window dimensions."""
        font_path = "Game/Content/Assets/Fonts/segoeuisymbol.ttf"
        try:
            base_size = min(36, max(24, self.window_width // 30))  # Scale with window size
            self.title_font = pygame.font.Font(font_path, base_size)
            self.card_font = pygame.font.Font(font_path, int(base_size * 0.7))
            self.detail_font = pygame.font.Font(font_path, int(base_size * 0.6))
            
            # Set up rarity symbols
            self.RARITY_SYMBOLS = {
                'COMMON': '◆',      # Diamond
                'UNCOMMON': '◆',    # Diamond
                'RARE': '◆',        # Diamond
                'LEGENDARY': '★'    # Star
            }
        except:
            logger.debug("Failed to load Segoe UI Symbol font, falling back to default")
            self.title_font = pygame.font.Font(None, base_size)
            self.card_font = pygame.font.Font(None, int(base_size * 0.7))
            self.detail_font = pygame.font.Font(None, int(base_size * 0.6))
            
            self.RARITY_SYMBOLS = {
                'COMMON': '*',      # Asterisk
                'UNCOMMON': '+',    # Plus
                'RARE': '#',        # Hash
                'LEGENDARY': '@'    # Star
            }

    def handle_resize(self):
        """Handle window resize event."""
        self.update_dimensions()
        self.create_surfaces()
        self.init_fonts()
        self.refresh_cards()

    def draw(self):
        """Draw the inventory menu if visible."""
        if not self.is_visible:
            return
            
        # Clear the window surface
        self.window.fill((0, 0, 0, 0))  # Clear with transparency
        
        # Draw left panel (Available Cards)
        self.left_panel.fill(self.PANEL_COLOR)
        pygame.draw.rect(self.left_panel, self.BORDER_COLOR, (0, 0, self.panel_width, self.panel_height), 2)
        title = self.title_font.render("Available Cards", True, self.TEXT_COLOR)
        self.left_panel.blit(title, (10, 10))
        
        # Draw right panel (Current Deck)
        self.right_panel.fill(self.PANEL_COLOR)
        pygame.draw.rect(self.right_panel, self.BORDER_COLOR, (0, 0, self.panel_width, self.panel_height), 2)
        title = self.title_font.render(f"Current Deck ({len(self.deck_cards)}/20)", True, self.TEXT_COLOR)
        self.right_panel.blit(title, (10, 10))
        
        # Draw bottom panel (Card Details)
        self.bottom_panel.fill(self.PANEL_COLOR)
        pygame.draw.rect(self.bottom_panel, self.BORDER_COLOR, (0, 0, self.window_width - 20, self.bottom_panel_height), 2)
        
        # Draw cards in left panel
        y_offset = 50
        for i, card in enumerate(self.available_cards[self.scroll_offset['left']:]):
            if y_offset >= self.panel_height - 30:  # Leave space at bottom
                break
                
            # Draw selection highlight
            if self.selected_panel == 'left' and i + self.scroll_offset['left'] == self.selected_card:
                pygame.draw.rect(self.left_panel, self.SELECTED_COLOR, 
                               (5, y_offset, self.panel_width - 10, 25))
            
            # Draw rarity symbol and name
            rarity_color = self.RARITY_COLORS.get(card.rarity.name, self.TEXT_COLOR)
            rarity_symbol = self.card_font.render(self.RARITY_SYMBOLS[card.rarity.name], True, rarity_color)
            
            # Calculate remaining quantity
            total_quantity = self.inventory.cards[card.id].quantity
            used_in_deck = sum(1 for c in self.deck_cards if c.id == card.id)
            remaining = total_quantity - used_in_deck
            
            # Show name with quantity
            name = self.card_font.render(f" {card.name} ({remaining}/{total_quantity})", True, self.TEXT_COLOR)
            
            self.left_panel.blit(rarity_symbol, (10, y_offset))
            self.left_panel.blit(name, (30, y_offset))
            
            # Draw uses if limited
            if card.max_uses > 0:
                uses_text = f"{card.current_uses}/{card.max_uses}"
                uses = self.card_font.render(uses_text, True, self.TEXT_COLOR)
                uses_rect = uses.get_rect(right=self.panel_width - 10, top=y_offset)
                self.left_panel.blit(uses, uses_rect)
            
            y_offset += 30
        
        # Draw cards in right panel
        y_offset = 50
        for i, card in enumerate(self.deck_cards[self.scroll_offset['right']:]):
            if y_offset >= self.panel_height - 30:
                break
                
            if self.selected_panel == 'right' and i + self.scroll_offset['right'] == self.selected_card:
                pygame.draw.rect(self.right_panel, self.SELECTED_COLOR, 
                               (5, y_offset, self.panel_width - 10, 25))
            
            rarity_color = self.RARITY_COLORS.get(card.rarity.name, self.TEXT_COLOR)
            rarity_symbol = self.card_font.render(self.RARITY_SYMBOLS[card.rarity.name], True, rarity_color)
            name = self.card_font.render(f" {card.name}", True, self.TEXT_COLOR)
            
            self.right_panel.blit(rarity_symbol, (10, y_offset))
            self.right_panel.blit(name, (30, y_offset))
            
            if card.max_uses > 0:
                uses_text = f"{card.current_uses}/{card.max_uses}"
                uses = self.card_font.render(uses_text, True, self.TEXT_COLOR)
                uses_rect = uses.get_rect(right=self.panel_width - 10, top=y_offset)
                self.right_panel.blit(uses, uses_rect)
            
            y_offset += 30
        
        # Draw selected card details in bottom panel
        if self.selected_card is not None:
            cards = self.available_cards if self.selected_panel == 'left' else self.deck_cards
            if 0 <= self.selected_card < len(cards):
                card = cards[self.selected_card]
                name = self.detail_font.render(card.name, True, self.TEXT_COLOR)
                desc = self.detail_font.render(card.description, True, self.TEXT_COLOR)
                stats = self.detail_font.render(
                    f"Success: {int(card.effect.success_rate * 100)}% | Duration: {'Permanent' if card.effect.duration == -1 else f'{int(card.effect.duration)}s'}", 
                    True, self.TEXT_COLOR
                )
                
                self.bottom_panel.blit(name, (10, 10))
                self.bottom_panel.blit(desc, (10, 35))
                self.bottom_panel.blit(stats, (10, 60))
        
        # Blit all panels to window
        self.window.blit(self.left_panel, (10, 10))
        self.window.blit(self.right_panel, (self.panel_width + 20, 10))
        self.window.blit(self.bottom_panel, (10, self.window_height - self.bottom_panel_height - 10))
        
        # Blit window to screen at centered position
        self.window_surface.blit(self.window, (self.window_x, self.window_y))
        
    def show(self):
        """Show the inventory menu."""
        self.is_visible = True
        self.refresh_cards()
        
    def hide(self):
        """Hide the inventory menu and save deck changes."""
        self.is_visible = False
        # Save deck changes when closing inventory
        if self.deck_cards:
            try:
                self.deck_manager.build_deck([card.id for card in self.deck_cards])
            except Exception as e:
                logger.error(f"Failed to save deck: {e}")
        
    def toggle(self):
        """Toggle the visibility of the inventory menu."""
        if self.is_visible:
            self.hide()
        else:
            self.show()
            
    def refresh_cards(self):
        """Refresh the card displays in both panels."""
        try:
            logger.debug("Loading cards from inventory...")
            # Always reload available cards to get current quantities
            self.available_cards = [
                stack.card for stack in self.inventory.cards.values()
            ]
            logger.debug(f"Loaded {len(self.available_cards)} cards")
            
            # Load current deck if empty
            if not self.deck_cards and self.deck_manager.state.deck_list:
                self.deck_cards = [
                    self.inventory.cards[card_id].card 
                    for card_id in self.deck_manager.state.deck_list
                ]
            
            # Set initial selection to first card if none selected
            if self.available_cards and self.selected_card is None:
                self.selected_card = 0
                logger.debug(f"Set initial selection to: {self.available_cards[0].name}")
            
            # Validate deck cards against inventory
            valid_deck_cards = []
            for card in self.deck_cards:
                if card.id in self.inventory.cards:
                    # Count how many of this card are already in the valid deck
                    deck_count = sum(1 for c in valid_deck_cards if c.id == card.id)
                    # Only keep the card if we haven't exceeded the inventory quantity
                    if deck_count < self.inventory.cards[card.id].quantity:
                        valid_deck_cards.append(card)
            
            # Update deck with valid cards
            self.deck_cards = valid_deck_cards
            
            logging.debug(f"Drawing {len(self.available_cards)} available cards")
            
        except Exception as e:
            logger.error(f"Error refreshing cards: {e}")  # Changed to error level
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the inventory menu.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        # If menu is not visible, only handle I key to show it
        if not self.is_visible:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                self.show()
                return True
            return False
        
        # Handle window resize
        if event.type == pygame.VIDEORESIZE:
            self.handle_resize()
            return True
        
        # Handle keyboard events when menu is visible
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.hide()
                return True
            elif event.key == pygame.K_LEFT:
                self.selected_panel = 'left'
                if self.selected_card is None and self.available_cards:
                    self.selected_card = 0
                return True
            elif event.key == pygame.K_RIGHT:
                self.selected_panel = 'right'
                if self.selected_card is None and self.deck_cards:
                    self.selected_card = 0
                return True
            elif event.key == pygame.K_UP:
                cards = self.available_cards if self.selected_panel == 'left' else self.deck_cards
                if cards and self.selected_card is not None and self.selected_card > 0:
                    self.selected_card -= 1
                    # Adjust scroll if needed
                    if self.selected_card < self.scroll_offset[self.selected_panel]:
                        self.scroll_offset[self.selected_panel] = self.selected_card
                return True
            elif event.key == pygame.K_DOWN:
                cards = self.available_cards if self.selected_panel == 'left' else self.deck_cards
                if not cards:
                    return True
                if self.selected_card is None:
                    self.selected_card = 0
                elif self.selected_card < len(cards) - 1:
                    self.selected_card += 1
                    # Adjust scroll if needed
                    visible_cards = (self.panel_height - 50) // 30
                    if self.selected_card >= self.scroll_offset[self.selected_panel] + visible_cards:
                        self.scroll_offset[self.selected_panel] = self.selected_card - visible_cards + 1
                return True
            elif event.key == pygame.K_RETURN:
                if self.selected_card is not None:
                    # Handle card selection/transfer between panels
                    if self.selected_panel == 'left' and len(self.deck_cards) < 20:
                        card = self.available_cards[self.selected_card]
                        # Check if we have enough copies of this card
                        card_stack = self.inventory.cards[card.id]
                        deck_count = sum(1 for c in self.deck_cards if c.id == card.id)
                        if deck_count < card_stack.quantity:
                            self.deck_cards.append(card)
                    elif self.selected_panel == 'right' and self.selected_card < len(self.deck_cards):
                        self.deck_cards.pop(self.selected_card)
                        if self.selected_card >= len(self.deck_cards):
                            self.selected_card = max(0, len(self.deck_cards) - 1) if self.deck_cards else None
                    return True
                
        return False 