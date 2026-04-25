"""
Quy tắc di chuyển nhân vật, đẩy thùng, kiểm tra hợp lệ và chiến thắng.
"""
from state.state import SokobanState

DIRECTIONS = {'U':(-1,0), 'D':(1,0), 'L':(0,-1), 'R':(0,1)}

def move_player(state, action):
    if action not in DIRECTIONS:
        return None
    dr, dc = DIRECTIONS[action]
    pr, pc = state.player
    nr, nc = pr + dr, pc + dc
    if not state.is_valid_pos(nr, nc):
        return None
    if (nr, nc) in state.boxes:
        br, bc = nr + dr, nc + dc
        if not state.is_valid_pos(br, bc) or (br, bc) in state.boxes:
            return None
        new_boxes = frozenset((state.boxes - {(nr,nc)}) | {(br,bc)})
        return SokobanState((nr,nc), new_boxes, state.walls, state.targets, state.width, state.height)
    return SokobanState((nr,nc), state.boxes, state.walls, state.targets, state.width, state.height)

def is_win(state):
    return state.is_goal()