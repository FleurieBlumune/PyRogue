"""
Entity management and movement for game zones.

Provides entity management functionality including:
- Entity addition and removal
- Movement and collision detection
- Turn management integration
- Event emission for entity actions
"""

import logging
from typing import List, Optional
from Core.Position import Position
from Entity.Entity import Entity
from Entity.Player import Player
from Core.Events import EventManager, GameEventType
from Core.EntityManager import EntityManager
from Core.TurnManager import TurnManager
from .Grid import TerrainGrid

class EntityContainer:
    """
    Manages entities within a zone including movement and collision.
    
    Handles all entity-related operations including adding/removing entities,
    managing their movement, handling collisions, and coordinating with the
    turn system.
    
    Attributes:
        grid (TerrainGrid): The terrain grid for collision checks
        entities (List[Entity]): List of all entities in the zone
        player (Optional[Entity]): Reference to the player entity
        entity_manager (EntityManager): Global entity management system
        turn_manager (TurnManager): Global turn management system
        event_manager (Optional[EventManager]): Event system for entity actions
        logger (Logger): Logger instance for debugging
    """
    
    def __init__(self, grid: TerrainGrid):
        """
        Initialize the entity container with a terrain grid.
        
        Args:
            grid (TerrainGrid): The terrain grid for collision detection
        """
        self.grid = grid
        self.entities: List[Entity] = []
        self._player: Optional[Player] = None
        self.entity_manager = EntityManager.get_instance()
        self.turn_manager = TurnManager.get_instance()
        self.event_manager: Optional[EventManager] = None
        self.logger = logging.getLogger(__name__)
        
    def set_event_manager(self, event_manager: EventManager) -> None:
        """
        Set the event manager for entity events.
        
        Args:
            event_manager (EventManager): The event system to use
        """
        self.event_manager = event_manager
        
    def add_entity(self, entity: Entity) -> None:
        """
        Add an entity and register it with the entity manager.
        
        Args:
            entity (Entity): The entity to add to the zone
        """
        self.entities.append(entity)
        if isinstance(entity, Player):
            self._player = entity
            
        if hasattr(entity, 'set_zone'):
            entity.set_zone(self)
            
        self.entity_manager.add_entity(entity)
        self.logger.debug(f"Added {entity.type.name} to zone and registered for turns")
        
    @property
    def player(self) -> Optional[Player]:
        """The player entity in the zone, if one exists."""
        return self._player
        
    def is_position_blocked(self, x: int, y: int, ignoring: Optional[Entity] = None) -> bool:
        """
        Check if a position is blocked by any entity.
        
        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            ignoring (Optional[Entity]): Entity to ignore in collision check
            
        Returns:
            bool: True if position is blocked by an entity
        """
        for entity in self.entities:
            if entity == ignoring:
                continue
            if entity.position.x == x and entity.position.y == y and entity.blocks_movement:
                return True
        return False
        
    def is_passable(self, x: int, y: int, ignoring: Optional[Entity] = None) -> bool:
        """
        Check if a position is passable (valid terrain and not blocked).
        
        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            ignoring (Optional[Entity]): Entity to ignore in collision check
            
        Returns:
            bool: True if position is passable
        """
        return (self.grid.is_passable_terrain(x, y) and 
                not self.is_position_blocked(x, y, ignoring))
                
    def move_entity(self, entity: Entity, dx: int, dy: int) -> bool:
        """
        Attempt to move an entity by the given delta.
        
        Handles movement validation, collision detection, combat interactions,
        event emission, and turn management integration.
        
        Args:
            entity (Entity): The entity to move
            dx (int): X-axis movement delta
            dy (int): Y-axis movement delta
            
        Returns:
            bool: True if movement was successful or combat occurred
        """
        if not self.event_manager:
            self.logger.error("Attempted to move entity with no event manager set")
            return False
            
        new_x = entity.position.x + dx
        new_y = entity.position.y + dy
        
        # Check for entities at the target position
        target_entity = self.get_entity_at(new_x, new_y)
        
        # If there's an entity and it's hostile, attempt combat
        if target_entity and entity.is_hostile_to(target_entity):
            self.logger.debug(f"{entity.type.name} attempting to attack {target_entity.type.name}")
            return entity.attack(target_entity)
        
        # Otherwise proceed with normal movement
        if self.is_passable(new_x, new_y, ignoring=entity) and entity.try_spend_movement():
            old_pos = Position(entity.position.x, entity.position.y)
            entity.position.x = new_x
            entity.position.y = new_y
            
            # Emit move event
            event_type = GameEventType.PLAYER_MOVED if entity == self.player else GameEventType.ENTITY_MOVED
            self.event_manager.emit(
                event_type,
                entity=entity,
                from_pos=old_pos,
                to_pos=Position(new_x, new_y)
            )
            
            # If player moved, start a new turn
            if entity == self.player:
                self.turn_manager.start_turn(self.entity_manager.get_entities())
                
            return True
        return False
        
    def get_entity_at(self, x: int, y: int) -> Optional[Entity]:
        """
        Get the entity at the specified position, if any.
        
        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            
        Returns:
            Optional[Entity]: The entity at the position, or None if empty
        """
        for entity in self.entities:
            if entity.position.x == x and entity.position.y == y:
                return entity
        return None