"""
Heuristic functions for Sokoban: Greedy BFS and A*.
"""

from collections import deque


# ── Hungarian algorithm ───────────────────────────────────────────────────────

def hungarian(cost_matrix):
    """Minimum cost assignment (square matrix). Returns total min cost."""
    n = len(cost_matrix)
    if n == 0:
        return 0
    u = [0] * (n + 1)
    v = [0] * (n + 1)
    p = [0] * (n + 1)
    way = [0] * (n + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [float('inf')] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], float('inf'), 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost_matrix[i0-1][j-1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    return -v[0]


# ── BFS distance precomputation ───────────────────────────────────────────────

def precompute_distances(grid):
    """
    BFS từ mỗi ô đi được, tính khoảng cách ngắn nhất đến mọi ô khác.
    Trả về hàm distance(a, b) -> int.
    """
    rows = len(grid)
    cols = max(len(row) for row in grid)
    walkable = [
        (r, c)
        for r in range(rows)
        for c in range(cols)
        if c < len(grid[r]) and grid[r][c] != '#'
    ]
    idx = {pos: i for i, pos in enumerate(walkable)}
    n = len(walkable)
    INF = 10 ** 9
    dist = [[INF] * n for _ in range(n)]

    for i, start in enumerate(walkable):
        dist[i][i] = 0
        q = deque([start])
        visited = {start}
        while q:
            r, c = q.popleft()
            d_cur = dist[i][idx[(r, c)]]
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) in idx and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    dist[i][idx[(nr, nc)]] = d_cur + 1  # chỉ ghi 1 chiều
                    q.append((nr, nc))

    def distance(a, b):
        ia, ib = idx.get(a), idx.get(b)
        if ia is None or ib is None:
            return INF
        return dist[ia][ib]

    return distance


# ── Heuristic class ───────────────────────────────────────────────────────────

class Heuristic:
    def __init__(self, grid, targets, use_bfs_distances=True):
        self.targets = frozenset(targets)
        self.target_list = list(targets)
        self.num_targets = len(self.target_list)
        if use_bfs_distances:
            self.dist = precompute_distances(grid)
        else:
            self.dist = lambda a, b: abs(a[0]-b[0]) + abs(a[1]-b[1])
        self.matching_cache = {}

    def _optimal_matching(self, boxes):
        """Hungarian matching: tổng khoảng cách tối ưu box→target."""
        key = tuple(sorted(boxes))
        if key in self.matching_cache:
            return self.matching_cache[key]
        boxes = list(boxes)
        cost = [[self.dist(b, t) for t in self.target_list] for b in boxes]
        total = hungarian(cost)
        self.matching_cache[key] = total
        return total

    def _greedy_matching(self, boxes):
        """Greedy matching (nhanh hơn, dùng cho Greedy BFS)."""
        boxes = list(boxes)
        targets = self.target_list[:]
        total = 0
        for box in boxes:
            if not targets:
                break
            best = min(targets, key=lambda t: self.dist(box, t))
            total += self.dist(box, best)
            targets.remove(best)
        return total

    def heuristic_greedy(self, state):
        return float(self._greedy_matching(state.boxes))

    def heuristic_astar(self, state):
        """
        Admissible heuristic cho A*:
        = optimal box→target matching (Hungarian + BFS dist)
        Không cộng player_cost vì cách tính cũ không admissible,
        dẫn đến A* bỏ qua đường tối ưu.
        """
        return float(self._optimal_matching(state.boxes))


# ── Legacy fallback ───────────────────────────────────────────────────────────

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def heuristic_greedy(state):
    boxes, targets = list(state.boxes), list(state.targets)
    total = 0
    for box in boxes:
        if targets:
            best = min(targets, key=lambda t: manhattan(box, t))
            total += manhattan(box, best)
    return float(total)

def heuristic_astar(state):
    boxes, targets = list(state.boxes), list(state.targets)
    total = 0
    for box in boxes:
        if targets:
            best = min(targets, key=lambda t: manhattan(box, t))
            total += manhattan(box, best)
    return float(total)

def get_heuristic(algo, grid=None, targets=None, use_optimized=True):
    if use_optimized and grid is not None and targets is not None:
        heur = Heuristic(grid, targets, use_bfs_distances=True)
        if algo == 'greedy':
            return heur.heuristic_greedy
        elif algo == 'astar':
            return heur.heuristic_astar
    if algo == 'greedy':
        return heuristic_greedy
    elif algo == 'astar':
        return heuristic_astar
    raise ValueError(f"Unknown algo: {algo}")