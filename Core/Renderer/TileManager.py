"""
Tile management system for creating, scaling, and caching game tiles.

This module provides the TileManager class which handles:
- Tile surface creation
- Tile scaling based on zoom level
- Tile caching for performance
- Tile color and border management
"""

import pygame
from typing import Dict, Tuple
import logging
from Zone.TileType import TileType

class TileManager:
    """
    Manages the creation, scaling, and caching of tile surfaces.
    
    The TileManager creates and maintains tile surfaces for different zoom levels,
    handling the creation of base tiles and their scaled versions efficiently.
    
    Attributes:
        base_tile_size (int): Base size of tiles in pixels
        zoom_level (float): Current zoom level multiplier
        min_zoom (float): Minimum allowed zoom level
        max_zoom (float): Maximum allowed zoom level
        zoom_step (float): Amount to adjust zoom per step
        base_tiles (Dict[TileType, pygame.Surface]): Original unscaled tile surfaces
        scaled_tiles (Dict[TileType, pygame.Surface]): Currently scaled tile surfaces
        logger (Logger): Logger instance for debugging
    """
    
    # Define colors for different tile types
    TILE_COLORS = {
        TileType.WALL: (128, 128, 128),    # Gray
        TileType.FLOOR: (64, 64, 64),      # Dark Gray
        TileType.DOOR: (139, 69, 19),      # Brown
        TileType.WATER: (0, 0, 139),       # Blue
        TileType.STAIRS: (255, 215, 0),    # Gold
    }
    
    def __init__(self, base_tile_size: int = 32):
        """
        Initialize the tile manager with specified base tile size.
        
        Args:
            base_tile_size (int): Base size of tiles in pixels
        """
        self.base_tile_size = base_tile_size
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        self.zoom_step = 0.1
        self.logger = logging.getLogger(__name__)
        
        # Create initial tile surfaces
        self.base_tiles = self._create_base_tiles()
        self.scaled_tiles = self._scale_tiles()
        
        self.logger.debug(f"TileManager initialized with base size {base_tile_size}")

    def _create_base_tiles(self) -> Dict[TileType, pygame.Surface]:
        """
        Create the base tile surfaces for each tile type.
        
        Returns:
            Dict[TileType, pygame.Surface]: Mapping of tile types to their base surfaces
        """
        base_tiles = {}
        for tile_type, color in self.TILE_COLORS.items():
            base_tiles[tile_type] = self._create_tile(color)
        self.logger.debug(f"Created base tiles for {len(base_tiles)} tile types")
        return base_tiles

    def _create_tile(self, color: Tuple[int, int, int]) -> pygame.Surface:
        """
        Create a single tile surface with specified color and border.
        
        Args:
            color (Tuple[int, int, int]): RGB color tuple for the tile
            
        Returns:
            pygame.Surface: Created tile surface
        """
        surface = pygame.Surface((self.base_tile_size, self.base_tile_size))
        surface.fill(color)
        # Add a black border
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 1)
        return surface

    def _scale_tiles(self) -> Dict[TileType, pygame.Surface]:
        """
        Scale all base tiles to the current zoom level.
        
        Returns:
            Dict[TileType, pygame.Surface]: Mapping of tile types to their scaled surfaces
        """
        scaled_size = self.current_tile_size
        scaled = {
            tile_type: pygame.transform.scale(surface, (scaled_size, scaled_size))
            for tile_type, surface in self.base_tiles.items()
        }
        self.logger.debug(f"Scaled tiles to size {scaled_size}")
        return scaled

    @property
    def current_tile_size(self) -> int:
        """Current tile size in pixels, adjusted for zoom level."""
        return int(self.base_tile_size * self.zoom_level)

    def adjust_zoom(self, amount: float) -> bool:
        """
        Adjust the zoom level and update scaled tiles if changed.
        
        Args:
            amount (float): Change in zoom level (positive=in, negative=out)
            
        Returns:
            bool: True if zoom level changed, False otherwise
        """
        old_zoom = self.zoom_level
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, self.zoom_level + amount))
        
        if old_zoom != self.zoom_level:
            self.scaled_tiles = self._scale_tiles()
            self.logger.debug(f"Zoom adjusted from {old_zoom} to {self.zoom_level}")
            return True
        return False

    def get_tile_surface(self, tile_type: TileType) -> pygame.Surface:
        """
        Get the current scaled surface for a tile type.
        
        Args:
            tile_type (TileType): The type of tile to get
            
        Returns:
            pygame.Surface: The scaled surface for the specified tile type
        """
        return self.scaled_tiles[tile_type] 