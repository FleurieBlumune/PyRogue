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
        self.event_manager.subscribe(GameEventType.PLAYER_MOVED, self._handle_player_moved)
        self.event_manager.subscribe(GameEventType.TURN_ENDED, self._handle_turn_ended)
        

    def _handle_player_moved(self, event):
        """
        Handle player movement events by updating pathfinding.

        Args:
            args (dict): Event arguments containing player entity and position
        """
        try:
            args = event.dict if hasattr(event, 'dict') else {}
            # Check if the event dictionary contains an "args" key
            if 'args' in args:
                args = args['args']
            player_pos = args.get('to_pos')
            if not player_pos:
                self.logger.warning("Player moved event missing position")
                return

            dx = abs(self.position.x - player_pos.x)
            dy = abs(self.position.y - player_pos.y)
            
            if dx <= self.detection_range and dy <= self.detection_range:
                # Use the inherited pathfinder.
                path = self.get_pathfinder().find_path(self.position, player_pos, self)
                if path:
                    self.current_path = path
                    self.logger.debug(f"NPC found path to player: {path}")
        except Exception as e:
            self.logger.error(f"Error handling player movement: {e}")

    def _handle_turn_ended(self, event):
        """Move along path when turn ends"""
        try:
            if not self.current_path:
                return

            next_pos = self.current_path[0]
            if not self.pathfinder.is_passable(next_pos.x, next_pos.y, self):
                self.logger.debug(f"Next position {next_pos} is not passable")
                self.current_path = []
                return

            dx = next_pos.x - self.position.x
            dy = next_pos.y - self.position.y
            
            # Remove the position we're moving to
            self.current_path.pop(0)
            
            # Update position before emitting event
            old_pos = Position(self.position.x, self.position.y)
            self.position = next_pos
            
            # Emit movement event
            self.event_manager.emit(
                GameEventType.ENTITY_MOVED,
                entity=self,
                from_pos=old_pos,
                to_pos=next_pos,
                dx=dx,
                dy=dy
            )
            self.logger.debug(f"NPC moved to {next_pos}")
        except Exception as e:
            self.logger.error(f"Error during turn end movement: {e}")
