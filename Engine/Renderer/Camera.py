"""
Camera system for managing view position and boundaries in the game world.

This module provides the Camera class which handles:
- View position tracking and constraints
- Viewport management and boundaries
- Coordinate transformations
- Movement and zooming behavior
- Cursor-based zooming
"""

import pygame
import logging
from typing import Tuple, Optional
from dataclasses import dataclass
from Engine.Core.Events import EventManager, GameEventType

@dataclass
class Viewport:
    """
    Represents the visible area of the game world.
    
    Attributes:
        width (int): Width of the viewport in pixels
        height (int): Height of the viewport in pixels
        world_x (int): X position in world coordinates
        world_y (int): Y position in world coordinates
    """
    width: int
    height: int
    world_x: int
    world_y: int

    @property
    def center(self) -> Tuple[int, int]:
        """Get the center point of the viewport in world coordinates."""
        return (
            self.world_x + self.width // 2,
            self.world_y + self.height // 2
        )

class Camera:
    """
    Manages the viewport position and movement in the game world.
    
    The camera maintains its own viewport and position, handling all
    coordinate transformations and boundary constraints internally.
    
    Attributes:
        viewport (Viewport): Current viewport configuration
        logger (Logger): Logger instance for debugging
        event_manager (EventManager): Event system for camera updates
    """
    
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """
        Initialize the camera with viewport dimensions and position.
        
        Args:
            x (int): Initial X position in world coordinates
            y (int): Initial Y position in world coordinates
            width (int): Viewport width in pixels
            height (int): Viewport height in pixels
        """
        self.viewport = Viewport(width, height, x, y)
        self.logger = logging.getLogger(__name__)
        self.event_manager = EventManager.get_instance()
        self._world_bounds: Optional[pygame.Rect] = None
        self.logger.debug(f"Camera initialized at ({x}, {y}) with viewport {width}x{height}")

    def move(self, dx: int, dy: int) -> None:
        """
        Move the camera by the specified offsets, respecting world boundaries.
        
        Args:
            dx (int): X-axis movement delta in pixels
            dy (int): Y-axis movement delta in pixels
        """
        new_x = self.viewport.world_x + dx
        new_y = self.viewport.world_y + dy
        
        if self._world_bounds:
            # Constrain to world boundaries
            new_x = max(self._world_bounds.left, min(new_x, self._world_bounds.right - self.viewport.width))
            new_y = max(self._world_bounds.top, min(new_y, self._world_bounds.bottom - self.viewport.height))
        
        if new_x != self.viewport.world_x or new_y != self.viewport.world_y:
            self.viewport.world_x = new_x
            self.viewport.world_y = new_y
            self._emit_camera_moved()
            self.logger.debug(f"Camera moved to ({new_x}, {new_y})")

    def set_position(self, x: int, y: int) -> None:
        """
        Set the camera's absolute position, respecting world boundaries.
        
        Args:
            x (int): New X position in world coordinates
            y (int): New Y position in world coordinates
        """
        self.move(x - self.viewport.world_x, y - self.viewport.world_y)

    def set_world_bounds(self, bounds: pygame.Rect) -> None:
        """
        Set the world boundaries that constrain camera movement.
        
        Args:
            bounds (pygame.Rect): Rectangle defining the world boundaries
        """
        self._world_bounds = bounds
        self.logger.debug(f"World bounds set to {bounds}")
        
        # Ensure current position respects new bounds
        self.set_position(self.viewport.world_x, self.viewport.world_y)

    def update_viewport(self, width: int, height: int) -> None:
        """
        Update the viewport dimensions and ensure camera position remains valid.
        
        Args:
            width (int): New viewport width in pixels
            height (int): New viewport height in pixels
        """
        # Store the center point before changing dimensions
        old_center_x, old_center_y = self.viewport.center
        
        # Update dimensions
        old_width, old_height = self.viewport.width, self.viewport.height
        self.viewport.width = width
        self.viewport.height = height
        
        # Adjust position to maintain the same center point
        self.viewport.world_x = old_center_x - width // 2
        self.viewport.world_y = old_center_y - height // 2
        
        # Ensure position still respects world bounds
        if self._world_bounds:
            self.set_position(self.viewport.world_x, self.viewport.world_y)
            
        self._emit_viewport_updated()
        self.logger.debug(f"Viewport updated from {old_width}x{old_height} to {width}x{height}")

    def adjust_for_zoom(self, old_tile_size: int, new_tile_size: int, cursor_pos: Optional[Tuple[int, int]] = None) -> None:
        """
        Adjust camera position when zooming to maintain either the cursor position or view center.
        
        Args:
            old_tile_size (int): Previous tile size in pixels
            new_tile_size (int): New tile size in pixels
            cursor_pos (Optional[Tuple[int, int]]): Screen coordinates of cursor position to zoom around.
                                                   If None, zooms around viewport center.
        """
        if cursor_pos is None:
            # Get the center point in tile coordinates before zoom
            center_x, center_y = self.viewport.center
            tile_center_x = center_x / old_tile_size
            tile_center_y = center_y / old_tile_size
            
            # Calculate new world position to maintain the same center in tile coordinates
            new_center_x = int(tile_center_x * new_tile_size)
            new_center_y = int(tile_center_y * new_tile_size)
            
            # Set new position maintaining the center point
            self.set_position(
                new_center_x - self.viewport.width // 2,
                new_center_y - self.viewport.height // 2
            )
        else:
            # Convert cursor screen position to world coordinates before zoom
            cursor_world_x, cursor_world_y = self.screen_to_world(*cursor_pos)
            
            # Convert cursor world position to tile coordinates
            cursor_tile_x = cursor_world_x / old_tile_size
            cursor_tile_y = cursor_world_y / old_tile_size
            
            # Calculate new world position of cursor after zoom
            new_cursor_world_x = int(cursor_tile_x * new_tile_size)
            new_cursor_world_y = int(cursor_tile_y * new_tile_size)
            
            # Calculate the offset needed to keep cursor at the same screen position
            dx = new_cursor_world_x - cursor_world_x
            dy = new_cursor_world_y - cursor_world_y
            
            # Adjust camera position to maintain cursor screen position
            self.set_position(
                self.viewport.world_x + dx,
                self.viewport.world_y + dy
            )

    def world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_x (int): X position in world coordinates
            world_y (int): Y position in world coordinates
            
        Returns:
            Tuple[int, int]: Screen coordinates (x, y)
        """
        screen_x = world_x - self.viewport.world_x
        screen_y = world_y - self.viewport.world_y
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
        world_x = screen_x + self.viewport.world_x
        world_y = screen_y + self.viewport.world_y
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
        start_x = max(0, self.viewport.world_x // tile_size)
        start_y = max(0, self.viewport.world_y // tile_size)
        
        # Calculate how many tiles fit in the visible area
        visible_tiles_x = self.viewport.width // tile_size + 2  # Add 2 for partial tiles at edges
        visible_tiles_y = self.viewport.height // tile_size + 2
        
        return pygame.Rect(start_x, start_y, visible_tiles_x, visible_tiles_y)

    def _emit_camera_moved(self) -> None:
        """Emit event when camera position changes."""
        self.event_manager.emit(GameEventType.CAMERA_MOVED, 
                              x=self.viewport.world_x, 
                              y=self.viewport.world_y)

    def _emit_viewport_updated(self) -> None:
        """Emit event when viewport dimensions change."""
        self.event_manager.emit(GameEventType.VIEWPORT_UPDATED,
                              width=self.viewport.width,
                              height=self.viewport.height) 