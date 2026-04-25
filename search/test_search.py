from game.game_logic import SokobanGame
from state.state import State
from search.search_algo import a_star_search, greedy_search

def test_compare(map_file):
    game = SokobanGame(map_file)
    initial_state = State(game.player_pos, game.boxes)
    
    print(f"--- TESTING MAP: {map_file} ---")
    
    # Chạy A*
    path_a, nodes_a = a_star_search(game, initial_state)
    if path_a:
        print(f"[A*]     Found solution: {len(path_a)} steps, {nodes_a} nodes explored.")
    else:
        print("[A*]     No solution found.")

    # Chạy Greedy
    path_g, nodes_g = greedy_search(game, initial_state)
    if path_g:
        print(f"[Greedy] Found solution: {len(path_g)} steps, {nodes_g} nodes explored.")
    else:
        print("[Greedy] No solution found.")
    print("-" * 40)

if __name__ == "__main__":
    # Test thử với map1
    try:
        test_compare("maps/map1.txt")
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file map. Hãy kiểm tra lại thư mục maps/")