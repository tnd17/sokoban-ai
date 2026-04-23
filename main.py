# Tạo để test các hàm 
from game.game_logic import SokobanGame
from ui.ui_manager import SokobanUI

def main():
    game = SokobanGame("maps/map1.txt")
    ui = SokobanUI(game)
    ui.run()

if __name__ == "__main__":
    main()