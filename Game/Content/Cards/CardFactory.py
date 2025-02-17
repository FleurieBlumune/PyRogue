"""
Factory for creating various types of serum injector cards.
"""

from typing import Dict, Optional
from . import Card, CardEffect, CardRarity, AnimalType

class CardFactory:
    """
    Factory class for creating serum injector cards.
    
    This class provides methods to create various types of serum injector cards
    with predefined effects and properties.
    """
    
    @staticmethod
    def create_basic_injector(animal_type: AnimalType) -> Card:
        """Create a basic serum injector card for the specified animal type."""
        animal_name = animal_type.name.lower().capitalize()
        
        effect = CardEffect(
            transformation=animal_type,
            duration=-1,  # Permanent transformation
            success_rate=0.75,  # 75% success rate
            side_effects=["Mild disorientation", "Temporary confusion"]
        )
        
        return Card(
            id=f"basic_{animal_type.name.lower()}_injector",
            name=f"Basic {animal_name} Serum",
            description=f"A standard serum that transforms the target into a {animal_name.lower()}. "
                       f"Success rate: 75%. Permanent effect.",
            rarity=CardRarity.COMMON,
            effect=effect,
            max_uses=3,
            current_uses=0
        )
    
    @staticmethod
    def create_advanced_injector(animal_type: AnimalType) -> Card:
        """Create an advanced serum injector card with higher success rate."""
        animal_name = animal_type.name.lower().capitalize()
        
        effect = CardEffect(
            transformation=animal_type,
            duration=-1,  # Permanent transformation
            success_rate=0.9,  # 90% success rate
            side_effects=["Minor discomfort"]
        )
        
        return Card(
            id=f"advanced_{animal_type.name.lower()}_injector",
            name=f"Advanced {animal_name} Serum",
            description=f"A refined serum that transforms the target into a {animal_name.lower()}. "
                       f"Success rate: 90%. Permanent effect.",
            rarity=CardRarity.UNCOMMON,
            effect=effect,
            max_uses=2,
            current_uses=0
        )
    
    @staticmethod
    def create_experimental_injector(animal_type: AnimalType) -> Card:
        """Create an experimental serum injector with unique properties."""
        animal_name = animal_type.name.lower().capitalize()
        
        effect = CardEffect(
            transformation=animal_type,
            duration=300,  # 5 minutes temporary transformation
            success_rate=1.0,  # 100% success rate
            side_effects=["Enhanced abilities", "Unpredictable behavior"]
        )
        
        return Card(
            id=f"experimental_{animal_type.name.lower()}_injector",
            name=f"Experimental {animal_name} Serum",
            description=f"An unstable but powerful serum that temporarily transforms the target "
                       f"into a {animal_name.lower()}. Duration: 5 minutes. Success rate: 100%.",
            rarity=CardRarity.RARE,
            effect=effect,
            max_uses=1,
            current_uses=0
        )
    
    @staticmethod
    def create_masterwork_injector(animal_type: AnimalType) -> Card:
        """Create a masterwork serum injector with perfect properties."""
        animal_name = animal_type.name.lower().capitalize()
        
        effect = CardEffect(
            transformation=animal_type,
            duration=-1,  # Permanent transformation
            success_rate=1.0,  # 100% success rate
            side_effects=[]  # No side effects
        )
        
        return Card(
            id=f"masterwork_{animal_type.name.lower()}_injector",
            name=f"Masterwork {animal_name} Serum",
            description=f"A perfect serum that transforms the target into a {animal_name.lower()}. "
                       f"Success rate: 100%. Permanent effect. No side effects.",
            rarity=CardRarity.LEGENDARY,
            effect=effect,
            max_uses=5,
            current_uses=0
        ) 