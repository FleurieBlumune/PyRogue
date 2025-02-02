from Entity.Entity import Entity, EntityType
from DataModel import Position
from Entity.Player import Player
from Pathfinding import find_path
import pygame

class Enemy(Entity):
    def __init__(self, position: Position):
        super().__init__(EntityType.ENEMY, position, blocks_movement=True)
        self.last_move_time = 0
        self.move_delay = 500  # Slower than player (500ms between moves)
        self.detection_range = 8  # How many tiles away the enemy can see the player
        self.current_path = []

    def update(self, current_time: int, player: Player, is_passable, player_moved: bool) -> tuple[int, int]:
        """
        Update the enemy's behavior and return movement direction if it's time to move.
        Returns a tuple of (dx, dy) movement direction.
        """
        print(f"Enemy update called at time {current_time} with player at {player.position}")

        # Only move if the player has moved this turn
        if not player_moved:
            return (0, 0)
            
        if current_time - self.last_move_time < self.move_delay:
            return (0, 0)

        # Calculate distance to player
        dx = abs(self.position.x - player.position.x)
        dy = abs(self.position.y - player.position.y)
        
        # If player is within detection range, try to path to them
        if dx <= self.detection_range and dy <= self.detection_range:
            path = find_path(self.position, player.position, is_passable)
            if path:  # Only update path if we found a valid one
                self.current_path = path
                next_pos = path[0]
                move_dx = next_pos.x - self.position.x
                move_dy = next_pos.y - self.position.y
                self.last_move_time = current_time
                return (move_dx, move_dy)
            
        return (0, 0)
