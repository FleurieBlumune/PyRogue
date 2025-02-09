"""Base statistics system for entities."""
import logging
import random

class Stats:
    """
    Container for entity statistics.
    
    Attributes:
        quickness (int): Speed/initiative stat, affects turn order and action points
        max_action_points (int): Maximum action points that can be accumulated
        action_points (int): Current action points available
        max_hp (int): Maximum hit points
        current_hp (int): Current hit points
        strength (int): Physical power, affects melee damage
    """
    
    def __init__(self, quickness: int = 100, max_action_points: int = 1000, max_hp: int = 100, strength: int = 10):
        self.quickness = quickness
        self.max_action_points = max_action_points
        self.action_points = max_action_points  # Start with max points
        self.max_hp = max_hp
        self.current_hp = max_hp  # Start with full health
        self.strength = strength
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
        
    def modify_hp(self, amount: int) -> int:
        """
        Modify current HP by the given amount (positive for healing, negative for damage).
        Returns the actual amount of HP changed.
        """
        old_hp = self.current_hp
        self.current_hp = max(0, min(self.current_hp + amount, self.max_hp))
        change = self.current_hp - old_hp
        self.logger.debug(f"HP modified: {old_hp} -> {self.current_hp} (change: {change})")
        return change
        
    def is_alive(self) -> bool:
        """Check if the entity is still alive."""
        return self.current_hp > 0
    
    def calculate_attack_damage(self) -> int:
        """
        Calculate damage for a basic attack.
        Includes some randomization based on strength.
        """
        base_damage = self.strength
        variance = random.randint(-2, 2)  # Add some randomness
        damage = max(1, base_damage + variance)  # Ensure at least 1 damage
        self.logger.debug(f"Attack damage calculated: {damage} (base: {base_damage}, variance: {variance})")
        return damage
    
    def take_damage(self, damage: int) -> int:
        """
        Take damage and return the actual amount of damage dealt.
        """
        return -self.modify_hp(-damage)  # Negative because damage reduces HP
    
    def can_attack(self) -> bool:
        """Check if entity has enough action points to attack."""
        return self.action_points >= self.get_scaled_cost(self.attack_cost)
