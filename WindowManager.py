import pygame
import ctypes
import os

class WindowManager:
    def __init__(self):
        self.resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1920, 1080)
        ]
        
        # Get monitor info
        try:
            user32 = ctypes.windll.user32
            self.monitor_width = user32.GetSystemMetrics(0)
            self.monitor_height = user32.GetSystemMetrics(1)
        except:
            # Fallback to pygame's method
            info = pygame.display.Info()
            self.monitor_width = info.current_w
            self.monitor_height = info.current_h
        
        self.current_width = self.resolutions[0][0]
        self.current_height = self.resolutions[0][1]
        self.fullscreen = False
        self.screen = None
        self.current_resolution_index = 0
        self.windowed_resolution_index = 0
        
    def set_mode(self, width: int, height: int, fullscreen: bool = False) -> pygame.Surface:
        """Set the display mode and return the screen surface."""
        self.current_width = width
        self.current_height = height
        self.fullscreen = fullscreen
        
        if fullscreen:
            # Use monitor resolution for fullscreen
            self.current_width = self.monitor_width
            self.current_height = self.monitor_height
            
            pygame.display.quit()
            os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
            pygame.display.init()
            self.screen = pygame.display.set_mode(
                (self.current_width, self.current_height),
                pygame.NOFRAME
            )
        else:
            pygame.display.quit()
            os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"
            pygame.display.init()
            self.screen = pygame.display.set_mode(
                (self.current_width, self.current_height),
                pygame.RESIZABLE
            )
            
        return self.screen
    
    def handle_resize(self, width: int, height: int) -> None:
        """Handle window resize events."""
        if not self.fullscreen:
            self.current_width = width
            self.current_height = height
            self.screen = pygame.display.set_mode(
                (width, height),
                pygame.RESIZABLE
            )
    
    def get_screen_size(self) -> tuple[int, int]:
        """Get current screen dimensions."""
        return self.current_width, self.current_height
    
    def get_monitor_size(self) -> tuple[int, int]:
        """Get monitor dimensions."""
        return self.monitor_width, self.monitor_height

    def cycle_resolution(self) -> tuple[int, int]:
        """Cycle to next available resolution and return it."""
        if not self.fullscreen:
            self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
            width, height = self.resolutions[self.current_resolution_index]
            self.set_mode(width, height, False)
        return self.get_screen_size()

    def get_current_resolution_index(self) -> int:
        """Get the index of current resolution in the resolutions list."""
        return self.current_resolution_index

    def toggle_fullscreen(self) -> None:
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.windowed_resolution_index = self.current_resolution_index
            if (self.monitor_width, self.monitor_height) not in self.resolutions:
                self.resolutions.append((self.monitor_width, self.monitor_height))
            self.current_resolution_index = self.resolutions.index((self.monitor_width, self.monitor_height))
        else:
            self.current_resolution_index = self.windowed_resolution_index
            
        width, height = self.resolutions[self.current_resolution_index]
        self.set_mode(width, height, self.fullscreen)

    def get_resolution_str(self) -> str:
        """Get current resolution as a string."""
        width, height = self.resolutions[self.current_resolution_index]
        return f"{width}x{height}"

    def get_current_resolution(self) -> tuple[int, int]:
        """Get current resolution based on fullscreen state."""
        return (self.monitor_width, self.monitor_height) if self.fullscreen else self.resolutions[self.current_resolution_index]
