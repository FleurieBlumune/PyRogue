"""
Manages the player's card inventory system, handling card collection, organization, and usage.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from . import Card, CardRarity
from .CardLoader import CardLoader, CardLoadError

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
    - Saving/loading inventory state
    
    This is a singleton class - only one instance should exist.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'InventoryManager':
        """Get the singleton instance of InventoryManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self, inventory_path: str = "Game/Content/Data/CSV/player_inventory.csv"):
        """
        Initialize the inventory manager.
        
        Args:
            inventory_path: Path to the inventory CSV file
        """
        # Ensure singleton pattern
        if InventoryManager._instance is not None:
            raise RuntimeError("InventoryManager is a singleton - use get_instance()")
            
        self.inventory_path = Path(inventory_path)
        self.cards: Dict[int, CardStack] = {}  # Changed to use integer keys
        self._active_cards: List[int] = []  # Changed to use integer IDs
        self.max_active_cards = 5
        
        # Load card templates first
        self.card_templates = CardLoader.load_cards()
        
        # Then try to load player inventory
        self.load_inventory()
    
    def save_inventory(self) -> None:
        """
        Save the current inventory state to CSV.
        
        The CSV will contain:
        - card_id: The unique integer identifier of the card
        - quantity: How many of this card the player has
        - current_uses: How many times the card has been used
        """
        try:
            # Ensure directory exists
            self.inventory_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.inventory_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['card_id', 'quantity', 'current_uses'])
                writer.writeheader()
                
                for card_id, stack in self.cards.items():
                    writer.writerow({
                        'card_id': card_id,
                        'quantity': stack.quantity,
                        'current_uses': stack.card.current_uses
                    })
        except Exception as e:
            raise CardLoadError(f"Failed to save inventory: {str(e)}")
    
    def load_inventory(self) -> None:
        """
        Load the inventory state from CSV.
        If the file doesn't exist, start with an empty inventory.
        """
        self.cards.clear()
        
        if not self.inventory_path.exists():
            return
            
        try:
            with open(self.inventory_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    card_id = int(row['card_id'])  # Convert to int
                    if card_id in self.card_templates:
                        # Create a copy of the template card
                        card = self.card_templates[card_id]
                        card_copy = Card(
                            id=card.id,
                            name=card.name,
                            description=card.description,
                            rarity=card.rarity,
                            effect=card.effect,
                            max_uses=card.max_uses,
                            current_uses=int(row['current_uses'])
                        )
                        self.cards[card_id] = CardStack(
                            card=card_copy,
                            quantity=int(row['quantity'])
                        )
        except Exception as e:
            raise CardLoadError(f"Failed to load inventory: {str(e)}")
    
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
            bool: True if successfully added
        """
        if card.id in self.cards:
            self.cards[card.id].quantity += quantity
            self.save_inventory()
            return True
            
        self.cards[card.id] = CardStack(card, quantity)
        self.save_inventory()
        return True
        
    def remove_card(self, card_id: int, quantity: int = 1) -> bool:  # Changed parameter type to int
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
                
        self.save_inventory()
        return True
        
    def set_active(self, card_id: int) -> bool:  # Changed parameter type to int
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
        
    def deactivate(self, card_id: int) -> bool:  # Changed parameter type to int
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
        
    def use_card(self, card_id: int) -> bool:  # Changed parameter type to int
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