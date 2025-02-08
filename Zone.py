import pygame
from DataModel import Grid, Position, Room, Corridor, TileType
from Entity.Entity import Entity
from Core.Events import EventManager, GameEventType
from Core.Pathfinding import PathFinder

class Zone:
    def __init__(self):
        self.grid = Grid(100, 100)
        self.rooms = []
        self.corridors = []
        self.entities = []
        self.player = None
        self.player_moved = False
        self.event_manager = None
        self.pathfinder = PathFinder.get_instance()
        self.pathfinder.set_zone(self)

    def set_event_manager(self, event_manager: EventManager) -> None:
        self.event_manager = event_manager

    def add_room(self, room: Room):
        self.rooms.append(room)
        self._carve_room(room)

    def add_corridor(self, corridor: Corridor):
        self.corridors.append(corridor)
        self._generate_corridor_path(corridor)
        self._carve_corridor(corridor)

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the zone"""
        self.entities.append(entity)
        if hasattr(entity, 'set_zone'):
            entity.set_zone(self)

    def _carve_room(self, room: Room):
        for y in range(room.position.y, room.position.y + room.height):
            for x in range(room.position.x, room.position.x + room.width):
                if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
                    self.grid.tiles[y][x] = TileType.FLOOR

    def _generate_corridor_path(self, corridor: Corridor):
        current_x, current_y = corridor.start.x, corridor.start.y
        end_x, end_y = corridor.end.x, corridor.end.y  # Fixed: was using end.y instead of corridor.end.y
        
        # Horizontal then vertical
        while current_x != end_x:
            corridor.path.append(Position(current_x, current_y))
            current_x += 1 if current_x < end_x else -1
            
        while current_y != end_y:
            corridor.path.append(Position(current_x, current_y))
            current_y += 1 if current_y < end_y else -1
        
        corridor.path.append(Position(end_x, end_y))

    def _carve_corridor(self, corridor: Corridor):
        for pos in corridor.path:
            if 0 <= pos.x < self.grid.width and 0 <= pos.y < self.grid.height:
                self.grid.tiles[pos.y][pos.x] = TileType.FLOOR
        
    def is_passable(self, x: int, y: int, ignoring: Entity = None) -> bool:
        if not (0 <= x < self.grid.width and 0 <= y < self.grid.height):
            return False
        
        tile = self.grid.tiles[y][x]
        if tile not in {TileType.FLOOR, TileType.DOOR, TileType.STAIRS}:
            return False
        
        for entity in self.entities:
            if entity == ignoring:
                continue
            if entity.position.x == x and entity.position.y == y and entity.blocks_movement:
                return False
        
        return True

    def move_entity(self, entity: Entity, dx: int, dy: int) -> bool:
        new_x = entity.position.x + dx
        new_y = entity.position.y + dy
        
        if self.is_passable(new_x, new_y, ignoring=entity):
            old_pos = Position(entity.position.x, entity.position.y)
            entity.position.x = new_x
            entity.position.y = new_y
            self._update_entity_room(entity)
            
            if entity == self.player:
                self.event_manager.emit(
                    GameEventType.PLAYER_MOVED,
                    args = {
                        'entity': entity,
                        'from_pos': old_pos,
                        'to_pos': Position(new_x, new_y)
                    }
                )
            return True
        return False

    def _update_entity_room(self, entity: Entity):
        for room in self.rooms:
            if (room.position.x <= entity.position.x < room.position.x + room.width and
                room.position.y <= entity.position.y < room.position.y + room.height):
                entity.room = room
                return
        entity.room = None


    def update(self, current_time: int) -> None:
        """Update all entities in the zone"""
        # No longer needed as updates are event-driven
        pass