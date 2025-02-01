import pygame
from Zone import Zone
from DataModel import TileType
from Entity import EntityType

class Camera:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

class Renderer:
    def __init__(self, width: int, height: int):
        pygame.init()
        self.width = width
        self.height = height
        self.tile_size = 32
        self.screen = pygame.display.set_mode((width, height))
        self.camera = Camera(0, 0)
        
        # Create basic colored tiles
        self.tiles = {
            TileType.WALL: self._create_tile((128, 128, 128)),  # Gray
            TileType.FLOOR: self._create_tile((64, 64, 64)),    # Dark Gray
            TileType.DOOR: self._create_tile((139, 69, 19)),    # Brown
            TileType.WATER: self._create_tile((0, 0, 139)),     # Blue
            TileType.STAIRS: self._create_tile((255, 215, 0)),  # Gold
        }
        
        self.entity_colors = {
            EntityType.PLAYER: (0, 255, 0),    # Green
            EntityType.ENEMY: (255, 0, 0),     # Red
            EntityType.CHEST: (255, 215, 0),   # Gold
            EntityType.KEY: (255, 255, 0),     # Yellow
        }

    def _create_tile(self, color):
        surface = pygame.Surface((self.tile_size, self.tile_size))
        surface.fill(color)
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 1)  # Black border
        return surface

    def render(self, zone: Zone):
        self.screen.fill((0, 0, 0))  # Black background
        
        # Calculate visible range based on camera position
        start_x = max(0, self.camera.x // self.tile_size)
        start_y = max(0, self.camera.y // self.tile_size)
        end_x = min(zone.grid.width, (self.camera.x + self.width) // self.tile_size + 1)
        end_y = min(zone.grid.height, (self.camera.y + self.height) // self.tile_size + 1)

        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * self.tile_size - self.camera.x
                screen_y = y * self.tile_size - self.camera.y
                tile_type = zone.grid.tiles[y][x]
                self.screen.blit(self.tiles[tile_type], (screen_x, screen_y))

        # Draw entities
        for entity in zone.entities:
            screen_x = entity.position.x * self.tile_size - self.camera.x
            screen_y = entity.position.y * self.tile_size - self.camera.y
            if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                pygame.draw.circle(
                    self.screen,
                    self.entity_colors[entity.type],
                    (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),
                    self.tile_size // 3
                )

        pygame.display.flip()

    def center_on_entity(self, entity):
        self.camera.x = entity.position.x * self.tile_size - self.width // 2
        self.camera.y = entity.position.y * self.tile_size - self.height // 2

    def cleanup(self):
        pygame.quit()
