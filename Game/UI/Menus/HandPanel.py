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
    
    def __init__(self, window_surface: pygame.Surface, deck_manager: DeckManager):
        """
        Initialize the hand panel.
        
        Args:
            window_surface: The main game window surface
            deck_manager: The deck management system
        """
        self.window_surface = window_surface
        self.deck_manager = deck_manager
        self.is_visible = True
        self.selected_card = None
        
        # Initialize dimensions
        self.update_dimensions()
        
        # Initialize fonts
        self.init_fonts()
        
    def update_dimensions(self):
        """Update panel dimensions based on window size."""
        screen_width = self.window_surface.get_width()
        screen_height = self.window_surface.get_height()
        
        # Panel takes up bottom 20% of screen
        self.height = min(int(screen_height * 0.2), 150)  # Cap at 150px
        self.width = screen_width
        self.x = 0
        self.y = screen_height - self.height
        
        # Create panel surface
        self.surface = pygame.Surface((self.width, self.height))
        
    def init_fonts(self):
        """Initialize fonts for rendering text."""
        base_size = min(24, max(16, self.height // 6))
        self.font = pygame.font.Font(None, base_size)
        
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
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Convert mouse position to panel coordinates
            mouse_x, mouse_y = event.pos
            if mouse_y < self.y:  # Click above panel
                self.selected_card = None
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
            
            self.selected_card = None
            return True
            
        elif event.type == pygame.KEYDOWN:
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