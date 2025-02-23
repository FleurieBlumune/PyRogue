"""
Implements a simple UI panel for managing the player's active cards and hand.
"""

import pygame
import logging
from Game.Content.Cards.DeckManager import DeckManager

logger = logging.getLogger(__name__)

class HandPanel:
    """
    A simple bottom panel UI for managing active cards.
    Shows current hand, draw pile, and discard pile.
    """
    
    # Color constants
    BACKGROUND_COLOR = (20, 20, 20, 200)  # Dark semi-transparent
    PANEL_COLOR = (40, 40, 40)
    TEXT_COLOR = (255, 255, 255)
    SELECTED_COLOR = (60, 60, 100)
    BORDER_COLOR = (80, 80, 80)
    HOTKEY_COLOR = (200, 200, 200)  # Light gray for hotkey numbers
    TOOLTIP_COLOR = (30, 30, 30, 240)  # Dark semi-transparent for tooltip
    TOOLTIP_BORDER = (100, 100, 100)  # Light gray for tooltip border
    
    def __init__(self, window_surface: pygame.Surface, deck_manager: DeckManager):
        """
        Initialize the hand panel.
        
        Args:
            window_surface: The main game window surface
            deck_manager: The deck management system
        """
        logger.info("Initializing HandPanel")
        self.window_surface = window_surface
        self.deck_manager = deck_manager
        self.is_visible = True
        self.selected_card = None
        self.hovered_card = None  # Track which card is being hovered
        self.tooltip_surface = None  # Surface for the tooltip
        
        # Calculate initial activity log width (same formula as Menu class)
        screen_width = window_surface.get_width()
        self.activity_log_width = min(screen_width // 3, 400) + 10  # +10 for padding
        
        # Log initial state
        draw_count, discard_count, hand_count = self.deck_manager.get_card_counts()
        logger.info(f"Initial deck state - Draw: {draw_count}, Discard: {discard_count}, Hand: {hand_count}")
        
        # Initialize dimensions
        self.update_dimensions()
        
        # Initialize fonts
        self.init_fonts()
        logger.info("HandPanel initialization complete")
        
    def update_dimensions(self):
        """Update panel dimensions based on window size."""
        screen_width = self.window_surface.get_width()
        screen_height = self.window_surface.get_height()
        
        # Panel takes up bottom 20% of screen
        self.height = min(int(screen_height * 0.2), 150)  # Cap at 150px
        # Adjust width to account for activity log
        self.width = screen_width - self.activity_log_width
        self.x = 0
        self.y = screen_height - self.height
        
        # Create panel surface
        self.surface = pygame.Surface((self.width, self.height))
        
    def init_fonts(self):
        """Initialize fonts for rendering text."""
        base_size = min(24, max(16, self.height // 6))
        self.font = pygame.font.Font(None, base_size)
        self.hotkey_font = pygame.font.Font(None, base_size - 2)  # Slightly smaller for hotkeys
        
    def draw(self):
        """Draw the hand panel."""
        if not self.is_visible:
            return
            
        # Clear panel
        self.surface.fill(self.PANEL_COLOR)
        pygame.draw.rect(self.surface, self.BORDER_COLOR, (0, 0, self.width, self.height), 2)
        
        # Draw pile counts
        draw_count, discard_count, hand_count = self.deck_manager.get_card_counts()
        counts_text = f"Draw: {draw_count} | Discard: {discard_count}"
        counts = self.font.render(counts_text, True, self.TEXT_COLOR)
        self.surface.blit(counts, (10, 10))
        
        # Draw cards in hand
        card_spacing = 20
        card_width = 120
        start_x = (self.width - (card_width + card_spacing) * len(self.deck_manager.state.hand)) // 2
        
        for i, card in enumerate(self.deck_manager.state.hand):
            x = start_x + i * (card_width + card_spacing)
            y = 40
            
            # Card background
            card_rect = pygame.Rect(x, y, card_width, self.height - y - 10)
            pygame.draw.rect(self.surface, 
                           self.SELECTED_COLOR if card == self.selected_card else self.BACKGROUND_COLOR, 
                           card_rect)
            pygame.draw.rect(self.surface, self.BORDER_COLOR, card_rect, 1)
            
            # Hotkey number (1-5)
            hotkey_text = str(i + 1)
            hotkey = self.hotkey_font.render(hotkey_text, True, self.HOTKEY_COLOR)
            hotkey_rect = hotkey.get_rect(left=card_rect.left + 5, top=card_rect.top + 5)
            self.surface.blit(hotkey, hotkey_rect)
            
            # Card name
            name = self.font.render(card.name, True, self.TEXT_COLOR)
            name_rect = name.get_rect(centerx=card_rect.centerx, top=card_rect.top + 5)
            self.surface.blit(name, name_rect)
            
            # Uses remaining
            if card.max_uses > 0:
                uses_text = f"Uses: {card.max_uses - card.current_uses}/{card.max_uses}"
                uses = self.font.render(uses_text, True, self.TEXT_COLOR)
                uses_rect = uses.get_rect(centerx=card_rect.centerx, bottom=card_rect.bottom - 5)
                self.surface.blit(uses, uses_rect)
        
        # Draw to window
        self.window_surface.blit(self.surface, (self.x, self.y))
        
        # Draw tooltip if needed
        if self.hovered_card and self.tooltip_surface:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            tooltip_x = min(mouse_x + 10, self.window_surface.get_width() - self.tooltip_surface.get_width())
            tooltip_y = max(mouse_y - self.tooltip_surface.get_height() - 10, 0)
            self.window_surface.blit(self.tooltip_surface, (tooltip_x, tooltip_y))
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            bool: True if event was handled
        """
        if not self.is_visible:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            # Convert mouse position to panel coordinates
            mouse_x, mouse_y = event.pos
            if mouse_y < self.y:  # Mouse above panel
                self.hovered_card = None
                return False
                
            # Calculate card positions
            card_spacing = 20
            card_width = 120
            start_x = (self.width - (card_width + card_spacing) * len(self.deck_manager.state.hand)) // 2
            
            # Check if mouse is over a card
            for i, card in enumerate(self.deck_manager.state.hand):
                x = start_x + i * (card_width + card_spacing)
                card_rect = pygame.Rect(x, 40, card_width, self.height - 50)
                
                if card_rect.collidepoint(mouse_x - self.x, mouse_y - self.y):
                    if self.hovered_card != card:
                        self.hovered_card = card
                        self._update_tooltip()
                    return True
            
            self.hovered_card = None
            return True
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Only handle left click (button 1) for card selection/deselection
            if event.button != 1:
                return False
                
            # Convert mouse position to panel coordinates
            mouse_x, mouse_y = event.pos
            if mouse_y < self.y:  # Click above panel - ignore it
                return False
                
            # Calculate card positions
            card_spacing = 20
            card_width = 120
            start_x = (self.width - (card_width + card_spacing) * len(self.deck_manager.state.hand)) // 2
            
            # Check if click was on a card
            for i, card in enumerate(self.deck_manager.state.hand):
                x = start_x + i * (card_width + card_spacing)
                card_rect = pygame.Rect(x, 40, card_width, self.height - 50)
                
                if card_rect.collidepoint(mouse_x - self.x, mouse_y - self.y):
                    self.selected_card = card
                    return True
            
            # Only deselect if clicking in empty space within the panel
            if mouse_y >= self.y:
                self.selected_card = None
            return True
            
        elif event.type == pygame.KEYDOWN:
            # Handle number keys 1-5 for card selection
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                # Convert key to index (0-4)
                index = event.key - pygame.K_1
                if index < len(self.deck_manager.state.hand):
                    self.selected_card = self.deck_manager.state.hand[index]
                    return True
            
            if event.key == pygame.K_SPACE and self.selected_card:
                # Try to use selected card
                if self.deck_manager.use_card(self.selected_card):
                    self.selected_card = None
                return True
            elif event.key == pygame.K_d:  # Draw card
                self.deck_manager.draw_hand()
                return True
                
        return False
        
    def handle_resize(self):
        """Handle window resize event."""
        self.update_dimensions()
        self.init_fonts() 

    def _update_tooltip(self):
        """Update the tooltip surface for the currently hovered card."""
        if not self.hovered_card:
            self.tooltip_surface = None
            return
            
        # Create tooltip content
        lines = [
            self.hovered_card.name,
            "",
            self.hovered_card.description,
            "",
            f"Success Rate: {int(self.hovered_card.effect.success_rate * 100)}%",
            f"Duration: {'Permanent' if self.hovered_card.effect.duration == -1 else f'{int(self.hovered_card.effect.duration)}s'}"
        ]
        
        # Calculate tooltip dimensions
        padding = 10
        line_height = 25
        max_width = 0
        rendered_lines = []
        
        for line in lines:
            if line:
                rendered = self.font.render(line, True, self.TEXT_COLOR)
                rendered_lines.append(rendered)
                max_width = max(max_width, rendered.get_width())
            else:
                rendered_lines.append(None)
        
        tooltip_width = max_width + (padding * 2)
        tooltip_height = (len(lines) * line_height) + (padding * 2)
        
        # Create tooltip surface
        self.tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        pygame.draw.rect(self.tooltip_surface, self.TOOLTIP_COLOR, (0, 0, tooltip_width, tooltip_height))
        pygame.draw.rect(self.tooltip_surface, self.TOOLTIP_BORDER, (0, 0, tooltip_width, tooltip_height), 1)
        
        # Draw text
        y = padding
        for rendered in rendered_lines:
            if rendered:
                text_rect = rendered.get_rect(left=padding, top=y)
                self.tooltip_surface.blit(rendered, text_rect)
            y += line_height 

    def set_activity_log_width(self, width: int):
        """Update the activity log width and adjust panel dimensions."""
        if width != self.activity_log_width:
            self.activity_log_width = width
            self.update_dimensions() 