from enum import Enum

class TileType(Enum):
    WALL = "#"
    FLOOR = "."
    DOOR = "D"
    WATER = "~"
    STAIRS = ">"

class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = [[TileType.WALL for _ in range(width)] for _ in range(height)]

class Room:
    def __init__(self, pos: Position, width: int, height: int):
        self.position = pos
        self.width = width
        self.height = height
        self.entities = []
        self.connections = []

    def center(self) -> Position:
        return Position(
            self.position.x + self.width // 2,
            self.position.y + self.height // 2
        )

class Corridor:
    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end
        self.path = []
        self.connected_rooms = []