"""
Input handling system for the game.
Processes keyboard and mouse input and converts them into game actions.
"""

import pygame
from Core.TurnManager import TurnManager
from Core.Position import Position
from Core.Events import EventManager, GameEventType
from MessageLog import ActivityLog

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
                elif event.button in (4, 5):  # Mouse wheel up/down
                    # Check if mouse is over activity log area (right side)
                    log_area_x = self.renderer.width * 2 / 3
                    is_over_log = event.pos[0] > log_area_x
                    
                    if is_over_log:
                        activity_log = ActivityLog.get_instance()
                        # Button 4 is wheel up (older messages), 5 is wheel down (newer messages)
                        # Note: We invert the direction because scrolling up should show older messages
                        scroll_direction = 1 if event.button == 4 else -1
                        # Use larger scroll amount if shift is held
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            scroll_amount = scroll_direction * 5  # Page scroll
                        else:
                            scroll_amount = scroll_direction  # Line scroll
                        activity_log.scroll(scroll_amount)
                    else:
                        # Regular zoom behavior when not over log
                        if event.button == 4:  # Mouse wheel up
                            self.renderer.adjust_zoom(self.renderer.zoom_step)
                        else:  # Mouse wheel down
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
                # Forward resize event to game systems
                self.event_manager.emit(GameEventType.WINDOW_RESIZED, width=event.w, height=event.h)

        self._handle_key_repeats(current_time)
        self._handle_path_movement()
        
        return quit_game

    def _handle_movement(self, key):
        dx, dy = self.zone.player.get_movement_from_key(key)
        if dx != 0 or dy != 0:
            # Move player, which will trigger turn processing in Zone.move_entity
            moved = self.zone.move_entity(self.zone.player, dx, dy)
            if moved:
                # Disable manual camera control and center on player
                self.manual_camera_control = False
                self.renderer.center_on_entity(self.zone.player)

    def _handle_mouse_click(self, pos):
        """Convert screen coordinates to tile coordinates and send to player"""
        # Check if click is in message log area using actual game area width
        if pos[0] > self.renderer.game_area_width:
            return  # Ignore clicks in the message log area
            
        # Get current tile size from tile manager
        tile_size = self.renderer.tile_manager.current_tile_size
        
        # Convert screen coordinates to tile coordinates
        tile_x = (pos[0] + self.renderer.camera.x) // tile_size
        tile_y = (pos[1] + self.renderer.camera.y) // tile_size
        self.zone.player.handle_click(tile_x, tile_y)

    def _handle_key_repeats(self, current_time):
        for key, start_time in list(self.pressed_keys.items()):
            elapsed = current_time - start_time
            if elapsed > self.key_repeat_delay:
                repeats = (elapsed - self.key_repeat_delay) // self.key_repeat_rate
                if repeats > 0:
                    self._handle_movement(key)
                    self.pressed_keys[key] = current_time - (elapsed % self.key_repeat_rate)

    def _handle_path_movement(self) -> None:
        """Handle movement along a pre-calculated path."""
        if not self.zone.player:
            return
        
        if self.zone.player.current_path:
            dx, dy = self.zone.player.get_next_move()
            
            # Move player, which will trigger turn processing in Zone.move_entity
            moved = self.zone.move_entity(self.zone.player, dx, dy)
            
            if moved:
                # Disable manual camera control and center on player
                self.manual_camera_control = False
                self.renderer.center_on_entity(self.zone.player)