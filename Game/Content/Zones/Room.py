"""
Room and corridor definitions for zone generation.

Provides classes for representing rooms and corridors in the game world,
including their positions, dimensions, and connections.
"""

from typing import List
from Engine.Core.Utils.Position import Position

class Room:
    """
    Represents a room in the game world.
    
    A room is a rectangular area defined by a position and dimensions.
    It can contain entities and be connected to other rooms via corridors.
    
    Attributes:
        position (Position): Top-left corner position
        width (int): Width in tiles
        height (int): Height in tiles
        entities (List): List of entities in the room
        connections (List): List of connected rooms
    """
    
    def __init__(self, pos: Position, width: int, height: int):
        """
        Initialize a room with position and dimensions.
        
        Args:
            pos (Position): Top-left corner position
            width (int): Width in tiles
            height (int): Height in tiles
        """
        self.position = pos
        self.width = width
        self.height = height
        self.entities = []
        self.connections = []

    def center(self) -> Position:
        """
        Get the center position of the room.
        
        Returns:
            Position: Center coordinates of the room
        """
        return Position(
            self.position.x + self.width // 2,
            self.position.y + self.height // 2
        )

class Corridor:
    """
    Represents a corridor connecting two rooms.
    
    A corridor is defined by start and end positions, with a path
    of positions connecting them.
    
    Attributes:
        start (Position): Starting position
        end (Position): Ending position
        path (List[Position]): List of positions making up the corridor
        connected_rooms (List): List of rooms this corridor connects
    """
    
    def __init__(self, start: Position, end: Position):
        """
        Initialize a corridor with start and end positions.
        
        Args:
            start (Position): Starting position
            end (Position): Ending position
        """
        self.start = start
        self.end = end
        self.path = []
        self.connected_rooms = [] 