"""Entity type definitions."""
from enum import Enum

class EntityType(Enum):
    PLAYER = "PLAYER"
    HUMANOID = "HUMANOID"
    BEAST = "BEAST"
    UNDEAD = "UNDEAD"
    MERCHANT = "MERCHANT"