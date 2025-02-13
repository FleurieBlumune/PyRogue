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
        hud_font (pygame.font.Font): Font for HUD items
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
        self.hud_font = pygame.font.Font(FONT_CONFIGS["HUD"]["Name"],
                                       FONT_CONFIGS["HUD"]["Size"])
        
    def create_menu(self, config: dict) -> Menu:
        """
        Create a menu from configuration data.
        
        Args:
            config: Dictionary containing menu configuration
            
        Returns:
            Menu: The created menu
        """
        # Use HUD font for HUD menus, otherwise use standard fonts
        font_small = self.hud_font if config.get("Position") == "top-left" else self.item_font
        
        menu = Menu(config["Title"], 
                   self.title_font, 
                   font_small,
                   position=config.get("Position", "center"))
        
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
        
        # Handle different item types
        if item_type == MenuItemType.STAT:
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
            callback=self.action_handlers.get(config["Action"])
        ) 