"""Entity type definitions."""
from enum import Enum

class EntityType(Enum):
    PLAYER = ("PLAYER", "PLAYER")
    HUMANOID = ("HUMANOID", "HUMANOID") 
    BEAST = ("BEAST", "BEAST")
    UNDEAD = ("UNDEAD", "UNDEAD")
    MERCHANT = ("MERCHANT", "MERCHANT")

    def __init__(self, type_name: str, faction: str):
        self.type_name = type_name
        self.faction = faction