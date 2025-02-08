from DataModel import Position, Room
from Core.Pathfinding import PathFinder
from Entity.StatsProvider import StatsProvider
from Entity.EntityType import EntityType

class Entity:
    def __init__(self, type: EntityType, pos: Position, room: Room = None, 
                 blocks_movement: bool = False):
        self.type = type
        self.position = pos
        self.room = room
        self.blocks_movement = blocks_movement
        # Get stats from provider based on entity type
        self.stats = StatsProvider.get_instance().create_stats(type)

    def get_pathfinder(self):
        """Get the singleton pathfinder instance"""
        return PathFinder.get_instance()

    def can_act(self) -> bool:
        """Check if entity has enough action points to act"""
        return self.stats.action_points >= self.stats.max_action_points