"""
Input handling system for the game.
Processes keyboard and mouse input and converts them into game actions.
"""

import pygame
from Core.TurnManager import TurnManager
from DataModel import Position
from Core.Events import EventManager, GameEventType

class InputHandler:
    """
    Handles all user input for the game.
    
    Processes keyboard and mouse events and converts them into appropriate
    game actions. Manages key repeating, mouse dragging, and camera control.
    
    Attributes:
        zone: The current game zone being handled
        renderer: The game's rendering system
        pressed_keys (dict): Currently pressed keys and their timestamps
        is_dragging (bool): Whether the user is currently dragging the view
        manual_camera_control (bool): Whether the camera is under manual control
        key_repeat_delay (int): Milliseconds before key repeat begins
        key_repeat_rate (int): Milliseconds between key repeats
    """
    
    def __init__(self, zone, renderer, event_manager: EventManager):
        """
        Initialize the input handler.

        Args:
            zone: The game zone to handle input for
            renderer: The game's rendering system
            event_manager (EventManager): The game's event management system
        """
        self.zone = zone
        self.renderer = renderer
        self.pressed_keys = {}
        self.key_repeat_delay = 200
        self.key_repeat_rate = 50
        
        # Add mouse drag tracking
        self.is_dragging = False
        self.last_mouse_pos = None
        self.manual_camera_control = False
        
        # Initialize pygame key repeat
        pygame.key.set_repeat(self.key_repeat_delay, self.key_repeat_rate)
        self.turn_manager = TurnManager.get_instance()

        self.event_manager = event_manager

    def handle_input(self) -> bool:
        """
        Process all pending input events.
        
        Returns:
            bool: True if the game should quit, False otherwise
        """
        current_time = pygame.time.get_ticks()
        quit_game = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.event_manager.emit(GameEventType.GAME_QUIT)
                quit_game = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.event_manager.emit(GameEventType.GAME_QUIT)
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
                elif event.button == 3:  # Right click
                    self.is_dragging = True
                    self.last_mouse_pos = event.pos
                    self.manual_camera_control = True
                elif event.button == 4:  # Mouse wheel up
                    self.renderer.adjust_zoom(self.renderer.zoom_step)
                elif event.button == 5:  # Mouse wheel down
                    self.renderer.adjust_zoom(-self.renderer.zoom_step)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:  # Right click release
                    self.is_dragging = False
                    self.last_mouse_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging and self.last_mouse_pos:
                    dx = self.last_mouse_pos[0] - event.pos[0]
                    dy = self.last_mouse_pos[1] - event.pos[1]
                    self.renderer.camera.move(dx, dy)
                    self.last_mouse_pos = event.pos
            elif event.type == pygame.VIDEORESIZE:
                self.renderer.handle_resize(event.w, event.h)

        self._handle_key_repeats(current_time)
        self._handle_path_movement()
        
        return quit_game

    def _handle_movement(self, key):
            dx, dy = self.zone.player.get_movement_from_key(key)
            if dx != 0 or dy != 0:
                # Move player first so that PLAYER_MOVED is emitted afterward.
                moved = self.zone.move_entity(self.zone.player, dx, dy)
                if moved:
                    # Now start the turn so that pending events (including PLAYER_MOVED) are processed.
                    self.turn_manager.start_turn()
                    # Reset manual camera control when player moves
                    if self.manual_camera_control:
                        self.manual_camera_control = False
                        self.renderer.center_on_entity(self.zone.player)

    def _handle_mouse_click(self, pos):
        """Convert screen coordinates to tile coordinates and send to player"""
        tile_x = (pos[0] + self.renderer.camera.x) // self.renderer.tile_size
        tile_y = (pos[1] + self.renderer.camera.y) // self.renderer.tile_size
        self.zone.player.handle_click(tile_x, tile_y)

    def _handle_key_repeats(self, current_time):
        for key, start_time in list(self.pressed_keys.items()):
            elapsed = current_time - start_time
            if elapsed > self.key_repeat_delay:
                repeats = (elapsed - self.key_repeat_delay) // self.key_repeat_rate
                if repeats > 0:
                    self._handle_movement(key)
                    self.pressed_keys[key] = current_time - (elapsed % self.key_repeat_rate)

    def _handle_path_movement(self):
        """Handle movement along a pre-calculated path"""
        if self.zone.player.current_path:
            dx, dy = self.zone.player.get_next_move()
            if dx != 0 or dy != 0:
                self.zone.move_entity(self.zone.player, dx, dy)
                self.turn_manager.start_turn()