"""
Chạy thống kê cho tất cả map + cả 2 thuật toán, lưu cache vào stats_cache.json.
"""
import os, json, time, hashlib
from collections import deque

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'stats_cache.json')


def _map_fingerprint(map_list):
    return hashlib.md5('|'.join(p for _, p in map_list).encode()).hexdigest()


def _bfs_dist(grid, start, end):
    """BFS tìm khoảng cách ngắn nhất từ start đến end trên grid."""
    if start == end:
        return 0
    rows, cols = len(grid), max(len(r) for r in grid)
    visited = {start}
    q = deque([(start, 0)])
    while q:
        (r, c), d = q.popleft()
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r+dr, c+dc
            if (nr, nc) == end:
                return d + 1
            if (0 <= nr < rows and 0 <= nc < len(grid[nr])
                    and grid[nr][nc] != '#' and (nr, nc) not in visited):
                visited.add((nr, nc))
                q.append(((nr, nc), d+1))
    return 999


def compute_complexity(grid, boxes, targets):
    """
    Tính độ phức tạp của map:
        complexity = (boxes^1.5 × 5) + (walkable × 0.2) + (avg_bfs_dist × 2) + (deadly_corners × 3)
    """
    rows = len(grid)
    cols = max(len(r) for r in grid)
    targets_set = set(targets)
    boxes_list  = list(boxes)

    # Số ô đi được
    walkable = sum(
        1 for r in range(rows) for c in range(cols)
        if c < len(grid[r]) and grid[r][c] != '#'
    )

    # Deadly corners: ô đi được, không phải target, bị tường chặn 2 hướng vuông góc
    deadly = 0
    for r in range(rows):
        for c in range(cols):
            if c >= len(grid[r]) or grid[r][c] == '#':
                continue
            if (r, c) in targets_set:
                continue
            def is_wall(nr, nc):
                return (nr < 0 or nr >= rows or nc < 0 or nc >= len(grid[nr])
                        or grid[nr][nc] == '#')
            for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                if is_wall(r+dr, c) and is_wall(r, c+dc):
                    deadly += 1
                    break

    # Avg BFS distance từ mỗi box đến target gần nhất
    if boxes_list and targets_set:
        total_dist = 0
        for box in boxes_list:
            nearest = min(_bfs_dist(grid, box, t) for t in targets_set)
            total_dist += nearest
        avg_dist = total_dist / len(boxes_list)
    else:
        avg_dist = 0

    nb = len(boxes_list)
    complexity = (nb ** 1.5) * 5 + walkable * 0.2 + avg_dist * 2 + deadly * 3
    return round(complexity, 2)


def run_stats(map_list, time_limit=30.0):
    """Chạy cả 2 thuật toán trên tất cả map, trả về dict kết quả."""
    from utils.map_loader import load_map, get_map_raw_grid
    from heuristic.heuristics import get_heuristic
    from search.algorithms import solve

    results = {}
    for name, path in map_list:
        results[name] = {}
        try:
            state    = load_map(path)
            raw_grid = get_map_raw_grid(path)
        except Exception as e:
            results[name] = {'error': str(e)}
            continue

        # Tính complexity
        results[name]['complexity'] = compute_complexity(
            raw_grid,
            list(state.boxes),
            list(state.targets),
        )

        for algo in ['greedy', 'astar']:
            h = get_heuristic(algo, raw_grid, state.targets, use_optimized=True)
            r = solve(state, algo, h, time_limit)
            nodes = r.nodes_explored
            moves = r.moves
            results[name][algo] = {
                'found':      r.found,
                'moves':      moves,
                'nodes':      nodes,
                'time':       round(r.time_elapsed, 4),
                'efficiency': round(nodes / moves, 2) if moves > 0 else None,
            }
    return results


def load_or_build_cache(map_list, time_limit=30.0, force=False):
    fp = _map_fingerprint(map_list)
    if not force and os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        if cache.get('fingerprint') == fp:
            return cache['data']

    print("[Stats] Đang chạy thống kê, vui lòng chờ...")
    t0 = time.time()
    data = run_stats(map_list, time_limit)
    print(f"[Stats] Hoàn tất sau {time.time()-t0:.1f}s")

    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump({'fingerprint': fp, 'data': data}, f, ensure_ascii=False, indent=2)
    return data