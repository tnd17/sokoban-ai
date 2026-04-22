class State:
    def __init__(self, player_pos, boxes, parent=None, action=None, g=0, h=0):
        self.player_pos = player_pos
        self.boxes = frozenset(boxes)  # Dùng frozenset để có thể làm key trong dictionary
        self.parent = parent
        self.action = action
        self.g = g  # Chi phí từ node bắt đầu
        self.h = h  # Dự đoán chi phí đến đích (Heuristic)
        self.f = g + h

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.player_pos == other.player_pos and self.boxes == other.boxes

    def __hash__(self):
        return hash((self.player_pos, self.boxes))