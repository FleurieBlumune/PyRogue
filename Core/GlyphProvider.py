"""Provides consistent access to game glyphs and symbols."""

class GlyphProvider:
    """Provides access to game glyphs and symbols through static methods."""
    
    # Static glyph definitions
    GLYPHS = {
        # Navigation/UI glyphs - using proper Unicode triangles
        'ARROW_UP': '△',      # WHITE UP-POINTING TRIANGLE U+25B3
        'ARROW_DOWN': '▽',    # WHITE DOWN-POINTING TRIANGLE U+25BD
        'ARROW_LEFT': '◁',    # WHITE LEFT-POINTING TRIANGLE U+25C1
        'ARROW_RIGHT': '▷',   # WHITE RIGHT-POINTING TRIANGLE U+25B7
        
        # Game symbols - using ASCII for maximum compatibility
        'PLAYER': '@',        # COMMERCIAL AT U+0040
        'WALL': '█',          # FULL BLOCK U+2588
        'FLOOR': '·',         # MIDDLE DOT U+00B7
        'DOOR': '╬',          # DOUBLE CROSS U+256C
        
        # Status indicators with proper Unicode
        'HEALTH': '♥',        # BLACK HEART SUIT U+2665
        'MANA': '✦',          # BLACK FOUR POINTED STAR U+2726
        'GOLD': '⚜',          # FLEUR-DE-LIS U+269C
    }

    # ASCII fallbacks for non-Unicode environments
    ASCII_FALLBACKS = {
        'ARROW_UP': '^',
        'ARROW_DOWN': 'v',
        'ARROW_LEFT': '<',
        'ARROW_RIGHT': '>',
        'WALL': '#',
        'FLOOR': '.',
        'DOOR': '+',
        'HEALTH': '+',
        'MANA': '*',
        'GOLD': '$'
    }

    @classmethod
    def get(cls, glyph_name: str, use_unicode: bool = True) -> str:
        """
        Get a glyph by name. Returns the name itself if glyph not found.
        Args:
            glyph_name: Name of the glyph to retrieve
            use_unicode: If False, returns ASCII fallbacks instead
        """
        if not use_unicode:
            return cls.ASCII_FALLBACKS.get(glyph_name, cls.GLYPHS.get(glyph_name, glyph_name))
        return cls.GLYPHS.get(glyph_name, glyph_name)