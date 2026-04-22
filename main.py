from game.game_logic import SokobanGame
from ui.ui_manager import SokobanUI

def main():
    # Load game logic
    map_path = 'maps/map_test.txt'
    game = SokobanGame(map_path)
    
    # Khởi động giao diện và menu chọn thuật toán
    ui = SokobanUI(game)
    ui.run_menu()

if __name__ == "__main__":
    main()