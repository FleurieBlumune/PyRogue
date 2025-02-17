"""
Game entity package.

This package contains:
- Entity base class
- Player and NPC implementations
- Stats and StatsProvider
- EntityType enum
"""

from .Entity import Entity
from .Player import Player
from .NPC import NPC
from .Stats import Stats
from .StatsProvider import StatsProvider
from .EntityType import EntityType

__all__ = ['Entity', 'Player', 'NPC', 'Stats', 'StatsProvider', 'EntityType']
