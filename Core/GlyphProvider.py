"""Provides consistent access to game glyphs and symbols."""

class GlyphProvider:
    """Singleton class that provides access to game glyphs and symbols."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlyphProvider, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize_glyphs()
            self._initialized = True

    def _initialize_glyphs(self):
        """Initialize the glyph mappings with very basic, widely-supported Unicode characters."""
        self.glyphs = {
            # Navigation/UI glyphs - using extremely basic Unicode arrows
            'ARROW_UP': '↑',      # UPWARDS ARROW U+2191
            'ARROW_DOWN': '↓',    # DOWNWARDS ARROW U+2193
            'ARROW_LEFT': '←',    # LEFTWARDS ARROW U+2190
            'ARROW_RIGHT': '→',   # RIGHTWARDS ARROW U+2192
            
            # Game symbols - using ASCII for maximum compatibility
            'PLAYER': '@',
            'WALL': '#',
            'FLOOR': '.',
            'DOOR': '+',
            
            # Status indicators with basic Unicode
            'HEALTH': '+',      # Using simple ASCII fallback
            'MANA': '*',        # Using simple ASCII fallback
            'GOLD': '$',        # Using simple ASCII fallback
        }

    @staticmethod
    def get_instance():
        """Get the singleton instance."""
        if GlyphProvider._instance is None:
            GlyphProvider()
        return GlyphProvider._instance

    def get(self, glyph_name: str, use_unicode: bool = True) -> str:
        """
        Get a glyph by name. Returns the name itself if glyph not found.
        Args:
            glyph_name: Name of the glyph to retrieve
            use_unicode: If False, returns ASCII fallbacks instead
        """
        if not use_unicode:
            # ASCII fallbacks
            fallbacks = {
                'ARROW_UP': '^',
                'ARROW_DOWN': 'v',
                'ARROW_LEFT': '<',
                'ARROW_RIGHT': '>',
                'HEALTH': '+',
                'MANA': '*',
                'GOLD': '$'
            }
            return fallbacks.get(glyph_name, self.glyphs.get(glyph_name, glyph_name))
            
        return self.glyphs.get(glyph_name, glyph_name)