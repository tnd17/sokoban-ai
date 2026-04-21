# Dùng để kiểm tra:
# 1. Đọc map thành công
# 2. Tạo trạng thái ban đầu
# 3. Sinh trạng thái kế tiếp đúng hay không

from game.game_logic import SokobanGame
from state.state import State, get_neighbors


def main():
    # Chọn map muốn test
    game = SokobanGame("maps/map1.txt")

    # Tạo trạng thái ban đầu từ dữ liệu map
    initial_state = State(
        player_pos=game.player_pos,
        boxes=game.boxes
    )

    print("===== INITIAL STATE =====")
    print("Player:", initial_state.player_pos)
    print("Boxes :", set(initial_state.boxes))
    print("Cost  :", initial_state.cost)
    print()

    # Sinh các trạng thái kế tiếp
    next_states = get_neighbors(game, initial_state)

    print("===== NEXT STATES =====")

    if not next_states:
        print("Không có nước đi hợp lệ.")
        return

    for i, state in enumerate(next_states, start=1):
        print(f"State {i}")
        print("Move  :", state.move)
        print("Player:", state.player_pos)
        print("Boxes :", set(state.boxes))
        print("Cost  :", state.cost)
        print("-" * 30)


if __name__ == "__main__":
    main()