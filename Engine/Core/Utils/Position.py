"""
Position representation in 2D space.

Provides a simple 2D position class used throughout the game for
entity positions, room positions, and general coordinate tracking.
"""

class Position:
    """
    Represents a position in 2D space.
    
    Attributes:
        x (int): X coordinate
        y (int): Y coordinate
    """
    
    def __init__(self, x: int, y: int):
        """
        Initialize a position with coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        """
        self.x = x
        self.y = y 