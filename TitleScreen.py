import pygame
import os
from enum import Enum, auto
import ctypes
from WindowManager import WindowManager

class MenuState(Enum):
    MAIN = auto()
    OPTIONS = auto()

class TitleScreen:
    def __init__(self, width: int, height: int):
        self.window_manager = WindowManager()
        self.resolutions = self.window_manager.resolutions
        self.current_resolution_index = 0  # Default to first resolution
        self.windowed_resolution_index = 0   # Track windowed mode resolution separately

        # Use the preset resolution as the starting window size.
        self.width, self.height = self.resolutions[self.current_resolution_index]
        self.screen = self.window_manager.set_mode(width, height)
        self.font_large = pygame.font.Font(None, 74)
        self.font_small = pygame.font.Font(None, 36)
        self.state = MenuState.MAIN
        self.fullscreen = False
        self.selected_option = 0

        # Get actual screen dimensions (including taskbar)
        try:
            # Windows-specific solution using ctypes for full screen size
            user32 = ctypes.windll.user32
            self.monitor_width = user32.GetSystemMetrics(0)   # SM_CXSCREEN
            self.monitor_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        except:
            # Fallback to pygame's method if ctypes fails
            modes = pygame.display.list_modes()
            if modes and len(modes) > 0:
                self.monitor_width, self.monitor_height = modes[0]
            else:
                self.monitor_width, self.monitor_height = width, height

    @property
    def current_resolution(self) -> tuple[int, int]:
        """
        Return the current resolution based on fullscreen state.
        In fullscreen mode, return the monitor's resolution; otherwise, use the preset resolution.
        """
        return (self.monitor_width, self.monitor_height) if self.fullscreen else self.resolutions[self.current_resolution_index]

    def render(self):
        self.screen.fill((0, 0, 0))
        
        if self.state == MenuState.MAIN:
            self._render_main_menu()
        elif self.state == MenuState.OPTIONS:
            self._render_options_menu()
            
        pygame.display.flip()
    
    def _render_main_menu(self):
        # Draw title
        title = self.font_large.render("PyRogue", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(title, title_rect)
        
        # Draw menu options
        options = ["Press ENTER to start", "Press O for options"]
        for i, text in enumerate(options):
            rendered = self.font_small.render(text, True, (200, 200, 200))
            pos = (self.width // 2, 2 * self.height // 3 + i * 40)
            rect = rendered.get_rect(center=pos)
            self.screen.blit(rendered, rect)
    
    def _render_options_menu(self):
        # Draw options title
        title = self.font_large.render("Options", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title, title_rect)
        
        # Draw options
        options = [
            f"Resolution: {self.resolutions[self.current_resolution_index][0]}x{self.resolutions[self.current_resolution_index][1]}",
            f"Fullscreen: {'On' if self.fullscreen else 'Off'}",
            "Back to Main Menu"
        ]
        
        for i, text in enumerate(options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            rendered = self.font_small.render(text, True, color)
            pos = (self.width // 2, self.height // 2 + i * 40)
            rect = rendered.get_rect(center=pos)
            self.screen.blit(rendered, rect)
    
    def _handle_fullscreen_toggle(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            # Save current windowed resolution index
            self.windowed_resolution_index = self.current_resolution_index
            monitor_res = self.window_manager.get_monitor_size()
            if monitor_res not in self.resolutions:
                self.resolutions.append(monitor_res)
            self.current_resolution_index = self.resolutions.index(monitor_res)
        else:
            # Restore windowed resolution
            self.current_resolution_index = self.windowed_resolution_index
            
        new_width, new_height = self.resolutions[self.current_resolution_index]
        self.screen = self.window_manager.set_mode(new_width, new_height, self.fullscreen)
        self.width, self.height = self.window_manager.get_screen_size()

    
    def _change_resolution(self):
        self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
        if not self.fullscreen:  # Only change resolution if not in fullscreen mode.
            new_width, new_height = self.resolutions[self.current_resolution_index]
            self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            self.width, self.height = new_width, new_height

    def handle_input(self) -> tuple[bool, dict]:
        """Return (should_exit, settings)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True, {}
                
            if event.type == pygame.KEYDOWN:
                if self.state == MenuState.MAIN:
                    if event.key == pygame.K_RETURN:
                        # When exiting, pass the current fullscreen status and resolution.
                        return True, {'fullscreen': self.fullscreen, 'resolution': self.current_resolution}
                    elif event.key == pygame.K_o:
                        self.state = MenuState.OPTIONS
                        
                elif self.state == MenuState.OPTIONS:
                    if event.key == pygame.K_ESCAPE:
                        self.state = MenuState.MAIN
                    elif event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % 3  # 3 options
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % 3  # 3 options
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:  # Change resolution
                            self._change_resolution()
                        elif self.selected_option == 1:  # Toggle fullscreen
                            self._handle_fullscreen_toggle()
                        elif self.selected_option == 2:  # Back to main menu
                            self.state = MenuState.MAIN
                    elif event.key == pygame.K_LEFT and self.selected_option == 0:
                        # Previous resolution.
                        self.current_resolution_index = (self.current_resolution_index - 1) % len(self.resolutions)
                        self._change_resolution()
                    elif event.key == pygame.K_RIGHT and self.selected_option == 0:
                        # Next resolution.
                        self._change_resolution()
                            
        # Always return the current settings.
        return False, {'fullscreen': self.fullscreen, 'resolution': self.current_resolution}
