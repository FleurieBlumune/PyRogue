"""Player entity class."""

import pygame
import logging
from Game.Content.Entities.Entity import Entity
from Game.Content.Entities.EntityType import EntityType
from Engine.Core.Utils.Position import Position
from Engine.Core.Events import EventManager, GameEventType
from Game.Content.Cards.DeckManager import DeckManager

class Player(Entity):
    def __init__(self, position: Position):
        super().__init__(EntityType.PLAYER, position)
        self.move_map = {
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_KP8: (0, -1),    # Numpad 8
            pygame.K_KP2: (0, 1),     # Numpad 2
            pygame.K_KP4: (-1, 0),    # Numpad 4
            pygame.K_KP6: (1, 0),     # Numpad 6
            pygame.K_KP7: (-1, -1),   # Numpad 7
            pygame.K_KP9: (1, -1),    # Numpad 9
            pygame.K_KP1: (-1, 1),    # Numpad 1
            pygame.K_KP3: (1, 1)      # Numpad 3
        }
        self.current_path = []
        self.event_manager = EventManager.get_instance()
        self.logger = logging.getLogger(__name__)
        self.event_manager.subscribe(GameEventType.ENTITY_TURN, self._do_turn)
        
        # Initialize deck manager
        self.deck_manager = DeckManager()
        # Build initial deck with some test cards for now
        try:
            self.deck_manager.build_deck([1, 2])  # Add some test card IDs
            self.deck_manager.draw_hand()  # Draw initial hand
        except Exception as e:
            self.logger.error(f"Error initializing deck: {e}", exc_info=True)

    def handle_click(self, tile_x: int, tile_y: int) -> bool:
        """Handle a click at the given tile coordinates"""           
        goal = Position(tile_x, tile_y)
        path = self.get_pathfinder().find_path(self.position, goal, self)
        
        if path:
            self.set_path(path)
            return True
        return False

    def get_movement_from_key(self, key):
        return self.move_map.get(key, (0, 0))

    def get_movement_to_position(self, target_x: int, target_y: int):
        dx = target_x - self.position.x
        dy = target_y - self.position.y
        
        # Get movement direction (-1, 0, or 1 for each component)
        return (
            dx and dx // abs(dx),
            dy and dy // abs(dy)
        )

    def set_path(self, path: list[Position]):
        self.current_path = path

    def get_next_move(self):
        if not self.current_path:
            return (0, 0)
        
        next_pos = self.current_path[0]
        dx = next_pos.x - self.position.x
        dy = next_pos.y - self.position.y
        
        # Remove the position we're moving to
        self.current_path.pop(0)
        
        return (dx, dy)

    def _do_turn(self, event):
        """Handle Player's turn including movement and action point processing"""
        try:
            if event.entity is not self:
                return

            if not self.can_act():
                self.logger.debug(f"{self.type.name} can't act: AP={self.stats.action_points}, last_turn={self.last_turn_acted}")
                return

            # Player-specific turn logic can be added here
            self.logger.debug(f"{self.type.name} is taking its turn")

        except Exception as e:
            self.logger.error(f"Error during Player turn: {e}", exc_info=True)
