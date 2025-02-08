"""
Main game loop handling initialization, game state management, and core game flow.
"""

import pygame
import Core.Events as Events
from DungeonGenerator import DungeonGenerator
from Core.Renderer import Renderer
from Core.InputHandler import InputHandler
from TitleScreen import TitleScreen
import logging

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
        self.event_manager = Events.EventManager.get_instance()  # Use singleton
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

    def _initialize_game(self, settings: dict):
        """
        Initialize game components based on settings.

        Args:
            settings (dict): Game settings from title screen
        """
        # Use the resolution provided by TitleScreen.
        if settings.get('resolution'):
            self.width, self.height = settings['resolution']
        
        self.zone = self._generate_dungeon()
        
        fullscreen = settings.get('fullscreen', False)
        self.renderer = Renderer(self.width, self.height, fullscreen)
        
        self.input_handler = InputHandler(self.zone, self.renderer, self.event_manager)
        
        # Connect renderer to input handler for camera control.
        self.renderer.set_input_handler(self.input_handler)
        self.zone.set_event_manager(self.event_manager)
        
        # Subscribe to quit event.
        self.event_manager.subscribe(Events.GameEventType.GAME_QUIT, self._handle_quit)

    def _handle_quit(self) -> None:
        """
        Handle the quit event to stop the game loop.
        """
        self.running = False

    def _generate_dungeon(self):
        """
        Generate a new dungeon layout.

        Returns:
            Dungeon: Generated dungeon instance
        """
        generator = DungeonGenerator(min_rooms=2, max_rooms=2)
        return generator.generate()

    def run(self):
        """
        Main game loop that handles input, updates, and rendering.
        """
        while self.running:
            current_time = pygame.time.get_ticks()
            
            if self.input_handler.handle_input():
                self.running = False
            
            self.zone.update(current_time)
            self.renderer.center_on_entity(self.zone.player)
            self.renderer.render(self.zone)
        
        self.renderer.cleanup()
