"""
Main game loop handling initialization, game state management, and core game flow.

Responsible for:
- Game initialization and settings
- Title screen management
- Game state coordination
- Update and render loop management
"""

import pygame
import Core.Events as Events
from Zone import DungeonZone
from Core.Renderer import Renderer
from Core.InputHandler import InputHandler
from TitleScreen import TitleScreen
from Menu import MenuFactory, MenuID, MENU_CONFIGS
from pathlib import Path
import logging
import os
import sys

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
        pygame.init()
        self.display_info = pygame.display.Info()
        self.width = width
        self.height = height
        self.running = True
        
        # Initialize core systems
        self.event_manager = Events.EventManager.get_instance()                    
        self.settings = self.show_title_screen()

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
        self.renderer = Renderer(self.width, self.height, fullscreen)
        
        # Set up input handling
        self.input_handler = InputHandler(self.zone, self.renderer, self.event_manager)
        
        # Connect systems
        self.renderer.set_input_handler(self.input_handler)
        self.zone.set_event_manager(self.event_manager)
        
        # Create HUD menu
        self._create_hud()
        
        # Subscribe to quit event
        self.event_manager.subscribe(Events.GameEventType.GAME_QUIT, self._handle_quit)

    def _create_hud(self) -> None:
        """Create the HUD menu with player stat handlers."""
        hud_handlers = {
            "GetPlayerHP": lambda: (self.zone.player.stats.current_hp, 
                                  self.zone.player.stats.max_hp)
        }
        menu_factory = MenuFactory(hud_handlers)
        self.hud_menu = menu_factory.create_menu(MENU_CONFIGS[MenuID.HUD])

    def _handle_quit(self) -> None:
        """Handle the quit event to stop the game loop."""
        self.running = False

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
        
        Coordinates the game systems in the following order:
        1. Process input
        2. Update game state
        3. Update camera
        4. Render frame and HUD
        5. Update display
        """
        while self.running:
            current_time = pygame.time.get_ticks()
            
            # Process input (may trigger quit)
            if self.input_handler.handle_input():
                self.running = False
                continue
            
            # Update game state
            self.zone.update(current_time)
            
            # Update camera and render everything
            if self.zone.player:  # Only center if we have a player
                self.renderer.center_on_entity(self.zone.player)
            
            # Clear screen
            self.renderer.screen.fill((0, 0, 0))
            
            # Render game world
            self.renderer.render_without_flip(self.zone)
            
            # Render HUD on top
            if hasattr(self, 'hud_menu'):
                self.hud_menu.render(self.renderer.screen, self.width, self.height)
            
            # Update display once per frame
            pygame.display.flip()
        
        # Clean up
        self.renderer.cleanup()
