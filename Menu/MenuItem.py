"""
MenuItem class for handling individual menu items and their behaviors.
"""

from typing import Callable, Any, Optional
from Menu.MenuTypes import MenuItemType  # Direct import from MenuTypes
import logging

class MenuItem:
    """
    A single menu item that can be displayed and interacted with.
    
    Attributes:
        text (str): Display text for the menu item
        type (MenuItemType): Type of menu item (TEXT, TOGGLE, SELECTOR, ACTION, STAT)
        callback (Optional[Callable]): Function to call when item is activated
        options (list[Any]): Available options for SELECTOR type items
        value (Any): Current value for TOGGLE and SELECTOR types
        selected (bool): Whether the item is currently selected
        value_getter (Optional[Callable]): Function to get current value for STAT type
    """
    
    def __init__(self, 
                 text: str, 
                 item_type: MenuItemType,
                 callback: Optional[Callable] = None,
                 options: list[Any] = None,
                 value: Any = None,
                 value_getter: Optional[Callable] = None):
        """
        Initialize a new menu item.
        
        Args:
            text: Display text for the menu item
            item_type: Type of menu item
            callback: Function to call when item is activated
            options: Available options for SELECTOR type items
            value: Current value for TOGGLE and SELECTOR types
            value_getter: Function to get current value for STAT type
        """
        self.text = text
        self.type = item_type
        self.callback = callback
        self.options = options
        self.value = value
        self.value_getter = value_getter
        self.selected = False
        self.logger = logging.getLogger(__name__)
        
    def activate(self) -> Any:
        """Activate the menu item and return any callback result."""
        if self.callback:
            return self.callback()
        return None
    
    def next_value(self) -> Any:
        """Cycle to the next value for SELECTOR and TOGGLE types."""
        if self.type == MenuItemType.SELECTOR and self.options:
            current_index = self.options.index(self.value)
            self.value = self.options[(current_index + 1) % len(self.options)]
        elif self.type == MenuItemType.TOGGLE:
            self.value = not self.value
        return self.value
    
    def previous_value(self) -> Any:
        """Cycle to the previous value for SELECTOR type."""
        if self.type == MenuItemType.SELECTOR and self.options:
            current_index = self.options.index(self.value)
            self.value = self.options[(current_index - 1) % len(self.options)]
        return self.value
    
    def get_display_text(self) -> str:
        """Get the text to display for this menu item."""
        if self.type == MenuItemType.TOGGLE:
            return f"{self.text}: {'On' if self.value else 'Off'}"
        elif self.type == MenuItemType.SELECTOR:
            return f"{self.text}: {self.value}"
        elif self.type == MenuItemType.STAT and self.value_getter:
            current_value = self.value_getter()
            if isinstance(current_value, tuple):
                current, maximum = current_value
                return f"{self.text}: {current}/{maximum}"
            return f"{self.text}: {current_value}"
        elif self.type == MenuItemType.LOG and self.value_getter:
            text = self.value_getter()
            return text
        return self.text