"""
NPC entity implementation with pathfinding and player tracking capabilities.
"""

from Entity.Entity import Entity, EntityType
from DataModel import Position
from Entity.Player import Player
from Core.Events import EventManager, GameEventType
import pygame
import logging

class NPC(Entity):
    """
    NPC entity that can track and follow the player.
    
    Features:
    - Player detection within range
    - Pathfinding to player position
    - Event-based movement updates
    
    Attributes:
        detection_range (int): How many tiles away the NPC can detect the player
        current_path (list): Current pathfinding route to player
    """

    def __init__(self, position: Position, entity_type: EntityType):
        """
        Initialize NPC at given position with specific type.

        Args:
            position (Position): Starting position of the NPC
            entity_type (EntityType): Type of NPC (HUMANOID, BEAST, etc.)
        """
        super().__init__(entity_type, position, blocks_movement=True)
        self.detection_range = 8  # How many tiles away the NPC can see the player
        self.current_path = []
        self.event_manager = EventManager.get_instance()
        self.logger = logging.getLogger(__name__)
        self.event_manager.subscribe(GameEventType.ENTITY_TURN, self._do_turn)
        self.logger.debug(f"Created {entity_type.name} with {self.stats.action_points} AP")
        

    def _do_turn(self, event):
        """Handle NPC's turn including hostile entity detection and movement"""
        try:
            # Check if this is our turn by looking directly at event attributes
            if event.entity is not self:
                return

            # Don't try to act if we can't
            if not self.can_act():
                self.logger.debug(f"{self.type.name} can't act: AP={self.stats.action_points}, last_turn={self.last_turn_acted}")
                return

            nearby_entities = event.visible_entities
            self.logger.debug(f"{self.type.name} sees {len(nearby_entities)} entities: {[e.type.name for e in nearby_entities]}")
            
            # Find closest hostile entity
            closest_target = None
            closest_dist = float('inf')
            
            for entity in nearby_entities:
                if self.is_hostile_to(entity):
                    dx = abs(self.position.x - entity.position.x)
                    dy = abs(self.position.y - entity.position.y)
                    dist = dx + dy
                    
                    if dist <= self.detection_range and dist < closest_dist:
                        closest_dist = dist
                        closest_target = entity
                        self.logger.debug(f"{self.type.name} considering target {entity.type.name} at distance {dist}")

            if closest_target:
                self.logger.debug(f"{self.type.name} found target {closest_target.type.name} at distance {closest_dist}")
                # If we're next to the target, don't calculate a path
                if closest_dist <= 1:
                    # TODO: Add attack logic here later
                    return
                
                # If we have a path, validate it still leads to target 
                if self.current_path:
                    next_pos = self.current_path[0]
                    dx_to_target = abs(next_pos.x - closest_target.position.x)
                    dy_to_target = abs(next_pos.y - closest_target.position.y)
                    
                    # Path is invalid if it doesn't get us closer to target
                    if dx_to_target + dy_to_target >= closest_dist:
                        self.logger.debug(f"{self.type.name} current path no longer valid - recalculating")
                        self.current_path = []
                    else:
                        dx = next_pos.x - self.position.x
                        dy = next_pos.y - self.position.y
                        self.logger.debug(f"{self.type.name} attempting move dx={dx}, dy={dy} along existing path")
                        if hasattr(self, 'zone'):
                            if self.zone.move_entity(self, dx, dy):
                                self.current_path.pop(0)
                                self.logger.debug(f"{self.type.name} moved using existing path, {len(self.current_path)} steps remaining")
                                return
                            else:
                                self.logger.debug(f"{self.type.name} failed to move using existing path")
                                self.current_path = []  # Path is blocked, clear it

                # No valid path exists, calculate new one
                if not self.current_path:
                    path = self.get_pathfinder().find_path(
                        self.position, 
                        closest_target.position,
                        self
                    )
                    if path:
                        self.logger.debug(f"{self.type.name} found new path of length {len(path)} to {closest_target.type.name}")
                        next_pos = path[0]
                        dx = next_pos.x - self.position.x
                        dy = next_pos.y - self.position.y
                        self.logger.debug(f"{self.type.name} attempting move dx={dx}, dy={dy} along new path")
                        
                        if hasattr(self, 'zone'):
                            if self.zone.move_entity(self, dx, dy):
                                self.current_path = path[1:] if len(path) > 1 else []
                                self.logger.debug(f"{self.type.name} moved using new path, saved {len(self.current_path)} remaining steps")
                            else:
                                self.logger.debug(f"{self.type.name} failed to move using new path")
                    else:
                        self.logger.debug(f"{self.type.name} failed to find path to target")
            else:
                self.logger.debug(f"{self.type.name} found no valid targets")
                    
        except Exception as e:
            self.logger.error(f"Error during NPC turn: {e}", exc_info=True)


    def set_zone(self, zone):
        """Set the zone reference for movement"""
        self.zone = zone
