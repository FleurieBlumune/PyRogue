from enum import Enum
from DataModel import Position, Room, TileType
from Core.Pathfinding import PathFinder  # New import

class EntityType(Enum):
    PLAYER = "P"
    ENEMY = "E"
    CHEST = "C"
    KEY = "K"

class Entity:
    def __init__(self, type: EntityType, pos: Position, room: Room = None, blocks_movement: bool = False):
        self.type = type
        self.position = pos
        self.room = room
        self.blocks_movement = blocks_movement

    def get_pathfinder(self):
        """Get the singleton pathfinder instance"""
        return PathFinder.get_instance()