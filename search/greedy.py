import heapq
from state.state import State
from heuristic.heuristic import basic_heuristic

def greedy_search(game):
    # Khởi tạo trạng thái bắt đầu
    start_state = State(game.player_pos, game.boxes, g=0, 
                        h=basic_heuristic(game.boxes, game.goals))
    
    frontier = []
    # Greedy chỉ ưu tiên theo h
    heapq.heappush(frontier, (start_state.h, start_state))
    visited = {start_state: 0}
    nodes_explored = 0 # Biến để đếm số node đã duyệt (phục vụ so sánh)

    while frontier:
        _, current_state = heapq.heappop(frontier)
        nodes_explored += 1

        if game.is_win(current_state.boxes):
            print(f"Greedy đã duyệt {nodes_explored} nodes.")
            return get_path(current_state)

        for action, next_player, next_boxes in game.get_successors(current_state):
            h = basic_heuristic(next_boxes, game.goals)
            neighbor = State(next_player, next_boxes, current_state, action, 
                             current_state.g + 1, h)

            if neighbor not in visited:
                visited[neighbor] = neighbor.g
                heapq.heappush(frontier, (neighbor.h, neighbor))
    return None

def get_path(state):
    path = []
    while state.action:
        path.append(state.action)
        state = state.parent
    return path[::-1]