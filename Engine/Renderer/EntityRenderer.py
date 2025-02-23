"""
Entity rendering system for visualizing game entities.

This module provides the EntityRenderer class which handles:
- Entity visualization
- Color management for different entity types
- Position calculation and transformation
- Visibility checks
"""

import pygame
from typing import Dict, Tuple, Optional, List
import logging
from Game.Content.Entities.Entity import Entity, EntityType
from Engine.Renderer.Camera import Camera
from Engine.Core.Events import EventManager, GameEventType

class EntityRenderer:
    """
    Handles the rendering of game entities with proper positioning and styling.
    
    The EntityRenderer manages entity colors and handles the conversion of
    entity positions to screen coordinates for rendering.
    
    Attributes:
        camera (Camera): Reference to the game camera for coordinate conversion
        tile_size (int): Current size of tiles in pixels
        entity_colors (Dict[EntityType, Tuple[int, int, int]]): Color mapping for entity types
        logger (Logger): Logger instance for debugging
    """
    
    # Define colors for different entity types
    ENTITY_COLORS = {
        EntityType.PLAYER: (0, 255, 255),    # Cyan for scientist/player
        EntityType.GUARD: (255, 0, 0),       # Red for security
        EntityType.CIVILIAN: (150, 150, 150), # Gray for civilians
        EntityType.RESEARCHER: (0, 255, 0),   # Green for friendly researchers
        EntityType.SUBJECT: (255, 165, 0),    # Orange for test subjects
    }
    
    def __init__(self, camera: Camera):
        """
        Initialize the entity renderer with a camera reference.
        
        Args:
            camera (Camera): The game camera for coordinate conversion
        """
        self.camera = camera
        self.tile_size = 32  # Default tile size
        self.entity_colors = self.ENTITY_COLORS.copy()
        self.logger = logging.getLogger(__name__)
        
        # Subscribe to camera events
        self.event_manager = EventManager.get_instance()
        self.event_manager.subscribe(GameEventType.VIEWPORT_UPDATED, self._on_viewport_updated)
        
        self.logger.debug("EntityRenderer initialized")

    def _on_viewport_updated(self, **kwargs) -> None:
        """Handle viewport update events."""
        # Update internal state if needed when viewport changes
        pass

    def update_tile_size(self, new_size: int) -> None:
        """
        Update the tile size used for entity rendering.
        
        Args:
            new_size (int): New tile size in pixels
        """
        self.tile_size = new_size
        self.logger.debug(f"Updated tile size to {new_size}")

    def get_entity_color(self, entity_type: EntityType) -> Tuple[int, int, int]:
        """
        Get the color for a specific entity type.
        
        Args:
            entity_type (EntityType): The type of entity
            
        Returns:
            Tuple[int, int, int]: RGB color tuple for the entity type
        """
        return self.entity_colors.get(entity_type, (255, 255, 255))  # White as default

    def is_visible(self, screen_x: int, screen_y: int) -> bool:
        """
        Check if a position is within the visible screen area.
        
        Args:
            screen_x (int): X position in screen coordinates
            screen_y (int): Y position in screen coordinates
            
        Returns:
            bool: True if the position is visible on screen
        """
        return (0 <= screen_x < self.camera.viewport.width and 
                0 <= screen_y < self.camera.viewport.height)

    def render_entities(self, screen: pygame.Surface, entities: List[Entity], highlighted_entity: Optional[Entity] = None) -> None:
        """
        Render a list of entities on the screen.
        
        Args:
            screen (pygame.Surface): Surface to render on
            entities (List[Entity]): List of entities to render
            highlighted_entity (Optional[Entity]): Entity to highlight, if any
        """
        for entity in entities:
            # Calculate screen position
            world_x = entity.position.x * self.tile_size
            world_y = entity.position.y * self.tile_size
            screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
            
            # Only render if visible on screen
            if self.is_visible(screen_x, screen_y):
                # Draw entity
                color = self.get_entity_color(entity.type)
                pygame.draw.circle(
                    screen,
                    color,
                    (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),
                    self.tile_size // 3
                )
                
                # Draw highlight if this is the highlighted entity
                if entity == highlighted_entity:
                    pygame.draw.circle(
                        screen,
                        (255, 255, 255),  # White highlight
                        (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),
                        self.tile_size // 2,
                        2  # Line width
                    ) 