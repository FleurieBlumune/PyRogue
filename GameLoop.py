from DungeonGenerator import DungeonGenerator
from Renderer import Renderer
from InputHandler import InputHandler

class GameLoop:
    def __init__(self, width=800, height=600):
        self.zone = self._generate_dungeon()
        self.renderer = Renderer(width, height)
        self.input_handler = InputHandler(self.zone, self.renderer)
        self.running = True

    def _generate_dungeon(self):
        generator = DungeonGenerator(min_rooms=5, max_rooms=10)
        return generator.generate()

    def run(self):
        while self.running:
            if self.input_handler.handle_input():
                self.running = False
            
            self.renderer.center_on_entity(self.zone.player)
            self.renderer.render(self.zone)
        
        self.renderer.cleanup()
