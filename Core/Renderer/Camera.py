"""
Camera system for managing view position and boundaries in the game world.

This module provides the Camera class which handles:
- View position tracking
- Boundary enforcement
- Smooth movement
- Screen-to-world coordinate conversion
"""

import pygame
import logging
from typing import Tuple

class Camera:
    """
    Manages the viewport position and movement in the game world.
    
    The camera maintains a position in world coordinates and provides methods
    to move the view and convert between screen and world coordinates.
    
    Attributes:
        x (int): X-axis position in world coordinates (pixels)
        y (int): Y-axis position in world coordinates (pixels)
        width (int): Viewport width in pixels
        height (int): Viewport height in pixels
        logger (Logger): Logger instance for debugging
    """
    
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """
        Initialize the camera at given coordinates with specified viewport dimensions.
        
        Args:
            x (int): Initial X position in world coordinates
            y (int): Initial Y position in world coordinates
            width (int): Viewport width in pixels
            height (int): Viewport height in pixels
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Camera initialized at ({x}, {y}) with viewport {width}x{height}")

    def move(self, dx: int, dy: int) -> None:
        """
        Move the camera by the specified offsets.
        
        Args:
            dx (int): X-axis movement delta in pixels
            dy (int): Y-axis movement delta in pixels
        """
        self.x += dx
        self.y += dy
        self.logger.debug(f"Camera moved by ({dx}, {dy}) to ({self.x}, {self.y})")

    def set_position(self, x: int, y: int) -> None:
        """
        Set the camera's absolute position.
        
        Args:
            x (int): New X position in world coordinates
            y (int): New Y position in world coordinates
        """
        self.x = x
        self.y = y
        self.logger.debug(f"Camera position set to ({x}, {y})")

    def update_viewport(self, width: int, height: int) -> None:
        """
        Update the viewport dimensions and ensure camera position remains valid.
        
        Args:
            width (int): New viewport width in pixels
            height (int): New viewport height in pixels
        """
        old_width, old_height = self.width, self.height
        self.width = width
        self.height = height
        self.logger.debug(f"Viewport updated from {old_width}x{old_height} to {width}x{height}")

    def world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_x (int): X position in world coordinates
            world_y (int): Y position in world coordinates
            
        Returns:
            Tuple[int, int]: Screen coordinates (x, y)
        """
        screen_x = world_x - self.x
        screen_y = world_y - self.y
        return screen_x, screen_y

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_x (int): X position in screen coordinates
            screen_y (int): Y position in screen coordinates
            
        Returns:
            Tuple[int, int]: World coordinates (x, y)
        """
        world_x = screen_x + self.x
        world_y = screen_y + self.y
        return world_x, world_y

    def get_visible_area(self, tile_size: int) -> pygame.Rect:
        """
        Calculate the visible area in tile coordinates.
        
        Args:
            tile_size (int): Size of a tile in pixels
            
        Returns:
            pygame.Rect: Rectangle representing visible area in tile coordinates
        """
        # Convert screen coordinates to tile coordinates
        start_x = max(0, self.x // tile_size)
        start_y = max(0, self.y // tile_size)
        
        # Calculate how many tiles fit in the visible area
        visible_tiles_x = self.width // tile_size + 2  # Add 2 for partial tiles at edges
        visible_tiles_y = self.height // tile_size + 2
        
        return pygame.Rect(start_x, start_y, visible_tiles_x, visible_tiles_y) 