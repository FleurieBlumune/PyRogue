import pygame
from DataModel import Position

class InputHandler:
    def __init__(self, zone, renderer):
        self.zone = zone
        self.renderer = renderer
        self.pressed_keys = {}
        self.key_repeat_delay = 200
        self.key_repeat_rate = 50
        
        # Initialize pygame key repeat
        pygame.key.set_repeat(self.key_repeat_delay, self.key_repeat_rate)

    def handle_input(self):
        current_time = pygame.time.get_ticks()
        quit_game = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game = True
                else:
                    self._handle_movement(event.key)
                    self.pressed_keys[event.key] = current_time
            elif event.type == pygame.KEYUP:
                if event.key in self.pressed_keys:
                    del self.pressed_keys[event.key]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)
                elif event.button == 4:  # Mouse wheel up
                    self.renderer.adjust_zoom(self.renderer.zoom_step)
                elif event.button == 5:  # Mouse wheel down
                    self.renderer.adjust_zoom(-self.renderer.zoom_step)

        self._handle_key_repeats(current_time)
        self._handle_path_movement(current_time)
        
        return quit_game

    def _handle_movement(self, key):
        current_time = pygame.time.get_ticks()
        if current_time - self.zone.player.last_move_time >= self.zone.player.move_delay:
            dx, dy = self.zone.player.get_movement_from_key(key)
            if dx != 0 or dy != 0:
                self.zone.move_entity(self.zone.player, dx, dy)
                self.zone.player.last_move_time = current_time

    def _handle_mouse_click(self, pos):
        tile_x = (pos[0] + self.renderer.camera.x) // self.renderer.tile_size
        tile_y = (pos[1] + self.renderer.camera.y) // self.renderer.tile_size
        
        start = self.zone.player.position
        goal = Position(tile_x, tile_y)
        
        from Pathfinding import find_path
        path = find_path(start, goal, self.zone.is_passable)
        self.zone.player.set_path(path)

    def _handle_key_repeats(self, current_time):
        for key, start_time in list(self.pressed_keys.items()):
            elapsed = current_time - start_time
            if elapsed > self.key_repeat_delay:
                repeats = (elapsed - self.key_repeat_delay) // self.key_repeat_rate
                if repeats > 0:
                    self._handle_movement(key)
                    self.pressed_keys[key] = current_time - (elapsed % self.key_repeat_rate)

    def _handle_path_movement(self, current_time):
        if self.zone.player.current_path:
            if current_time - self.zone.player.last_move_time >= self.zone.player.move_delay:
                dx, dy = self.zone.player.get_next_move()
                if dx != 0 or dy != 0:
                    self.zone.move_entity(self.zone.player, dx, dy)
                    self.zone.player.last_move_time = current_time
