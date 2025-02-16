"""
Entity rendering system for visualizing game entities.

This module provides the EntityRenderer class which handles:
- Entity visualization
- Color management for different entity types
- Position calculation and transformation
- Visibility checks
"""

import pygame
from typing import Dict, Tuple, Optional
import logging
from Entity.Entity import Entity, EntityType
from Core.Renderer.Camera import Camera

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
        EntityType.PLAYER: (0, 255, 0),     # Green
        EntityType.HUMANOID: (0, 0, 255),   # Blue
        EntityType.BEAST: (255, 0, 0),      # Red
        EntityType.UNDEAD: (255, 215, 0),   # Gold
        EntityType.MERCHANT: (255, 255, 0),  # Yellow
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
        self.logger.debug("EntityRenderer initialized")

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
        return (0 <= screen_x < self.camera.width and 
                0 <= screen_y < self.camera.height)

    def render_entity(self, 
                     surface: pygame.Surface, 
                     entity: Entity, 
                     highlight: bool = False) -> None:
        """
        Render a single entity on the screen.
        
        Args:
            surface (pygame.Surface): The surface to render on
            entity (Entity): The entity to render
            highlight (bool): Whether to highlight the entity
        """
        try:
            # Convert world position to screen position
            world_x = entity.position.x * self.tile_size
            world_y = entity.position.y * self.tile_size
            screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
            
            # Check if entity is visible on screen
            if not self.is_visible(screen_x, screen_y):
                return
                
            # Calculate center position for the entity
            center_x = screen_x + self.tile_size // 2
            center_y = screen_y + self.tile_size // 2
            
            # Get entity color
            color = self.get_entity_color(entity.type)
            
            # Draw entity circle
            radius = self.tile_size // 3
            pygame.draw.circle(surface, color, (center_x, center_y), radius)
            
            # Add highlight if requested
            if highlight:
                highlight_radius = radius + 2
                pygame.draw.circle(
                    surface, 
                    (255, 255, 255),  # White highlight
                    (center_x, center_y), 
                    highlight_radius,
                    2  # Line width
                )
                
        except Exception as e:
            self.logger.error(f"Error rendering entity {entity.type.name}: {e}", exc_info=True)

    def render_entities(self, 
                       surface: pygame.Surface, 
                       entities: list[Entity],
                       highlighted_entity: Optional[Entity] = None) -> None:
        """
        Render a list of entities, optionally highlighting one.
        
        Args:
            surface (pygame.Surface): The surface to render on
            entities (list[Entity]): List of entities to render
            highlighted_entity (Optional[Entity]): Entity to highlight, if any
        """
        try:
            for entity in entities:
                self.render_entity(
                    surface, 
                    entity, 
                    highlight=(entity is highlighted_entity)
                )
            
        except Exception as e:
            self.logger.error(f"Error rendering entities: {e}", exc_info=True) 