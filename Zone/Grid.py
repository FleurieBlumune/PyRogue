"""
Grid and map management for game zones.

Provides terrain management and spatial queries for game zones, including:
- Tile type management
- Boundary checking
- Passability queries
- Grid dimensions
"""

import logging
from .TileType import TileType

class Grid:
    """
    Base grid class that manages a 2D array of tiles.
    
    Attributes:
        width (int): Width of the grid in tiles
        height (int): Height of the grid in tiles
        tiles (List[List[TileType]]): 2D array of tile types
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize a grid with given dimensions.
        
        Args:
            width (int): Width of the grid in tiles
            height (int): Height of the grid in tiles
        """
        self.width = width
        self.height = height
        self.tiles = [[TileType.WALL for _ in range(width)] for _ in range(height)]

class TerrainGrid:
    """
    Handles the terrain grid component of a zone including tile management.
    
    Manages a 2D grid of tiles that forms the base terrain of a game zone.
    Provides methods for querying and modifying the terrain, checking boundaries,
    and determining passability.
    
    Attributes:
        grid (Grid): The underlying 2D grid of tiles
        logger (Logger): Logger instance for debugging
    """
    
    def __init__(self, width: int = 100, height: int = 100):
        """
        Initialize a new terrain grid with specified dimensions.
        
        Args:
            width (int): Width of the grid in tiles
            height (int): Height of the grid in tiles
        """
        self.grid = Grid(width, height)
        self.logger = logging.getLogger(__name__)
        
    def is_in_bounds(self, x: int, y: int) -> bool:
        """
        Check if coordinates are within grid bounds.
        
        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            
        Returns:
            bool: True if coordinates are within bounds
        """
        return 0 <= x < self.grid.width and 0 <= y < self.grid.height
        
    def set_tile(self, x: int, y: int, tile_type: TileType) -> None:
        """
        Set a tile type at the given coordinates if in bounds.
        
        Args:
            x (int): X coordinate of tile
            y (int): Y coordinate of tile
            tile_type (TileType): Type of tile to set
        """
        if self.is_in_bounds(x, y):
            self.grid.tiles[y][x] = tile_type
            
    def get_tile(self, x: int, y: int) -> TileType:
        """
        Get the tile type at the given coordinates.
        
        Args:
            x (int): X coordinate of tile
            y (int): Y coordinate of tile
            
        Returns:
            TileType: Type of tile at coordinates, WALL if out of bounds
        """
        if self.is_in_bounds(x, y):
            return self.grid.tiles[y][x]
        return TileType.WALL  # Default to wall for out of bounds
        
    def is_passable_terrain(self, x: int, y: int) -> bool:
        """
        Check if the terrain at given coordinates is passable.
        
        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            
        Returns:
            bool: True if terrain is passable (floor, door, or stairs)
        """
        if not self.is_in_bounds(x, y):
            return False
        return self.grid.tiles[y][x] in {TileType.FLOOR, TileType.DOOR, TileType.STAIRS}
        
    @property
    def width(self) -> int:
        """Width of the grid in tiles."""
        return self.grid.width
        
    @property
    def height(self) -> int:
        """Height of the grid in tiles."""
        return self.grid.height 