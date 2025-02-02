import pygame
from typing import Dict, Tuple, List
from Zone import Zone
from DataModel import TileType
from Entity.Entity import EntityType  # Assumes an Entity class exists elsewhere


class Camera:
    """
    A simple camera to track the view offset in the game world.
    """
    def __init__(self, x: int, y: int) -> None:
        """
        Initialize the camera at the given coordinates.
        """
        self.x = x
        self.y = y

    def move(self, dx: int, dy: int) -> None:
        """
        Move the camera by the specified offsets.

        Args:
            dx (int): The offset to move along the x-axis.
            dy (int): The offset to move along the y-axis.
        """
        self.x += dx
        self.y += dy


class Renderer:
    """
    Handles rendering of the game world including tiles and entities.
    """
    def __init__(self, width: int, height: int, fullscreen: bool = False) -> None:
        """
        Initialize the renderer with a specified window size and default settings.

        Args:
            width (int): The width of the window.
            height (int): The height of the window.
            fullscreen (bool): Whether to start in fullscreen mode.
        """
        pygame.init()
        self.width = width
        self.height = height

        # Set display mode based on fullscreen setting
        if fullscreen:
            # Get monitor size for borderless fullscreen
            info = pygame.display.Info()
            self.width = info.current_w
            self.height = info.current_h
            self.screen = pygame.display.set_mode(
                (self.width, self.height),
                pygame.NOFRAME
            )
        else:
            self.screen = pygame.display.set_mode(
                (width, height),
                pygame.RESIZABLE
            )

        self.base_tile_size: int = 32  # Base size for tiles
        self.zoom_level: float = 1.0   # Current zoom level
        self.min_zoom: float = 0.5     # Minimum zoom (farthest out)
        self.max_zoom: float = 2.0     # Maximum zoom (closest in)
        self.zoom_step: float = 0.1    # Amount to adjust zoom per scroll

        self.camera = Camera(0, 0)

        # Define colors for different entity types.
        self.entity_colors: Dict[EntityType, Tuple[int, int, int]] = {
            EntityType.PLAYER: (0, 255, 0),    # Green
            EntityType.ENEMY: (255, 0, 0),     # Red
            EntityType.CHEST: (255, 215, 0),   # Gold
            EntityType.KEY: (255, 255, 0),     # Yellow
        }

        # Create base tile surfaces and initialize the scaled versions.
        self._create_base_tiles()
        self.scaled_tiles: Dict[TileType, pygame.Surface] = self._scale_tiles()

    def _create_base_tiles(self) -> None:
        """
        Create the base tile surfaces for each tile type at the original size.
        """
        self.base_tiles: Dict[TileType, pygame.Surface] = {
            TileType.WALL: self._create_tile((128, 128, 128)),   # Gray
            TileType.FLOOR: self._create_tile((64, 64, 64)),      # Dark Gray
            TileType.DOOR: self._create_tile((139, 69, 19)),       # Brown
            TileType.WATER: self._create_tile((0, 0, 139)),        # Blue
            TileType.STAIRS: self._create_tile((255, 215, 0)),     # Gold
        }

    def _create_tile(self, color: Tuple[int, int, int]) -> pygame.Surface:
        """
        Create a tile surface of the base size with a border.

        Args:
            color (Tuple[int, int, int]): The fill color for the tile.

        Returns:
            pygame.Surface: The created tile surface.
        """
        surface = pygame.Surface((self.base_tile_size, self.base_tile_size))
        surface.fill(color)
        # Draw a 1-pixel black border around the tile.
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 1)
        return surface

    def _scale_tiles(self) -> Dict[TileType, pygame.Surface]:
        """
        Scale the base tiles to the current zoom level.

        Returns:
            Dict[TileType, pygame.Surface]: A dictionary mapping each tile type to its scaled surface.
        """
        scaled_size = self.tile_size
        return {
            tile_type: pygame.transform.scale(surface, (scaled_size, scaled_size))
            for tile_type, surface in self.base_tiles.items()
        }

    @property
    def tile_size(self) -> int:
        """
        Get the current tile size adjusted for the zoom level.

        Returns:
            int: The current tile size.
        """
        return int(self.base_tile_size * self.zoom_level)

    def adjust_zoom(self, amount: float) -> None:
        """
        Adjust the zoom level by a given amount and update the scaled tiles and camera offset.

        Args:
            amount (float): The change in zoom level (positive to zoom in, negative to zoom out).
        """
        old_zoom = self.zoom_level
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, self.zoom_level + amount))

        if old_zoom != self.zoom_level:
            # Update scaled tiles to reflect the new zoom level.
            self.scaled_tiles = self._scale_tiles()

            # Adjust camera position to keep the screen center fixed.
            zoom_factor = self.zoom_level / old_zoom
            center_x = self.camera.x + self.width // 2
            center_y = self.camera.y + self.height // 2
            self.camera.x = int(center_x * zoom_factor - self.width // 2)
            self.camera.y = int(center_y * zoom_factor - self.height // 2)

    def handle_resize(self, new_width: int, new_height: int) -> None:
        """
        Handle window resize events.
        """
        self.width = new_width
        self.height = new_height
        self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

    def render(self, zone: Zone) -> None:
        """
        Render the current zone, drawing both tiles and entities.

        Args:
            zone (Zone): The zone to render.
        """
        # Get current window size in case of resize
        self.width, self.height = self.screen.get_size()
        self.screen.fill((0, 0, 0))  # Clear the screen with a black background

        # Calculate the range of grid coordinates visible on screen.
        start_x = max(0, self.camera.x // self.tile_size)
        start_y = max(0, self.camera.y // self.tile_size)
        end_x = min(zone.grid.width, (self.camera.x + self.width) // self.tile_size + 1)
        end_y = min(zone.grid.height, (self.camera.y + self.height) // self.tile_size + 1)

        # Draw the tiles within the visible range.
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * self.tile_size - self.camera.x
                screen_y = y * self.tile_size - self.camera.y
                tile_type = zone.grid.tiles[y][x]
                self.screen.blit(self.scaled_tiles[tile_type], (screen_x, screen_y))

        # Draw each entity as a circle.
        entity_radius = self.tile_size // 3
        for entity in zone.entities:
            screen_x = entity.position.x * self.tile_size - self.camera.x
            screen_y = entity.position.y * self.tile_size - self.camera.y

            # Only draw the entity if it's within the screen bounds.
            if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                pygame.draw.circle(
                    self.screen,
                    self.entity_colors[entity.type],
                    (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),
                    entity_radius
                )

        pygame.display.flip()

    def center_on_entity(self, entity) -> None:
        """
        Center the camera on the specified entity.

        Args:
            entity: An entity with a 'position' attribute.
        """
        # Only center if we're not in manual camera control mode
        if not hasattr(self, '_input_handler') or not self._input_handler.manual_camera_control:
            self.camera.x = entity.position.x * self.tile_size - self.width // 2
            self.camera.y = entity.position.y * self.tile_size - self.height // 2

    def set_input_handler(self, input_handler) -> None:
        """
        Set the input handler reference for camera control checks.
        """
        self._input_handler = input_handler

    def cleanup(self) -> None:
        """
        Clean up the renderer by quitting pygame.
        """
        pygame.quit()
