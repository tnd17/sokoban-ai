"""
Biểu diễn trạng thái bài toán Sokoban.
"""

class SokobanState:
    def __init__(self, player, boxes, walls, targets, width, height):
        self.player = player        # (row, col)
        self.boxes = boxes          # frozenset of (row, col)
        self.walls = walls          # frozenset of (row, col)
        self.targets = targets      # frozenset of (row, col)
        self.width = width
        self.height = height

    def is_goal(self):
        return self.boxes == self.targets

    def is_valid_pos(self, row, col):
        if row < 0 or row >= self.height or col < 0 or col >= self.width:
            return False
        return (row, col) not in self.walls

    def _is_wall(self, r, c):
        """Ô ngoài biên hoặc là tường đều coi là tường."""
        if r < 0 or r >= self.height or c < 0 or c >= self.width:
            return True
        return (r, c) in self.walls

    def get_neighbors(self):
        neighbors = []
        for dr, dc, action in [(-1,0,'U'),(1,0,'D'),(0,-1,'L'),(0,1,'R')]:
            pr, pc = self.player
            nr, nc = pr + dr, pc + dc
            if not self.is_valid_pos(nr, nc):
                continue
            if (nr, nc) in self.boxes:
                br, bc = nr + dr, nc + dc
                if not self.is_valid_pos(br, bc) or (br, bc) in self.boxes:
                    continue
                new_boxes = frozenset((self.boxes - {(nr, nc)}) | {(br, bc)})
                new_state = SokobanState((nr,nc), new_boxes, self.walls, self.targets, self.width, self.height)
            else:
                new_state = SokobanState((nr,nc), self.boxes, self.walls, self.targets, self.width, self.height)
            neighbors.append((new_state, action))
        return neighbors

    def _is_corner_deadlock(self, box):
        """Thùng bị kẹt góc và không ở đích."""
        r, c = box
        if box in self.targets:
            return False
        # Kiểm tra 4 kiểu góc: (trên+trái), (trên+phải), (dưới+trái), (dưới+phải)
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if self._is_wall(r + dr, c) and self._is_wall(r, c + dc):
                return True
        return False

    def is_deadlock(self):
        for box in self.boxes:
            if self._is_corner_deadlock(box):
                return True

        # 2x2 block deadlock
        boxes_set = set(self.boxes)
        for r, c in self.boxes:
            cells = [(r,c),(r+1,c),(r,c+1),(r+1,c+1)]
            if (all(cell in boxes_set for cell in cells) and
                    not any(cell in self.targets for cell in cells)):
                return True

        return False

    def __eq__(self, other):
        return isinstance(other, SokobanState) and self.player == other.player and self.boxes == other.boxes

    def __hash__(self):
        return hash((self.player, self.boxes))