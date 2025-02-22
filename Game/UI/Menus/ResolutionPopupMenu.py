"""
Resolution selection popup menu implementation.
"""

import pygame
import pygame_gui
from typing import Callable, List, Tuple
from .PopupMenu import PopupMenu
from Engine.Core.WindowManager import WindowManager

class ResolutionPopupMenu(PopupMenu):
    """
    A popup menu for selecting screen resolutions.
    
    This class provides a specialized popup menu for selecting from available
    screen resolutions. It formats the resolution options and handles the
    selection callback.
    """
    
    def __init__(self,
                 rect: pygame.Rect,
                 window_manager: WindowManager,
                 callback: Callable[[str], None],
                 manager: pygame_gui.UIManager,
                 on_close: Callable[[], None]):
        """
        Initialize the resolution popup menu.
        
        Args:
            rect: The rectangle defining the popup's position and size
            window_manager: The window manager instance
            callback: Function to call when a resolution is selected
            manager: The UI manager
            on_close: Function to call when popup is closed
        """
        # Format resolution options as strings
        resolution_options = [f"{w}x{h}" for w, h in window_manager.resolutions]
        
        # Initialize base popup with resolution options
        super().__init__(
            rect=rect,
            options=resolution_options,
            callback=callback,
            manager=manager,
            on_close=on_close,
            window_title="Select Resolution"
        ) 