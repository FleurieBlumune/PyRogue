import pygame
from enum import Enum, auto
from WindowManager import WindowManager
from Core.MenuSystem import Menu, MenuFactory, MenuItem, MenuItemType
from MenuConfigs import MENU_CONFIGS, MenuID

class MenuState(Enum):
    MAIN = auto()
    OPTIONS = auto()

class TitleScreen:
    def __init__(self, width: int, height: int):
        self.window_manager = WindowManager()
        self.screen = self.window_manager.set_mode(width, height)
        self.width, self.height = self.window_manager.get_screen_size()
        self.state = MenuState.MAIN
        
        # Create action handlers with PascalCase names
        self.menu_actions = {
            "StartGame": lambda: {"exit": True, "fullscreen": self.window_manager.fullscreen, 
                              "resolution": self.window_manager.get_current_resolution()},
            "ShowOptions": lambda: setattr(self, "state", MenuState.OPTIONS),
            "MenuBack": lambda: setattr(self, "state", MenuState.MAIN),
            "ChangeResolution": self._update_resolution,
            "ToggleFullscreen": self._toggle_fullscreen,
            "GetAvailableResolutions": lambda: [f"{w}x{h}" for w, h in self.window_manager.resolutions],
            "GetCurrentResolution": self.window_manager.get_resolution_str,
            "GetFullscreenState": lambda: self.window_manager.fullscreen
        }
        
        # Create menu factory
        self.menu_factory = MenuFactory(self.menu_actions)
        self._create_menus()
        
    def _create_menus(self):
        self.main_menu = self.menu_factory.create_menu(MENU_CONFIGS[MenuID.MAIN])
        self.options_menu = self.menu_factory.create_menu(MENU_CONFIGS[MenuID.OPTIONS])
        
    def _update_resolution(self):
        self.width, self.height = self.window_manager.cycle_resolution()
        self.screen = self.window_manager.screen
        # Recreate menus with new dimensions
        self._create_menus()
        
    def _toggle_fullscreen(self):
        self.window_manager.toggle_fullscreen()
        self.width, self.height = self.window_manager.get_screen_size()
        self.screen = self.window_manager.screen
        # Recreate menus with new dimensions
        self._create_menus()

    def render(self):
        self.screen.fill((0, 0, 0))
        if self.state == MenuState.MAIN:
            self.main_menu.render(self.screen, self.width, self.height)
        else:
            self.options_menu.render(self.screen, self.width, self.height)
        pygame.display.flip()

    def handle_input(self) -> tuple[bool, dict]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True, {}
            
            result = None
            if self.state == MenuState.MAIN:
                result = self.main_menu.handle_input(event)
            else:
                result = self.options_menu.handle_input(event)
                
            if isinstance(result, dict) and result.get('exit'):
                return True, result
                
        return False, {}
