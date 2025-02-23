"""
Main game loop handling initialization, game state management, and core game flow.
"""

import pygame
import Engine.Core.Events as Events
from Game.Content.Zones.DungeonZone import DungeonZone
from Engine.Renderer import Renderer
from Engine.Core.InputHandler import InputHandler
from Game.UI.TitleScreen import TitleScreen
from Game.UI.Menus.MenuFactory import MenuFactory
from Engine.UI.MenuSystem.MenuTypes import MenuID, MenuState
from Game.UI.Menus.MenuConfigs import MENU_CONFIGS
from Game.UI.Menus.InventoryMenu import InventoryMenu
from Game.UI.Menus.PauseMenu import PauseMenu
from pathlib import Path
import logging
import os
import sys
from Game.UI.Menus.MessageLog import ActivityLog
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

@dataclass
class GameState:
    """
    Container for game state data to reduce direct attribute access and coupling.
    
    Attributes:
        width (int): Current window width
        height (int): Current window height
        running (bool): Whether the game is running
        needs_render (bool): Whether the screen needs to be redrawn
        settings (dict): Game settings from title screen
    """
    width: int
    height: int
    running: bool = True
    needs_render: bool = True
    settings: Dict[str, Any] = None

class GameSystemManager:
    """
    Manages core game systems and their initialization.
    
    This class handles the creation and coordination of core game systems
    like rendering, input handling, and menu management.
    """
    
    def __init__(self, state: GameState):
        """
        Initialize game systems manager.
        
        Args:
            state (GameState): Current game state
        """
        self.logger = logging.getLogger(__name__)
        self.state = state
        self.event_manager = Events.EventManager.get_instance()
        
        # Core systems
        self.renderer: Optional[Renderer] = None
        self.input_handler: Optional[InputHandler] = None
        self.zone: Optional[DungeonZone] = None
        
        # Menu systems
        self.activity_log: Optional[ActivityLog] = None
        self.hud_menu = None
        self.activity_log_menu = None
        self.inventory_menu = None
        self.pause_menu = None
    
    def initialize_game_systems(self, settings: Dict[str, Any]) -> None:
        """
        Initialize all game systems with the provided settings.
        
        Args:
            settings (Dict[str, Any]): Game settings from title screen
        """
        try:
            # Update state with settings
            self.state.settings = settings
            if settings.get('resolution'):
                self.state.width, self.state.height = settings['resolution']
            
            # Initialize core systems in order
            self._init_zone()
            self._init_renderer(settings.get('fullscreen', False))
            self._init_input_handler()
            self._init_menus()
            
            # Set up event subscriptions
            self._setup_event_handlers()
            
            # Initial camera setup
            if self.zone.player:
                self.renderer.center_on_entity(self.zone.player)
                self.input_handler.manual_camera_control = False
                
        except Exception as e:
            self.logger.error(f"Error initializing game systems: {e}", exc_info=True)
            raise
    
    def _init_zone(self) -> None:
        """Initialize the game zone."""
        self.zone = DungeonZone(min_rooms=2, max_rooms=2)
    
    def _init_renderer(self, fullscreen: bool) -> None:
        """Initialize the rendering system."""
        self.renderer = Renderer(self.state.width, self.state.height, fullscreen)
    
    def _init_input_handler(self) -> None:
        """Initialize the input handling system."""
        self.input_handler = InputHandler(self.zone, self.renderer, self.event_manager)
        self.renderer.set_input_handler(self.input_handler)
        self.zone.set_event_manager(self.event_manager)
    
    def _init_menus(self) -> None:
        """Initialize menu systems."""
        self.activity_log = ActivityLog.get_instance()
        
        menu_handlers = {
            "GetPlayerHP": lambda: (self.zone.player.stats.current_hp, 
                                  self.zone.player.stats.max_hp),
            "GetActivityLogMessages": self.activity_log
        }
        
        menu_factory = MenuFactory(menu_handlers)
        self.hud_menu = menu_factory.create_menu(MENU_CONFIGS[MenuID.HUD])
        self.activity_log_menu = menu_factory.create_menu(MENU_CONFIGS[MenuID.ACTIVITY_LOG])
        self.inventory_menu = InventoryMenu(self.renderer.screen)
        self.pause_menu = PauseMenu(self.renderer.screen)
        
        # Configure activity log
        self._configure_activity_log()
    
    def _configure_activity_log(self) -> None:
        """Configure activity log parameters and callbacks."""
        wrap_width = max(50, self.activity_log_menu.log_width - 2 * self.activity_log_menu.padding - 12)
        self.activity_log.set_wrap_params(wrap_width, self.activity_log_menu.font_small)
        
        def on_resize(width: int) -> None:
            self.activity_log_menu.log_width = width
            self.renderer.set_game_area_width(self.state.width - width - self.activity_log_menu.padding)
            wrap_width = max(50, width - 2 * self.activity_log_menu.padding - 12)
            self.activity_log.set_wrap_params(wrap_width, self.activity_log_menu.font_small)
            
        def on_resize_end() -> None:
            if self.zone.player:
                self.renderer.center_on_entity(self.zone.player)
        
        self.activity_log_menu.set_resize_callback(on_resize, on_resize_end)
    
    def _setup_event_handlers(self) -> None:
        """Set up event subscriptions."""
        self.event_manager.subscribe(Events.GameEventType.GAME_QUIT, self._handle_quit)
        self.event_manager.subscribe(Events.GameEventType.WINDOW_RESIZED, self._handle_resize)
    
    def _handle_quit(self) -> None:
        """Handle quit event."""
        self.state.running = False
    
    def _handle_resize(self, event) -> None:
        """
        Handle window resize events.
        
        Args:
            event: Pygame resize event
        """
        try:
            old_width, old_height = self.state.width, self.state.height
            original_log_width = getattr(self.activity_log_menu, 'log_width', None)
            
            self.state.width = event.w
            self.state.height = event.h
            
            # Update systems
            self._update_renderer_size(event.w, event.h, old_width, old_height)
            self._update_menu_size(event.w, event.h, original_log_width)
            self._recenter_camera()
            
        except Exception as e:
            self.logger.error(f"Error handling resize event: {e}", exc_info=True)
    
    def _update_renderer_size(self, new_width: int, new_height: int, old_width: int, old_height: int) -> None:
        """Update renderer dimensions."""
        try:
            self.renderer.handle_resize(new_width, new_height)
        except Exception as e:
            self.logger.error(f"Error in renderer resize: {e}", exc_info=True)
            self.state.width, self.state.height = old_width, old_height
            self.renderer.handle_resize(old_width, old_height)
    
    def _update_menu_size(self, width: int, height: int, original_log_width: Optional[int]) -> None:
        """Update menu dimensions."""
        if hasattr(self, 'activity_log_menu'):
            self.activity_log_menu.handle_window_resize(width, height)
            if all(hasattr(self.activity_log_menu, attr) for attr in ['log_width', 'on_resize']) and original_log_width:
                self.activity_log_menu.on_resize(original_log_width + 1)
                self.activity_log_menu.on_resize(original_log_width)
    
    def _recenter_camera(self) -> None:
        """Recenter camera on player if available."""
        if self.zone.player:
            try:
                self.renderer.center_on_entity(self.zone.player)
            except Exception as e:
                self.logger.error(f"Error centering on player: {e}", exc_info=True)
    
    def cleanup(self) -> None:
        """Clean up game systems."""
        try:
            if self.renderer:
                self.renderer.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}", exc_info=True)

