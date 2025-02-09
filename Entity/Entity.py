"""Entity base class."""

from Core.Position import Position
from Core.Pathfinding import PathFinder
from Entity.StatsProvider import StatsProvider
from Entity.EntityType import EntityType
from Data.GameData import GameData
from Core.Events import EventManager, GameEventType
from Zone.Room import Room
import logging

class Entity:
    def __init__(self, type: EntityType, pos: Position, room: Room = None, 
                 blocks_movement: bool = False):
        self.type = type
        self.position = pos
        self.room = room
        self.blocks_movement = blocks_movement
        self.stats = StatsProvider.get_instance().create_stats(type)
        self.faction = type.faction
        self.game_data = GameData.get_instance()
        self.detection_range = 8  # Default detection range
        self.last_turn_acted = 0  # Track which turn this entity last acted in
        self.logger = logging.getLogger(__name__)
        
        # Set up event handling
        self.event_manager = EventManager.get_instance()
        self.event_manager.subscribe(GameEventType.ENTITY_TURN, self._handle_turn)
        
        self.logger.debug(f"Created {type.name} entity with faction {self.faction}")

    def get_pathfinder(self):
        """Get the singleton pathfinder instance"""
        return PathFinder.get_instance()

    def can_act(self) -> bool:
        """Check if entity has enough action points to act and hasn't acted this turn"""
        from Core.TurnManager import TurnManager
        current_turn = TurnManager.get_instance().current_turn
        can = (self.stats.action_points >= self.stats.move_cost and 
               self.last_turn_acted < current_turn)
        self.logger.debug(f"{self.type.name} can_act check: AP={self.stats.action_points}, move_cost={self.stats.move_cost}, last_turn={self.last_turn_acted}, current_turn={current_turn}, result={can}")
        return can

    def try_spend_movement(self) -> bool:
        """Attempt to spend action points for movement"""
        if self.stats.spend_action_points(self.stats.move_cost):
            from Core.TurnManager import TurnManager
            self.last_turn_acted = TurnManager.get_instance().current_turn
            return True
        return False

    def is_hostile_to(self, other: 'Entity') -> bool:
        """Check if this entity is hostile to another based on faction relations"""
        disposition = self.game_data.get_faction_disposition(self.faction, other.faction)
        self.logger.debug(f"{self.type.name}({self.faction}) disposition to {other.type.name}({other.faction}): {disposition}")
        return disposition < 0

    def _handle_turn(self, event):
        """Base turn handler that ensures AP recovery for all entities"""
        if event.entity is not self:
            return

        # Always recover AP at start of turn
        old_ap = self.stats.action_points
        self.stats.accumulate_action_points()
        self.logger.debug(f"{self.type.name} AP recovered: {old_ap} -> {self.stats.action_points}")