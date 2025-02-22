"""
Menu system enums.
"""

from enum import Enum, auto

class MenuState(Enum):
    """Menu state indicators."""
    MAIN = auto()
    OPTIONS = auto()
    PAUSE = auto()
    INVENTORY = auto()
    DECK_BUILDER = auto()
    CARD_DETAIL = auto()
    IN_GAME_CARDS = auto() 