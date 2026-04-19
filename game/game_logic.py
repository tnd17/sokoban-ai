import os

class SokobanGame:
    def __init__(self, map_file):
        self.map_data = []
        self.player_pos = None
        self.goals = set()
        self.boxes = set()
        self.walls = set()
        self.load_map(map_file)

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