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
        try:
            from Core.LogConfig import log_display_state
            
            self.logger.debug(f"Setting display mode: {width}x{height} (fullscreen={fullscreen})")
            
            # Store current state
            self.current_width = width
            self.current_height = height
            self.fullscreen = fullscreen
            
            # Calculate flags
            if fullscreen:
                self.current_width = self.monitor_width
                self.current_height = self.monitor_height
                flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                self.logger.debug(f"Using fullscreen resolution: {self.current_width}x{self.current_height}")
            else:
                flags = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
            
            # Get current display info before mode change
            try:
                if pygame.display.get_init():
                    info = pygame.display.Info()
                    old_info = {
                        'width': info.current_w,
                        'height': info.current_h,
                        'hw_available': bool(info.hw),
                        'wm_available': bool(info.wm)
                    }
                    self.logger.debug(f"Current display info before mode change: {old_info}")
            except Exception as e:
                self.logger.warning(f"Could not get old display info: {e}")
            
            # Set the new display mode
            try:
                self.screen = pygame.display.set_mode(
                    (self.current_width, self.current_height),
                    flags
                )
                
                # Verify the mode change
                actual_size = self.screen.get_size()
                self.logger.debug(f"Screen surface size: {actual_size}")
                
                # Log display flags through Info object
                info = pygame.display.Info()
                info_dict = {
                    'width': info.current_w,
                    'height': info.current_h,
                    'hw_available': bool(info.hw),
                    'wm_available': bool(info.wm)
                }
                self.logger.debug(f"Display info after mode change: {info_dict}")
                
            except Exception as e:
                self.logger.error(f"Failed to set display mode: {e}", exc_info=True)
                raise
            
            # Force a screen refresh
            try:
                pygame.display.flip()
                self.logger.debug("Display mode set successfully")
            except Exception as e:
                self.logger.error(f"Error during screen refresh: {e}", exc_info=True)
                raise
                
            return self.screen
            
        except Exception as e:
            self.logger.error(f"Error setting display mode: {e}", exc_info=True)
            raise
    
    def handle_resize(self, width: int, height: int) -> None:
        """Handle window resize events."""
        try:
            if not self.fullscreen:
                self.logger.debug(f"Handling resize event: {width}x{height}")
                self.current_width = width
                self.current_height = height
                
                # Use RESIZABLE and SHOWN flags to ensure proper window behavior
                self.logger.debug("Setting new display mode for resize")
                self.screen = pygame.display.set_mode(
                    (width, height),
                    pygame.RESIZABLE | pygame.SHOWN
                )
                
                # Store the new dimensions immediately
                self.current_width, self.current_height = self.screen.get_size()
                self.logger.debug(f"New screen size after resize: {self.current_width}x{self.current_height}")
                
                # Force refresh
                pygame.event.post(pygame.event.Event(pygame.VIDEOEXPOSE))
                self.logger.debug("Posted VIDEOEXPOSE event")
                
        except Exception as e:
            self.logger.error(f"Error handling resize: {e}", exc_info=True)
            raise  # Re-raise to allow caller to handle
    
    def get_screen_size(self) -> tuple[int, int]:
        """Get current screen dimensions."""
        return self.current_width, self.current_height
    
    def get_monitor_size(self) -> tuple[int, int]:
        """Get monitor dimensions."""
        return self.monitor_width, self.monitor_height

    def cycle_resolution(self) -> tuple[int, int]:
        """Cycle to next available resolution and return it."""
        try:
            if not self.fullscreen:
                old_index = self.current_resolution_index
                self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
                width, height = self.resolutions[self.current_resolution_index]
                
                self.logger.debug(f"Cycling resolution from index {old_index} ({self.resolutions[old_index]}) to {self.current_resolution_index} ({width}x{height})")
                
                # Set new mode
                self.logger.debug(f"Setting new display mode: {width}x{height}")
                self.screen = self.set_mode(width, height, False)
                
                # Update internal dimensions
                self.current_width, self.current_height = width, height
                self.logger.debug(f"Updated internal dimensions to {width}x{height}")
                
                # Force a screen refresh
                pygame.display.flip()
                self.logger.debug("Screen refresh completed")
                
            return self.get_screen_size()
        except Exception as e:
            self.logger.error(f"Error cycling resolution: {e}", exc_info=True)
            # Try to recover by setting to first resolution
            self.logger.info("Attempting recovery with first resolution")
            self.current_resolution_index = 0
            width, height = self.resolutions[0]
            self.screen = self.set_mode(width, height, False)
            return self.get_screen_size()

    def get_current_resolution_index(self) -> int:
        """Get the index of current resolution in the resolutions list."""
        return self.current_resolution_index

    def toggle_fullscreen(self) -> None:
        """Toggle between fullscreen and windowed mode."""
        try:
            self.logger.debug(f"Toggling fullscreen. Current state: fullscreen={self.fullscreen}")
            self.logger.debug(f"Current resolution index: {self.current_resolution_index}, dimensions: {self.resolutions[self.current_resolution_index]}")
            
            # Store old state for recovery
            old_fullscreen = self.fullscreen
            old_resolution_index = self.current_resolution_index
            old_width, old_height = self.current_width, self.current_height
            
            # Update state
            self.fullscreen = not self.fullscreen
            
            if self.fullscreen:
                self.logger.debug("Switching to fullscreen mode")
                self.windowed_resolution_index = self.current_resolution_index
                if (self.monitor_width, self.monitor_height) not in self.resolutions:
                    self.logger.debug(f"Adding monitor resolution {(self.monitor_width, self.monitor_height)} to available resolutions")
                    self.resolutions.append((self.monitor_width, self.monitor_height))
                self.current_resolution_index = self.resolutions.index((self.monitor_width, self.monitor_height))
            else:
                self.logger.debug("Switching to windowed mode")
                self.current_resolution_index = self.windowed_resolution_index
            
            width, height = self.resolutions[self.current_resolution_index]
            self.logger.debug(f"Setting new mode: {width}x{height}, fullscreen={self.fullscreen}")
            
            try:
                self.screen = self.set_mode(width, height, self.fullscreen)
                self.logger.debug("Successfully changed display mode")
            except Exception as e:
                self.logger.error(f"Failed to set new display mode: {e}", exc_info=True)
                # Try to recover
                self.logger.info("Attempting to recover previous display mode")
                self.fullscreen = old_fullscreen
                self.current_resolution_index = old_resolution_index
                self.screen = self.set_mode(old_width, old_height, old_fullscreen)
                raise
                
        except Exception as e:
            self.logger.error(f"Error in toggle_fullscreen: {e}", exc_info=True)
            raise

    def get_resolution_str(self) -> str:
        """Get current resolution as a string."""
        width, height = self.resolutions[self.current_resolution_index]
        return f"{width}x{height}"

    def get_current_resolution(self) -> tuple[int, int]:
        """Get current resolution based on fullscreen state."""
        return (self.monitor_width, self.monitor_height) if self.fullscreen else self.resolutions[self.current_resolution_index]
