"""
Tile type definitions for zone terrain.

Defines the different types of tiles that can exist in a zone's terrain grid.
Each tile type has an associated character representation and color.
"""

from enum import Enum
from typing import Tuple

class TileType(Enum):
    """
    Types of tiles that can exist in the game world.
    
    Each tile type has:
    - A character representation for ASCII display
    - An RGB color tuple for graphical display
    """
    WALL = ("#", (128, 128, 128))    # Gray
    FLOOR = (".", (64, 64, 64))      # Dark Gray
    DOOR = ("D", (139, 69, 19))      # Brown
    WATER = ("~", (0, 0, 139))       # Blue
    STAIRS = (">", (255, 215, 0))    # Gold
    
    def __init__(self, char: str, color: Tuple[int, int, int]):
        """
        Initialize a tile type with its display properties.
        
        Args:
            char (str): ASCII character representation
            color (Tuple[int, int, int]): RGB color tuple
        """
        self.char = char
        self._color = color
        
    @property
    def color(self) -> Tuple[int, int, int]:
        """Get the RGB color tuple for this tile type."""
        return self._color 