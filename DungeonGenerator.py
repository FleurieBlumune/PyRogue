from Zone import Zone
from DataModel import Room, Position, Corridor
from Entity.Player import Player
from Entity.Enemy import Enemy
import random

class DungeonGenerator:
    def __init__(self, min_rooms=5, max_rooms=10):
        self.min_rooms = min_rooms
        self.max_rooms = max_rooms
        self.min_room_size = 4
        self.max_room_size = 10
        self.dungeon_padding = 2
        self.num_enemies = 3  # Number of enemies to spawn

    def generate(self) -> Zone:
        zone = Zone()
        rooms = self._generate_rooms()
        
        # Add rooms to zone
        for room in rooms:
            zone.add_room(room)

        # Connect rooms
        for i in range(len(rooms) - 1):
            corridor = Corridor(rooms[i].center(), rooms[i + 1].center())
            zone.add_corridor(corridor)

        # Place player in first room
        player = Player(rooms[0].center())
        zone.player = player
        zone.entities.append(player)
        
        # Place enemies in random rooms (excluding first room)
        for _ in range(self.num_enemies):
            if len(rooms) > 1:  # Only if we have rooms other than the starting room
                room = random.choice(rooms[1:])  # Select random room except first
                enemy_pos = Position(
                    random.randint(room.position.x + 1, room.position.x + room.width - 2),
                    random.randint(room.position.y + 1, room.position.y + room.height - 2)
                )
                enemy = Enemy(enemy_pos)
                zone.entities.append(enemy)
        
        return zone

    def _generate_rooms(self) -> list[Room]:
        rooms = []
        num_rooms = random.randint(self.min_rooms, self.max_rooms)
        
        for _ in range(num_rooms):
            for attempt in range(50):  # Limit attempts to prevent infinite loops
                width = random.randint(self.min_room_size, self.max_room_size)
                height = random.randint(self.min_room_size, self.max_room_size)
                x = random.randint(self.dungeon_padding, 100 - width - self.dungeon_padding)
                y = random.randint(self.dungeon_padding, 100 - height - self.dungeon_padding)
                
                new_room = Room(Position(x, y), width, height)
                
                # Check if room overlaps with existing rooms
                if not self._rooms_overlap(new_room, rooms):
                    rooms.append(new_room)
                    break
                    
        return rooms

    def _rooms_overlap(self, new_room: Room, existing_rooms: list[Room]) -> bool:
        for room in existing_rooms:
            # Add padding between rooms
            if (new_room.position.x - 2 < room.position.x + room.width and
                new_room.position.x + new_room.width + 2 > room.position.x and
                new_room.position.y - 2 < room.position.y + room.height and
                new_room.position.y + new_room.height + 2 > room.position.y):
                return True
        return False
