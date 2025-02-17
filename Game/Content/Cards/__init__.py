"""
The Cards module handles the game's card-based inventory system.
Each card represents a serum injector that can transform entities into different animals.
"""

from typing import Dict, List, Optional, Type
from dataclasses import dataclass
from enum import Enum, auto

class CardRarity(Enum):
    """Defines the rarity levels for cards."""
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    LEGENDARY = auto()

class AnimalType(Enum):
    """Defines the possible animal transformations."""
    RAT = auto()
    CAT = auto()
    DOG = auto()
    WOLF = auto()
    BEAR = auto()
    # More animals can be added as needed

@dataclass
class CardEffect:
    """Represents the effect a card has when used."""
    transformation: AnimalType
    duration: float  # Duration in seconds, -1 for permanent
    success_rate: float  # 0.0 to 1.0
    side_effects: List[str]  # Potential side effects

@dataclass
class Card:
    """Base class for all cards in the game."""
    id: str
    name: str
    description: str
    rarity: CardRarity
    effect: CardEffect
    max_uses: int  # -1 for infinite
    current_uses: int
    
    def can_use(self) -> bool:
        """Check if the card can still be used."""
        return self.max_uses == -1 or self.current_uses < self.max_uses
    
    def use(self) -> bool:
        """Use the card if possible."""
        if not self.can_use():
            return False
        if self.max_uses > 0:
            self.current_uses += 1
        return True 