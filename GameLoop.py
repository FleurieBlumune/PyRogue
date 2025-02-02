import pygame
import Events
# from Events import EventType, Event
from DungeonGenerator import DungeonGenerator
from Renderer import Renderer
from InputHandler import InputHandler
from TitleScreen import TitleScreen

class GameLoop:
    def __init__(self, width=800, height=600):
        pygame.init()  # Move pygame.init() here
        self.display_info = pygame.display.Info()
        self.width = width
        self.height = height
        self.running = True
        self.settings = self.show_title_screen()

    def show_title_screen(self) -> dict:
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
        # Use the resolution provided by TitleScreen.
        if settings.get('resolution'):
            self.width, self.height = settings['resolution']
        
        # Remove the block that overrides resolution when fullscreen is set.
        # The TitleScreen already sets self.width/self.height correctly for fullscreen.
        
        self.event_manager = Events.EventManager()
        self.zone = self._generate_dungeon()
        
        fullscreen = settings.get('fullscreen', False)
        self.renderer = Renderer(self.width, self.height, fullscreen)
        
        self.input_handler = InputHandler(self.zone, self.renderer, self.event_manager)
        
        # Connect renderer to input handler for camera control.
        self.renderer.set_input_handler(self.input_handler)
        self.zone.set_event_manager(self.event_manager)
        
        # Subscribe to quit event.
        self.event_manager.subscribe(Events.EventType.GAME_QUIT, self._handle_quit)


    def _handle_quit(self, event: Events.Event) -> None:
        self.running = False

    def _generate_dungeon(self):
        generator = DungeonGenerator(min_rooms=5, max_rooms=10)
        return generator.generate()

    def run(self):
        while self.running:
            current_time = pygame.time.get_ticks()
            
            if self.input_handler.handle_input():
                self.running = False
            
            self.zone.update(current_time)
            self.renderer.center_on_entity(self.zone.player)
            self.renderer.render(self.zone)
        
        self.renderer.cleanup()
