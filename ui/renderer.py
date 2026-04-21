"""Vẽ bản đồ Sokoban — visual nâng cấp."""
import pygame
from ui.colors import *

TILE = 46

def draw_board(surface, state, raw_grid, offset_x, offset_y, tile=TILE):
    rows, cols = state.height, state.width

    for r in range(rows):
        for c in range(cols):
            x = offset_x + c * tile
            y = offset_y + r * tile
            rect = pygame.Rect(x, y, tile, tile)

            if (r, c) in state.walls:
                pygame.draw.rect(surface, WALL, rect)
                pygame.draw.line(surface, WALL_LIGHT, (x, y), (x+tile-1, y), 2)
                pygame.draw.line(surface, WALL_LIGHT, (x, y), (x, y+tile-1), 2)
                pygame.draw.line(surface, WALL_DARK,  (x+tile-1, y), (x+tile-1, y+tile), 1)
                pygame.draw.line(surface, WALL_DARK,  (x, y+tile-1), (x+tile, y+tile-1), 1)
            else:
                col = FLOOR_ALT if (r+c) % 2 == 0 else FLOOR
                pygame.draw.rect(surface, col, rect)

            if (r, c) in state.targets and (r, c) not in state.boxes:
                mx, my = x + tile//2, y + tile//2
                s = tile // 3
                pts = [(mx, my-s), (mx+s, my), (mx, my+s), (mx-s, my)]
                pygame.draw.polygon(surface, TARGET_GLOW, pts)
                pygame.draw.polygon(surface, TARGET_CLR, pts, 2)

    # Boxes
    for (br, bc) in state.boxes:
        x = offset_x + bc * tile
        y = offset_y + br * tile
        on_target = (br, bc) in state.targets
        c1 = BOX_OK_CLR  if on_target else BOX_CLR
        c2 = BOX_OK_DARK if on_target else BOX_DARK

        pad = max(3, tile // 10)
        outer = pygame.Rect(x+pad, y+pad, tile-pad*2, tile-pad*2)
        inner = pygame.Rect(x+pad+2, y+pad+2, tile-pad*2-4, tile-pad*2-4)

        pygame.draw.rect(surface, c2, outer, border_radius=5)
        pygame.draw.rect(surface, c1, inner, border_radius=4)
        pygame.draw.rect(surface, WHITE, outer, 1, border_radius=5)

        # Highlight góc trên trái
        hl = pygame.Rect(x+pad+3, y+pad+3, (tile-pad*2)//3, 3)
        s = pygame.Surface((hl.width, hl.height), pygame.SRCALPHA)
        s.fill((255,255,255,80))
        surface.blit(s, hl.topleft)

    # Player
    pr, pc = state.player
    cx = offset_x + pc * tile + tile//2
    cy = offset_y + pr * tile + tile//2
    r  = tile//2 - 5

    shadow = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
    pygame.draw.circle(shadow, (0,0,0,60), (r+2, r+4), r)
    surface.blit(shadow, (cx-r-2, cy-r-2))

    pygame.draw.circle(surface, PLAYER_DARK, (cx, cy), r)
    pygame.draw.circle(surface, PLAYER_CLR,  (cx, cy), r-2)
    pygame.draw.circle(surface, WHITE, (cx, cy), r-2, 1)

    er = max(2, tile//14)
    pygame.draw.circle(surface, BG, (cx - tile//7, cy - tile//9), er)
    pygame.draw.circle(surface, BG, (cx + tile//7, cy - tile//9), er)
    mouth_r = pygame.Rect(cx - tile//8, cy + tile//12, tile//4, tile//14)
    pygame.draw.ellipse(surface, BG, mouth_r)


def board_pixel_size(state, tile=TILE):
    return state.width * tile, state.height * tile

def board_center_offset(surface_w, surface_h, state, tile=TILE):
    bw, bh = board_pixel_size(state, tile)
    return (surface_w - bw) // 2, (surface_h - bh) // 2