"""Manager for entity faction relations and reputations."""

import sqlite3
import os
from pathlib import Path

class ReputationManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ReputationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.db_path = Path("Data/game.db")
            self._initialize_database()
            self._initialized = True

    @staticmethod
    def get_instance():
        if ReputationManager._instance is None:
            ReputationManager()
        return ReputationManager._instance

    def _initialize_database(self):
        """Initialize the SQLite database with schema"""
        if not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True)
        
        with sqlite3.connect(self.db_path) as conn:
            with open('Data/Schema/reputation.sql') as f:
                conn.executescript(f.read())

    def get_disposition(self, faction1: str, faction2: str) -> int:
        """Get the disposition between two factions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT disposition FROM faction_relations
                JOIN entity_factions f1 ON faction_id = f1.id
                JOIN entity_factions f2 ON other_faction_id = f2.id
                WHERE f1.name = ? AND f2.name = ?
            """, (faction1, faction2))
            result = cursor.fetchone()
            return result[0] if result else 0

    def is_hostile(self, faction1: str, faction2: str) -> bool:
        """Check if two factions are hostile to each other"""
        return self.get_disposition(faction1, faction2) < -20

    def modify_disposition(self, faction1: str, faction2: str, amount: int):
        """Modify the disposition between two factions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE faction_relations 
                SET disposition = CLAMP(disposition + ?, -100, 100)
                WHERE faction_id IN (SELECT id FROM entity_factions WHERE name = ?)
                AND other_faction_id IN (SELECT id FROM entity_factions WHERE name = ?)
            """, (amount, faction1, faction2))
            conn.commit()
