from DataModel import Position
from typing import List, Dict, Tuple
import heapq
import math

def manhattan_distance(a: Position, b: Position) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)

def euclidean_distance(a: Position, b: Position) -> float:
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def find_path(start: Position, goal: Position, is_passable_func) -> List[Position]:
    frontier = [(0, start.x, start.y)]
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    cost_so_far: Dict[Tuple[int, int], float] = {(start.x, start.y): 0}
    
    # Include diagonal movements
    directions = [
        (0, 1), (1, 0), (0, -1), (-1, 0),  # Cardinal directions
        (1, 1), (-1, 1), (1, -1), (-1, -1)  # Diagonal directions
    ]
    
    while frontier:
        _, current_x, current_y = heapq.heappop(frontier)
        current_pos = (current_x, current_y)
        
        if current_x == goal.x and current_y == goal.y:
            break
            
        for dx, dy in directions:
            next_x, next_y = current_x + dx, current_y + dy
            next_pos = (next_x, next_y)
            
            if not is_passable_func(next_x, next_y):
                continue
            
            # Use 1.414 (√2) for diagonal movement cost
            movement_cost = 1.414 if dx != 0 and dy != 0 else 1.0
            new_cost = cost_so_far[current_pos] + movement_cost
            
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                # Use euclidean distance for better diagonal path estimation
                priority = new_cost + euclidean_distance(Position(next_x, next_y), goal)
                heapq.heappush(frontier, (priority, next_x, next_y))
                came_from[next_pos] = current_pos
    
    # Reconstruct path
    path = []
    current_pos = (goal.x, goal.y)
    if current_pos not in came_from and current_pos != (start.x, start.y):
        return path  # No path found
        
    while current_pos != (start.x, start.y):
        x, y = current_pos
        path.append(Position(x, y))
        if current_pos not in came_from:
            break
        current_pos = came_from[current_pos]
    
    path.reverse()
    return path
