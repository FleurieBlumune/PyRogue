"""
Handles loading card definitions from CSV files and creating Card instances.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional
from . import Card, CardEffect, CardRarity, AnimalType

class CardLoadError(Exception):
    """Raised when there is an error loading cards from CSV."""
    pass

class CardLoader:
    """
    Utility class for loading card definitions from CSV files and creating Card instances.
    
    The CSV file should have the following columns:
    - id: Unique integer identifier for the card
    - name: Display name of the card
    - description: Card description
    - rarity: One of COMMON, UNCOMMON, RARE, LEGENDARY
    - transformation: The AnimalType this card transforms into
    - duration: Duration in seconds (-1 for permanent)
    - success_rate: Float between 0.0 and 1.0
    - side_effects: Comma-separated list of side effects
    - max_uses: Integer number of uses (-1 for infinite)
    """
    
    @staticmethod
    def load_cards(csv_path: str = "Game/Content/Data/CSV/cards.csv") -> Dict[int, Card]:
        """
        Load all cards from the specified CSV file.
        
        Args:
            csv_path: Path to the CSV file containing card definitions
            
        Returns:
            Dict[int, Card]: Dictionary mapping card IDs to Card instances
            
        Raises:
            CardLoadError: If there is an error loading the cards
        """
        cards: Dict[int, Card] = {}
        
        try:
            print(f"Attempting to load cards from: {csv_path}")  # Debug
            csv_file = Path(csv_path)
            if not csv_file.exists():
                print(f"File not found at: {csv_file.absolute()}")  # Debug
                raise CardLoadError(f"Card data file not found: {csv_path}")
                
            print(f"Found CSV file at: {csv_file.absolute()}")  # Debug
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        print(f"Processing card: {row.get('id', 'Unknown')}")  # Debug
                        # Parse the side effects list
                        side_effects = [
                            effect.strip() 
                            for effect in row['side_effects'].strip('"').split(',')
                            if effect.strip()
                        ]
                        
                        # Create the card effect
                        effect = CardEffect(
                            transformation=AnimalType[row['transformation']],
                            duration=float(row['duration']),
                            success_rate=float(row['success_rate']),
                            side_effects=side_effects
                        )
                        
                        # Create the card
                        card = Card(
                            id=int(row['id']),  # Convert ID to integer
                            name=row['name'],
                            description=row['description'],
                            rarity=CardRarity[row['rarity']],
                            effect=effect,
                            max_uses=int(row['max_uses']),
                            current_uses=0  # New cards start with 0 uses
                        )
                        
                        cards[card.id] = card
                        print(f"Successfully loaded card: {card.name} (ID: {card.id})")  # Debug
                        
                    except (KeyError, ValueError) as e:
                        print(f"Error loading card {row.get('id', 'Unknown')}: {e}")  # Debug
                        raise CardLoadError(f"Error parsing card data: {row.get('id', 'Unknown')}: {str(e)}")
                        
        except Exception as e:
            print(f"Failed to load cards: {e}")  # Debug
            raise CardLoadError(f"Failed to load cards: {str(e)}")
            
        print(f"Successfully loaded {len(cards)} cards")  # Debug
        return cards
        
    @staticmethod
    def validate_card_data(card: Card) -> bool:
        """
        Validate a card's data for correctness.
        
        Args:
            card: The card to validate
            
        Returns:
            bool: True if the card data is valid
            
        Raises:
            CardLoadError: If the card data is invalid
        """
        if not 0.0 <= card.effect.success_rate <= 1.0:
            raise CardLoadError(f"Invalid success rate for card {card.id}: {card.effect.success_rate}")
            
        if card.effect.duration != -1 and card.effect.duration <= 0:
            raise CardLoadError(f"Invalid duration for card {card.id}: {card.effect.duration}")
            
        if card.max_uses != -1 and card.max_uses <= 0:
            raise CardLoadError(f"Invalid max uses for card {card.id}: {card.max_uses}")
            
        return True 