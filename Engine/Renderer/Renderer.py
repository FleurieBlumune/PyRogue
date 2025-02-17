"""
Main rendering system that coordinates all visual aspects of the game.

This module provides the Renderer class which:
- Manages the game window and display
- Coordinates camera, tiles, and entity rendering
- Handles window resizing and fullscreen
- Manages the game viewport and zoom
"""

import pygame
import logging
from typing import Optional, Tuple
from Engine.Core.WindowManager import WindowManager
from Engine.Renderer.Camera import Camera
from Engine.Renderer.TileManager import TileManager
from Engine.Renderer.EntityRenderer import EntityRenderer
from Engine.Core.Events import EventManager, GameEventType
from Game.Content.Zones.Zone import Zone
from Game.Content.Entities.Entity import Entity

class Renderer:
    """
    Main rendering system that coordinates all visual components.
    
    The Renderer manages the game window and coordinates the various
    rendering subsystems (camera, tiles, entities) to produce the final
    game display.
    
    Attributes:
        width (int): Window width in pixels
        height (int): Window height in pixels
        screen (Surface): Pygame display surface
        camera (Camera): View position tracker
        tile_manager (TileManager): Tile creation and scaling manager
        entity_renderer (EntityRenderer): Entity visualization manager
        game_area_width (int): Width of the game rendering area
        logger (Logger): Logger instance for debugging
    """
    
    def __init__(self, width: int, height: int, fullscreen: bool = False):
        """
        Initialize the renderer with specified dimensions.
        
        Args:
            width (int): Initial window width in pixels
            height (int): Initial window height in pixels
            fullscreen (bool): Whether to start in fullscreen mode
        """
        self.logger = logging.getLogger(__name__)
        self.event_manager = EventManager.get_instance()
        
        # Initialize window management
        self.window_manager = WindowManager()
        self.width = width
        self.height = height
        self.screen = self.window_manager.set_mode(width, height, fullscreen)
        
        # Initialize game area (excluding UI elements)
        self.game_area_width = int(width * 2/3)
        
        # Initialize rendering components
        self.camera = Camera(0, 0, self.game_area_width, height)
        self.tile_manager = TileManager()
        self.entity_renderer = EntityRenderer(self.camera)
        
        # Set up input handler reference (will be set later)
        self._input_handler = None
        
        # Subscribe to camera events
        self.event_manager.subscribe(GameEventType.CAMERA_MOVED, self._on_camera_moved)
        self.event_manager.subscribe(GameEventType.VIEWPORT_UPDATED, self._on_viewport_updated)
        
        self.logger.debug(f"Renderer initialized with dimensions {width}x{height}")

    def _on_camera_moved(self, **kwargs) -> None:
        """Handle camera movement events."""
        # Force a redraw when camera moves
        if hasattr(self, '_input_handler') and self._input_handler.zone:
            self.render(self._input_handler.zone)

    def _on_viewport_updated(self, **kwargs) -> None:
        """Handle viewport update events."""
        # Update related systems when viewport changes
        if hasattr(self, 'entity_renderer'):
            self.entity_renderer.update_tile_size(self.tile_manager.current_tile_size)

    @property
    def zoom_step(self) -> float:
        """Get the zoom step amount from tile manager."""
        return self.tile_manager.zoom_step

    @property
    def current_zoom(self) -> float:
        """Get the current zoom level from tile manager."""
        return self.tile_manager.zoom_level

    def handle_resize(self, new_width: int, new_height: int) -> None:
        """
        Handle window resize events.
        
        Args:
            new_width (int): New window width in pixels
            new_height (int): New window height in pixels
        """
        try:
            # Update window manager
            self.window_manager.handle_resize(new_width, new_height)
            
            # Get actual screen dimensions after resize
            self.width, self.height = self.window_manager.get_screen_size()
            self.screen = pygame.display.get_surface()
            
            # Maintain game area ratio unless manually set
            if not hasattr(self, '_manual_game_area_width'):
                old_game_area = self.game_area_width
                new_game_area = int(self.width * 2/3)
                
                # Only update if the change is significant
                if abs(old_game_area - new_game_area) > 10:
                    self.game_area_width = new_game_area
            
            # Update camera viewport
            self.camera.update_viewport(self.game_area_width, self.height)
            
            # Force a screen refresh
            pygame.display.flip()
            
            self.logger.debug(f"Resized to {self.width}x{self.height}, game area: {self.game_area_width}")
            
        except Exception as e:
            self.logger.error(f"Error handling resize: {e}", exc_info=True)
            # Try to recover by forcing a new display surface
            self.screen = pygame.display.set_mode(
                (self.width, self.height),
                pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
            )

    def set_game_area_width(self, width: int) -> None:
        """
        Set the width of the game rendering area.
        
        Args:
            width (int): New width in pixels
        """
        self.game_area_width = width
        self._manual_game_area_width = True
        self.camera.update_viewport(width, self.height)
        self.logger.debug(f"Game area width set to {width}")

    def adjust_zoom(self, amount: float) -> None:
        """
        Adjust the zoom level and update related components.
        
        Args:
            amount (float): Change in zoom level (positive=in, negative=out)
        """
        # Store old tile size for camera adjustment
        old_tile_size = self.tile_manager.current_tile_size
        
        if self.tile_manager.adjust_zoom(amount):
            # Update entity renderer with new tile size
            new_tile_size = self.tile_manager.current_tile_size
            self.entity_renderer.update_tile_size(new_tile_size)
            
            # Get current mouse position for cursor-based zooming
            cursor_pos = pygame.mouse.get_pos()
            # Only use cursor position if it's within the game area
            if cursor_pos[0] <= self.game_area_width:
                self.camera.adjust_for_zoom(old_tile_size, new_tile_size, cursor_pos)
            else:
                # Fall back to center-based zooming if cursor is outside game area
                self.camera.adjust_for_zoom(old_tile_size, new_tile_size)
            
            # Emit zoom changed event
            self.event_manager.emit(GameEventType.ZOOM_CHANGED, 
                                  level=self.current_zoom,
                                  tile_size=new_tile_size)
            
            self.logger.debug(f"Zoom adjusted by {amount}, new level: {self.current_zoom}")
            
            # Recenter on player if we have one and aren't in manual camera control
            if (hasattr(self, '_input_handler') and 
                not self._input_handler.manual_camera_control and
                isinstance(self._input_handler.zone, Zone) and 
                self._input_handler.zone.player):
                self.center_on_entity(self._input_handler.zone.player)

    def center_on_entity(self, entity: Entity) -> None:
        """
        Center the camera on a specific entity.
        
        Args:
            entity (Entity): The entity to center on
        """
        # Only center if we're not in manual camera control mode
        if not self._input_handler or not self._input_handler.manual_camera_control:
            # Calculate world coordinates
            world_x = entity.position.x * self.tile_manager.current_tile_size
            world_y = entity.position.y * self.tile_manager.current_tile_size
            
            # Center camera on entity
            self.camera.set_position(
                world_x - self.game_area_width // 2,
                world_y - self.height // 2
            )
            self.logger.debug(f"Centered camera on entity at ({world_x}, {world_y})")

    def render(self, zone: Zone) -> None:
        """
        Render the current zone and update the display.
        
        Args:
            zone (Zone): The zone to render
        """
        self.render_without_flip(zone)
        pygame.display.flip()

    def render_without_flip(self, zone: Zone) -> None:
        """
        Render the current zone without updating the display.
        
        Args:
            zone (Zone): The zone to render
        """
        try:
            # Create a clip rect that uses the current game area width
            game_area = pygame.Rect(0, 0, self.game_area_width, self.height)
            old_clip = self.screen.get_clip()
            self.screen.set_clip(game_area)
            
            # Get visible area
            visible_area = self.camera.get_visible_area(self.tile_manager.current_tile_size)
            
            # Draw visible tiles
            self._render_tiles(zone, visible_area)
            
            # Draw visible entities
            self._render_entities(zone, visible_area)
            
            # Restore original clip rect
            self.screen.set_clip(old_clip)
            
        except Exception as e:
            self.logger.error(f"Error rendering frame: {e}", exc_info=True)

    def _render_tiles(self, zone: Zone, visible_area: pygame.Rect) -> None:
        """
        Render the visible tiles in the zone.
        
        Args:
            zone (Zone): The zone containing the tiles
            visible_area (pygame.Rect): The visible area in tile coordinates
        """
        try:
            for y in range(visible_area.top, visible_area.bottom + 1):
                for x in range(visible_area.left, visible_area.right + 1):
                    tile_type = zone.grid.get_tile(x, y)
                    tile_surface = self.tile_manager.get_tile_surface(tile_type)
                    
                    # Convert tile position to screen coordinates
                    world_x = x * self.tile_manager.current_tile_size
                    world_y = y * self.tile_manager.current_tile_size
                    screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
                    
                    self.screen.blit(tile_surface, (screen_x, screen_y))
                    
        except Exception as e:
            self.logger.error(f"Error rendering tiles: {e}", exc_info=True)

    def _render_entities(self, zone: Zone, visible_area: pygame.Rect) -> None:
        """
        Render the visible entities in the zone.
        
        Args:
            zone (Zone): The zone containing the entities
            visible_area (pygame.Rect): The visible area in tile coordinates
        """
        try:
            visible_entities = zone.get_entities_in_area(visible_area)
            self.entity_renderer.render_entities(
                self.screen,
                visible_entities,
                highlighted_entity=zone.player if hasattr(zone, 'player') else None
            )
        except Exception as e:
            self.logger.error(f"Error rendering entities: {e}", exc_info=True)

    def set_input_handler(self, input_handler) -> None:
        """
        Set the input handler reference for camera control checks.
        
        Args:
            input_handler: The input handler to use
        """
        self._input_handler = input_handler
        self.logger.debug("Input handler reference set")

    def cleanup(self) -> None:
        """Clean up the renderer by quitting pygame."""
        pygame.quit()
        self.logger.debug("Renderer cleanup completed") 