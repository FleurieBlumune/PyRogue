import pygame
from enum import Enum, auto

class MenuState(Enum):
    MAIN = auto()
    OPTIONS = auto()

class TitleScreen:
    def __init__(self, width: int, height: int):
        self.resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1920, 1080)
        ]
        self.current_resolution_index = 0  # Default to first resolution
        # Use the preset resolution as the starting window size.
        self.width, self.height = self.resolutions[self.current_resolution_index]
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font_large = pygame.font.Font(None, 74)
        self.font_small = pygame.font.Font(None, 36)
        self.state = MenuState.MAIN
        self.fullscreen = False
        self.selected_option = 0
        # Get the current display info for borderless fullscreen
        self.display_info = pygame.display.Info()
        self.monitor_width = self.display_info.current_w
        self.monitor_height = self.display_info.current_h

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
            # Use monitor resolution for borderless fullscreen.
            self.screen = pygame.display.set_mode(
                (self.monitor_width, self.monitor_height),
                pygame.NOFRAME
            )
            self.width, self.height = self.monitor_width, self.monitor_height
        else:
            # Return to windowed mode with a default resolution.
            new_width, new_height = self.resolutions[self.current_resolution_index]
            self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            self.width, self.height = new_width, new_height
    
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
