import time
from game.game_logic import SokobanGame
from search.a_star import a_star_search

def main():
    # Đảm bảo đường dẫn map chính xác
    map_path = 'maps/map1.txt'
    game = SokobanGame(map_path)
    
    print("Bản đồ ban đầu:")
    game.display_board(game.player_pos, game.boxes)
    
    print("\nĐang tìm lời giải bằng A*...")
    solution = a_star_search(game)
    
    if solution:
        print(f"Tìm thấy lời giải sau {len(solution)} bước!")
        
        # Chạy mô phỏng giao diện console
        curr_player = game.player_pos
        curr_boxes = game.boxes
        
        for step, action in enumerate(solution):
            time.sleep(0.5) # Dừng một chút để kịp nhìn
            print(f"\nBước {step + 1}: {action}")
            
            # Cập nhật vị trí để vẽ
            moves = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1)}
            res = game.get_next_state(curr_player, curr_boxes, moves[action])
            curr_player, curr_boxes = res
            
            game.display_board(curr_player, curr_boxes)
    else:
        print("Không tìm thấy lời giải. Hãy kiểm tra lại file map hoặc hàm Heuristic.")

if __name__ == "__main__":
    main()