import os

class SokobanGame:
    def __init__(self, map_file):
        self.map_data = []
        self.player_pos = None
        self.goals = set()
        self.boxes = set()
        self.walls = set()
        self.load_map(map_file)
        self.goals = frozenset(self.goals) # Thêm dòng này
        
    def load_map(self, map_file):
        with open(map_file, 'r') as f:
            lines = f.readlines()
            for r, line in enumerate(lines):
                row_data = list(line.strip('\n'))
                for c, char in enumerate(row_data):
                    if char == '#':
                        self.walls.add((r, c))
                    elif char == '.':
                        self.goals.add((r, c))
                    elif char == '@':
                        self.player_pos = (r, c)
                    elif char == '$':
                        self.boxes.add((r, c))
                    elif char == '*':
                        self.boxes.add((r, c))
                        self.goals.add((r, c))
                    elif char == '+':
                        self.player_pos = (r, c)
                        self.goals.add((r, c))
                self.map_data.append(row_data)
        

    def is_win(self, current_boxes):
        # Kiểm tra xem tất cả vị trí hộp có trùng với các vị trí đích không
        return self.goals == current_boxes

    def get_next_state(self, player_pos, boxes, direction):
        """
        Xử lý logic di chuyển
        direction: (dr, dc) ví dụ (0, 1) là sang phải
        """
        dr, dc = direction
        new_p = (player_pos[0] + dr, player_pos[1] + dc)

        # 1. Gặp tường
        if new_p in self.walls:
            return None

        # 2. Gặp hộp
        if new_p in boxes:
            new_box_p = (new_p[0] + dr, new_p[1] + dc)
            # Kiểm tra xem phía sau hộp có đẩy được không (không là tường, không là hộp khác)
            if new_box_p not in self.walls and new_box_p not in boxes:
                new_boxes = set(boxes)
                new_boxes.remove(new_p)
                new_boxes.add(new_box_p)
                return new_p, new_boxes
            else:
                return None  # Không đẩy được

        # 3. Ô trống hoặc đích
        return new_p, boxes
    
    def get_successors(self, state):
        """
        Dựa trên state hiện tại, trả về danh sách các trạng thái kế tiếp có thể có.
        Dùng để cung cấp dữ liệu cho vòng lặp của thuật toán A*.
        """
        successors = []
        # 4 hướng di chuyển cơ bản
        moves = {
            'UP': (-1, 0),
            'DOWN': (1, 0),
            'LEFT': (0, -1),
            'RIGHT': (0, 1)
        }

        for action_name, direction in moves.items():
            # Sử dụng hàm get_next_state có sẵn của Ám Vân
            result = self.get_next_state(state.player_pos, state.boxes, direction)
            
            if result:
                new_player_pos, new_boxes = result
                # QUAN TRỌNG: Chuyển set thành frozenset để A* có thể lưu vào visited (hashable)
                successors.append((action_name, new_player_pos, frozenset(new_boxes)))
        
        return successors
    
    def display_board(self, player_pos, boxes):
        """Hiển thị trạng thái hiện tại của game ra console"""
        for r in range(len(self.map_data)):
            row_str = ""
            for c in range(len(self.map_data[r])):
                pos = (r, c)
                if pos == player_pos:
                    row_str += "@" if pos not in self.goals else "+"
                elif pos in boxes:
                    row_str += "$" if pos not in self.goals else "*"
                elif pos in self.walls:
                    row_str += "#"
                elif pos in self.goals:
                    row_str += "."
                else:
                    row_str += " "
            print(row_str)