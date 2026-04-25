"""
Greedy Best-First Search and A* Search for Sokoban.
"""

import heapq
import time


class SearchResult:
    def __init__(self, solution, nodes_explored, time_elapsed, found):
        self.solution = solution
        self.nodes_explored = nodes_explored
        self.time_elapsed = time_elapsed
        self.found = found

    @property
    def moves(self):
        return len(self.solution) if self.solution else 0


def greedy_search(initial, heuristic_func, time_limit=30.0):
    start_time = time.time()
    nodes_explored = 0
    counter = 0
    heap = [(heuristic_func(initial), counter, initial, [])]
    visited = set()

    while heap:
        if time.time() - start_time > time_limit:
            break
        _, _, state, path = heapq.heappop(heap)
        key = (state.player, state.boxes)
        if key in visited:
            continue
        visited.add(key)
        nodes_explored += 1

        if state.is_goal():
            return SearchResult(path, nodes_explored, time.time() - start_time, True)

        for next_state, action in state.get_neighbors():
            nkey = (next_state.player, next_state.boxes)
            if nkey not in visited and not next_state.is_deadlock():
                counter += 1
                heapq.heappush(heap, (
                    heuristic_func(next_state), counter,
                    next_state, path + [action]
                ))

    return SearchResult(None, nodes_explored, time.time() - start_time, False)


def astar_search(initial, heuristic_func, time_limit=30.0):
    start_time = time.time()
    nodes_explored = 0
    counter = 0
    h0 = heuristic_func(initial)
    # (f, counter, g, state, path)
    heap = [(h0, counter, 0, initial, [])]
    best_g = {}  # key -> best g đã xử lý

    while heap:
        if time.time() - start_time > time_limit:
            break
        f, _, g, state, path = heapq.heappop(heap)
        key = (state.player, state.boxes)

        # Chỉ xử lý nếu chưa thấy state này với g tốt hơn hoặc bằng
        if key in best_g and best_g[key] <= g:
            continue
        best_g[key] = g
        nodes_explored += 1

        if state.is_goal():
            return SearchResult(path, nodes_explored, time.time() - start_time, True)

        for next_state, action in state.get_neighbors():
            nkey = (next_state.player, next_state.boxes)
            ng = g + 1
            if (nkey not in best_g or best_g[nkey] > ng) and not next_state.is_deadlock():
                counter += 1
                heapq.heappush(heap, (
                    ng + heuristic_func(next_state), counter,
                    ng, next_state, path + [action]
                ))

    return SearchResult(None, nodes_explored, time.time() - start_time, False)


def solve(initial, algo, heuristic_func, time_limit=30.0):
    if algo == 'greedy':
        return greedy_search(initial, heuristic_func, time_limit)
    elif algo == 'astar':
        return astar_search(initial, heuristic_func, time_limit)
    raise ValueError(f"Unknown algo: {algo}")