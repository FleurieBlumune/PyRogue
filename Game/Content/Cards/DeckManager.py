"""
Manages the player's deck of cards during gameplay.

The deck system handles:
- Drawing cards
- Discarding cards
- Shuffling
- Hand management
- Deck construction from inventory
"""

import random
import csv
import logging
from pathlib import Path
from typing import List, Set, Optional
from dataclasses import dataclass, field
from . import Card, CardRarity
from .InventoryManager import InventoryManager, CardStack

@dataclass
class DeckState:
    """Represents the current state of a player's deck during gameplay."""
    draw_pile: List[Card] = field(default_factory=list)
    discard_pile: List[Card] = field(default_factory=list)
    hand: List[Card] = field(default_factory=list)
    deck_list: Set[int] = field(default_factory=set)  # Set of integer card IDs that make up the deck

class DeckError(Exception):
    """Raised when there is an error with deck operations."""
    pass

class DeckManager:
    """
    Manages a player's deck of cards during gameplay.
    
    The DeckManager handles all deck-related operations including:
    - Building decks from inventory
    - Drawing cards
    - Managing the discard pile
    - Shuffling
    - Hand management
    """
    
    MAX_DECK_SIZE = 20
    HAND_SIZE = 5
    
    def __init__(self, deck_path: str = "Game/Content/Data/CSV/player_deck.csv"):
        """Initialize a new deck manager."""
        self.inventory = InventoryManager.get_instance()
        self.state = DeckState()
        self.deck_path = Path(deck_path)
        self.load_deck()
        
    def save_deck(self) -> None:
        """Save the current deck list to CSV."""
        # Ensure the directory exists
        self.deck_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.deck_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['card_id'])  # Header
            for card_id in self.state.deck_list:
                writer.writerow([card_id])
                
    def load_deck(self) -> None:
        """Load the deck from CSV and build it."""
        if not self.deck_path.exists():
            return
            
        try:
            card_ids = []
            with open(self.deck_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    card_ids.append(int(row['card_id']))
            
            if card_ids:
                self.build_deck(card_ids)
        except Exception as e:
            logging.error(f"Failed to load deck: {e}")
            
    def build_deck(self, card_ids: List[int]) -> None:
        """
        Build a new deck from the specified card IDs.
        
        Args:
            card_ids: List of integer card IDs to include in the deck
            
        Raises:
            DeckError: If the deck construction fails
        """
        if len(card_ids) > self.MAX_DECK_SIZE:
            raise DeckError(f"Deck size exceeds maximum of {self.MAX_DECK_SIZE}")
            
        # Verify all cards exist in inventory
        for card_id in card_ids:
            if card_id not in self.inventory.cards:
                raise DeckError(f"Card {card_id} not found in inventory")
                
        # Clear current deck state
        self.state = DeckState()
        self.state.deck_list = set(card_ids)
        
        # Create initial draw pile
        self.state.draw_pile = [
            self.inventory.cards[card_id].card  # Access the Card object from CardStack
            for card_id in card_ids
        ]
        self.shuffle_deck()
        
        # Save the deck after building
        self.save_deck()
        
    def shuffle_deck(self) -> None:
        """Shuffle the draw pile."""
        random.shuffle(self.state.draw_pile)
        
    def shuffle_discard_into_draw(self) -> None:
        """Move all cards from discard pile to draw pile and shuffle."""
        self.state.draw_pile.extend(self.state.discard_pile)
        self.state.discard_pile.clear()
        self.shuffle_deck()
        
    def draw_card(self) -> Optional[Card]:
        """
        Draw a single card from the draw pile.
        
        Returns:
            Card if available, None if no cards remain
        """
        if not self.state.draw_pile and self.state.discard_pile:
            self.shuffle_discard_into_draw()
            
        return self.state.draw_pile.pop() if self.state.draw_pile else None
        
    def draw_hand(self) -> List[Card]:
        """
        Draw up to HAND_SIZE cards to fill the hand.
        
        Returns:
            List of cards drawn
        """
        cards_to_draw = self.HAND_SIZE - len(self.state.hand)
        drawn_cards = []
        
        for _ in range(cards_to_draw):
            card = self.draw_card()
            if card:
                drawn_cards.append(card)
                self.state.hand.append(card)
            else:
                break
                
        return drawn_cards
        
    def discard_card(self, card: Card) -> None:
        """
        Discard a card from hand.
        
        Args:
            card: The card to discard
            
        Raises:
            DeckError: If the card is not in hand
        """
        if card not in self.state.hand:
            raise DeckError("Cannot discard a card that is not in hand")
            
        self.state.hand.remove(card)
        self.state.discard_pile.append(card)
        
    def discard_hand(self) -> None:
        """Discard all cards in hand."""
        self.state.discard_pile.extend(self.state.hand)
        self.state.hand.clear()
        
    def get_deck_size(self) -> int:
        """Get the total number of cards in the deck."""
        return len(self.state.deck_list)
        
    def get_card_counts(self) -> tuple[int, int, int]:
        """
        Get the current count of cards in each pile.
        
        Returns:
            Tuple of (draw_pile_count, discard_pile_count, hand_count)
        """
        return (
            len(self.state.draw_pile),
            len(self.state.discard_pile),
            len(self.state.hand)
        )
        
    def use_card(self, card: Card) -> bool:
        """
        Use a card from hand.
        
        Args:
            card: The card to use
            
        Returns:
            bool: True if the card was successfully used
            
        Raises:
            DeckError: If the card is not in hand
        """
        if card not in self.state.hand:
            raise DeckError("Cannot use a card that is not in hand")
            
        # Try to use the card
        if self.inventory.use_card(card.id):
            self.state.hand.remove(card)
            
            # If the card was consumed (removed from inventory), also remove it from deck
            if card.id not in self.inventory.cards:
                self.state.deck_list.remove(card.id)
            else:
                # Otherwise, move it to discard pile
                self.state.discard_pile.append(card)
            return True
            
        return False 