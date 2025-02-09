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

    def attack(self, target: 'Entity') -> bool:
        """
        Attempt to attack another entity.
        Returns True if the attack was successful, False otherwise.
        """
        if not self.stats.can_attack():
            self.logger.debug(f"{self.type.name} cannot attack: insufficient AP")
            return False
            
        if not self.is_adjacent_to(target):
            self.logger.debug(f"{self.type.name} cannot attack: target not adjacent")
            return False
            
        # Calculate and deal damage
        damage = self.stats.calculate_attack_damage()
        actual_damage = target.take_damage(damage)
        
        # Spend action points for the attack
        self.stats.spend_action_points(self.stats.attack_cost)
        
        # Update last turn acted
        from Core.TurnManager import TurnManager
        self.last_turn_acted = TurnManager.get_instance().current_turn
        
        self.logger.info(f"{self.type.name} attacked {target.type.name} for {actual_damage} damage")
        
        # Emit combat event
        self.event_manager.emit(GameEventType.COMBAT_ACTION, attacker=self, defender=target, damage=actual_damage)
        
        return True

    def take_damage(self, damage: int) -> int:
        """
        Take damage and return the actual amount of damage dealt.
        """
        actual_damage = self.stats.take_damage(damage)
        
        if not self.stats.is_alive():
            self.die()
            
        return actual_damage

    def die(self):
        """Handle entity death."""
        self.logger.info(f"{self.type.name} has died")
        self.event_manager.emit(GameEventType.ENTITY_DIED, {'entity': self})
        # Additional death logic can be added here (e.g., dropping items, removing from game)

    def is_adjacent_to(self, other: 'Entity') -> bool:
        """Check if this entity is adjacent to another entity."""
        dx = abs(self.position.x - other.position.x)
        dy = abs(self.position.y - other.position.y)
        return dx <= 1 and dy <= 1 and not (dx == 0 and dy == 0)