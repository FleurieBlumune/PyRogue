"""
Menu-related enums and types.
"""

from enum import Enum, auto

class MenuID(Enum):
    """Identifies different menu types in the game."""
    MAIN = auto()
    OPTIONS = auto()
    PAUSE = auto()
    HUD = auto()
    ACTIVITY_LOG = auto()  # Newly added for activity log
    INVENTORY = auto()      # Inventory management screen
    DECK_BUILDER = auto()   # Deck building interface
    CARD_DETAIL = auto()    # Card details view
    IN_GAME_CARDS = auto()  # In-game card display

class MenuItemType(Enum):
    """Types of menu items available in the menu system."""
    TEXT = auto()      # Static text
    HEADER = auto()    # Section header
    TOGGLE = auto()    # Toggle option
    SELECTOR = auto()  # Option selector
    ACTION = auto()    # Action button
    STAT = auto()      # Stat display
    LOG = auto()       # Log messages
    LIST = auto()      # Scrollable list

class MenuState(Enum):
    """States for menu navigation."""
    MAIN = auto()
    OPTIONS = auto()
    INVENTORY = auto()
    DECK_BUILDER = auto()
    CARD_DETAIL = auto()
    IN_GAME = auto() 