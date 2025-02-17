"""
Tests for the deck management system.
"""

import pytest
from Game.Content.Cards import Card, CardEffect, CardRarity, AnimalType
from Game.Content.Cards.InventoryManager import InventoryManager
from Game.Content.Cards.DeckManager import DeckManager, DeckError

@pytest.fixture
def test_cards():
    """Create a set of test cards."""
    cards = [
        Card(
            id="test_card_1",
            name="Test Card 1",
            description="A test card",
            rarity=CardRarity.COMMON,
            effect=CardEffect(
                transformation=AnimalType.RAT,
                duration=-1,
                success_rate=0.75,
                side_effects=["test_effect"]
            ),
            max_uses=3,
            current_uses=0
        ),
        Card(
            id="test_card_2",
            name="Test Card 2",
            description="Another test card",
            rarity=CardRarity.UNCOMMON,
            effect=CardEffect(
                transformation=AnimalType.CAT,
                duration=-1,
                success_rate=0.9,
                side_effects=["test_effect"]
            ),
            max_uses=2,
            current_uses=0
        )
    ]
    return cards

@pytest.fixture
def inventory(test_cards):
    """Create a test inventory with some cards."""
    inventory = InventoryManager()
    for card in test_cards:
        inventory.add_card(card)
    return inventory

@pytest.fixture
def deck_manager(inventory):
    """Create a test deck manager."""
    return DeckManager(inventory)

def test_build_deck(deck_manager, test_cards):
    """Test building a deck from inventory cards."""
    card_ids = [card.id for card in test_cards]
    deck_manager.build_deck(card_ids)
    
    assert deck_manager.get_deck_size() == len(test_cards)
    draw, discard, hand = deck_manager.get_card_counts()
    assert draw == len(test_cards)
    assert discard == 0
    assert hand == 0

def test_draw_hand(deck_manager, test_cards):
    """Test drawing a hand of cards."""
    card_ids = [card.id for card in test_cards]
    deck_manager.build_deck(card_ids)
    
    drawn_cards = deck_manager.draw_hand()
    assert len(drawn_cards) == len(test_cards)  # Since we have fewer test cards than hand size
    assert len(deck_manager.state.hand) == len(drawn_cards)
    assert len(deck_manager.state.draw_pile) == 0

def test_discard_card(deck_manager, test_cards):
    """Test discarding a card from hand."""
    card_ids = [card.id for card in test_cards]
    deck_manager.build_deck(card_ids)
    deck_manager.draw_hand()
    
    card_to_discard = deck_manager.state.hand[0]
    deck_manager.discard_card(card_to_discard)
    
    assert card_to_discard not in deck_manager.state.hand
    assert card_to_discard in deck_manager.state.discard_pile
    assert len(deck_manager.state.hand) == len(test_cards) - 1

def test_shuffle_discard_into_draw(deck_manager, test_cards):
    """Test shuffling the discard pile back into the draw pile."""
    card_ids = [card.id for card in test_cards]
    deck_manager.build_deck(card_ids)
    deck_manager.draw_hand()
    deck_manager.discard_hand()
    
    assert len(deck_manager.state.discard_pile) == len(test_cards)
    assert len(deck_manager.state.draw_pile) == 0
    
    deck_manager.shuffle_discard_into_draw()
    
    assert len(deck_manager.state.discard_pile) == 0
    assert len(deck_manager.state.draw_pile) == len(test_cards)

def test_use_card(deck_manager, test_cards):
    """Test using a card from hand."""
    card_ids = [card.id for card in test_cards]
    deck_manager.build_deck(card_ids)
    deck_manager.draw_hand()
    
    card_to_use = deck_manager.state.hand[0]
    initial_uses = card_to_use.current_uses
    result = deck_manager.use_card(card_to_use)
    
    assert result is True
    assert card_to_use not in deck_manager.state.hand
    assert card_to_use in deck_manager.state.discard_pile
    assert card_to_use.current_uses == initial_uses + 1

def test_use_consumed_card(deck_manager, test_cards):
    """Test using a card that gets consumed (reaches max uses)."""
    # Create a card with only 1 use remaining
    test_card = test_cards[0]
    test_card.current_uses = test_card.max_uses - 1
    
    deck_manager.build_deck([test_card.id])
    deck_manager.draw_hand()
    
    card_to_use = deck_manager.state.hand[0]
    result = deck_manager.use_card(card_to_use)
    
    assert result is True
    assert card_to_use not in deck_manager.state.hand
    assert card_to_use not in deck_manager.state.discard_pile  # Card should be consumed
    assert card_to_use.id not in deck_manager.state.deck_list  # Card should be removed from deck
    assert card_to_use.id not in deck_manager.inventory.cards  # Card should be removed from inventory

def test_deck_size_limit(deck_manager):
    """Test that deck size limit is enforced."""
    # Create more cards than the maximum deck size
    card_ids = [f"test_card_{i}" for i in range(DeckManager.MAX_DECK_SIZE + 1)]
    
    with pytest.raises(DeckError):
        deck_manager.build_deck(card_ids)

def test_invalid_card_id(deck_manager):
    """Test handling of invalid card IDs."""
    with pytest.raises(DeckError):
        deck_manager.build_deck(["nonexistent_card"])

def test_discard_invalid_card(deck_manager, test_cards):
    """Test discarding a card that isn't in hand."""
    card_ids = [card.id for card in test_cards]
    deck_manager.build_deck(card_ids)
    
    with pytest.raises(DeckError):
        deck_manager.discard_card(test_cards[0])  # Card not in hand yet 