class GameLoop:
    """
    Core game loop handler that manages the main game flow and initialization.
    
    This class has been refactored to delegate most of its responsibilities to
    specialized components, focusing mainly on coordinating the game loop itself.
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize the game loop.
        
        Args:
            width (int): Initial window width
            height (int): Initial window height
        """
        self.logger = logging.getLogger(__name__)
        try:
            pygame.init()
            self.state = GameState(width=width, height=height)
            self.systems = None  # Will be initialized after title screen
            self.settings = self.show_title_screen()
        except Exception as e:
            self.logger.error(f"Error initializing GameLoop: {e}", exc_info=True)
            raise
    
    def show_title_screen(self) -> Dict[str, Any]:
        """
        Display the title screen and get initial settings.
        
        Returns:
            Dict[str, Any]: Game settings selected by the user
        """
        title_screen = TitleScreen(self.state.width, self.state.height)
        settings = {}
        
        while self.state.running:
            title_screen.render()
            should_exit, new_settings = title_screen.handle_input()
            if should_exit:
                if new_settings:
                    settings = new_settings
                break
        
        if self.state.running:
            self.systems = GameSystemManager(self.state)
            self.systems.initialize_game_systems(settings)
        
        return settings
    
    def run(self) -> None:
        """Main game loop."""
        try:
            clock = pygame.time.Clock()
            TARGET_FPS = 60
            
            while self.state.running:
                frame_start_time = pygame.time.get_ticks()
                
                try:
                    self._process_frame(frame_start_time)
                    clock.tick(TARGET_FPS)
                    
                except Exception as e:
                    self.logger.error(f"Error in game loop iteration: {e}", exc_info=True)
                    if isinstance(e, (pygame.error, SystemError)):
                        raise
                        
        except Exception as e:
            self.logger.critical(f"Fatal error in game loop: {e}", exc_info=True)
            raise
        finally:
            if self.systems:
                self.systems.cleanup()
    
    def _process_frame(self, frame_start_time: int) -> None:
        """
        Process a single frame of the game loop.
        
        Args:
            frame_start_time (int): Start time of the current frame
        """
        self._handle_events()
        
        # Process input and update game state
        if self.systems.input_handler.handle_input():
            self.state.running = False
            return
            
        self.state.needs_render = True  # Always render after input processing
        
        if self.systems.zone.update(frame_start_time):
            self.state.needs_render = True
        
        if self.state.needs_render:
            self._render_frame()
    
    def _handle_events(self) -> None:
        """Process all pending events."""
        for event in pygame.event.get():
            # Try menu handling first
            if self._handle_menu_event(event):
                continue
                
            # Handle system events
            if not handled and event.type == pygame.VIDEORESIZE:
                self.systems._handle_resize(event)
                self.state.needs_render = True
                continue
                
            # Handle mouse events
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                self._handle_mouse_wheel(event)
                continue
                
            # Post unhandled events back to the queue
            pygame.event.post(event)
            
            # Mark for render on specific events
            if event.type in (pygame.VIDEORESIZE, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                self.state.needs_render = True
    
    def _handle_menu_event(self, event) -> bool:
        """
        Handle menu-related events.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            bool: True if event was handled by menus
        """
        # Handle inventory menu first if it's visible
        if hasattr(self.systems, 'inventory_menu'):
            if self.systems.inventory_menu.handle_event(event):
                self.state.needs_render = True
                return True
        
        # Handle pause menu only if no other menu is visible
        if hasattr(self.systems, 'pause_menu'):
            # Only check for other menus when trying to open pause menu
            any_menu_visible = (
                (hasattr(self.systems, 'inventory_menu') and self.systems.inventory_menu.is_visible)
            )
            
            if not any_menu_visible or self.systems.pause_menu.is_visible:
                handled, action = self.systems.pause_menu.handle_event(event)
                if handled:
                    if action == "QUIT":
                        self.state.running = False
                    self.state.needs_render = True
                    return True
                
        # Handle other menus
        if hasattr(self.systems, 'activity_log_menu'):
            if self.systems.activity_log_menu.handle_input(event):
                self.state.needs_render = True
                return True
                
        if hasattr(self.systems, 'hud_menu'):
            if self.systems.hud_menu.handle_input(event):
                self.state.needs_render = True
                return True
                
        return False
    
    def _handle_mouse_wheel(self, event) -> None:
        """
        Handle mouse wheel events for zooming and scrolling.
        
        Args:
            event: Pygame mouse event
        """
        log_area_x = self.state.width - self.systems.activity_log_menu.log_width - self.systems.activity_log_menu.padding
        is_over_log = event.pos[0] > log_area_x
        
        if is_over_log:
            scroll_amount = -1 if event.button == 4 else 1
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                scroll_amount *= 5
            self.systems.activity_log.scroll(scroll_amount)
        else:
            zoom_amount = self.systems.renderer.zoom_step if event.button == 4 else -self.systems.renderer.zoom_step
            self.systems.renderer.adjust_zoom(zoom_amount)
            
        self.state.needs_render = True
    
    def _render_frame(self) -> None:
        """Render the current frame."""
        try:
            self.state.width, self.state.height = self.systems.renderer.screen.get_size()
            
            self.systems.renderer.screen.fill((0, 0, 0))
            self.systems.renderer.render_without_flip(self.systems.zone)
            
            # Render UI elements
            if self.systems.hud_menu:
                self.systems.hud_menu.render(self.systems.renderer.screen, self.state.width, self.state.height)
            if self.systems.activity_log_menu:
                self.systems.activity_log_menu.render(self.systems.renderer.screen, self.state.width, self.state.height)
            if self.systems.inventory_menu:
                self.systems.inventory_menu.draw()
            if self.systems.pause_menu:
                self.systems.pause_menu.draw()
            
            pygame.display.flip()
            self.state.needs_render = False
            
        except pygame.error as e:
            self.logger.error(f"Pygame error during rendering: {e}", exc_info=True)
            self.systems.renderer.handle_resize(self.state.width, self.state.height)
            self.state.needs_render = True
