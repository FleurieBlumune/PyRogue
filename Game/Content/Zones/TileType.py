"""
Tile type definitions for zone terrain.

Defines the different types of tiles that can exist in a zone's terrain grid.
"""

from enum import Enum

class TileType(Enum):
    """Types of tiles that can exist in the game world."""
    WALL = "#"
    FLOOR = "."
    DOOR = "D"
    WATER = "~"
    STAIRS = ">" 