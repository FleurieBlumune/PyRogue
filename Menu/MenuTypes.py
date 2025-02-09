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

class MenuItemType(Enum):
    """Types of menu items available in the menu system."""
    TEXT = auto()
    TOGGLE = auto()
    SELECTOR = auto()
    ACTION = auto()
    STAT = auto()  # New type for displaying stats

class MenuState(Enum):
    """States for menu navigation."""
    MAIN = auto()
    OPTIONS = auto() 