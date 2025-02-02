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
        self.screen = self.window_manager.set_mode(width, height)
        self.width, self.height = self.window_manager.get_screen_size()
        self.font_large = pygame.font.Font(None, 74)
        self.font_small = pygame.font.Font(None, 36)
        self.state = MenuState.MAIN
        self.selected_option = 0

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
            f"Resolution: {self.window_manager.get_resolution_str()}",
            f"Fullscreen: {'On' if self.window_manager.fullscreen else 'Off'}",
            "Back to Main Menu"
        ]
        
        for i, text in enumerate(options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            rendered = self.font_small.render(text, True, color)
            pos = (self.width // 2, self.height // 2 + i * 40)
            rect = rendered.get_rect(center=pos)
            self.screen.blit(rendered, rect)

    def handle_input(self) -> tuple[bool, dict]:
        """Return (should_exit, settings)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True, {}
                
            if event.type == pygame.KEYDOWN:
                if self.state == MenuState.MAIN:
                    if event.key == pygame.K_RETURN:
                        # When exiting, pass the current fullscreen status and resolution.
                        return True, {'fullscreen': self.window_manager.fullscreen, 'resolution': self.window_manager.get_current_resolution()}
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
                            self.width, self.height = self.window_manager.cycle_resolution()
                            self.screen = self.window_manager.screen
                        elif self.selected_option == 1:  # Toggle fullscreen
                            self.window_manager.toggle_fullscreen()
                            self.width, self.height = self.window_manager.get_screen_size()
                            self.screen = self.window_manager.screen
                        elif self.selected_option == 2:  # Back to main menu
                            self.state = MenuState.MAIN
                    elif event.key == pygame.K_LEFT and self.selected_option == 0:
                        # Previous resolution.
                        self.width, self.height = self.window_manager.cycle_resolution()
                        self.screen = self.window_manager.screen
                    elif event.key == pygame.K_RIGHT and self.selected_option == 0:
                        # Next resolution.
                        self.width, self.height = self.window_manager.cycle_resolution()
                        self.screen = self.window_manager.screen
                            
        # Always return the current settings.
        return False, {'fullscreen': self.window_manager.fullscreen, 'resolution': self.window_manager.get_current_resolution()}
