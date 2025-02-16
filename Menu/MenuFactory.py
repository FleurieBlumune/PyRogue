"""
Factory class for creating menus from configuration data.
"""

from typing import Callable, Dict, List, Optional
import pygame
import logging
import os
from Menu.Menu import Menu
from Menu.MenuItem import MenuItem
from Menu.MenuTypes import MenuItemType
from Menu.MenuConfigs import FONT_CONFIGS

logger = logging.getLogger(__name__)
logger.debug("Importing MenuFactory module")

class MenuFactory:
    """
    Factory for creating menus from configuration data.
    
    Attributes:
        action_handlers (dict[str, Callable]): Map of action names to handler functions
        title_font (pygame.font.Font): Font for menu titles
        item_font (pygame.font.Font): Font for menu items
        hud_font (pygame.font.Font): Font for HUD items
        log_font (pygame.font.Font): Font for activity log
    """
    
    def __init__(self, action_handlers: Dict[str, Callable]):
        """
        Initialize the menu factory.
        
        Args:
            action_handlers: Map of action names to handler functions
        """
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing MenuFactory")
        self.action_handlers = action_handlers

        # Initialize fonts with Unicode support
        pygame.font.init()
        
        def get_font_path(font_name: str) -> Optional[str]:
            """Find font file path, checking Windows system locations"""
            # Try current directory first
            if os.path.exists(font_name):
                return os.path.abspath(font_name)
            
            # Try Windows Fonts directory
            try:
                windows_font_dir = os.path.join(os.environ.get('WINDIR', ''), 'Fonts')
                font_path = os.path.join(windows_font_dir, font_name)
                if os.path.exists(font_path):
                    return font_path
            except:
                pass
                
            return None

        def create_font(config) -> pygame.font.Font:
            """Create font with proper fallbacks for Windows"""
            # Try Consolas first since we know it exists
            try:
                font_path = get_font_path("consolas.ttf")
                if font_path:
                    return pygame.font.Font(font_path, config["Size"])
            except:
                pass
                
            # Fall back to system default font
            try:
                return pygame.font.SysFont("arial", config["Size"])
            except:
                # Last resort - use pygame default
                return pygame.font.Font(None, config["Size"])

        # Create fonts with Unicode support
        self.title_font = create_font(FONT_CONFIGS["Title"])
        self.item_font = create_font(FONT_CONFIGS["MenuItem"])
        self.hud_font = create_font(FONT_CONFIGS["HUD"])
        self.log_font = create_font(FONT_CONFIGS["ActivityLog"])
        
        self.logger.debug("MenuFactory initialized with Unicode-enabled fonts")
        
    def create_menu(self, config: dict) -> Menu:
        """
        Create a menu from configuration data.
        
        Args:
            config: Dictionary containing menu configuration
            
        Returns:
        Create a menu from configuration data.
        
        Args:
            config: Dictionary containing menu configuration
            
        Returns:
            Menu: The created menu
        """
        self.logger.debug(f"Creating menu from config: {config.get('Title', 'Untitled')}")
        # Use appropriate font based on menu position/type
        if config.get("Position") == "top-left":
            font_small = self.hud_font
        elif config.get("Position") == "right":  # Check position instead of comparing configs
            font_small = self.log_font
        else:
            font_small = self.item_font
        
        menu = Menu(config["Title"], 
                   self.title_font, 
                   font_small,
                   position=config.get("Position", "center"))
        
        for item_config in config["Items"]:
            menu.add_item(self._create_menu_item(item_config))
        
        self.logger.debug(f"Created menu with {len(menu.items)} items")    
        return menu
    
    def _create_menu_item(self, config: dict) -> MenuItem:
        """
        Create a menu item from configuration data.
        
        Args:
            config: Dictionary containing menu item configuration
            
        Returns:
            MenuItem: The created menu item
        """
        item_type = MenuItemType[config["Type"]]
        
        # Handle different item types
        if item_type in [MenuItemType.STAT, MenuItemType.LOG]:
            value_getter = self.action_handlers[config["GetValue"]]
            return MenuItem(
                config["Text"],
                item_type,
                value_getter=value_getter
            )
        elif item_type == MenuItemType.SELECTOR:
            options_getter = self.action_handlers[config["GetOptions"]]
            current_getter = self.action_handlers[config["GetCurrent"]]
            return MenuItem(
                config["Text"],
                item_type,
                callback=self.action_handlers.get(config["Action"]),
                options=options_getter(),
                value=current_getter()
            )
        elif item_type == MenuItemType.TOGGLE:
            current_getter = self.action_handlers[config["GetCurrent"]]
            return MenuItem(
                config["Text"],
                item_type,
                callback=self.action_handlers.get(config["Action"]),
                value=current_getter()
            )
        
        return MenuItem(
            config["Text"],
            item_type,
            callback=self.action_handlers.get(config.get("Action"))  # Use get() to handle missing Action
        )