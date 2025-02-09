"""Base statistics system for entities."""
import logging

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
        self.action_points = max_action_points  # Start with max points
        self.logger = logging.getLogger(__name__)
        
        # Action costs
        self.move_cost = 100  # Base cost for movement
        self.attack_cost = 150  # Base cost for attacks
        self.skill_cost = 200  # Base cost for special abilities
        
    def accumulate_action_points(self) -> bool:
        """
        Add quickness-based points to action_points.
        Returns True if max_action_points is reached.
        """
        if self.action_points >= self.max_action_points:
            self.logger.debug(f"Already at max AP ({self.action_points}/{self.max_action_points}), skipping accumulation")
            return True

        old_points = self.action_points
        gain = self.quickness
        new_points = min(old_points + gain, self.max_action_points)
        self.action_points = new_points
        
        self.logger.debug(f"AP accumulated: {old_points} + {gain} -> {self.action_points} (max: {self.max_action_points})")
        return self.action_points >= self.max_action_points
    
    def get_scaled_cost(self, base_cost: int) -> int:
        """Calculate actual cost scaled by quickness"""
        scaled = int(base_cost * (100 / self.quickness))
        self.logger.debug(f"Scaled cost {base_cost} -> {scaled} (quickness: {self.quickness})")
        return scaled
    
    def spend_action_points(self, cost: int) -> bool:
        """
        Attempt to spend action points.
        Returns True if successful, False if insufficient points.
        """
        actual_cost = self.get_scaled_cost(cost)
        if self.action_points >= actual_cost:
            self.action_points -= actual_cost
            self.logger.debug(f"AP spent: {actual_cost} (base: {cost}), remaining: {self.action_points}")
            return True
        self.logger.debug(f"Failed to spend AP: need {actual_cost}, have {self.action_points}")
        return False
