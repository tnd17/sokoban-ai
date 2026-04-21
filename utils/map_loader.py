"""
Đọc file bản đồ Sokoban.
"""
import os
from state.sokoban_state import SokobanState

MAPS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'maps')

def load_map(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    grid = [l.rstrip('\n') for l in lines if not l.startswith(';')]

    walls, targets, boxes = set(), set(), set()
    player = None
    height = len(grid)
    width = max((len(l) for l in grid), default=0)

    char_map = {
        '#': 'wall', '@': 'player', '$': 'box',
        '.': 'target', '*': 'box_on', '+': 'player_on'
    }
    for r, line in enumerate(grid):
        for c, ch in enumerate(line):
            if ch == '#': walls.add((r,c))
            elif ch == '@': player = (r,c)
            elif ch == '$': boxes.add((r,c))
            elif ch == '.': targets.add((r,c))
            elif ch == '*': boxes.add((r,c)); targets.add((r,c))
            elif ch == '+': player = (r,c); targets.add((r,c))

    if player is None:
        raise ValueError(f"No player in {filepath}")

    return SokobanState(player, frozenset(boxes), frozenset(walls), frozenset(targets), width, height)

def get_map_list():
    if not os.path.exists(MAPS_DIR):
        return []
    files = [f for f in os.listdir(MAPS_DIR) if f.endswith('.txt') and f != 'note.txt']
    # Sort by numeric part to ensure map1, map2, ... map10 order
    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))) if any(c.isdigit() for c in f) else 0)
    return [(f.replace('.txt','').replace('_',' ').title(), os.path.join(MAPS_DIR, f)) for f in files]

def get_map_raw_grid(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return [l.rstrip('\n') for l in lines if not l.startswith(';')]