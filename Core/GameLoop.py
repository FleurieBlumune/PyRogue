"""
Main game loop handling initialization, game state management, and core game flow.
"""

import pygame
import Core.Events as Events
from Zone import DungeonZone
from Core.Renderer import Renderer  # Import from new modular package
from Core.InputHandler import InputHandler
from TitleScreen import TitleScreen
from Menu.MenuFactory import MenuFactory
from Menu.MenuTypes import MenuID, MenuState
from Menu.MenuConfigs import MENU_CONFIGS
from pathlib import Path
import logging
import os
import sys
from MessageLog import ActivityLog

class GameLoop:
    """
    Core game loop handler that manages the main game flow and initialization.

    Responsible for:
    - Initializing game systems
    - Showing title screen
    - Managing game state
    - Coordinating updates and rendering
    
    Attributes:
        width (int): Window width
        height (int): Window height
        running (bool): Game running state
        event_manager (EventManager): Central event system
        settings (dict): Game settings from title screen
        zone (Zone): Current game zone
        renderer (Renderer): Game rendering system
        input_handler (InputHandler): Input processing system
        hud_menu (Menu): HUD menu for displaying stats
    """

    def __init__(self, width=800, height=600):
        """
        Initialize the game loop with specified dimensions.

        Args:
            width (int): Initial window width
            height (int): Initial window height
        """
        self.logger = logging.getLogger(__name__)
        try:
            pygame.init()
            self.display_info = pygame.display.Info()
            self.logger.debug(f"Initial display info: {self.display_info}")
            self.width = width
            self.height = height
            self.running = True
            
            # Initialize core systems
            self.event_manager = Events.EventManager.get_instance()                    
            self.settings = self.show_title_screen()
        except Exception as e:
            self.logger.error(f"Error initializing GameLoop: {e}", exc_info=True)
            raise

    def show_title_screen(self) -> dict:
        """
        Display the title screen and get initial settings.

        Returns:
            dict: Game settings selected by the user
        """
        title_screen = TitleScreen(self.width, self.height)
        settings = {}
        while self.running:
            title_screen.render()
            should_exit, new_settings = title_screen.handle_input()
            if should_exit:
                if new_settings:  # If we have settings, start the game
                    settings = new_settings
                break
        
        if self.running:  # Only initialize game if we didn't quit
            self._initialize_game(settings)
        
        return settings

    def _initialize_game(self, settings: dict) -> None:
        """
        Initialize game components based on settings.

        Args:
            settings (dict): Game settings from title screen
        """
        # Use the resolution provided by TitleScreen.
        if settings.get('resolution'):
            self.width, self.height = settings['resolution']
        
        # Generate initial zone
        self.zone = self._generate_dungeon()
        
        # Initialize renderer with settings
        fullscreen = settings.get('fullscreen', False)
        self.renderer = Renderer(self.width, self.height, fullscreen)  # Uses new modular Renderer
        
        # Set up input handling
        self.input_handler = InputHandler(self.zone, self.renderer, self.event_manager)
        
        # Connect systems
        self.renderer.set_input_handler(self.input_handler)
        self.zone.set_event_manager(self.event_manager)
        
        # Create HUD and activity log menus
        self._create_menus()
        
        # Subscribe to quit and resize events
        self.event_manager.subscribe(Events.GameEventType.GAME_QUIT, self._handle_quit)
        self.event_manager.subscribe(Events.GameEventType.WINDOW_RESIZED, self._handle_resize)
        
        # Initial camera centering on player
        if self.zone.player:
            self.renderer.center_on_entity(self.zone.player)
            # Force manual camera control off initially
            self.input_handler.manual_camera_control = False

    def _create_menus(self) -> None:
        """Create the HUD and activity log menus with their handlers."""
        # Get singleton instance and keep a reference
        self.activity_log = ActivityLog.get_instance()
        
        menu_handlers = {
            "GetPlayerHP": lambda: (self.zone.player.stats.current_hp, 
                                  self.zone.player.stats.max_hp),
            "GetActivityLogMessages": self.activity_log  # Pass the instance itself, not just the method
        }
        menu_factory = MenuFactory(menu_handlers)
        self.hud_menu = menu_factory.create_menu(MENU_CONFIGS[MenuID.HUD])
        self.activity_log_menu = menu_factory.create_menu(MENU_CONFIGS[MenuID.ACTIVITY_LOG])
        
        # Set up initial log width for text wrapping
        wrap_width = max(50, self.activity_log_menu.log_width - 2 * self.activity_log_menu.padding - 12)
        self.activity_log.set_wrap_params(wrap_width, self.activity_log_menu.font_small)
        
        # Set up resize callbacks for activity log
        def on_resize(width):
            # Update the menu's internal width
            self.activity_log_menu.log_width = width
            
            # Update game area width during drag
            self.renderer.set_game_area_width(self.width - width - self.activity_log_menu.padding)
            
            # Update wrap width when log width changes
            wrap_width = max(50, width - 2 * self.activity_log_menu.padding - 12)
            self.activity_log.set_wrap_params(wrap_width, self.activity_log_menu.font_small)
            
            self.logger.debug(f"Activity log resized to {width}, game area width: {self.width - width - self.activity_log_menu.padding}")
            
        def on_resize_end():
            # Recenter the view after resizing is complete
            if self.zone.player:
                self.renderer.center_on_entity(self.zone.player)
                
        self.activity_log_menu.set_resize_callback(on_resize, on_resize_end)

    def _handle_quit(self) -> None:
        """Handle the quit event to stop the game loop."""
        self.running = False

    def _handle_resize(self, event) -> None:
        """Handle window resize events."""
        try:
            self.logger.debug(f"Handling resize event in GameLoop: {event.w}x{event.h}")
            old_width, old_height = self.width, self.height
            
            # Store original log width before any resizing
            original_log_width = None
            if hasattr(self, 'activity_log_menu') and hasattr(self.activity_log_menu, 'log_width'):
                original_log_width = self.activity_log_menu.log_width
                self.logger.debug(f"Original message log width: {original_log_width}")
            
            self.width = event.w
            self.height = event.h
            
            # Update the renderer's dimensions
            try:
                self.logger.debug("Updating renderer dimensions...")
                self.renderer.handle_resize(event.w, event.h)
            except Exception as e:
                self.logger.error(f"Error in renderer resize: {e}", exc_info=True)
                # Try to recover
                self.width, self.height = old_width, old_height
                self.renderer.handle_resize(old_width, old_height)
                return
            
            # Update menu dimensions
            if hasattr(self, 'activity_log_menu'):
                self.logger.debug("Handling activity log menu resize...")
                self.activity_log_menu.handle_window_resize(event.w, event.h)
                # Force a small resize to sync everything up
                if hasattr(self.activity_log_menu, 'log_width') and self.activity_log_menu.on_resize and original_log_width is not None:
                    self.logger.debug(f"Forcing sync with original width: {original_log_width}")
                    # First set to original width + 1, then back to original width
                    self.activity_log_menu.on_resize(original_log_width + 1)
                    self.activity_log_menu.on_resize(original_log_width)
                    self.logger.debug("Sync adjustment complete")
                else:
                    self.logger.warning("Activity log menu missing required attributes for sync")
            else:
                self.logger.warning("No activity log menu found during resize")
            
            # Recenter on player if available
            if self.zone.player:
                try:
                    self.renderer.center_on_entity(self.zone.player)
                except Exception as e:
                    self.logger.error(f"Error centering on player: {e}", exc_info=True)
                    
        except Exception as e:
            self.logger.error(f"Error handling resize event: {e}", exc_info=True)

    def _generate_dungeon(self):
        """
        Generate a new dungeon zone.

        Returns:
            DungeonZone: Generated dungeon zone
        """
        return DungeonZone(min_rooms=2, max_rooms=2)

    def run(self) -> None:
        """
        Main game loop that handles input, updates, and rendering.
        """
        try:
            clock = pygame.time.Clock()
            TARGET_FPS = 60
            needs_render = True  # Force initial render
            
            while self.running:
                frame_start_time = pygame.time.get_ticks()
                
                try:
                    # Process all events
                    for event in pygame.event.get():
                        # First try to handle with menus
                        menu_handled = False
                        if hasattr(self, 'activity_log_menu'):
                            if self.activity_log_menu.handle_input(event):
                                menu_handled = True
                                needs_render = True
                        if not menu_handled and hasattr(self, 'hud_menu'):
                            if self.hud_menu.handle_input(event):
                                menu_handled = True
                                needs_render = True
                        
                        # Handle resize events directly
                        if event.type == pygame.VIDEORESIZE:
                            self._handle_resize(event)
                            needs_render = True
                            continue
                        
                        # If menus didn't handle it, add it back to the event queue for the game
                        if not menu_handled:
                            # Handle zoom events directly
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if event.button in (4, 5):  # Mouse wheel
                                    # Check if mouse is over activity log area (right side)
                                    log_area_x = self.renderer.width * 2 / 3
                                    is_over_log = event.pos[0] > log_area_x
                                    
                                    if not is_over_log:
                                        # Regular zoom behavior when not over log
                                        zoom_amount = self.renderer.zoom_step if event.button == 4 else -self.renderer.zoom_step
                                        self.renderer.adjust_zoom(zoom_amount)
                                        needs_render = True
                                        continue
                            pygame.event.post(event)
                            
                        # Mark for render on specific events
                        if event.type in (pygame.VIDEORESIZE, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                            needs_render = True
                    
                    # Process remaining input (may trigger quit)
                    if self.input_handler.handle_input():
                        self.running = False
                        continue
                    needs_render = True  # Always render after input processing
                    
                    # Update game state
                    if self.zone.update(frame_start_time):
                        needs_render = True
                    
                    # Only render if something has changed
                    if needs_render:
                        # Get current screen dimensions from renderer
                        self.width, self.height = self.renderer.screen.get_size()
                        
                        # Clear screen and render frame
                        try:
                            self.renderer.screen.fill((0, 0, 0))
                            self.renderer.render_without_flip(self.zone)
                            
                            # Render HUD and activity log on top
                            if hasattr(self, 'hud_menu'):
                                self.hud_menu.render(self.renderer.screen, self.width, self.height)
                            if hasattr(self, 'activity_log_menu'):
                                self.activity_log_menu.render(self.renderer.screen, self.width, self.height)
                            
                            # Update display once per frame
                            pygame.display.flip()
                            needs_render = False
                            
                        except pygame.error as e:
                            self.logger.error(f"Pygame error during rendering: {e}", exc_info=True)
                            # Try to recover by reinitializing the display
                            self.renderer.handle_resize(self.width, self.height)
                            needs_render = True
                    
                    # Control frame rate
                    clock.tick(TARGET_FPS)
                        
                except Exception as e:
                    self.logger.error(f"Error in game loop iteration: {e}", exc_info=True)
                    # Only exit if it's a fatal error
                    if isinstance(e, (pygame.error, SystemError)):
                        raise
        except Exception as e:
            self.logger.critical(f"Fatal error in game loop: {e}", exc_info=True)
            raise
        finally:
            # Clean up
            try:
                self.renderer.cleanup()
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}", exc_info=True)
