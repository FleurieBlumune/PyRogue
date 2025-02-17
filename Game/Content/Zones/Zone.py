"""
Main Zone class that composes and coordinates zone components.

The Zone class is the primary interface for game zone functionality, composing:
- Terrain grid management (TerrainGrid)
- Entity management (EntityContainer)
- Room and corridor management (RoomManager)
- Event coordination
- Pathfinding integration
"""

import logging
from Engine.Core.Events import EventManager
from Engine.Core.Utils.Pathfinding import PathFinder
from Engine.Core.Utils.Position import Position
from Game.Content.Entities.Entity import Entity
from .Grid import TerrainGrid
from .EntityContainer import EntityContainer
from .RoomManager import RoomManager
from .Room import Room, Corridor
import pygame

class Zone:
    """
    A game zone that manages the map, entities, and game state.
    
    Composes functionality from TerrainGrid, EntityContainer, and RoomManager
    to provide a complete interface for zone operations. Acts as the primary
    point of interaction for game systems that need to interact with the zone.
    
    Attributes:
        grid (TerrainGrid): Terrain and tile management
        entity_container (EntityContainer): Entity and movement management
        room_manager (RoomManager): Room and corridor management
        pathfinder (PathFinder): Pathfinding system instance
        logger (Logger): Logger instance for debugging
    """
    
    def __init__(self, width: int = 100, height: int = 100):
        """
        Initialize a new zone with specified dimensions.
        
        Args:
            width (int): Width of the zone in tiles
            height (int): Height of the zone in tiles
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.grid = TerrainGrid(width, height)
        self.entity_container = EntityContainer(self.grid)
        self.room_manager = RoomManager(self.grid)
        
        # Set up pathfinding
        self.pathfinder = PathFinder.get_instance()
        self.pathfinder.set_zone(self)
        
        self.logger.debug("Zone initialized")
        
    def update(self, current_time: int) -> None:
        """
        Update the zone state for the current frame.
        
        Updates all entities and systems that need per-frame updates.
        
        Args:
            current_time (int): Current game time in milliseconds
        """
        # Currently, we don't have any per-frame updates needed
        # This is called by the game loop, but our turn-based systems
        # are driven by the event system instead of frame updates
        pass
        
    def set_event_manager(self, event_manager: EventManager) -> None:
        """
        Set the event manager for the zone and its components.
        
        Args:
            event_manager (EventManager): The event system to use
        """
        self.entity_container.set_event_manager(event_manager)
        
    # Grid delegation
    @property
    def width(self) -> int:
        """Width of the zone in tiles."""
        return self.grid.width
        
    @property
    def height(self) -> int:
        """Height of the zone in tiles."""
        return self.grid.height
        
    def is_passable(self, x: int, y: int, ignoring: Entity = None) -> bool:
        """
        Check if a position is passable.
        
        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            ignoring (Entity): Entity to ignore in collision check
            
        Returns:
            bool: True if position is passable
        """
        return self.entity_container.is_passable(x, y, ignoring)
        
    # Room management delegation
    def add_room(self, room: Room) -> None:
        """
        Add a room to the zone.
        
        Args:
            room (Room): The room to add
        """
        self.room_manager.add_room(room)
        
    def add_corridor(self, corridor: Corridor) -> None:
        """
        Add a corridor to the zone.
        
        Args:
            corridor (Corridor): The corridor to add
        """
        self.room_manager.add_corridor(corridor)
        
    # Entity management delegation
    def add_entity(self, entity: Entity) -> None:
        """
        Add an entity to the zone.
        
        Args:
            entity (Entity): The entity to add
        """
        self.entity_container.add_entity(entity)
        if hasattr(entity, 'is_player') and entity.is_player:
            self.entity_container.player = entity
            
    def move_entity(self, entity: Entity, dx: int, dy: int) -> bool:
        """
        Attempt to move an entity.
        
        Args:
            entity (Entity): The entity to move
            dx (int): X-axis movement delta
            dy (int): Y-axis movement delta
            
        Returns:
            bool: True if movement was successful
        """
        moved = self.entity_container.move_entity(entity, dx, dy)
        if moved:
            room = self.room_manager.get_containing_room(entity.position.x, entity.position.y)
            if hasattr(entity, 'room'):
                entity.room = room
        return moved
        
    # Property access for compatibility
    @property
    def player(self) -> Entity:
        """The player entity in the zone."""
        return self.entity_container.player
        
    @property
    def entities(self) -> list[Entity]:
        """List of all entities in the zone."""
        return self.entity_container.entities
        
    def get_entities_in_area(self, area: pygame.Rect) -> list[Entity]:
        """
        Get all entities within a given rectangular area.
        
        Args:
            area (pygame.Rect): The area to check in tile coordinates
            
        Returns:
            list[Entity]: List of entities within the area
        """
        return [
            entity for entity in self.entities
            if (area.left <= entity.position.x <= area.right and
                area.top <= entity.position.y <= area.bottom)
        ] 