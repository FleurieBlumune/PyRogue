"""
Core game engine systems.

This module contains fundamental game systems including:
- Event management
- Input handling
- Game loop
- Window management
"""

from .Events import EventManager, GameEventType
from .GameLoop import GameLoop
from .InputHandler import InputHandler
from .LogConfig import setup_logging, log_system_info
from .WindowManager import WindowManager

__all__ = [
    'EventManager',
    'GameEventType',
    'GameLoop',
    'InputHandler',
    'setup_logging',
    'log_system_info',
    'WindowManager'
]
