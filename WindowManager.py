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
