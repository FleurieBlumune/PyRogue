from DataModel import Grid, Position, Room, Corridor, TileType
from Entity import Entity

class Zone:
    def __init__(self):
        self.grid = Grid(100, 100)
        self.rooms = []
        self.corridors = []
        self.entities = []
        self.player = None

    def add_room(self, room: Room):
        self.rooms.append(room)
        self._carve_room(room)

    def add_corridor(self, corridor: Corridor):
        self.corridors.append(corridor)
        self._generate_corridor_path(corridor)
        self._carve_corridor(corridor)

    def _carve_room(self, room: Room):
        for y in range(room.position.y, room.position.y + room.height):
            for x in range(room.position.x, room.position.x + room.width):
                if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
                    self.grid.tiles[y][x] = TileType.FLOOR

    def _generate_corridor_path(self, corridor: Corridor):
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

    def _carve_corridor(self, corridor: Corridor):
        for pos in corridor.path:
            if 0 <= pos.x < self.grid.width and 0 <= pos.y < self.grid.height:
                self.grid.tiles[pos.y][pos.x] = TileType.FLOOR

    def get_ascii_map(self, padding=2):
        if not self.rooms:
            return "Empty dungeon!"

        min_x = max(0, min(r.position.x for r in self.rooms) - padding)
        min_y = max(0, min(r.position.y for r in self.rooms) - padding)
        max_x = min(self.grid.width-1, max(r.position.x + r.width for r in self.rooms) + padding)
        max_y = min(self.grid.height-1, max(r.position.y + r.height for r in self.rooms) + padding)

        output = []
        for y in range(min_y, max_y+1):
            row = []
            for x in range(min_x, max_x+1):
                entity_here = next(
                    (e for e in self.entities 
                     if e.position.x == x and e.position.y == y),
                    None
                )
                
                if entity_here:
                    row.append('P' if entity_here == self.player else entity_here.type.value[0])
                else:
                    row.append(self.grid.tiles[y][x].value)
            output.append(''.join(row))
        
        return "\n".join(output)
        
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
            entity.position.x = new_x
            entity.position.y = new_y
            self._update_entity_room(entity)
            return True
        return False
    
    def _update_entity_room(self, entity: Entity):
        for room in self.rooms:
            if (room.position.x <= entity.position.x < room.position.x + room.width and
                room.position.y <= entity.position.y < room.position.y + room.height):
                entity.room = room
                return
        entity.room = None