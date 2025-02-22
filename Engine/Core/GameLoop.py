"""
Main game loop handling initialization, game state management, and core game flow.
"""

import pygame
import pygame_gui
import Engine.Core.Events as Events
from Game.Content.Zones.DungeonZone import DungeonZone
from Engine.Renderer import Renderer
from Engine.Core.InputHandler import InputHandler
from Game.UI.TitleScreen import TitleScreen
from Engine.UI.MenuSystem import MenuState
from pathlib import Path
import logging
import os
import sys
from Game.UI.Menus import MessageLog
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
        
        # UI systems
        self.ui_manager: Optional[pygame_gui.UIManager] = None
        self.message_log: Optional[MessageLog] = None
        self.hud_panel: Optional[pygame_gui.elements.UIPanel] = None
        self.hud_label: Optional[pygame_gui.elements.UILabel] = None
        
        # Subscribe to window resize events
        self.event_manager.subscribe(Events.GameEventType.WINDOW_RESIZED, self._handle_resize)
        
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
            self._init_ui()
            
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
    
    def _init_ui(self) -> None:
        """Initialize UI systems."""
        # Initialize pygame-gui manager
        theme_path = os.path.join('Game', 'UI', 'theme.json')
        self.ui_manager = pygame_gui.UIManager((self.state.width, self.state.height), theme_path)
        
        # Initialize message log
        log_width = 300  # Default width for message log
        self.message_log = MessageLog(
            ui_manager=self.ui_manager,
            rect=pygame.Rect(self.state.width - log_width, 0, log_width, self.state.height)
        )
        
        # Initialize HUD panel
        hud_height = 40
        self.hud_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (self.state.width - log_width, hud_height)),
            manager=self.ui_manager,
            object_id="#hud_panel"
        )
        
        # Initialize HUD label inside the panel
        self.hud_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 0), (200, hud_height)),
            text=f"HP: {self.zone.player.stats.current_hp}/{self.zone.player.stats.max_hp}",
            manager=self.ui_manager,
            container=self.hud_panel
        )
        
        # Update renderer game area width and offset
        self.renderer.set_game_area_width(self.state.width - log_width)
        self.renderer.set_vertical_offset(hud_height)
    
    def _setup_event_handlers(self) -> None:
        """Set up event subscriptions."""
        self.event_manager.subscribe(Events.GameEventType.GAME_QUIT, self._handle_quit)
        self.event_manager.subscribe(Events.GameEventType.WINDOW_RESIZED, self._handle_resize)
    
    def _handle_quit(self) -> None:
        """Handle quit event."""
        self.state.running = False
        
    def _handle_resize(self, old_width: int, old_height: int, new_width: int, new_height: int) -> None:
        """
        Handle window resize events.
        
        Args:
            old_width (int): Previous window width
            old_height (int): Previous window height
            new_width (int): New window width
            new_height (int): New window height
        """
        try:
            # Update state dimensions
            self.state.width = new_width
            self.state.height = new_height
            
            # Update UI manager dimensions
            self.ui_manager.set_window_resolution((new_width, new_height))
            
            # Update game area width based on message log position
            if self.message_log:
                game_area_width = self.message_log.rect.left
                self.renderer.set_game_area_width(game_area_width)
            
            # Force a redraw
            self.state.needs_render = True
            
            # Update HUD panel width if it exists
            if self.hud_panel:
                game_area_width = self.renderer.game_area_width
                self.hud_panel.set_dimensions((game_area_width, self.hud_panel.rect.height))
            
            self.logger.debug(f"Handled resize from {old_width}x{old_height} to {new_width}x{new_height}")
            
        except Exception as e:
            self.logger.error(f"Error handling resize: {e}", exc_info=True)
            
    def update_hud(self) -> None:
        """Update the HUD display."""
        if self.hud_label and self.zone.player:
            self.hud_label.set_text(
                f"HP: {self.zone.player.stats.current_hp}/{self.zone.player.stats.max_hp}"
            )
            
    def cleanup(self) -> None:
        """Clean up resources before shutdown."""
        if self.ui_manager:
            self.ui_manager.clear_and_reset()
            
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
                settings = new_settings
                break
                
        return settings
        
    def run(self) -> None:
        """Run the main game loop."""
        try:
            # Initialize game systems
            self.systems = GameSystemManager(self.state)
            self.systems.initialize_game_systems(self.settings)
            
            clock = pygame.time.Clock()
            
            # Main game loop
            while self.state.running:
                time_delta = clock.tick(60)/1000.0
                
                # Process input and update
                self._process_frame(time_delta)
                
                # Render
                if self.state.needs_render:
                    self._render_frame()
                    self.state.needs_render = False
                    
        except Exception as e:
            self.logger.error(f"Error in main game loop: {e}", exc_info=True)
            raise
        finally:
            if self.systems:
                self.systems.cleanup()
            pygame.quit()
            
    def _process_frame(self, time_delta: float) -> None:
        """
        Process a single frame of the game.
        
        Args:
            time_delta (float): Time since last frame in seconds
        """
        try:
            # Handle events
            self._handle_events()
            
            # Update UI
            if self.systems.ui_manager:
                self.systems.ui_manager.update(time_delta)
            
            # Update HUD
            self.systems.update_hud()
            
            self.state.needs_render = True
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}", exc_info=True)
            
    def _handle_events(self) -> None:
        """Handle all pending events."""
        try:
            # Get all events once
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    self.state.running = False
                    return
                
                # Let UI manager handle events first
                if self.systems.ui_manager:
                    self.systems.ui_manager.process_events(event)
            
            # Pass all events to input handler
            if self.systems.input_handler.handle_input(events):
                self.state.running = False
                return
                    
        except Exception as e:
            self.logger.error(f"Error handling events: {e}", exc_info=True)
            
    def _render_frame(self) -> None:
        """Render a frame of the game."""
        try:
            # Render game world
            self.systems.renderer.render(self.systems.zone)
            
            # Render UI
            if self.systems.ui_manager:
                self.systems.ui_manager.draw_ui(self.systems.renderer.screen)
            
            # Update display
            pygame.display.flip()
            
        except Exception as e:
            self.logger.error(f"Error rendering frame: {e}", exc_info=True)
