"""
Title screen implementation using the menu system.
"""

import pygame
from Engine.Core.WindowManager import WindowManager
from Engine.UI.MenuSystem.MenuTypes import MenuID, MenuState
from Game.UI.Menus.MenuConfigs import MENU_CONFIGS
from Game.UI.Menus.MenuFactory import MenuFactory

class TitleScreen:
    """
    Title screen implementation that manages menus and window settings.
    
    Attributes:
        window_manager (WindowManager): Manages window settings and display
        screen (pygame.Surface): The screen surface to render to
        width (int): Current screen width
        height (int): Current screen height
        state (MenuState): Current menu state
        main_menu (Menu): The main menu
        options_menu (Menu): The options menu
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize the title screen.
        
        Args:
            width: Initial screen width
            height: Initial screen height
        """
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
        """Create the main and options menus."""
        self.main_menu = self.menu_factory.create_menu(MENU_CONFIGS[MenuID.MAIN])
        self.options_menu = self.menu_factory.create_menu(MENU_CONFIGS[MenuID.OPTIONS])
        
    def _update_resolution(self):
        """Update the screen resolution."""
        self.width, self.height = self.window_manager.cycle_resolution()
        self.screen = self.window_manager.screen
        # Recreate menus with new dimensions
        self._create_menus()
        
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.window_manager.toggle_fullscreen()
        self.width, self.height = self.window_manager.get_screen_size()
        self.screen = self.window_manager.screen
        # Recreate menus with new dimensions
        self._create_menus()

    def render(self):
        """Render the current menu."""
        self.screen.fill((0, 0, 0))
        if self.state == MenuState.MAIN:
            self.main_menu.render(self.screen, self.width, self.height)
        else:
            self.options_menu.render(self.screen, self.width, self.height)
        pygame.display.flip()

    def handle_input(self) -> tuple[bool, dict]:
        """
        Handle input events.
        
        Returns:
            tuple[bool, dict]: (should_exit, settings)
        """
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
