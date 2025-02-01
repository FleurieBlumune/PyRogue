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
        self.base_tile_size = 32  # Base size for tiles
        self.zoom_level = 1.0     # Current zoom level
        self.min_zoom = 0.5       # Maximum zoom out
        self.max_zoom = 2.0       # Maximum zoom in
        self.zoom_step = 0.1      # How much to zoom per scroll
        self.screen = pygame.display.set_mode((width, height))
        self.camera = Camera(0, 0)
        
        # Entity colors
        self.entity_colors = {
            EntityType.PLAYER: (0, 255, 0),    # Green
            EntityType.ENEMY: (255, 0, 0),     # Red
            EntityType.CHEST: (255, 215, 0),   # Gold
            EntityType.KEY: (255, 255, 0),     # Yellow
        }
        
        # Create and store base tiles at original size
        self._create_base_tiles()
        # Initialize scaled tiles with current zoom
        self.scaled_tiles = self._scale_tiles()

    def _create_base_tiles(self):
        self.base_tiles = {
            TileType.WALL: self._create_tile((128, 128, 128)),   # Gray
            TileType.FLOOR: self._create_tile((64, 64, 64)),     # Dark Gray
            TileType.DOOR: self._create_tile((139, 69, 19)),     # Brown
            TileType.WATER: self._create_tile((0, 0, 139)),      # Blue
            TileType.STAIRS: self._create_tile((255, 215, 0)),   # Gold
        }

    def _create_tile(self, color):
        surface = pygame.Surface((self.base_tile_size, self.base_tile_size))
        surface.fill(color)
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 1)
        return surface

    def _scale_tiles(self):
        scaled_size = int(self.base_tile_size * self.zoom_level)
        return {
            tile_type: pygame.transform.scale(surface, (scaled_size, scaled_size))
            for tile_type, surface in self.base_tiles.items()
        }

    @property
    def tile_size(self):
        return int(self.base_tile_size * self.zoom_level)

    def adjust_zoom(self, amount):
        old_zoom = self.zoom_level
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, self.zoom_level + amount))
        
        if old_zoom != self.zoom_level:
            # Update scaled tiles
            self.scaled_tiles = self._scale_tiles()
            
            # Adjust camera to keep the center point the same
            zoom_factor = self.zoom_level / old_zoom
            center_x = self.camera.x + self.width // 2
            center_y = self.camera.y + self.height // 2
            self.camera.x = int(center_x * zoom_factor - self.width // 2)
            self.camera.y = int(center_y * zoom_factor - self.height // 2)

    def render(self, zone: Zone):
        self.screen.fill((0, 0, 0))  # Black background
        
        # Calculate visible range based on camera position
        start_x = max(0, self.camera.x // self.tile_size)
        start_y = max(0, self.camera.y // self.tile_size)
        end_x = min(zone.grid.width, (self.camera.x + self.width) // self.tile_size + 1)
        end_y = min(zone.grid.height, (self.camera.y + self.height) // self.tile_size + 1)

        # Draw tiles using scaled tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * self.tile_size - self.camera.x
                screen_y = y * self.tile_size - self.camera.y
                tile_type = zone.grid.tiles[y][x]
                self.screen.blit(self.scaled_tiles[tile_type], (screen_x, screen_y))

        # Draw entities with scaled size
        entity_radius = int(self.tile_size // 3)
        for entity in zone.entities:
            screen_x = entity.position.x * self.tile_size - self.camera.x
            screen_y = entity.position.y * self.tile_size - self.camera.y
            if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                pygame.draw.circle(
                    self.screen,
                    self.entity_colors[entity.type],
                    (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),
                    entity_radius
                )

        pygame.display.flip()

    def center_on_entity(self, entity):
        self.camera.x = entity.position.x * self.tile_size - self.width // 2
        self.camera.y = entity.position.y * self.tile_size - self.height // 2

    def cleanup(self):
        pygame.quit()
