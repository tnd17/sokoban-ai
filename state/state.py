from game.game_logic import SokobanGame


class State:
    """
    Một trạng thái của trò chơi Sokoban gồm:

    - player_pos : vị trí người chơi (row, col)
    - boxes      : tập vị trí các thùng
    - parent     : trạng thái cha (để truy vết lời giải)
    - move       : hành động tạo ra trạng thái này
    - cost       : số bước đã đi từ trạng thái đầu (g(n))
    """

    def __init__(self, player_pos, boxes, parent=None, move=None, cost=0):
        self.player_pos = player_pos

        # Dùng frozenset để:
        # 1. Không bị thay đổi ngoài ý muốn
        # 2. Có thể hash() để dùng visited set
        self.boxes = frozenset(boxes)

        self.parent = parent
        self.move = move
        self.cost = cost

    def __hash__(self):
        """
        Cho phép State dùng trong set / dict
        """
        return hash((self.player_pos, self.boxes))

    def __eq__(self, other):
        """
        Hai trạng thái bằng nhau nếu:
        - người chơi cùng vị trí
        - các thùng cùng vị trí
        """
        return (
            isinstance(other, State)
            and self.player_pos == other.player_pos
            and self.boxes == other.boxes
        )

    def __repr__(self):
        """
        Hiển thị đẹp khi print(State)
        """
        return f"State(player={self.player_pos}, boxes={set(self.boxes)}, cost={self.cost})"


def get_neighbors(game, current_state):
    """
    Sinh các trạng thái kế tiếp từ current_state

    Mỗi lần thử 4 hướng:
    UP / DOWN / LEFT / RIGHT

    Nếu di chuyển hợp lệ theo luật game_logic.py
    thì tạo State mới và đưa vào danh sách neighbors
    """

    directions = {
        "UP": (-1, 0),
        "DOWN": (1, 0),
        "LEFT": (0, -1),
        "RIGHT": (0, 1)
    }

    neighbors = []

    for move_name, direction in directions.items():

        # Gọi logic game để kiểm tra đi được hay không
        result = game.get_next_state(
            current_state.player_pos,
            set(current_state.boxes),   # đổi về set thường để xử lý
            direction
        )

        # Nếu hợp lệ sẽ trả về trạng thái mới
        if result:
            new_player_pos, new_boxes = result

            new_state = State(
                player_pos=new_player_pos,
                boxes=new_boxes,
                parent=current_state,
                move=move_name,
                cost=current_state.cost + 1
            )

            neighbors.append(new_state)

    return neighbors


def get_path(goal_state):
    """
    Truy vết từ trạng thái đích về đầu
    để lấy chuỗi hành động lời giải
    """

    path = []
    current = goal_state

    while current.parent is not None:
        path.append(current.move)
        current = current.parent

    path.reverse()
    return path