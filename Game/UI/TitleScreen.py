"""
Title screen implementation using pygame-gui.
"""

import pygame
import pygame_gui
import os
import logging
from Engine.Core.WindowManager import WindowManager
from Engine.UI.MenuSystem import MenuState
from Engine.UI.MenuSystem.Menu import Menu
from Game.UI.Menus.ResolutionPopupMenu import ResolutionPopupMenu

logger = logging.getLogger(__name__)


class TitleScreen(Menu):
    """
    Title screen implementation that manages menus and window settings.
    
    Attributes:
        window_manager (WindowManager): Manages window settings and display
        screen (pygame.Surface): The screen surface to render to
        state (MenuState): Current menu state
        resolution_popup (ResolutionPopupMenu): Popup menu for resolution selection
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
        self.state = MenuState.MAIN  # Set state before super().__init__
        self.resolution_popup = None
        
        theme_path = os.path.join('Game', 'UI', 'theme.json')
        super().__init__(width, height, theme_path)  # This will call _init_gui_elements
        
    def _init_gui_elements(self):
        """Initialize pygame-gui UI elements."""
        # Clear any existing elements
        super()._init_gui_elements()
        
        # Calculate center positions
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Create title text
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((center_x - 100, center_y - 150), (200, 50)),
            text="PyRogue",
            manager=self.ui_manager
        )
        
        # Create main menu buttons
        button_width = 200
        button_height = 50
        button_spacing = 20
        
        if self.state == MenuState.MAIN:
            # Start Game button
            self.start_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((center_x - button_width//2, 
                                         center_y - button_height//2), 
                                        (button_width, button_height)),
                text="Start Game",
                manager=self.ui_manager
            )
            self.menu_items.append(self.start_button)
            
            # Options button
            self.options_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((center_x - button_width//2, 
                                         center_y + button_height//2 + button_spacing), 
                                        (button_width, button_height)),
                text="Options",
                manager=self.ui_manager
            )
            self.menu_items.append(self.options_button)
        else:  # OPTIONS state
            # Options menu elements
            self.resolution_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((center_x - 150, center_y - 100), (300, 30)),
                text="Resolution",
                manager=self.ui_manager
            )
            
            # Resolution button (replacing dropdown)
            self.resolution_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((center_x - 100, center_y - 60), (200, 30)),
                text=self.window_manager.get_resolution_str(),
                manager=self.ui_manager
            )
            self.menu_items.append(self.resolution_button)
            
            self.fullscreen_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((center_x - 100, center_y), (200, 30)),
                text="Fullscreen: " + ("On" if self.window_manager.fullscreen else "Off"),
                manager=self.ui_manager
            )
            self.menu_items.append(self.fullscreen_button)
            
            self.back_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((center_x - 100, center_y + 60), (200, 30)),
                text="Back",
                manager=self.ui_manager
            )
            self.menu_items.append(self.back_button)
        
        # Set initial focus
        self._update_selection()
    
    def _handle_selection(self):
        """Handle selection of the current menu item."""
        selected_item = self.menu_items[self.selected_index]
        
        if self.state == MenuState.MAIN:
            if selected_item == self.start_button:
                return True, {
                    "exit": True,
                    "fullscreen": self.window_manager.fullscreen,
                    "resolution": self.window_manager.get_current_resolution()
                }
            elif selected_item == self.options_button:
                self.state = MenuState.OPTIONS
                self._init_gui_elements()
        else:  # OPTIONS state
            if selected_item == self.fullscreen_button:
                self._toggle_fullscreen()
            elif selected_item == self.back_button:
                self.state = MenuState.MAIN
                self._init_gui_elements()
            elif selected_item == self.resolution_button:
                # Show resolution popup
                popup_width = 250
                popup_height = 300
                center_x = self.width // 2
                center_y = self.height // 2
                popup_rect = pygame.Rect(
                    center_x - popup_width // 2,
                    center_y - popup_height // 2,
                    popup_width,
                    popup_height
                )
                
                self.resolution_popup = ResolutionPopupMenu(
                    rect=popup_rect,
                    window_manager=self.window_manager,
                    callback=self._handle_resolution_selection,
                    manager=self.ui_manager,
                    on_close=self._handle_popup_close
                )
        
        return False, {}
        
    def _handle_resolution_selection(self, resolution: str):
        """Handle resolution selection from the popup menu."""
        width, height = map(int, resolution.split('x'))
        self.width, self.height = self.window_manager.set_resolution(width, height)
        self.screen = self.window_manager.screen
        self.ui_manager.set_window_resolution((self.width, self.height))
        self._init_gui_elements()
        
    def _handle_popup_close(self):
        """Handle popup being closed."""
        self.resolution_popup = None
        
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.window_manager.toggle_fullscreen()
        self.width, self.height = self.window_manager.get_screen_size()
        self.screen = self.window_manager.screen
        self.ui_manager.set_window_resolution((self.width, self.height))
        self._init_gui_elements()

    def handle_input(self) -> tuple[bool, dict]:
        """
        Handle input events.
        
        Returns:
            tuple[bool, dict]: (should_exit, settings)
        """
        time_delta = pygame.time.Clock().tick(60)/1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True, {}
            
            # If popup is active, let it handle input first
            if self.resolution_popup is not None:
                # Let UI manager process events for the popup
                self.ui_manager.process_events(event)
                self.ui_manager.update(time_delta)
                return False, {}
            
            # Handle keyboard navigation
            result = super()._handle_keyboard_navigation(event)
            if result is not None:
                return result
                
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if self.state == MenuState.MAIN:
                        if event.ui_element == self.start_button:
                            return True, {
                                "exit": True,
                                "fullscreen": self.window_manager.fullscreen,
                                "resolution": self.window_manager.get_current_resolution()
                            }
                        elif event.ui_element == self.options_button:
                            self.state = MenuState.OPTIONS
                            self._init_gui_elements()
                    else:  # OPTIONS state
                        if event.ui_element == self.fullscreen_button:
                            self._toggle_fullscreen()
                        elif event.ui_element == self.back_button:
                            self.state = MenuState.MAIN
                            self._init_gui_elements()
            
            self.ui_manager.process_events(event)
            
        self.ui_manager.update(time_delta)
        return False, {}

    def render(self):
        """Render the current menu."""
        super().render(self.screen)
