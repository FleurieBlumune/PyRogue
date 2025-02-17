"""Base classes for manager interfaces."""

from abc import ABC, abstractmethod
from typing import List, Any

class IEntity(ABC):
    """Interface defining required Entity properties"""
    @property
    @abstractmethod
    def type(self) -> Any:
        pass

    @property
    @abstractmethod
    def position(self) -> Any:
        pass

    @property
    @abstractmethod
    def stats(self) -> Any:
        pass

    @property
    @abstractmethod
    def detection_range(self) -> int:
        pass

class IEntityContainer(ABC):
    """Interface for classes that manage collections of entities"""
    @abstractmethod
    def get_entities(self) -> List[IEntity]:
        pass

    @abstractmethod
    def add_entity(self, entity: IEntity) -> None:
        pass

    @abstractmethod
    def remove_entity(self, entity: IEntity) -> None:
        pass