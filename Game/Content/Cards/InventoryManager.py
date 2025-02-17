"""
Manages the player's card inventory system, handling card collection, organization, and usage.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from . import Card, CardRarity

@dataclass
class CardStack:
    """Represents a stack of identical cards in the inventory."""
    card: Card
    quantity: int = 1

class InventoryManager:
    """
    Manages the player's card inventory.
    
    This class handles:
    - Adding and removing cards
    - Organizing cards by type/rarity
    - Managing card quantities
    - Card usage and effects
    """
    
    def __init__(self, max_unique_cards: int = 30):
        self.max_unique_cards = max_unique_cards
        self.cards: Dict[str, CardStack] = {}  # card_id -> CardStack
        self._active_cards: List[str] = []  # List of card IDs in active slots
        self.max_active_cards = 5  # Number of cards that can be "equipped" at once
        
    @property
    def active_cards(self) -> List[Card]:
        """Get the currently active/equipped cards."""
        return [self.cards[card_id].card for card_id in self._active_cards]
    
    def add_card(self, card: Card, quantity: int = 1) -> bool:
        """
        Add card(s) to the inventory.
        
        Args:
            card: The card to add
            quantity: Number of copies to add
            
        Returns:
            bool: True if successfully added, False if inventory is full
        """
        if card.id in self.cards:
            self.cards[card.id].quantity += quantity
            return True
            
        if len(self.cards) >= self.max_unique_cards:
            return False
            
        self.cards[card.id] = CardStack(card, quantity)
        return True
        
    def remove_card(self, card_id: str, quantity: int = 1) -> bool:
        """
        Remove card(s) from the inventory.
        
        Args:
            card_id: ID of the card to remove
            quantity: Number of copies to remove
            
        Returns:
            bool: True if successfully removed, False if card not found or insufficient quantity
        """
        if card_id not in self.cards:
            return False
            
        stack = self.cards[card_id]
        if stack.quantity < quantity:
            return False
            
        stack.quantity -= quantity
        if stack.quantity == 0:
            del self.cards[card_id]
            # Remove from active cards if it was active
            if card_id in self._active_cards:
                self._active_cards.remove(card_id)
                
        return True
        
    def set_active(self, card_id: str) -> bool:
        """
        Set a card as active/equipped.
        
        Args:
            card_id: ID of the card to activate
            
        Returns:
            bool: True if successfully activated, False otherwise
        """
        if card_id not in self.cards:
            return False
            
        if card_id in self._active_cards:
            return True
            
        if len(self._active_cards) >= self.max_active_cards:
            return False
            
        self._active_cards.append(card_id)
        return True
        
    def deactivate(self, card_id: str) -> bool:
        """
        Remove a card from active slots.
        
        Args:
            card_id: ID of the card to deactivate
            
        Returns:
            bool: True if successfully deactivated, False if card wasn't active
        """
        if card_id in self._active_cards:
            self._active_cards.remove(card_id)
            return True
        return False
        
    def get_cards_by_rarity(self, rarity: CardRarity) -> List[CardStack]:
        """Get all cards of a specific rarity."""
        return [stack for stack in self.cards.values() 
                if stack.card.rarity == rarity]
        
    def use_card(self, card_id: str) -> bool:
        """
        Attempt to use a card from the inventory.
        
        Args:
            card_id: ID of the card to use
            
        Returns:
            bool: True if card was successfully used, False otherwise
        """
        if card_id not in self.cards:
            return False
            
        card = self.cards[card_id].card
        if not card.can_use():
            return False
            
        if card.use():
            # If the card has limited uses and is now exhausted, remove it
            if card.max_uses > 0 and card.current_uses >= card.max_uses:
                self.remove_card(card_id)
            return True
            
        return False 