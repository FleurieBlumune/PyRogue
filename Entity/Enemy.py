"""
Enemy entity implementation with pathfinding and player tracking capabilities.
"""

from Entity.Entity import Entity, EntityType
from DataModel import Position
from Entity.Player import Player
from Pathfinding import find_path
from Core.Events import EventManager, GameEventType
import pygame

class Enemy(Entity):
    """
    Enemy entity that can track and follow the player.
    
    Features:
    - Player detection within range
    - Pathfinding to player position
    - Event-based movement updates
    
    Attributes:
        detection_range (int): How many tiles away the enemy can detect the player
        current_path (list): Current pathfinding route to player
    """

    def __init__(self, position: Position):
        """
        Initialize enemy at given position.

        Args:
            position (Position): Starting position of the enemy
        """
        super().__init__(EntityType.ENEMY, position, blocks_movement=True)
        self.detection_range = 8  # How many tiles away the enemy can see the player
        self.current_path = []
        event_manager = EventManager.get_instance()
        event_manager.subscribe(GameEventType.PLAYER_MOVED, self._handle_player_moved)

    def _handle_player_moved(self, args: dict):
        """
        Handle player movement events by updating pathfinding.

        Args:
            args (dict): Event arguments containing player entity and position
        """
        player = args['entity']
        player_pos = args['to_pos']
        print(f"Player moved to {player_pos} at time {pygame.time.get_ticks()}")
        dx = abs(self.position.x - player_pos.x)
        dy = abs(self.position.y - player_pos.y)
        
        if dx <= self.detection_range and dy <= self.detection_range:
            path = find_path(self.position, player_pos, self.is_passable)
            if path:
                self.current_path = path


    # def update(self, current_time: int, player: Player, is_passable, player_moved: bool) -> tuple[int, int]:
    #     """
    #     Update the enemy's behavior and return movement direction if it's time to move.
    #     Returns a tuple of (dx, dy) movement direction.
    #     """
    #     print(f"Enemy update called at time {current_time} with player at {player.position}")

    #     # Only move if the player has moved this turn
    #     if not player_moved:
    #         return (0, 0)
            
    #     if current_time - self.last_move_time < self.move_delay:
    #         return (0, 0)

    #     # Calculate distance to player
    #     dx = abs(self.position.x - player.position.x)
    #     dy = abs(self.position.y - player.position.y)
        
    #     # If player is within detection range, try to path to them
    #     if dx <= self.detection_range and dy <= self.detection_range:
    #         path = find_path(self.position, player.position, is_passable)
    #         if path:  # Only update path if we found a valid one
    #             self.current_path = path
    #             next_pos = path[0]
    #             move_dx = next_pos.x - self.position.x
    #             move_dy = next_pos.y - self.position.y
    #             self.last_move_time = current_time
    #             return (move_dx, move_dy)
            
    #     return (0, 0)
