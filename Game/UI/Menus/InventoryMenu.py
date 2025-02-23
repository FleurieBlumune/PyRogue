"""
Inventory menu implementation for managing cards and deck building.
"""

import pygame
import logging
from Engine.UI.MenuSystem.Menu import Menu
from Engine.UI.MenuSystem.MenuTypes import MenuID, MenuItemType
from Game.Content.Cards.CardLoader import CardLoader
from Game.Content.Cards.InventoryManager import InventoryManager
from Game.Content.Cards.DeckManager import DeckManager
from Game.UI.Menus.MenuConfigs import MENU_CONFIGS

logger = logging.getLogger(__name__)

class InventoryMenu(Menu):
    """
    Implements the inventory menu system for managing cards and deck building.
    This menu is toggled with the 'I' key and can be closed with ESC.
    """
    
    # Color constants - preserve original styling
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
        config = MENU_CONFIGS[MenuID.INVENTORY]
        super().__init__(
            title="Inventory",
            font_large=pygame.font.Font("Game/Content/Assets/Fonts/segoeuisymbol.ttf", 36),
            font_small=pygame.font.Font("Game/Content/Assets/Fonts/segoeuisymbol.ttf", 24),
            position="center"
        )
        
        self.window_surface = window_surface
        self.config = config
        self.is_visible = False
        
        # Initialize dimensions based on window size
        self.update_dimensions()
        
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
        
        # Test Unicode support
        try:
            test_surface = self.font_small.render('◆★', True, self.TEXT_COLOR)
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
        self._update_dimensions_from_size(screen_width, screen_height)
        
    def _update_dimensions_from_size(self, width: int, height: int):
        """Update dimensions based on provided width and height."""
        # Calculate proportional sizes (80% of screen width, 90% of screen height)
        self.window_width = min(int(width * 0.8), 1200)  # Cap at 1200px
        self.window_height = min(int(height * 0.9), 800)  # Cap at 800px
        
        # Center the window
        self.window_x = (width - self.window_width) // 2
        self.window_y = (height - self.window_height) // 2
        
        # Calculate panel sizes
        self.panel_width = (self.window_width - 30) // 2  # 15px padding on sides
        self.panel_height = self.window_height - 120  # Space for bottom panel
        self.bottom_panel_height = 90

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
            self.update_dimensions()
            return True
            
        # Handle keyboard navigation
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
                self._handle_up_key()
                return True
            elif event.key == pygame.K_DOWN:
                self._handle_down_key()
                return True
            elif event.key == pygame.K_RETURN:
                self._handle_enter_key()
                return True
                
        return False

    def _handle_up_key(self):
        """Handle up key navigation."""
        cards = self.available_cards if self.selected_panel == 'left' else self.deck_cards
        if cards and self.selected_card is not None and self.selected_card > 0:
            self.selected_card -= 1
            # Adjust scroll if needed
            if self.selected_card < self.scroll_offset[self.selected_panel]:
                self.scroll_offset[self.selected_panel] = self.selected_card

    def _handle_down_key(self):
        """Handle down key navigation."""
        cards = self.available_cards if self.selected_panel == 'left' else self.deck_cards
        if not cards:
            return
        if self.selected_card is None:
            self.selected_card = 0
        elif self.selected_card < len(cards) - 1:
            self.selected_card += 1
            # Adjust scroll if needed
            visible_cards = (self.panel_height - 50) // 30
            if self.selected_card >= self.scroll_offset[self.selected_panel] + visible_cards:
                self.scroll_offset[self.selected_panel] = self.selected_card - visible_cards + 1

    def _handle_enter_key(self):
        """Handle enter key selection."""
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
            
        except Exception as e:
            logger.error(f"Error refreshing cards: {e}")

    def render(self, screen: pygame.Surface, width: int, height: int) -> None:
        """
        Render the inventory menu.
        
        Args:
            screen: The surface to render to
            width: Screen width
            height: Screen height
        """
        if not self.is_visible:
            return
            
        # Update dimensions based on current screen size
        self._update_dimensions_from_size(width, height)
            
        # Create menu surface
        menu_surface = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        menu_surface.fill(self.BACKGROUND_COLOR)  # Use original background color
        
        # Draw left panel (Available Cards)
        self._render_card_panel(menu_surface, 'left')
        
        # Draw right panel (Current Deck)
        self._render_card_panel(menu_surface, 'right')
        
        # Draw bottom panel (Card Details)
        self._render_bottom_panel(menu_surface)
        
        # Blit menu to screen at centered position
        screen.blit(menu_surface, (self.window_x, self.window_y))

    def _render_card_panel(self, surface: pygame.Surface, panel: str):
        """Render a card panel (left or right)."""
        is_left = panel == 'left'
        cards = self.available_cards if is_left else self.deck_cards
        x = 10 if is_left else self.panel_width + 20
        
        # Draw panel background
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.fill(self.PANEL_COLOR)  # Use original panel color
        pygame.draw.rect(panel_surface, self.BORDER_COLOR, (0, 0, self.panel_width, self.panel_height), 2)
        
        # Draw title
        title_text = "Available Cards" if is_left else f"Current Deck ({len(self.deck_cards)}/20)"
        title = self.font_large.render(title_text, True, self.TEXT_COLOR)  # Use original text color
        panel_surface.blit(title, (10, 10))
        
        # Draw cards
        y_offset = 50
        for i, card in enumerate(cards[self.scroll_offset[panel]:]):
            if y_offset >= self.panel_height - 30:
                break
                
            # Draw selection highlight
            if self.selected_panel == panel and i + self.scroll_offset[panel] == self.selected_card:
                pygame.draw.rect(panel_surface, self.SELECTED_COLOR,  # Use original selected color
                               (5, y_offset, self.panel_width - 10, 25))
            
            # Draw card info
            self._render_card_info(panel_surface, card, y_offset, is_left)
            y_offset += 30
            
        surface.blit(panel_surface, (x, 10))

    def _render_card_info(self, surface: pygame.Surface, card, y_offset: int, is_left: bool):
        """Render card information in a panel."""
        # Draw rarity symbol
        rarity_color = self.RARITY_COLORS.get(card.rarity.name, self.TEXT_COLOR)
        rarity_symbol = self.font_small.render(self.RARITY_SYMBOLS[card.rarity.name], True, rarity_color)
        surface.blit(rarity_symbol, (10, y_offset))
        
        # Draw name and quantity
        if is_left:
            total_quantity = self.inventory.cards[card.id].quantity
            used_in_deck = sum(1 for c in self.deck_cards if c.id == card.id)
            remaining = total_quantity - used_in_deck
            name_text = f" {card.name} ({remaining}/{total_quantity})"
        else:
            name_text = f" {card.name}"
            
        name = self.font_small.render(name_text, True, self.TEXT_COLOR)  # Use original text color
        surface.blit(name, (30, y_offset))
        
        # Draw uses if limited
        if card.max_uses > 0:
            uses_text = f"{card.current_uses}/{card.max_uses}"
            uses = self.font_small.render(uses_text, True, self.TEXT_COLOR)  # Use original text color
            uses_rect = uses.get_rect(right=self.panel_width - 10, top=y_offset)
            surface.blit(uses, uses_rect)

    def _render_bottom_panel(self, surface: pygame.Surface):
        """Render the bottom panel with card details."""
        panel_surface = pygame.Surface((self.window_width - 20, self.bottom_panel_height))
        panel_surface.fill(self.PANEL_COLOR)  # Use original panel color
        pygame.draw.rect(panel_surface, self.BORDER_COLOR,  # Use original border color
                        (0, 0, self.window_width - 20, self.bottom_panel_height), 2)
        
        if self.selected_card is not None:
            cards = self.available_cards if self.selected_panel == 'left' else self.deck_cards
            if 0 <= self.selected_card < len(cards):
                card = cards[self.selected_card]
                name = self.font_small.render(card.name, True, self.TEXT_COLOR)  # Use original text color
                desc = self.font_small.render(card.description, True, self.TEXT_COLOR)  # Use original text color
                stats = self.font_small.render(
                    f"Success: {int(card.effect.success_rate * 100)}% | Duration: {'Permanent' if card.effect.duration == -1 else f'{int(card.effect.duration)}s'}", 
                    True, self.TEXT_COLOR  # Use original text color
                )
                
                panel_surface.blit(name, (10, 10))
                panel_surface.blit(desc, (10, 35))
                panel_surface.blit(stats, (10, 60))
                
        surface.blit(panel_surface, (10, self.window_height - self.bottom_panel_height - 10)) 