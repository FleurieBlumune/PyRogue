"""Entity type definitions."""
from enum import Enum

class EntityType(Enum):
    PLAYER = ("SCIENTIST", "RESEARCHER")      # Player is a scientist/researcher
    GUARD = ("GUARD", "SECURITY")            # Security personnel
    CIVILIAN = ("CIVILIAN", "NEUTRAL")       # Regular NPCs that can be transformed
    RESEARCHER = ("RESEARCHER", "RESEARCH")   # Other scientists (neutral/friendly)
    SUBJECT = ("SUBJECT", "TEST_SUBJECT")    # Already transformed test subjects
    
    def __init__(self, type_name: str, faction: str):
        self.type_name = type_name
        self.faction = faction