"""
Chạy thống kê cho tất cả map + cả 2 thuật toán, lưu cache vào stats_cache.json.
Độ khó (difficulty) = log2(astar_nodes + 1) — thước đo thực nghiệm trực tiếp.
"""
import os, json, time, hashlib, math

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'stats_cache.json')


def _map_fingerprint(map_list):
    return hashlib.md5('|'.join(p for _, p in map_list).encode()).hexdigest()


def compute_difficulty(astar_nodes: int) -> float:
    """
    Độ khó thực nghiệm dựa trên số node A* đã duyệt.
    Dùng log2(nodes + 1) để cân bằng khi nodes chênh lệch lớn.
    Ví dụ:
        nodes=0     → difficulty=0.00
        nodes=10    → difficulty=3.46
        nodes=100   → difficulty=6.66
        nodes=1000  → difficulty=9.97
        nodes=10000 → difficulty=13.29
    """
    return round(math.log2(astar_nodes + 1), 2)


def run_stats(map_list, time_limit=30.0):
    """Chạy cả 2 thuật toán trên tất cả map, trả về dict kết quả."""
    from utils.map_loader import load_map, get_map_raw_grid
    from heuristic.heuristics import get_heuristic
    from search.search_aglo import solve

    results = {}
    for name, path in map_list:
        results[name] = {}
        try:
            state    = load_map(path)
            raw_grid = get_map_raw_grid(path)
        except Exception as e:
            results[name] = {'error': str(e)}
            continue

        # Chạy từng thuật toán
        algo_results = {}
        for algo in ['greedy', 'astar']:
            h = get_heuristic(algo, raw_grid, state.targets, use_optimized=True)
            r = solve(state, algo, h, time_limit)
            nodes = r.nodes_explored
            moves = r.moves
            algo_results[algo] = {
                'found':      r.found,
                'moves':      moves,
                'nodes':      nodes,
                'time':       round(r.time_elapsed, 4),
                'efficiency': round(nodes / moves, 2) if moves > 0 else None,
            }

        # Độ khó = log2(astar_nodes + 1)
        # Nếu A* không tìm được lời giải, fallback sang greedy_nodes
        astar_nodes  = algo_results['astar']['nodes']
        greedy_nodes = algo_results['greedy']['nodes']
        base_nodes   = astar_nodes if algo_results['astar']['found'] else greedy_nodes
        results[name]['difficulty'] = compute_difficulty(base_nodes)

        # Giữ thêm complexity_label để hiển thị dễ đọc
        diff = results[name]['difficulty']
        if diff < 4:
            results[name]['difficulty_label'] = 'Easy'
        elif diff < 8:
            results[name]['difficulty_label'] = 'Medium'
        elif diff < 11:
            results[name]['difficulty_label'] = 'Hard'
        else:
            results[name]['difficulty_label'] = 'Very Hard'

        results[name]['greedy'] = algo_results['greedy']
        results[name]['astar']  = algo_results['astar']

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