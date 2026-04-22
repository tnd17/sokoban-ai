import heapq
from state.state import State
from heuristic.heuristic import basic_heuristic

def a_star_search(game):
    start_state = State(game.player_pos, game.boxes, g=0, 
                        h=basic_heuristic(game.boxes, game.goals))
    
    frontier = []
    heapq.heappush(frontier, start_state)
    visited = {start_state: 0}

    while frontier:
        current_state = heapq.heappop(frontier)

        # Kiểm tra điều kiện thắng (tất cả hộp nằm trên ô đích)
        if current_state.boxes == game.goals:
            return get_path(current_state)

        for action, next_player, next_boxes in game.get_successors(current_state):
            h = basic_heuristic(next_boxes, game.goals)
            neighbor = State(next_player, next_boxes, current_state, action, 
                             current_state.g + 1, h)

            if neighbor not in visited or neighbor.g < visited[neighbor]:
                visited[neighbor] = neighbor.g
                heapq.heappush(frontier, neighbor)
    
    return None # Không tìm thấy đường đi

def get_path(state):
    path = []
    while state.action:
        path.append(state.action)
        state = state.parent
    return path[::-1]