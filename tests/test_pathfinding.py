import pytest
from Core.Pathfinding import PathFinder
from DataModel import Position, Grid, TileType
from Entity.Entity import Entity, EntityType

class MiniZone:
    """Minimal concrete Zone implementation for testing"""
    def __init__(self, width: int, height: int):
        self.grid = Grid(width, height)
        self.entities = []
        
        # Set all tiles to floor by default
        for y in range(height):
            for x in range(width):
                self.grid.tiles[y][x] = TileType.FLOOR

    def add_wall(self, x: int, y: int):
        """Add a wall at the specified position"""
        self.grid.tiles[y][x] = TileType.WALL

    def add_entity(self, entity: Entity):
        """Add an entity to the zone"""
        self.entities.append(entity)

    def is_passable(self, x: int, y: int, ignoring: Entity = None) -> bool:
        """Real passability check using actual game logic"""
        if not (0 <= x < self.grid.width and 0 <= y < self.grid.height):
            return False
        
        if self.grid.tiles[y][x] not in {TileType.FLOOR, TileType.DOOR, TileType.STAIRS}:
            return False
            
        for entity in self.entities:
            if entity == ignoring:
                continue
            if entity.position.x == x and entity.position.y == y and entity.blocks_movement:
                return False
                
        return True

@pytest.fixture
def pathfinder():
    """Get the PathFinder singleton instance"""
    return PathFinder.get_instance()

@pytest.fixture
def empty_zone():
    """Create a 10x10 zone with all floor tiles"""
    return MiniZone(10, 10)

@pytest.fixture
def walled_zone():
    """Create a 10x10 zone with a vertical wall"""
    zone = MiniZone(10, 10)
    for y in range(5):
        zone.add_wall(2, y)
    return zone

@pytest.fixture
def blocked_zone():
    """Create a 10x10 zone with a horizontal wall"""
    zone = MiniZone(10, 10)
    for x in range(10):
        zone.add_wall(x, 5)
    return zone

class TestPathFinder:
    def test_singleton_behavior(self):
        p1 = PathFinder.get_instance()
        p2 = PathFinder.get_instance()
        assert p1 is p2

    @pytest.mark.parametrize("start,end,expected_length", [
        ((0, 0), (1, 1), 1),    # Diagonal move
        ((0, 0), (2, 0), 2),    # Horizontal move
        ((0, 0), (0, 2), 2),    # Vertical move
        ((0, 0), (2, 2), 2),    # Mixed move
    ])
    def test_path_lengths(self, pathfinder, empty_zone, start, end, expected_length):
        pathfinder.set_zone(empty_zone)
        path = pathfinder.find_path(
            Position(start[0], start[1]),
            Position(end[0], end[1]),
            None
        )
        assert len(path) == expected_length

    def test_wall_avoidance(self, pathfinder, walled_zone):
        pathfinder.set_zone(walled_zone)
        path = pathfinder.find_path(
            Position(0, 2),
            Position(4, 2),
            None
        )
        # Path should go around the wall
        assert len(path) > 4  # Direct path would be 4, but must be longer to go around
        # Verify no position in path is a wall
        for pos in path:
            assert walled_zone.is_passable(pos.x, pos.y)

    def test_path_with_blocking_entity(self, pathfinder, empty_zone):
        pathfinder.set_zone(empty_zone)
        
        # Create a blocking entity in the middle
        blocker = Entity(EntityType.ENEMY, Position(2, 2), blocks_movement=True)
        empty_zone.add_entity(blocker)
        
        # Try to path from left to right of blocker
        test_entity = Entity(EntityType.PLAYER, Position(0, 2))
        path = pathfinder.find_path(
            Position(0, 2),
            Position(4, 2),
            test_entity
        )
        
        # Debug print the path
        path_coords = [(pos.x, pos.y) for pos in path]
        print(f"\nPath found: {path_coords}")
        print(f"Blocker at: ({blocker.position.x}, {blocker.position.y})")
        
        # Path must be either 4 steps (up and over) or 6 steps (around)
        assert len(path) in (4, 6), f"Expected path length 4 or 6 (valid detours), got {len(path)}"
        
        # Verify each step in the path is passable
        for pos in path:
            assert empty_zone.is_passable(pos.x, pos.y, test_entity), \
                f"Position {pos.x},{pos.y} in path is not passable"
            assert not (pos.x == blocker.position.x and pos.y == blocker.position.y), \
                f"Path goes through blocking entity at {pos}"
        
        # Verify path reaches destination
        assert path[-1].x == 4 and path[-1].y == 2, "Path didn't reach destination"

    def test_no_path_possible(self, pathfinder, blocked_zone):
        pathfinder.set_zone(blocked_zone)
        path = pathfinder.find_path(
            Position(5, 0),
            Position(5, 9),
            None
        )
        assert len(path) == 0

    def test_path_optimality(self, pathfinder, empty_zone):
        pathfinder.set_zone(empty_zone)
        path = pathfinder.find_path(
            Position(0, 0),
            Position(3, 3),
            None
        )
        assert len(path) == 3  # Should prefer 3 diagonal steps over 6 cardinal steps
