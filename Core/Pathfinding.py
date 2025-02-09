"""Pathfinding system for the game."""

import heapq
import math
import logging
from typing import List, Dict, Tuple, Callable
from Core.Position import Position

def manhattan_distance(a: Position, b: Position) -> int:
    """
    Calculate the Manhattan distance between two positions.
    """
    return abs(a.x - b.x) + abs(a.y - b.y)

class PathFinder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PathFinder, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.zone = None
            self.logger = logging.getLogger(__name__)
            self._initialized = True

    @staticmethod
    def get_instance():
        if PathFinder._instance is None:
            PathFinder()
        return PathFinder._instance

    def set_zone(self, zone):
        """Set the zone reference for pathfinding checks"""
        self.zone = zone

    def is_passable(self, x: int, y: int, entity) -> bool:
        """Delegate passability check to zone"""
        if not self.zone:
            return True
        result = self.zone.is_passable(x, y, entity)
        self.logger.debug(f"Checking passability at ({x}, {y}) for {entity}: {result}")
        return result

    @staticmethod
    def euclidean_distance(a: Position, b: Position) -> float:
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

    def is_diagonal_safe(self, x: int, y: int, dx: int, dy: int, entity) -> bool:
        """Check if a diagonal move is safe (no corner cutting)"""
        # Check both adjacent squares to ensure we're not cutting corners
        return (self.is_passable(x + dx, y, entity) and 
                self.is_passable(x, y + dy, entity))

    def find_path(self, start: Position, goal: Position, entity) -> List[Position]:
        """Find a path avoiding obstacles and other entities"""
        if not self.zone:
            self.logger.warning("Attempting to find path with no zone set")
            return []

        # Log the pathfinding request
        self.logger.debug(f"Finding path from {start} to {goal} for {entity}")
        
        # Verify start and end positions are valid
        if not self.is_passable(goal.x, goal.y, entity):
            self.logger.debug(f"Goal position {goal} is not passable")
            return []

        start_coords = (start.x, start.y)
        goal_coords = (goal.x, goal.y)
        frontier: List[Tuple[float, Tuple[int, int]]] = [(0, start_coords)]
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        cost_so_far: Dict[Tuple[int, int], float] = {start_coords: 0.0}

        # Cardinal and diagonal directions.
        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),
            (1, 1), (-1, 1), (1, -1), (-1, -1)
        ]

        while frontier:
            current_priority, current_coords = heapq.heappop(frontier)
            if current_coords == goal_coords:
                break
            current_x, current_y = current_coords
            for dx, dy in directions:
                next_coords = (current_x + dx, current_y + dy)
                next_x, next_y = next_coords
                
                # For diagonal moves, check if we're cutting corners
                if dx != 0 and dy != 0:
                    if not self.is_diagonal_safe(current_x, current_y, dx, dy, entity):
                        self.logger.debug(f"Rejecting diagonal move to {next_coords} - unsafe corners")
                        continue
                
                if not self.is_passable(next_x, next_y, entity):
                    self.logger.debug(f"Position {next_coords} is not passable")
                    continue
                movement_cost = 1.414 if dx != 0 and dy != 0 else 1.0
                new_cost = cost_so_far[current_coords] + movement_cost
                if next_coords not in cost_so_far or new_cost < cost_so_far[next_coords]:
                    cost_so_far[next_coords] = new_cost
                    priority = new_cost + self.euclidean_distance(Position(next_x, next_y), goal)
                    heapq.heappush(frontier, (priority, next_coords))
                    came_from[next_coords] = current_coords

        path: List[Position] = []
        current = goal_coords
        if current not in came_from and current != start_coords:
            return path  # No path found.
        while current != start_coords:
            x, y = current
            path.append(Position(x, y))
            if current not in came_from:
                break
            current = came_from[current]
        path.reverse()
        return path
