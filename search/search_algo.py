import heapq
from state.state import State, get_neighbors, get_path
from heuristic.heuristic import basic_heuristic

def a_star_search(game, initial_state):
    # Priority Queue lưu: (f_score, state)
    frontier = []
    h_start = basic_heuristic(initial_state.boxes, game.goals)
    heapq.heappush(frontier, (initial_state.cost + h_start, initial_state))
    
    visited = {initial_state: initial_state.cost}
    nodes_explored = 0

    while frontier:
        _, current_state = heapq.heappop(frontier)
        nodes_explored += 1

        # Kiểm tra đích bằng hàm của game_logic
        if game.is_win(current_state.boxes):
            return get_path(current_state), nodes_explored

        for neighbor in get_neighbors(game, current_state):
            if neighbor not in visited or neighbor.cost < visited[neighbor]:
                visited[neighbor] = neighbor.cost
                h = basic_heuristic(neighbor.boxes, game.goals)
                # A* dùng f = g + h
                f_score = neighbor.cost + h
                heapq.heappush(frontier, (f_score, neighbor))
                
    return None, nodes_explored

def greedy_search(game, initial_state):
    frontier = []
    h_start = basic_heuristic(initial_state.boxes, game.goals)
    # Greedy chỉ dùng f = h
    heapq.heappush(frontier, (h_start, initial_state))
    
    visited = {initial_state}
    nodes_explored = 0

    while frontier:
        _, current_state = heapq.heappop(frontier)
        nodes_explored += 1

        if game.is_win(current_state.boxes):
            return get_path(current_state), nodes_explored

        for neighbor in get_neighbors(game, current_state):
            if neighbor not in visited:
                visited.add(neighbor)
                h = basic_heuristic(neighbor.boxes, game.goals)
                heapq.heappush(frontier, (h, neighbor))
                
    return None, nodes_explored