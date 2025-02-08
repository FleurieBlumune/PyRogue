CREATE TABLE IF NOT EXISTS entity_factions (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS faction_relations (
    faction_id INTEGER,
    other_faction_id INTEGER,
    disposition INTEGER NOT NULL DEFAULT 0, -- -100 to 100
    PRIMARY KEY (faction_id, other_faction_id),
    FOREIGN KEY (faction_id) REFERENCES entity_factions(id),
    FOREIGN KEY (other_faction_id) REFERENCES entity_factions(id)
);

-- Initial data
INSERT INTO entity_factions (name) VALUES 
    ('PLAYER'),
    ('HUMANOID'),
    ('BEAST'),
    ('UNDEAD'),
    ('MERCHANT');

-- Initial relations
INSERT INTO faction_relations (faction_id, other_faction_id, disposition) VALUES
    (1, 2, -20),   -- Player vs Humanoid: Slight distrust
    (1, 3, -50),   -- Player vs Beast: Hostile
    (1, 4, -80),   -- Player vs Undead: Very hostile
    (1, 5, 50),    -- Player vs Merchant: Friendly
    (2, 3, -30),   -- Humanoid vs Beast: Unfriendly
    (2, 4, -90),   -- Humanoid vs Undead: Extremely hostile
    (2, 5, 30);    -- Humanoid vs Merchant: Somewhat friendly
