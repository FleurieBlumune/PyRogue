from DataModel import Position
from typing import List, Dict, Tuple, Callable
import heapq
import math

def manhattan_distance(a: Position, b: Position) -> int:
    """
    Calculate the Manhattan distance between two positions.
    """
    return abs(a.x - b.x) + abs(a.y - b.y)

def euclidean_distance(a: Position, b: Position) -> float:
    """
    Calculate the Euclidean distance between two positions.
    """
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def find_path(
    start: Position,
    goal: Position,
    is_passable_func: Callable[[int, int], bool]
) -> List[Position]:
    """
    Find a path from the start position to the goal position using the A* algorithm.

    Args:
        start (Position): The starting position.
        goal (Position): The target position.
        is_passable_func (Callable[[int, int], bool]): A function that returns True if a given (x, y)
            coordinate is passable.

    Returns:
        List[Position]: A list of positions representing the path from start to goal. If no path is found,
        an empty list is returned.
    """
    start_coords = (start.x, start.y)
    goal_coords = (goal.x, goal.y)

    # Priority queue: elements are tuples of (priority, (x, y))
    frontier: List[Tuple[float, Tuple[int, int]]] = [(0, start_coords)]
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    cost_so_far: Dict[Tuple[int, int], float] = {start_coords: 0.0}

    # Possible movement directions (cardinal and diagonal)
    directions = [
        (0, 1), (1, 0), (0, -1), (-1, 0),   # Cardinal directions
        (1, 1), (-1, 1), (1, -1), (-1, -1)    # Diagonal directions
    ]

    while frontier:
        current_priority, current_coords = heapq.heappop(frontier)
        current_x, current_y = current_coords

        # Check if we reached the goal.
        if current_coords == goal_coords:
            break

        for dx, dy in directions:
            next_coords = (current_x + dx, current_y + dy)
            next_x, next_y = next_coords

            # Skip if the next position is not passable.
            if not is_passable_func(next_x, next_y):
                continue

            # Use 1.414 (~√2) for diagonal moves, otherwise 1.0.
            movement_cost = 1.414 if dx != 0 and dy != 0 else 1.0
            new_cost = cost_so_far[current_coords] + movement_cost

            # Update if this path to next_coords is better than any previous one.
            if next_coords not in cost_so_far or new_cost < cost_so_far[next_coords]:
                cost_so_far[next_coords] = new_cost
                priority = new_cost + euclidean_distance(Position(next_x, next_y), goal)
                heapq.heappush(frontier, (priority, next_coords))
                came_from[next_coords] = current_coords

    # Reconstruct the path from goal to start.
    path: List[Position] = []
    current = goal_coords
    if current not in came_from and current != start_coords:
        # No path found.
        return path

    while current != start_coords:
        x, y = current
        path.append(Position(x, y))
        if current not in came_from:
            break
        current = came_from[current]

    path.reverse()
    return path
