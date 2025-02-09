"""
Unit tests for Zone functionality.

Tests both base Zone functionality and DungeonZone-specific features.
"""

import pytest
from Zone import Zone, DungeonZone
from Zone.Room import Room
from Zone.TileType import TileType
from Core.Position import Position
from Entity.Player import Player
from Entity.NPC import NPC
from Entity.EntityType import EntityType

class TestBaseZone:
    """Tests for the base Zone class functionality."""
    
    @pytest.fixture
    def zone(self):
        """Create a basic zone for testing."""
        return Zone(width=20, height=20)
        
    def test_zone_initialization(self, zone):
        """Test that zone is initialized with correct dimensions."""
        assert zone.width == 20
        assert zone.height == 20
        assert zone.player is None
        assert len(zone.entities) == 0
        
    def test_add_entity(self, zone):
        """Test adding entities to the zone."""
        player = Player(Position(5, 5))
        npc = NPC(Position(10, 10), EntityType.BEAST)
        
        zone.add_entity(player)
        assert len(zone.entities) == 1
        assert zone.player == player
        
        zone.add_entity(npc)
        assert len(zone.entities) == 2
        assert npc in zone.entities
        
    def test_add_room(self, zone):
        """Test adding a room to the zone."""
        room = Room(Position(5, 5), width=3, height=3)
        zone.add_room(room)
        
        # Check that floor tiles were placed
        for y in range(5, 8):
            for x in range(5, 8):
                assert zone.grid.get_tile(x, y) == TileType.FLOOR
                
    def test_is_passable(self, zone):
        """Test passability checks."""
        # Add a room with floor tiles
        room = Room(Position(5, 5), width=3, height=3)
        zone.add_room(room)
        
        # Floor should be passable
        assert zone.is_passable(6, 6) == True
        
        # Walls should not be passable
        assert zone.is_passable(0, 0) == False
        
        # Add an entity and check collision
        npc = NPC(Position(6, 6), EntityType.BEAST)
        npc.blocks_movement = True
        zone.add_entity(npc)
        
        assert zone.is_passable(6, 6) == False
        assert zone.is_passable(6, 6, ignoring=npc) == True
        
class TestDungeonZone:
    """Tests for the DungeonZone class functionality."""
    
    @pytest.fixture
    def dungeon(self):
        """Create a dungeon zone with controlled parameters for testing."""
        return DungeonZone(min_rooms=2, max_rooms=2, width=30, height=30)
        
    def test_dungeon_initialization(self, dungeon):
        """Test that dungeon is initialized with correct parameters."""
        assert dungeon.width == 30
        assert dungeon.height == 30
        assert dungeon.min_rooms == 2
        assert dungeon.max_rooms == 2
        assert dungeon.max_corridor_length == 5
        
    def test_dungeon_generation(self, dungeon):
        """Test that dungeon generates with expected features."""
        # Should have a player
        assert dungeon.player is not None
        
        # Should have NPCs
        assert len([e for e in dungeon.entities if isinstance(e, NPC)]) > 0
        
        # Should have rooms with floor tiles
        has_floor = False
        for y in range(dungeon.height):
            for x in range(dungeon.width):
                if dungeon.grid.get_tile(x, y) == TileType.FLOOR:
                    has_floor = True
                    break
            if has_floor:
                break
        assert has_floor
        
    def test_room_placement(self, dungeon):
        """Test that rooms are placed within bounds and don't overlap."""
        floor_positions = set()
        
        # Collect all floor tile positions
        for y in range(dungeon.height):
            for x in range(dungeon.width):
                if dungeon.grid.get_tile(x, y) == TileType.FLOOR:
                    floor_positions.add((x, y))
        
        # Should have some floor tiles
        assert len(floor_positions) > 0
        
        # All floor tiles should be within bounds
        for x, y in floor_positions:
            assert 0 <= x < dungeon.width
            assert 0 <= y < dungeon.height
            
    def test_room_connectivity(self, dungeon):
        """Test that all rooms are connected by corridors."""
        # Find all floor tiles
        floor_tiles = set()
        for y in range(dungeon.height):
            for x in range(dungeon.width):
                if dungeon.grid.get_tile(x, y) == TileType.FLOOR:
                    floor_tiles.add((x, y))
        
        # Flood fill from player position to ensure all floor tiles are reachable
        start = (dungeon.player.position.x, dungeon.player.position.y)
        reachable = self._flood_fill(dungeon, start)
        
        # Find unreachable tiles for debugging
        unreachable = floor_tiles - reachable
        if unreachable:
            # Print a simple ASCII map for debugging
            print("\nDungeon Map ('P'=player, 'R'=reachable, 'U'=unreachable, '.'=wall):")
            for y in range(dungeon.height):
                row = ""
                for x in range(dungeon.width):
                    if (x, y) == start:
                        row += "P"
                    elif (x, y) in unreachable:
                        row += "U"
                    elif (x, y) in reachable:
                        row += "R"
                    else:
                        row += "."
                print(row)
            
            print(f"\nFound {len(unreachable)} unreachable floor tiles!")
            
        # All floor tiles should be reachable
        assert len(unreachable) == 0, f"Found {len(unreachable)} unreachable floor tiles"
        
    def _flood_fill(self, dungeon, start: tuple[int, int]) -> set[tuple[int, int]]:
        """Helper method to flood fill from a position."""
        to_visit = {start}
        visited = set()
        
        while to_visit:
            x, y = to_visit.pop()
            if (x, y) in visited:
                continue
                
            visited.add((x, y))
            
            # Check cardinal and diagonal directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0),
                          (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                new_x, new_y = x + dx, y + dy
                if (new_x, new_y) not in visited and dungeon.grid.is_passable_terrain(new_x, new_y):
                    to_visit.add((new_x, new_y))
                    
        return visited 