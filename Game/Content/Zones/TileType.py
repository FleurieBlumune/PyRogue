"""
Tile type definitions for zone terrain.

Defines the different types of tiles that can exist in a zone's terrain grid.
"""

from enum import Enum
from typing import Dict, Optional


class TileType(Enum):
    """
    Types of tiles that can exist in the game world.
    
    Each tile type has a character representation and properties that define
    its behavior in the game.
    """
    WALL = "#"
    FLOOR = "."
    DOOR = "D"
    WINDOW = "W"
    STAIRS_UP = "<"
    STAIRS_DOWN = ">"
    UNEXPLORED = "?"
    PREVIOUSLY_SEEN = "~"
    
    # ASCII to TileType mapping for quick lookup
    _char_to_tile: Dict[str, 'TileType'] = {}
    
    def __init__(self, char: str):
        """Initialize a tile type with its character representation."""
        self._char = char
        TileType._char_to_tile[char] = self
    
    @property
    def char(self) -> str:
        """Get the character representation of this tile type."""
        return self._char
    
    def blocks_movement(self) -> bool:
        """Determine if this tile type blocks movement."""
        return self in [TileType.WALL, TileType.DOOR, TileType.WINDOW]
    
    def blocks_vision(self) -> bool:
        """Determine if this tile type blocks vision."""
        return self in [TileType.WALL]
    
    def is_interactive(self) -> bool:
        """Determine if this tile type can be interacted with."""
        return self in [TileType.DOOR, TileType.STAIRS_UP, TileType.STAIRS_DOWN]
    
    @classmethod
    def from_char(cls, char: str) -> Optional['TileType']:
        """
        Convert a character representation to a TileType.
        
        Args:
            char: The character representation of a tile type.
            
        Returns:
            The corresponding TileType or None if no match is found.
        """
        return cls._char_to_tile.get(char) 