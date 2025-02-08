"""Base statistics system for entities."""

class Stats:
    """
    Container for entity statistics.
    
    Attributes:
        quickness (int): Speed/initiative stat, affects turn order and action points
        max_action_points (int): Maximum action points that can be accumulated
        action_points (int): Current action points available
    """
    
    def __init__(self, quickness: int = 100, max_action_points: int = 1000):
        self.quickness = quickness
        self.max_action_points = max_action_points
        self.action_points = 0
        
    def accumulate_action_points(self) -> bool:
        """
        Add quickness-based points to action_points.
        Returns True if max_action_points is reached.
        """
        self.action_points = min(self.action_points + self.quickness, self.max_action_points)
        return self.action_points >= self.max_action_points
    
    def spend_action_points(self, cost: int) -> bool:
        """
        Attempt to spend action points.
        Returns True if successful, False if insufficient points.
        """
        if self.action_points >= cost:
            self.action_points -= cost
            return True
        return False
