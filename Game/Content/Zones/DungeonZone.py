"""
Dungeon-specific zone implementation.

Provides dungeon generation and management functionality including:
- Room placement and sizing
- Corridor connections
- Entity placement
- Initial dungeon state setup
"""

import random
import logging
from Engine.Core.Utils.Position import Position
from Game.Content.Entities.Player import Player
from Game.Content.Entities.NPC import NPC
from Game.Content.Entities.EntityType import EntityType
from .Zone import Zone
from .Room import Room, Corridor
from .TileType import TileType

class DungeonZone(Zone):
    """
    A specialized zone type for dungeon environments.
    
    Handles the procedural generation and management of dungeon-specific
    features like rooms, corridors, and appropriate entity placement.
    
    Attributes:
        min_rooms (int): Minimum number of rooms to generate
        max_rooms (int): Maximum number of rooms to generate
        min_room_size (int): Minimum room dimension
        max_room_size (int): Maximum room dimension
        dungeon_padding (int): Padding around the dungeon edges
        max_corridor_length (int): Maximum length of any corridor
    """
    
    def __init__(self, min_rooms: int = 5, max_rooms: int = 10, 
                 width: int = 50, height: int = 50):
        """
        Initialize a new dungeon zone.
        
        Args:
            min_rooms (int): Minimum number of rooms
            max_rooms (int): Maximum number of rooms
            width (int): Width of the dungeon in tiles
            height (int): Height of the dungeon in tiles
        """
        super().__init__(width, height)
        
        self.min_rooms = min_rooms
        self.max_rooms = max_rooms
        self.min_room_size = 4
        self.max_room_size = 16
        self.dungeon_padding = 1
        self.max_corridor_length = 5
        
        self.logger = logging.getLogger(__name__)
        
        # Generate the dungeon layout
        self._generate()
        
    def _generate(self) -> None:
        """Generate the complete dungeon layout with rooms and corridors."""
        rooms = self._generate_rooms()
        
        # Add rooms to zone
        for room in rooms:
            self.add_room(room)
            
        # Connect rooms using nearest neighbor to minimize corridor length
        self._connect_rooms(rooms)
            
        # Place player in first room
        player = Player(rooms[0].center())
        self.add_entity(player)
        
        # Place NPCs in other rooms
        self._place_entities(rooms[1:])
        
    def _generate_rooms(self) -> list[Room]:
        """
        Generate a list of non-overlapping rooms.
        
        Returns:
            list[Room]: List of generated rooms
        """
        rooms = []
        num_rooms = random.randint(self.min_rooms, self.max_rooms)
        max_attempts = 100  # Maximum attempts to place all rooms
        
        # Place first room near center
        center_x = self.width // 2
        center_y = self.height // 2
        first_width = random.randint(self.min_room_size, self.max_room_size)
        first_height = random.randint(self.min_room_size, self.max_room_size)
        first_room = Room(
            Position(
                center_x - first_width // 2,
                center_y - first_height // 2
            ),
            first_width,
            first_height
        )
        rooms.append(first_room)
        
        # Place remaining rooms
        attempts = 0
        while len(rooms) < num_rooms and attempts < max_attempts:
            # Pick a reference room to place near
            ref_room = random.choice(rooms)
            ref_center = ref_room.center()
            
            # Try to place a room near the reference room
            width = random.randint(self.min_room_size, self.max_room_size)
            height = random.randint(self.min_room_size, self.max_room_size)
            
            # Calculate position near reference room
            angle = random.uniform(0, 6.28)  # Random angle in radians
            distance = random.randint(3, self.max_corridor_length)  # Random distance within corridor limit
            
            x = int(ref_center.x + distance * (width / 2) * (random.choice([-1, 1])))
            y = int(ref_center.y + distance * (height / 2) * (random.choice([-1, 1])))
            
            # Ensure room is within bounds
            x = max(self.dungeon_padding, min(x, self.width - width - self.dungeon_padding))
            y = max(self.dungeon_padding, min(y, self.height - height - self.dungeon_padding))
            
            new_room = Room(Position(x, y), width, height)
            
            # Check if room overlaps with existing rooms
            if not self._rooms_overlap(new_room, rooms):
                rooms.append(new_room)
            
            attempts += 1
                    
        return rooms
        
    def _rooms_overlap(self, new_room: Room, existing_rooms: list[Room]) -> bool:
        """
        Check if a room overlaps with any existing rooms.
        
        Args:
            new_room (Room): Room to check
            existing_rooms (list[Room]): List of existing rooms
            
        Returns:
            bool: True if room overlaps with any existing room
        """
        for room in existing_rooms:
            # Add padding between rooms
            if (new_room.position.x - 1 < room.position.x + room.width and
                new_room.position.x + new_room.width + 1 > room.position.x and
                new_room.position.y - 1 < room.position.y + room.height and
                new_room.position.y + new_room.height + 1 > room.position.y):
                return True
        return False
        
    def _connect_rooms(self, rooms: list[Room]) -> None:
        """
        Connect rooms using a nearest-neighbor approach.
        
        Args:
            rooms (list[Room]): List of rooms to connect
        """
        connected = {rooms[0]}  # Start with first room
        unconnected = set(rooms[1:])
        
        while unconnected:
            best_distance = float('inf')
            best_connection = None
            
            # Find the closest unconnected room to any connected room
            for connected_room in connected:
                for unconnected_room in unconnected:
                    dist = self._room_distance(connected_room, unconnected_room)
                    if dist < best_distance:
                        best_distance = dist
                        best_connection = (connected_room, unconnected_room)
            
            if best_connection:
                room1, room2 = best_connection
                self._create_corridor(room1, room2)
                connected.add(room2)
                unconnected.remove(room2)
                
    def _create_corridor(self, room1: Room, room2: Room) -> None:
        """
        Create a corridor between two rooms using L-shaped paths.
        
        Args:
            room1 (Room): First room to connect
            room2 (Room): Second room to connect
        """
        # Get room centers
        start = room1.center()
        end = room2.center()
        
        # Create L-shaped corridor by going horizontal then vertical
        # This ensures we don't get diagonal corridors that can't be walked
        mid_x = start.x
        mid_y = end.y
        
        # Randomly choose whether to go horizontal or vertical first
        if random.choice([True, False]):
            # Horizontal then vertical
            self._place_corridor_segment(start.x, start.y, mid_x, start.y)  # Horizontal
            self._place_corridor_segment(mid_x, start.y, mid_x, end.y)      # Vertical
            self._place_corridor_segment(mid_x, end.y, end.x, end.y)        # Horizontal
        else:
            # Vertical then horizontal
            self._place_corridor_segment(start.x, start.y, start.x, mid_y)  # Vertical
            self._place_corridor_segment(start.x, mid_y, end.x, mid_y)      # Horizontal
            self._place_corridor_segment(end.x, mid_y, end.x, end.y)        # Vertical
            
    def _place_corridor_segment(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """
        Place a straight corridor segment between two points.
        
        Args:
            x1 (int): Starting X coordinate
            y1 (int): Starting Y coordinate
            x2 (int): Ending X coordinate
            y2 (int): Ending Y coordinate
        """
        # Determine direction and distance
        dx = 1 if x2 > x1 else -1 if x2 < x1 else 0
        dy = 1 if y2 > y1 else -1 if y2 < y1 else 0
        
        # Place corridor tiles
        x, y = x1, y1
        while True:
            self.grid.set_tile(x, y, TileType.FLOOR)
            if x == x2 and y == y2:
                break
            x += dx
            y += dy
        
    def _room_distance(self, room1: Room, room2: Room) -> float:
        """
        Calculate the Manhattan distance between two rooms' centers.
        
        Args:
            room1 (Room): First room
            room2 (Room): Second room
            
        Returns:
            float: Manhattan distance between room centers
        """
        center1 = room1.center()
        center2 = room2.center()
        return abs(center1.x - center2.x) + abs(center1.y - center2.y)
        
    def _place_entities(self, rooms: list[Room]) -> None:
        """
        Place NPCs in the given rooms.
        
        Args:
            rooms (list[Room]): List of rooms to place entities in
        """
        for room in rooms:
            pos = Position(
                random.randint(room.position.x + 1, room.position.x + room.width - 2),
                random.randint(room.position.y + 1, room.position.y + room.height - 2)
            )
            # Random selection of NPC type
            npc_type = random.choice([
                # EntityType.BEAST,
                EntityType.UNDEAD
            ])
            new_npc = NPC(pos, npc_type)
            self.add_entity(new_npc) 