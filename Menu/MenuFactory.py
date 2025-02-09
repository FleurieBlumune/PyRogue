"""
Factory class for creating menus from configuration data.
"""

from typing import Callable, Dict
import pygame
from Menu.Menu import Menu
from Menu.MenuItem import MenuItem
from Menu.MenuTypes import MenuItemType
from Menu.MenuConfigs import FONT_CONFIGS

class MenuFactory:
    """
    Factory for creating menus from configuration data.
    
    Attributes:
        action_handlers (dict[str, Callable]): Map of action names to handler functions
        title_font (pygame.font.Font): Font for menu titles
        item_font (pygame.font.Font): Font for menu items
    """
    
    def __init__(self, action_handlers: Dict[str, Callable]):
        """
        Initialize the menu factory.
        
        Args:
            action_handlers: Map of action names to handler functions
        """
        self.action_handlers = action_handlers
        self.title_font = pygame.font.Font(FONT_CONFIGS["Title"]["Name"], 
                                         FONT_CONFIGS["Title"]["Size"])
        self.item_font = pygame.font.Font(FONT_CONFIGS["MenuItem"]["Name"], 
                                        FONT_CONFIGS["MenuItem"]["Size"])
        
    def create_menu(self, config: dict) -> Menu:
        """
        Create a menu from configuration data.
        
        Args:
            config: Dictionary containing menu configuration
            
        Returns:
            Menu: The created menu
        """
        menu = Menu(config["Title"], self.title_font, self.item_font)
        
        for item_config in config["Items"]:
            menu.add_item(self._create_menu_item(item_config))
            
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
        
        # Get callback handler
        callback = self.action_handlers.get(config["Action"])
        
        # Handle special types
        if item_type == MenuItemType.SELECTOR:
            options_getter = self.action_handlers[config["GetOptions"]]
            current_getter = self.action_handlers[config["GetCurrent"]]
            return MenuItem(
                config["Text"],
                item_type,
                callback,
                options=options_getter(),
                value=current_getter()
            )
        elif item_type == MenuItemType.TOGGLE:
            current_getter = self.action_handlers[config["GetCurrent"]]
            return MenuItem(
                config["Text"],
                item_type,
                callback,
                value=current_getter()
            )
        
        return MenuItem(config["Text"], item_type, callback) 