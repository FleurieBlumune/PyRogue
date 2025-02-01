import pygame
from Zone import Zone
from DungeonGenerator import DungeonGenerator
from Renderer import Renderer
from Pathfinding import find_path
from DataModel import Position
import sys
import time

class Game:
    def __init__(self):
        self.zone = self._generate_dungeon()
        self.running = True
        self.renderer = Renderer(800, 600)  # Window size
        
        # Key repeat settings
        self.key_repeat_delay = 200    # Milliseconds before key starts repeating
        self.key_repeat_rate = 50      # Milliseconds between repeats
        self.pressed_keys = {}         # Dictionary to store pressed keys and their timestamps
        
        # Initialize pygame key repeat
        pygame.key.set_repeat(self.key_repeat_delay, self.key_repeat_rate)

    def _generate_dungeon(self):
        generator = DungeonGenerator(min_rooms=5, max_rooms=10)
        return generator.generate()

    def handle_input(self):
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self._handle_movement(event.key)
                    self.pressed_keys[event.key] = current_time
            elif event.type == pygame.KEYUP:
                if event.key in self.pressed_keys:
                    del self.pressed_keys[event.key]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)
        
        # Handle key repeats
        for key, start_time in list(self.pressed_keys.items()):
            elapsed = current_time - start_time
            if elapsed > self.key_repeat_delay:
                repeats = (elapsed - self.key_repeat_delay) // self.key_repeat_rate
                if repeats > 0:
                    self._handle_movement(key)
                    # Update timestamp to account for the handled repeats
                    self.pressed_keys[key] = current_time - (elapsed % self.key_repeat_rate)
        
        # Handle player movement along path
        if self.zone.player.current_path:
            if current_time - self.zone.player.last_move_time >= self.zone.player.move_delay:
                dx, dy = self.zone.player.get_next_move()
                if dx != 0 or dy != 0:
                    self.zone.move_entity(self.zone.player, dx, dy)
                    self.zone.player.last_move_time = current_time

    def _handle_movement(self, key):
        current_time = pygame.time.get_ticks()
        if current_time - self.zone.player.last_move_time >= self.zone.player.move_delay:
            dx, dy = self.zone.player.get_movement_from_key(key)
            if dx != 0 or dy != 0:
                self.zone.move_entity(self.zone.player, dx, dy)
                self.zone.player.last_move_time = current_time

    def _handle_mouse_click(self, pos):
        # Convert screen coordinates to world coordinates
        tile_x = (pos[0] + self.renderer.camera.x) // self.renderer.tile_size
        tile_y = (pos[1] + self.renderer.camera.y) // self.renderer.tile_size
        
        # Find path to clicked position
        start = self.zone.player.position
        goal = Position(tile_x, tile_y)
        
        path = find_path(start, goal, self.zone.is_passable)
        self.zone.player.set_path(path)

    def run(self):
        while self.running:
            self.handle_input()
            self.renderer.center_on_entity(self.zone.player)
            self.renderer.render(self.zone)
        
        self.renderer.cleanup()

if __name__ == "__main__":
    Game().run()