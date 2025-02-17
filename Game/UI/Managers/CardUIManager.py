"""
Manages the UI for card-related features including inventory and deck building.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from Engine.UI.MenuSystem.MenuTypes import MenuID, MenuState
from Game.Content.Cards import Card, CardRarity
from Game.Content.Cards.InventoryManager import InventoryManager
from Game.Content.Cards.DeckManager import DeckManager

@dataclass
class CardUIState:
    """Tracks the state of card-related UI elements."""
    selected_card: Optional[Card] = None
    deck_in_progress: List[str] = None  # List of card IDs for deck being built
    scroll_position: int = 0
    filter_rarity: Optional[CardRarity] = None

class CardUIManager:
    """
    Manages card-related UI interactions including:
    - Inventory display
    - Deck building
    - Card details
    - In-game card display
    """
    
    def __init__(self, inventory: InventoryManager, deck: DeckManager):
        """
        Initialize the card UI manager.
        
        Args:
            inventory: The player's inventory manager
            deck: The player's deck manager
        """
        self.inventory = inventory
        self.deck = deck
        self.state = CardUIState()
        self.state.deck_in_progress = []
        
    def get_action_handlers(self) -> Dict[str, Callable]:
        """
        Get all action handlers for card-related UI.
        
        Returns:
            Dict mapping action names to handler functions
        """
        return {
            # Inventory handlers
            "GetInventoryCards": self._get_inventory_cards,
            "SelectCard": self._select_card,
            
            # Deck building handlers
            "GetAvailableCards": self._get_available_cards,
            "GetCurrentDeck": self._get_current_deck,
            "AddCardToDeck": self._add_card_to_deck,
            "RemoveCardFromDeck": self._remove_card_from_deck,
            "SaveDeck": self._save_deck,
            "CanSaveDeck": self._can_save_deck,
            
            # Card detail handlers
            "GetCardStats": self._get_card_stats,
            "UseCard": self._use_card,
            "CanUseCard": self._can_use_card,
            
            # In-game handlers
            "GetCurrentHand": self._get_current_hand,
            "SelectHandCard": self._select_hand_card,
            "GetDrawPileCount": self._get_draw_pile_count,
            "GetDiscardPileCount": self._get_discard_pile_count
        }
        
    def _get_inventory_cards(self) -> List[str]:
        """Get formatted strings for inventory card display."""
        cards = []
        for card_id, stack in self.inventory.cards.items():
            card = stack.card
            count = stack.quantity
            rarity_symbol = self._get_rarity_symbol(card.rarity)
            cards.append(f"{rarity_symbol} {card.name} (x{count})")
        return cards
        
    def _get_rarity_symbol(self, rarity: CardRarity) -> str:
        """Get a symbol representing card rarity."""
        return {
            CardRarity.COMMON: "◆",      # White diamond
            CardRarity.UNCOMMON: "◆",    # Green diamond
            CardRarity.RARE: "◆",        # Blue diamond
            CardRarity.LEGENDARY: "★"    # Gold star
        }[rarity]
        
    def _select_card(self, index: int) -> None:
        """Handle card selection from inventory."""
        card_id = list(self.inventory.cards.keys())[index]
        self.state.selected_card = self.inventory.cards[card_id].card
        
    def _get_available_cards(self) -> List[str]:
        """Get formatted strings for available cards in deck builder."""
        cards = []
        for card_id, stack in self.inventory.cards.items():
            if card_id not in self.state.deck_in_progress:
                card = stack.card
                rarity_symbol = self._get_rarity_symbol(card.rarity)
                cards.append(f"{rarity_symbol} {card.name}")
        return cards
        
    def _get_current_deck(self) -> List[str]:
        """Get formatted strings for current deck being built."""
        return [
            f"{self._get_rarity_symbol(self.inventory.cards[card_id].card.rarity)} "
            f"{self.inventory.cards[card_id].card.name}"
            for card_id in self.state.deck_in_progress
        ]
        
    def _add_card_to_deck(self, index: int) -> None:
        """Add a card to the deck being built."""
        available_cards = [
            card_id for card_id in self.inventory.cards.keys()
            if card_id not in self.state.deck_in_progress
        ]
        if index < len(available_cards):
            self.state.deck_in_progress.append(available_cards[index])
            
    def _remove_card_from_deck(self, index: int) -> None:
        """Remove a card from the deck being built."""
        if index < len(self.state.deck_in_progress):
            self.state.deck_in_progress.pop(index)
            
    def _save_deck(self) -> None:
        """Save the current deck being built."""
        if self._can_save_deck():
            self.deck.build_deck(self.state.deck_in_progress)
            self.state.deck_in_progress = []
            
    def _can_save_deck(self) -> bool:
        """Check if the current deck can be saved."""
        return (0 < len(self.state.deck_in_progress) <= DeckManager.MAX_DECK_SIZE)
        
    def _get_card_stats(self) -> str:
        """Get formatted card stats for the selected card."""
        card = self.state.selected_card
        if not card:
            return ""
            
        stats = [
            f"Rarity: {card.rarity.name.title()}",
            f"Success Rate: {int(card.effect.success_rate * 100)}%",
            f"Duration: {'Permanent' if card.effect.duration == -1 else f'{int(card.effect.duration)}s'}",
            f"Uses: {card.max_uses - card.current_uses}/{card.max_uses}"
        ]
        
        if card.effect.side_effects:
            stats.append(f"Side Effects: {', '.join(card.effect.side_effects)}")
            
        return "\n".join(stats)
        
    def _use_card(self) -> None:
        """Use the selected card."""
        if self._can_use_card():
            self.deck.use_card(self.state.selected_card)
            self.state.selected_card = None
            
    def _can_use_card(self) -> bool:
        """Check if the selected card can be used."""
        return (
            self.state.selected_card is not None and
            self.state.selected_card in self.deck.state.hand
        )
        
    def _get_current_hand(self) -> List[str]:
        """Get formatted strings for cards in hand."""
        return [
            f"{self._get_rarity_symbol(card.rarity)} {card.name}"
            for card in self.deck.state.hand
        ]
        
    def _select_hand_card(self, index: int) -> None:
        """Handle card selection from hand."""
        if index < len(self.deck.state.hand):
            self.state.selected_card = self.deck.state.hand[index]
            
    def _get_draw_pile_count(self) -> str:
        """Get the number of cards in the draw pile."""
        return f"Draw Pile: {len(self.deck.state.draw_pile)}"
        
    def _get_discard_pile_count(self) -> str:
        """Get the number of cards in the discard pile."""
        return f"Discard Pile: {len(self.deck.state.discard_pile)}" 