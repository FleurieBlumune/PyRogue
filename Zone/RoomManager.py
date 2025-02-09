"""
Room and corridor management for game zones.

Provides room and corridor management functionality including:
- Room addition and tracking
- Corridor path generation
- Map carving operations
- Room containment queries
"""

import logging
from typing import List, Optional
from Core.Position import Position
from .Grid import TerrainGrid
from .Room import Room, Corridor
from .TileType import TileType

class RoomManager:
    """
    Manages rooms and corridors within a zone.
    
    Handles the creation, tracking, and modification of rooms and corridors,
    including their integration with the terrain grid.
    
    Attributes:
        grid (TerrainGrid): The terrain grid to carve rooms into
        rooms (List[Room]): List of all rooms in the zone
        corridors (List[Corridor]): List of all corridors in the zone
        logger (Logger): Logger instance for debugging
    """
    
    def __init__(self, grid: TerrainGrid):
        """
        Initialize the room manager with a terrain grid.
        
        Args:
            grid (TerrainGrid): The terrain grid to carve rooms into
        """
        self.grid = grid
        self.rooms: List[Room] = []
        self.corridors: List[Corridor] = []
        self.logger = logging.getLogger(__name__)
        
    def add_room(self, room: Room) -> None:
        """
        Add a room and carve it into the grid.
        
        Args:
            room (Room): The room to add to the zone
        """
        self.rooms.append(room)
        self._carve_room(room)
        
    def add_corridor(self, corridor: Corridor) -> None:
        """
        Add a corridor, generate its path, and carve it.
        
        Args:
            corridor (Corridor): The corridor to add to the zone
        """
        self.corridors.append(corridor)
        self._generate_corridor_path(corridor)
        self._carve_corridor(corridor)
        
    def get_containing_room(self, x: int, y: int) -> Optional[Room]:
        """
        Get the room containing the given coordinates, if any.
        
        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            
        Returns:
            Optional[Room]: The room containing the coordinates, or None
        """
        for room in self.rooms:
            if (room.position.x <= x < room.position.x + room.width and
                room.position.y <= y < room.position.y + room.height):
                return room
        return None
        
    def _carve_room(self, room: Room) -> None:
        """
        Carve a room into the grid by setting floor tiles.
        
        Args:
            room (Room): The room to carve into the terrain
        """
        for y in range(room.position.y, room.position.y + room.height):
            for x in range(room.position.x, room.position.x + room.width):
                self.grid.set_tile(x, y, TileType.FLOOR)
                
    def _generate_corridor_path(self, corridor: Corridor) -> None:
        """
        Generate a path for a corridor using simple horizontal-then-vertical approach.
        
        Args:
            corridor (Corridor): The corridor to generate a path for
        """
        current_x, current_y = corridor.start.x, corridor.start.y
        end_x, end_y = corridor.end.x, corridor.end.y
        
        # Horizontal then vertical
        while current_x != end_x:
            corridor.path.append(Position(current_x, current_y))
            current_x += 1 if current_x < end_x else -1
            
        while current_y != end_y:
            corridor.path.append(Position(current_x, current_y))
            current_y += 1 if current_y < end_y else -1
            
        corridor.path.append(Position(end_x, end_y))
        
    def _carve_corridor(self, corridor: Corridor) -> None:
        """
        Carve a corridor's path into the grid.
        
        Args:
            corridor (Corridor): The corridor to carve into the terrain
        """
        for pos in corridor.path:
            self.grid.set_tile(pos.x, pos.y, TileType.FLOOR) 