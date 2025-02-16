import pygame
import ctypes
import os
import logging

class WindowManager:
    def __init__(self):
        # Force SDL to use specific configuration before ANY pygame init
        os.environ['PYTHONUTF8'] = '1'  # Force UTF-8 mode in Python
        os.environ['SDL_VIDEODRIVER'] = 'windows'  # Use native Windows driver
        os.environ['SDL_HINT_RENDER_DRIVER'] = 'direct3d'  # Use D3D for better text
        os.environ['SDL_HINT_IME_SHOW_UI'] = '1'  # Enable IME for Unicode input
        os.environ['SDL_HINT_VIDEO_HIGHDPI_DISABLED'] = '0'  # Enable high DPI
        os.environ['SDL_HINT_RENDER_SCALE_QUALITY'] = '1'  # Enable smoothing
        
        # Initialize pygame modules in specific order
        pygame.display.init()  # Initialize display first
        pygame.font.init()  # Then initialize font system
        
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
        self.logger = logging.getLogger(__name__)

    def set_mode(self, width: int, height: int, fullscreen: bool = False) -> pygame.Surface:
        """Set the display mode and return the screen surface."""
        self.current_width = width
        self.current_height = height
        self.fullscreen = fullscreen
        
        # Reinitialize pygame with proper settings each mode change
        pygame.display.quit()
        pygame.font.quit()
        
        if fullscreen:
            # Use monitor resolution for fullscreen
            self.current_width = self.monitor_width
            self.current_height = self.monitor_height
            flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        else:
            flags = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
            
        # Reinit in proper order
        pygame.display.init()
        pygame.font.init()
        
        self.screen = pygame.display.set_mode(
            (self.current_width, self.current_height),
            flags
        )
        
        # Force a screen refresh
        pygame.display.flip()
            
        return self.screen
    
    def handle_resize(self, width: int, height: int) -> None:
        """Handle window resize events."""
        if not self.fullscreen:
            self.current_width = width
            self.current_height = height
            self.logger.debug(f"Setting mode to {width}x{height}")
            # Use RESIZABLE and SHOWN flags to ensure proper window behavior
            self.screen = pygame.display.set_mode(
                (width, height),
                pygame.RESIZABLE | pygame.SHOWN
            )
            # Store the new dimensions immediately
            self.current_width, self.current_height = self.screen.get_size()
            self.logger.debug(f"New screen size: {self.current_width}x{self.current_height}")
            # Force refresh
            pygame.event.post(pygame.event.Event(pygame.VIDEOEXPOSE))
    
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
