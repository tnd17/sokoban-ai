"""
Màn hình: Menu, Game, Analysis — redesign.
"""
import pygame, threading, os, math
from ui.colors import *
from ui.renderer import draw_board, board_center_offset, TILE

SIDEBAR_W = 260

# ══════════════════════════════════════════════════════════════════════════════
# Helper UI
# ══════════════════════════════════════════════════════════════════════════════

def draw_text(surf, text, x, y, font, color=TEXT, center=False, right=False):
    img = font.render(str(text), True, color)
    r   = img.get_rect()
    if center: r.center   = (x, y)
    elif right: r.right   = x; r.top = y
    else:       r.topleft = (x, y)
    surf.blit(img, r)
    return r

def draw_rect_border(surf, rect, color, width=1, radius=8):
    pygame.draw.rect(surf, color, rect, width, border_radius=radius)

def draw_card(surf, rect, color=CARD_BG, border=BTN_BORDER, radius=10):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    draw_rect_border(surf, rect, border, 1, radius)

def draw_button(surf, text, rect, font, hover=False, active=False, color=None):
    if color is None:
        bg = BTN_ACTIVE if active else (BTN_HOVER if hover else BTN_BG)
    else:
        bg = color
    pygame.draw.rect(surf, bg, rect, border_radius=8)
    border_col = ACCENT if active else (ACCENT if hover else BTN_BORDER)
    draw_rect_border(surf, rect, border_col, 1, 8)
    draw_text(surf, text, rect.centerx, rect.centery, font, WHITE, center=True)

def draw_arrow_btn(surf, rect, direction, font, hover=False):
    """Nút mũi tên ◀ ▶."""
    draw_button(surf, '◀' if direction == 'left' else '▶', rect, font, hover=hover)

def draw_sidebar(surf, rect):
    pygame.draw.rect(surf, SIDEBAR_BG, rect)
    pygame.draw.line(surf, DIVIDER, rect.topright, rect.bottomright, 1)

def draw_progress_bar(surf, rect, progress, color=ACCENT, bg=BTN_BG, radius=5):
    pygame.draw.rect(surf, bg, rect, border_radius=radius)
    if progress > 0:
        fw = max(radius*2, int(rect.width * progress))
        filled = pygame.Rect(rect.x, rect.y, fw, rect.height)
        pygame.draw.rect(surf, color, filled, border_radius=radius)


# ══════════════════════════════════════════════════════════════════════════════
# MenuScreen
# ══════════════════════════════════════════════════════════════════════════════

class MenuScreen:
    ALGOS = [('greedy', 'Greedy Best-First'), ('astar', 'A* Search')]
    SPEEDS = [('0.5×', 0.85), ('1×', 0.42), ('2×', 0.20), ('4×', 0.08), ('8×', 0.03)]

    def __init__(self, screen, fonts, map_list):
        self.screen       = screen
        self.fonts        = fonts
        self.map_list     = map_list
        self.map_idx      = 0
        self.algo_idx     = 1          # default A*
        self.speed_idx    = 1          # default 1×
        self.result       = None
        
        # Animation state
        self.initial_state = None
        self.state         = None
        self.solving       = False
        self.solve_result  = None
        self.animating     = False
        self.anim_index    = 0
        self.anim_states   = []
        self.anim_timer    = 0.0
        self.finished      = False
        self.paused        = False
        self.status_msg    = ""
        self.error_msg     = ""
        self.stats         = None
        
        self._load_current_map()

    def _load_current_map(self):
        from utils.map_loader import load_map
        if self.map_list:
            _, path = self.map_list[self.map_idx]
            self.initial_state = load_map(path)
            self.state = load_map(path)

    @property
    def selected_algo(self):
        return self.ALGOS[self.algo_idx][0]

    # ── worker ───────────────────────────────────────────────────────────────
    def _solve_worker(self):
        from heuristic.heuristics import get_heuristic
        from search.algorithms import solve
        from utils.map_loader import get_map_raw_grid
        _, path = self.map_list[self.map_idx]
        grid = get_map_raw_grid(path)
        h    = get_heuristic(self.selected_algo, grid, self.initial_state.targets,
                             use_optimized=True)
        self.solve_result = solve(self.initial_state, self.selected_algo, h, 60.0)
        self.solving      = False

    def _build_anim_states(self, actions):
        from game.rules import move_player
        states = [self.initial_state]
        cur    = self.initial_state
        for a in actions:
            ns = move_player(cur, a)
            if ns: states.append(ns); cur = ns
        return states

    def _reset(self):
        from utils.map_loader import load_map
        if self.map_list:
            _, path = self.map_list[self.map_idx]
            self.state       = load_map(path)
        self.animating   = False
        self.solving     = False
        self.anim_index  = 0
        self.anim_states = []
        self.finished    = False
        self.paused      = False
        self.status_msg  = ""
        self.error_msg   = ""
        self.solve_result= None
        self.stats       = None

    def handle_event(self, event, mouse_pos):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        W, H = self.screen.get_size()
        btns = self._get_rects(W, H)
        
        # Map selection
        if btns['map_prev'].collidepoint(mouse_pos):
            self.map_idx = (self.map_idx - 1) % max(1, len(self.map_list))
            self._reset()
            self._load_current_map()
        if btns['map_next'].collidepoint(mouse_pos):
            self.map_idx = (self.map_idx + 1) % max(1, len(self.map_list))
            self._reset()
            self._load_current_map()
        
        # Algorithm selection
        if btns['algo_prev'].collidepoint(mouse_pos):
            self.algo_idx = (self.algo_idx - 1) % len(self.ALGOS)
        if btns['algo_next'].collidepoint(mouse_pos):
            self.algo_idx = (self.algo_idx + 1) % len(self.ALGOS)
        
        # Speed selection
        if btns['speed_prev'].collidepoint(mouse_pos):
            self.speed_idx = (self.speed_idx - 1) % len(self.SPEEDS)
        if btns['speed_next'].collidepoint(mouse_pos):
            self.speed_idx = (self.speed_idx + 1) % len(self.SPEEDS)
        
        # Solve button
        if btns['solve'].collidepoint(mouse_pos) and not self.solving and not self.finished:
            self.solving    = True
            self.status_msg = "Solving..."
            self.error_msg  = ""
            threading.Thread(target=self._solve_worker, daemon=True).start()
        
        # Pause button
        if btns['pause'].collidepoint(mouse_pos) and self.animating:
            self.paused = not self.paused
        
        # Reset button
        if btns['reset'].collidepoint(mouse_pos):
            self._reset()
        
        # Analysis button
        if btns['analysis'].collidepoint(mouse_pos):
            self.result = ('analysis',)

    def _get_rects(self, W, H):
        sw = SIDEBAR_W
        x_start = 20
        y_start = 150
        row_height = 70
        
        return {
            'map_prev':   pygame.Rect(x_start, y_start, 36, 36),
            'map_next':   pygame.Rect(sw - 56, y_start, 36, 36),
            'algo_prev':  pygame.Rect(x_start, y_start + row_height, 36, 36),
            'algo_next':  pygame.Rect(sw - 56, y_start + row_height, 36, 36),
            'speed_prev': pygame.Rect(x_start, y_start + row_height*2, 36, 36),
            'speed_next': pygame.Rect(sw - 56, y_start + row_height*2, 36, 36),
            'solve':      pygame.Rect(x_start, y_start + row_height*3 + 20, sw - 40, 44),
            'reset':      pygame.Rect(x_start, y_start + row_height*3 + 74, sw - 40, 44),
            'pause':      pygame.Rect(x_start, y_start + row_height*3 + 128, sw - 40, 44),
            'analysis':   pygame.Rect(x_start, H - 60, sw - 40, 44),
        }

    def update(self, dt):
        if self.solve_result is not None and not self.animating and not self.finished:
            r = self.solve_result; self.solve_result = None
            if r.found:
                self.anim_states = self._build_anim_states(r.solution)
                self.animating   = True
                self.anim_index  = 0
                self.anim_timer  = 0.0
                self.stats       = r
                self.status_msg  = (f"Found!  {r.moves} moves  |  "
                                    f"{r.nodes_explored:,} nodes  |  {r.time_elapsed:.3f}s")
            else:
                self.error_msg  = "No solution found within time limit."
                self.status_msg = ""

        if self.animating and self.anim_states and not self.paused:
            self.anim_timer += dt
            delay = self.SPEEDS[self.speed_idx][1]
            if self.anim_timer >= delay:
                self.anim_timer = 0.0
                self.anim_index += 1
                if self.anim_index >= len(self.anim_states):
                    self.anim_index = len(self.anim_states) - 1
                    self.animating  = False
                    self.finished   = True
                else:
                    self.state = self.anim_states[self.anim_index]

    def draw(self, mouse_pos):
        W, H = self.screen.get_size()
        self.screen.fill(BG)
        sw   = SIDEBAR_W
        btns = self._get_rects(W, H)

        # ── Sidebar ──────────────────────────────────────────────────────────
        draw_sidebar(self.screen, pygame.Rect(0, 0, sw, H))

        # Logo / title
        draw_text(self.screen, "SOKOBAN", sw//2, 50, self.fonts['xl'],
                  ACCENT, center=True)
        draw_text(self.screen, "AI  SOLVER", sw//2, 95, self.fonts['md'],
                  ACCENT3, center=True)

        # Divider
        pygame.draw.line(self.screen, DIVIDER, (20, 120), (sw-20, 120), 1)

        # Map selection
        draw_text(self.screen, "Map", sw//2, 138, self.fonts['xs'], TEXT_DIM, center=True)
        draw_arrow_btn(self.screen, btns['map_prev'], 'left', self.fonts['sm'],
                       hover=btns['map_prev'].collidepoint(mouse_pos))
        draw_arrow_btn(self.screen, btns['map_next'], 'right', self.fonts['sm'],
                       hover=btns['map_next'].collidepoint(mouse_pos))
        map_name = self.map_list[self.map_idx][0] if self.map_list else "—"
        draw_text(self.screen, map_name[:15], sw//2, 168, self.fonts['sm'], WHITE, center=True)
        draw_text(self.screen, f"{self.map_idx+1}/{len(self.map_list)}", sw//2, 188, 
                  self.fonts['xs'], TEXT_DIM, center=True)

        # Algorithm selection
        draw_text(self.screen, "Algorithm", sw//2, 208, self.fonts['xs'], TEXT_DIM, center=True)
        draw_arrow_btn(self.screen, btns['algo_prev'], 'left', self.fonts['sm'],
                       hover=btns['algo_prev'].collidepoint(mouse_pos))
        draw_arrow_btn(self.screen, btns['algo_next'], 'right', self.fonts['sm'],
                       hover=btns['algo_next'].collidepoint(mouse_pos))
        draw_text(self.screen, self.ALGOS[self.algo_idx][1], sw//2, 238, 
                  self.fonts['sm'], ACCENT, center=True)

        # Speed selection
        draw_text(self.screen, "Speed", sw//2, 278, self.fonts['xs'], TEXT_DIM, center=True)
        draw_arrow_btn(self.screen, btns['speed_prev'], 'left', self.fonts['sm'],
                       hover=btns['speed_prev'].collidepoint(mouse_pos))
        draw_arrow_btn(self.screen, btns['speed_next'], 'right', self.fonts['sm'],
                       hover=btns['speed_next'].collidepoint(mouse_pos))
        draw_text(self.screen, self.SPEEDS[self.speed_idx][0], sw//2, 308, 
                  self.fonts['sm'], WHITE, center=True)

        # Solve button
        lbl = "⏳ Solving…" if self.solving else "▶ Solve"
        draw_button(self.screen, lbl, btns['solve'], self.fonts['sm'],
                    hover=btns['solve'].collidepoint(mouse_pos),
                    active=self.solving, color=BTN_ACTIVE)

        # Pause button
        if self.animating:
            pause_lbl = "▶ Resume" if self.paused else "⏸ Pause"
            draw_button(self.screen, pause_lbl, btns['pause'], self.fonts['sm'],
                        hover=btns['pause'].collidepoint(mouse_pos))

        # Reset button
        draw_button(self.screen, "⟳ Reset", btns['reset'], self.fonts['sm'],
                    hover=btns['reset'].collidepoint(mouse_pos))

        # Analysis button
        draw_button(self.screen, "📊 Analysis", btns['analysis'], self.fonts['sm'],
                    hover=btns['analysis'].collidepoint(mouse_pos))

        # ── Main area (Map display) ─────────────────────────────────────────────
        if self.state:
            tile = min(TILE, (W-sw-60)//(max(self.state.width,1)),
                             (H-100)//(max(self.state.height,1)))
            ox, oy = board_center_offset(W-sw-60, H-100, self.state, tile)
            ox += sw + 30
            oy += 50
            draw_board(self.screen, self.state, None, ox, oy, tile)

        # Progress bar
        if self.anim_states:
            total = max(len(self.anim_states)-1, 1)
            draw_progress_bar(self.screen,
                              pygame.Rect(sw+40, H-26, W-sw-80, 8),
                              self.anim_index / total)

        # Status
        if self.error_msg:
            draw_text(self.screen, self.error_msg,
                      sw + (W-sw)//2, H-46, self.fonts['sm'], DANGER, center=True)
        elif self.status_msg:
            draw_text(self.screen, self.status_msg,
                      sw + (W-sw)//2, H-46, self.fonts['sm'], SUCCESS, center=True)

        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
# GameScreen
# ══════════════════════════════════════════════════════════════════════════════

class GameScreen:
    SPEEDS = [('0.5×', 0.85), ('1×', 0.42), ('2×', 0.20), ('4×', 0.08), ('8×', 0.03)]

    def __init__(self, screen, fonts, map_path, algo):
        self.screen   = screen
        self.fonts    = fonts
        self.map_path = map_path
        self.algo     = algo
        self.result   = None

        from utils.map_loader import load_map
        self.initial_state = load_map(map_path)
        self.state         = load_map(map_path)
        self.map_name = (os.path.basename(map_path)
                         .replace('.txt','').replace('_',' ').title())

        self.solving     = False
        self.solve_result= None
        self.animating   = False
        self.anim_index  = 0
        self.anim_states = []
        self.anim_timer  = 0.0
        self.speed_idx   = 1
        self.finished    = False
        self.status_msg  = ""
        self.error_msg   = ""
        self.stats       = None

    # ── worker ───────────────────────────────────────────────────────────────
    def _solve_worker(self):
        from heuristic.heuristics import get_heuristic
        from search.algorithms import solve
        from utils.map_loader import get_map_raw_grid
        grid = get_map_raw_grid(self.map_path)
        h    = get_heuristic(self.algo, grid, self.initial_state.targets,
                             use_optimized=True)
        self.solve_result = solve(self.initial_state, self.algo, h, 60.0)
        self.solving      = False

    def _build_anim_states(self, actions):
        from game.rules import move_player
        states = [self.initial_state]
        cur    = self.initial_state
        for a in actions:
            ns = move_player(cur, a)
            if ns: states.append(ns); cur = ns
        return states

    def _reset(self):
        from utils.map_loader import load_map
        self.state       = load_map(self.map_path)
        self.animating   = False
        self.solving     = False
        self.anim_index  = 0
        self.anim_states = []
        self.finished    = False
        self.status_msg  = ""
        self.error_msg   = ""
        self.solve_result= None
        self.stats       = None

    # ── events ───────────────────────────────────────────────────────────────
    def handle_event(self, event, mouse_pos):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        W, H = self.screen.get_size()
        btns = self._get_rects(W, H)

        if btns['back'].collidepoint(mouse_pos):
            self.result = ('menu',); return
        if btns['reset'].collidepoint(mouse_pos):
            self._reset(); return
        if btns['solve'].collidepoint(mouse_pos) and not self.solving and not self.animating and not self.finished:
            self.solving    = True
            self.status_msg = "Solving..."
            self.error_msg  = ""
            threading.Thread(target=self._solve_worker, daemon=True).start()
        if btns['speed'].collidepoint(mouse_pos) and self.animating:
            self.speed_idx = (self.speed_idx + 1) % len(self.SPEEDS)

        if self.finished:
            if btns.get('again') and btns['again'].collidepoint(mouse_pos):
                self._reset()
            if btns.get('menu2') and btns['menu2'].collidepoint(mouse_pos):
                self.result = ('menu',)

    def _get_rects(self, W, H):
        sw = SIDEBAR_W
        r = {
            'back':  pygame.Rect(10,   10, 80, 34),
            'reset': pygame.Rect(100,  10, 80, 34),
            'solve': pygame.Rect(W-150,10, 140, 34),
            'speed': pygame.Rect(W-150,52, 140, 30),
        }
        if self.finished:
            cx = sw + (W-sw)//2
            r['again'] = pygame.Rect(cx-190, H//2+100, 160, 44)
            r['menu2'] = pygame.Rect(cx+30,  H//2+100, 160, 44)
        return r

    # ── update ───────────────────────────────────────────────────────────────
    def update(self, dt):
        if self.solve_result is not None and not self.animating and not self.finished:
            r = self.solve_result; self.solve_result = None
            if r.found:
                self.anim_states = self._build_anim_states(r.solution)
                self.animating   = True
                self.anim_index  = 0
                self.anim_timer  = 0.0
                self.stats       = r
                self.status_msg  = (f"Found!  {r.moves} moves  |  "
                                    f"{r.nodes_explored:,} nodes  |  {r.time_elapsed:.3f}s")
            else:
                self.error_msg  = "No solution found within time limit."
                self.status_msg = ""

        if self.animating and self.anim_states:
            self.anim_timer += dt
            delay = self.SPEEDS[self.speed_idx][1]
            if self.anim_timer >= delay:
                self.anim_timer = 0.0
                self.anim_index += 1
                if self.anim_index >= len(self.anim_states):
                    self.anim_index = len(self.anim_states) - 1
                    self.animating  = False
                    self.finished   = True
                else:
                    self.state = self.anim_states[self.anim_index]

    # ── draw ─────────────────────────────────────────────────────────────────
    def draw(self, mouse_pos):
        W, H = self.screen.get_size()
        self.screen.fill(BG)
        btns = self._get_rects(W, H)

        # Top bar
        pygame.draw.rect(self.screen, PANEL_BG, pygame.Rect(0, 0, W, 52))
        pygame.draw.line(self.screen, DIVIDER, (0, 52), (W, 52), 1)

        draw_button(self.screen, "← Back",  btns['back'],  self.fonts['sm'],
                    hover=btns['back'].collidepoint(mouse_pos))
        draw_button(self.screen, "⟳ Reset", btns['reset'], self.fonts['sm'],
                    hover=btns['reset'].collidepoint(mouse_pos))

        algo_label = "Greedy" if self.algo == 'greedy' else "A*"
        draw_text(self.screen, f"{self.map_name}  ·  {algo_label}",
                  W//2, 26, self.fonts['md'], TEXT_BRIGHT, center=True)

        lbl = "⏳ Solving…" if self.solving else "▶ Solve"
        draw_button(self.screen, lbl, btns['solve'], self.fonts['sm'],
                    hover=btns['solve'].collidepoint(mouse_pos),
                    active=self.solving)
        if self.animating:
            draw_button(self.screen,
                        f"⚡ {self.SPEEDS[self.speed_idx][0]}",
                        btns['speed'], self.fonts['xs'],
                        hover=btns['speed'].collidepoint(mouse_pos))

        # Board
        tile = min(TILE, (W-60)//(max(self.state.width,1)),
                         (H-140)//(max(self.state.height,1)))
        ox, oy = board_center_offset(W, H-120, self.state, tile)
        oy += 62
        draw_board(self.screen, self.state, None, ox, oy, tile)

        # Progress bar
        if self.anim_states:
            total = max(len(self.anim_states)-1, 1)
            draw_progress_bar(self.screen,
                              pygame.Rect(40, H-26, W-80, 8),
                              self.anim_index / total)

        # Status
        if self.error_msg:
            draw_text(self.screen, self.error_msg,
                      W//2, H-46, self.fonts['sm'], DANGER, center=True)
        elif self.status_msg:
            draw_text(self.screen, self.status_msg,
                      W//2, H-46, self.fonts['sm'], SUCCESS, center=True)

        if self.finished:
            self._draw_win_overlay(mouse_pos)

        pygame.display.flip()

    def _draw_win_overlay(self, mouse_pos):
        W, H  = self.screen.get_size()
        sw    = SIDEBAR_W
        cx    = sw + (W-sw)//2

        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        self.screen.blit(ov, (0, 0))

        pw, ph = 460, 320
        panel  = pygame.Rect(cx - pw//2, H//2 - ph//2 - 20, pw, ph)
        pygame.draw.rect(self.screen, CARD_BG,  panel, border_radius=14)
        pygame.draw.rect(self.screen, SUCCESS,  panel, 2,  border_radius=14)

        draw_text(self.screen, "🎉  Solved!", cx, panel.y+36,
                  self.fonts['lg'], SUCCESS, center=True)
        pygame.draw.line(self.screen, DIVIDER,
                         (panel.x+20, panel.y+68), (panel.right-20, panel.y+68), 1)

        if self.stats:
            r   = self.stats
            al  = "Greedy" if self.algo=='greedy' else "A*"
            rows = [("Algorithm", al),
                    ("Time",      f"{r.time_elapsed:.4f} s"),
                    ("Moves",     str(r.moves)),
                    ("Nodes",     f"{r.nodes_explored:,}"),
                    ("Efficiency",f"{r.nodes_explored/max(r.moves,1):.1f} n/m")]
            for i,(lbl,val) in enumerate(rows):
                y = panel.y + 86 + i*36
                draw_text(self.screen, lbl, cx-180, y, self.fonts['sm'], TEXT_DIM)
                draw_text(self.screen, val, cx+180, y, self.fonts['sm'], WHITE, right=True)

        btns = self._get_rects(W, H)
        draw_button(self.screen, "⟳ Play again", btns['again'], self.fonts['sm'],
                    hover=btns['again'].collidepoint(mouse_pos))
        draw_button(self.screen, "🏠 Menu", btns['menu2'], self.fonts['sm'],
                    hover=btns['menu2'].collidepoint(mouse_pos))


# ══════════════════════════════════════════════════════════════════════════════
# AnalysisScreen
# ══════════════════════════════════════════════════════════════════════════════

ANALYSIS_TABS = ["Overview", "Time", "Moves", "Nodes", "Efficiency", "Map Compare"]
ANALYSIS_SW   = 200   # sidebar width inside analysis

class AnalysisScreen:
    def __init__(self, screen, fonts, cache_data, map_list):
        self.screen   = screen
        self.fonts    = fonts
        self.data     = cache_data
        self.map_list = map_list
        self.result   = None
        self.tab      = 0
        self.cmp_idx  = 0   # selected map for "Map Compare"

        self.sorted_maps = sorted(
            map_list,
            key=lambda nm: cache_data.get(nm[0], {}).get('difficulty', 0)
        )

    # ── helpers ──────────────────────────────────────────────────────────────
    def _avg(self, algo, metric):
        vals = [self.data[n][algo][metric]
                for n,_ in self.map_list
                if n in self.data and algo in self.data[n]
                and self.data[n][algo].get('found')
                and self.data[n][algo].get(metric) is not None]
        return sum(vals)/len(vals) if vals else 0

    def _eff(self, name, algo):
        d = self.data.get(name,{}).get(algo,{})
        if not d.get('found'): return None
        m = d.get('moves',0)
        return round(d.get('nodes',0)/m, 2) if m else None

    # ── events ───────────────────────────────────────────────────────────────
    def handle_event(self, event, mouse_pos):
        if event.type != pygame.MOUSEBUTTONDOWN: return
        W, H = self.screen.get_size()

        if pygame.Rect(10,10,90,34).collidepoint(mouse_pos):
            self.result = ('menu',); return

        for i in range(len(ANALYSIS_TABS)):
            if pygame.Rect(10, 60+i*46, ANALYSIS_SW-20, 38).collidepoint(mouse_pos):
                self.tab = i

        if self.tab == 5:
            content_x = ANALYSIS_SW + 10
            content_w = W - ANALYSIS_SW - 20
            # arrow buttons for map compare
            if pygame.Rect(content_x + 8, 73, 30, 28).collidepoint(mouse_pos):
                self.cmp_idx = (self.cmp_idx-1) % max(1,len(self.map_list))
            if pygame.Rect(content_x + content_w - 38, 73, 30, 28).collidepoint(mouse_pos):
                self.cmp_idx = (self.cmp_idx+1) % max(1,len(self.map_list))

    # ── draw ─────────────────────────────────────────────────────────────────
    def draw(self, mouse_pos):
        W, H = self.screen.get_size()
        self.screen.fill(BG)

        # Sidebar
        draw_sidebar(self.screen, pygame.Rect(0, 0, ANALYSIS_SW, H))
        draw_button(self.screen, "← Back",
                    pygame.Rect(10,10,90,34), self.fonts['sm'],
                    hover=pygame.Rect(10,10,90,34).collidepoint(mouse_pos))
        draw_text(self.screen, "ANALYSIS", ANALYSIS_SW//2, 52,
                  self.fonts['xs'], ACCENT, center=True)

        for i, tab in enumerate(ANALYSIS_TABS):
            r      = pygame.Rect(10, 60+i*46, ANALYSIS_SW-20, 38)
            active = (i == self.tab)
            if active:
                pygame.draw.rect(self.screen, BTN_ACTIVE, r, border_radius=7)
                pygame.draw.rect(self.screen, ACCENT, r, 1, border_radius=7)
            else:
                hover = r.collidepoint(mouse_pos)
                pygame.draw.rect(self.screen, BTN_HOVER if hover else BTN_BG,
                                 r, border_radius=7)
            draw_text(self.screen, tab, r.centerx, r.centery,
                      self.fonts['sm'], WHITE if active else TEXT, center=True)

        # Content
        content_x = ANALYSIS_SW + 10
        content_w = W - ANALYSIS_SW - 20
        funcs = [
            self._draw_overview,
            lambda: self._draw_line_chart('time',  '⏱  Time (normalised per algo)', CHART_G, CHART_A),
            lambda: self._draw_line_chart('moves', '👣  Moves (normalised per algo)', CHART_G, CHART_A),
            lambda: self._draw_line_chart('nodes', '🔵  Nodes (normalised per algo)', CHART_G, CHART_A),
            lambda: self._draw_line_chart('efficiency','⚡  Efficiency nodes/move (normalised)', CHART_G, CHART_A),
            lambda: self._draw_map_compare(mouse_pos),
        ]
        funcs[self.tab]()
        pygame.display.flip()

    # ── tab 0: overview ──────────────────────────────────────────────────────
    def _draw_overview(self):
        W, H  = self.screen.get_size()
        cx    = ANALYSIS_SW + (W - ANALYSIS_SW)//2
        y     = 70

        draw_text(self.screen, "Average statistics across all maps",
                  cx, y, self.fonts['md'], TEXT_BRIGHT, center=True)

        metrics = [
            ("Time (s)",      'time',       True),
            ("Moves",         'moves',      True),
            ("Nodes",         'nodes',      True),
            ("Efficiency n/m",'efficiency', True),
        ]
        col_lbl = ANALYSIS_SW + 20
        col_g   = ANALYSIS_SW + 260
        col_a   = ANALYSIS_SW + 420
        col_bar = ANALYSIS_SW + 560
        bar_max_w = W - col_bar - 30

        y = 105
        # Header
        draw_card(self.screen, pygame.Rect(ANALYSIS_SW+10, y-6, W-ANALYSIS_SW-20, 32),
                  color=(30,30,50))
        draw_text(self.screen, "Metric",     col_lbl, y, self.fonts['xs'], ACCENT)
        draw_text(self.screen, "Greedy",     col_g,   y, self.fonts['xs'], CHART_G)
        draw_text(self.screen, "A*",         col_a,   y, self.fonts['xs'], CHART_A)
        draw_text(self.screen, "Ratio bar",  col_bar, y, self.fonts['xs'], TEXT_DIM)
        y += 36

        for label, metric, lower_better in metrics:
            gv = self._avg('greedy', metric)
            av = self._avg('astar',  metric)
            g_better = (gv <= av) if lower_better else (gv >= av)
            a_better = not g_better if gv != av else True

            draw_card(self.screen,
                      pygame.Rect(ANALYSIS_SW+10, y-4, W-ANALYSIS_SW-20, 34),
                      color=CARD_BG)
            draw_text(self.screen, label, col_lbl, y, self.fonts['sm'], TEXT)

            fmt = (lambda v: f"{v:.4f}") if metric=='time' else (
                  (lambda v: f"{v:.2f}")  if metric=='efficiency' else
                  (lambda v: f"{v:.1f}"))
            gc = SUCCESS if g_better else TEXT
            ac = SUCCESS if a_better else TEXT
            if g_better:
                draw_rect_border(self.screen,
                                 pygame.Rect(col_g-6, y-3, 130, 28), SUCCESS, 1, 6)
            if a_better:
                draw_rect_border(self.screen,
                                 pygame.Rect(col_a-6, y-3, 130, 28), SUCCESS, 1, 6)
            draw_text(self.screen, fmt(gv), col_g, y, self.fonts['sm'], gc)
            draw_text(self.screen, fmt(av), col_a, y, self.fonts['sm'], ac)

            # Ratio bar — normalised so sum = bar_max_w
            total = gv + av
            if total > 0:
                gw = int(bar_max_w * gv / total)
                aw = bar_max_w - gw
                pygame.draw.rect(self.screen, CHART_G,
                                 pygame.Rect(col_bar, y+2, gw, 20), border_radius=3)
                pygame.draw.rect(self.screen, CHART_A,
                                 pygame.Rect(col_bar+gw, y+2, aw, 20), border_radius=3)
                draw_text(self.screen, f"{gv/(total)*100:.0f}%",
                          col_bar+gw//2, y+12, self.fonts['xs'], BG, center=True)
                draw_text(self.screen, f"{av/(total)*100:.0f}%",
                          col_bar+gw+aw//2, y+12, self.fonts['xs'], BG, center=True)
            y += 40

    # ── tabs 1-4: scatter + regression line ──────────────────────────────────
    def _draw_line_chart(self, metric, title, color_g, color_a):
        W, H = self.screen.get_size()
        cx   = ANALYSIS_SW + (W - ANALYSIS_SW) // 2

        draw_text(self.screen, title, cx, 68, self.fonts['md'], TEXT_BRIGHT, center=True)

        ordered = self.sorted_maps
        names   = [n for n, _ in ordered]
        if len(names) < 2:
            draw_text(self.screen, "Need ≥ 2 maps", cx, H // 2,
                      self.fonts['md'], TEXT_DIM, center=True)
            return

        chart_x = ANALYSIS_SW + 70
        chart_y = 100
        chart_w = W - ANALYSIS_SW - 90
        chart_h = H - 230

        # ── Thu thập dữ liệu thô ─────────────────────────────────────────────
        def get_vals(algo):
            if metric == 'efficiency':
                return [self._eff(n, algo) for n in names]
            return [
                self.data.get(n, {}).get(algo, {}).get(metric)
                if self.data.get(n, {}).get(algo, {}).get('found') else None
                for n in names
            ]

        raw_g = get_vals('greedy')
        raw_a = get_vals('astar')

        # X = difficulty (thực nghiệm), Y = giá trị metric
        diff_vals = [self.data.get(n, {}).get('difficulty', 0) for n in names]

        # ── Chuẩn hóa Y độc lập từng algo ───────────────────────────────────
        def normalise(vals):
            clean = [v for v in vals if v is not None]
            if not clean:
                return [None] * len(vals)
            lo, hi = min(clean), max(clean)
            if hi == lo:
                return [0.5 if v is not None else None for v in vals]
            return [(v - lo) / (hi - lo) if v is not None else None for v in vals]

        norm_g = normalise(raw_g)
        norm_a = normalise(raw_a)

        # X chuẩn hóa để vẽ lên chart (diff → pixel)
        diff_clean = [v for v in diff_vals if v is not None]
        diff_lo  = min(diff_clean) if diff_clean else 0
        diff_hi  = max(diff_clean) if diff_clean else 1
        diff_rng = diff_hi - diff_lo if diff_hi != diff_lo else 1

        def diff_to_px(d):
            return int(chart_x + (d - diff_lo) / diff_rng * chart_w)

        def val_to_py(v):
            return int(chart_y + chart_h - v * chart_h)

        # ── Vẽ nền + grid ───────────────────────────────────────────────────
        pygame.draw.rect(self.screen, (20, 20, 36),
                         pygame.Rect(chart_x, chart_y, chart_w, chart_h))
        for k in range(6):
            yp  = chart_y + int(chart_h * k / 5)
            pygame.draw.line(self.screen, CHART_GRID,
                             (chart_x, yp), (chart_x + chart_w, yp), 1)
            lbl = f"{(1 - k/5)*100:.0f}%"
            draw_text(self.screen, lbl, chart_x - 8, yp - 7,
                      self.fonts['xs'], TEXT_DIM, right=True)

        # Axes
        pygame.draw.line(self.screen, CHART_AXIS,
                         (chart_x, chart_y), (chart_x, chart_y + chart_h), 2)
        pygame.draw.line(self.screen, CHART_AXIS,
                         (chart_x, chart_y + chart_h),
                         (chart_x + chart_w, chart_y + chart_h), 2)

        # ── Helper: linear regression trên norm values ────────────────────────
        def poly2_regression(xs, ys):
            """
            Hồi quy bậc 2: y = a*x² + b*x + c
            Dùng phương pháp bình phương tối thiểu (normal equations).
            Trả về (a, b, c) hoặc None nếu không đủ điểm.
            """
            pts = [(x, y) for x, y in zip(xs, ys)
                   if x is not None and y is not None]
            if len(pts) < 3:
                # Fallback bậc 1 nếu ít hơn 3 điểm
                if len(pts) < 2:
                    return None
                n   = len(pts)
                sx  = sum(p[0] for p in pts)
                sy  = sum(p[1] for p in pts)
                sxx = sum(p[0]**2 for p in pts)
                sxy = sum(p[0]*p[1] for p in pts)
                denom = n * sxx - sx * sx
                if abs(denom) < 1e-12:
                    return None
                b1 = (n * sxy - sx * sy) / denom
                b0 = (sy - b1 * sx) / n
                return (0.0, b1, b0)   # a=0 → vẫn dùng chung công thức

            # Normal equations cho bậc 2
            # [S4 S3 S2] [a]   [Sx2y]
            # [S3 S2 S1] [b] = [Sxy ]
            # [S2 S1 S0] [c]   [Sy  ]
            S0  = len(pts)
            S1  = sum(p[0]    for p in pts)
            S2  = sum(p[0]**2 for p in pts)
            S3  = sum(p[0]**3 for p in pts)
            S4  = sum(p[0]**4 for p in pts)
            Sy  = sum(p[1]          for p in pts)
            Sxy = sum(p[0]*p[1]     for p in pts)
            Sx2y= sum(p[0]**2*p[1]  for p in pts)

            # Giải hệ 3×3 bằng Cramer / Gaussian elimination đơn giản
            A = [
                [S4,  S3,  S2,  Sx2y],
                [S3,  S2,  S1,  Sxy ],
                [S2,  S1,  S0,  Sy  ],
            ]
            # Forward elimination
            for col in range(3):
                # Pivot
                max_row = max(range(col, 3), key=lambda r: abs(A[r][col]))
                A[col], A[max_row] = A[max_row], A[col]
                if abs(A[col][col]) < 1e-14:
                    continue
                for row in range(col + 1, 3):
                    factor = A[row][col] / A[col][col]
                    for k in range(col, 4):
                        A[row][k] -= factor * A[col][k]
            # Back substitution
            coeffs = [0.0, 0.0, 0.0]
            for row in range(2, -1, -1):
                if abs(A[row][row]) < 1e-14:
                    coeffs[row] = 0.0
                else:
                    coeffs[row] = (A[row][3] - sum(A[row][j] * coeffs[j]
                                                    for j in range(row+1, 3))) / A[row][row]
            return tuple(coeffs)   # (a, b, c)

        # ── Vẽ scatter + regression cho từng algo ────────────────────────────
        def draw_scatter_regression(norm_vals, raw_vals, color):
            # Scatter points
            scatter_pts = []
            for i, (nv, rv) in enumerate(zip(norm_vals, raw_vals)):
                if nv is None:
                    continue
                px = diff_to_px(diff_vals[i])
                py = val_to_py(nv)
                scatter_pts.append((px, py, i))

                # Vòng ngoài mờ (glow)
                glow = pygame.Surface((22, 22), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*color, 50), (11, 11), 11)
                self.screen.blit(glow, (px - 11, py - 11))
                # Chấm chính
                pygame.draw.circle(self.screen, color, (px, py), 6)
                pygame.draw.circle(self.screen, BG,    (px, py), 3)

            # Regression line
            xs_norm = [(diff_vals[i] - diff_lo) / diff_rng
                       for i, nv in enumerate(norm_vals) if nv is not None]
            ys_norm = [nv for nv in norm_vals if nv is not None]
            reg = poly2_regression(xs_norm, ys_norm)
            if reg:
                a, b, c = reg

                # Tìm điểm cực trị của parabol: x* = -b / (2a)
                # Nếu a > 0 (parabol mở lên): có cực tiểu tại x*
                #   → bên trái x* clamp nằm ngang tại f(x*)
                # Nếu a <= 0 hoặc x* ngoài [0,1]: vẽ bình thường
                if a > 1e-9:
                    x_min = -b / (2 * a)   # đỉnh parabol (cực tiểu)
                else:
                    x_min = None           # không có cực tiểu trong vùng cần xử lý

                SAMPLES   = 120
                curve_pts = []
                for s in range(SAMPLES + 1):
                    t  = s / SAMPLES
                    if x_min is not None and t < x_min:
                        # Bên trái cực tiểu → nằm ngang tại giá trị cực tiểu
                        yv = a * x_min**2 + b * x_min + c
                    else:
                        yv = a * t*t + b * t + c
                    yv   = max(0.0, min(1.0, yv))
                    px_c = int(chart_x + t * chart_w)
                    py_c = val_to_py(yv)
                    curve_pts.append((px_c, py_c))

                # Vẽ nét đứt dọc theo đường cong
                dash_len = 10
                gap_len  = 5
                seg_buf  = 0
                drawing  = True
                for k in range(len(curve_pts) - 1):
                    x0, y0 = curve_pts[k]
                    x1, y1 = curve_pts[k + 1]
                    seg_len = math.hypot(x1 - x0, y1 - y0)
                    remain  = seg_len
                    fx, fy  = float(x0), float(y0)
                    dx = (x1 - x0) / seg_len if seg_len > 0 else 0
                    dy = (y1 - y0) / seg_len if seg_len > 0 else 0
                    while remain > 0:
                        step = (dash_len - seg_buf) if drawing else (gap_len - seg_buf)
                        step = min(step, remain)
                        ex   = fx + dx * step
                        ey   = fy + dy * step
                        if drawing:
                            pygame.draw.line(self.screen, color,
                                             (int(fx), int(fy)),
                                             (int(ex), int(ey)), 2)
                        fx, fy   = ex, ey
                        seg_buf += step
                        remain  -= step
                        target   = dash_len if drawing else gap_len
                        if seg_buf >= target - 0.5:
                            seg_buf = 0
                            drawing = not drawing

                # R² so với đường bậc 2
                ys_pred = [a * x*x + b * x + c for x in xs_norm]
                y_mean  = sum(ys_norm) / len(ys_norm)
                ss_res  = sum((y - yp)**2 for y, yp in zip(ys_norm, ys_pred))
                ss_tot  = sum((y - y_mean)**2 for y in ys_norm)
                r2      = 1 - ss_res / ss_tot if ss_tot > 1e-12 else 1.0
                return r2
            return None

        r2_g = draw_scatter_regression(norm_g, raw_g, color_g)
        r2_a = draw_scatter_regression(norm_a, raw_a, color_a)

        # ── X-axis labels (map names dưới trục) ──────────────────────────────
        for i, name in enumerate(names):
            px   = diff_to_px(diff_vals[i])
            dlbl = self.data.get(name, {}).get('difficulty_label', '')
            diff = self.data.get(name, {}).get('difficulty', '?')
            # Tick
            pygame.draw.line(self.screen, CHART_AXIS,
                             (px, chart_y + chart_h),
                             (px, chart_y + chart_h + 5), 1)
            draw_text(self.screen, name[:7],
                      px, chart_y + chart_h + 8,
                      self.fonts['xs'], TEXT_DIM, center=True)
            draw_text(self.screen, f"d={diff}",
                      px, chart_y + chart_h + 22,
                      self.fonts['xs'], (70, 70, 100), center=True)

        # ── Tooltip hover ─────────────────────────────────────────────────────
        mx, my = pygame.mouse.get_pos()
        if chart_x <= mx <= chart_x + chart_w and chart_y <= my <= chart_y + chart_h:
            nearest = min(
                range(len(names)),
                key=lambda i: abs(diff_to_px(diff_vals[i]) - mx)
            )
            n    = names[nearest]
            graw = raw_g[nearest]
            araw = raw_a[nearest]
            fmt  = ((lambda v: f"{v:.4f}") if metric == 'time' else
                    (lambda v: f"{v:.2f}")  if metric == 'efficiency' else
                    (lambda v: str(int(v))  if v is not None else "N/A"))
            tip  = (f"{n}  |  Greedy: {fmt(graw) if graw is not None else 'N/A'}"
                    f"  ·  A*: {fmt(araw) if araw is not None else 'N/A'}")
            tw   = self.fonts['xs'].size(tip)[0] + 16
            tx   = min(mx + 10, W - tw - 10)
            ty2  = max(chart_y + 4, my - 28)
            draw_card(self.screen,
                      pygame.Rect(tx - 8, ty2 - 4, tw, 26),
                      color=(30, 30, 50), border=ACCENT)
            draw_text(self.screen, tip, tx, ty2, self.fonts['xs'], TEXT_BRIGHT)

        # ── Legend + R² ───────────────────────────────────────────────────────
        lx = chart_x
        ly = chart_y + chart_h + 44

        # Greedy
        pygame.draw.line(self.screen, color_g,
                         (lx, ly + 2), (lx + 22, ly + 2), 2)
        pygame.draw.circle(self.screen, color_g, (lx + 11, ly + 2), 5)
        pygame.draw.circle(self.screen, BG,       (lx + 11, ly + 2), 3)
        r2g_str = f"  R²={r2_g:.2f}" if r2_g is not None else ""
        draw_text(self.screen, f"Greedy{r2g_str}",
                  lx + 28, ly - 5, self.fonts['xs'], color_g)

        # A*
        lx2 = lx + 140
        pygame.draw.line(self.screen, color_a,
                         (lx2, ly + 2), (lx2 + 22, ly + 2), 2)
        pygame.draw.circle(self.screen, color_a, (lx2 + 11, ly + 2), 5)
        pygame.draw.circle(self.screen, BG,       (lx2 + 11, ly + 2), 3)
        r2a_str = f"  R²={r2_a:.2f}" if r2_a is not None else ""
        draw_text(self.screen, f"A*{r2a_str}",
                  lx2 + 28, ly - 5, self.fonts['xs'], color_a)

        draw_text(self.screen, "X = difficulty (log₂ A* nodes)   ·   Y = normalised per algo",
                  cx, ly + 14, self.fonts['xs'], (70, 70, 100), center=True)

    # ── tab 5: map compare ───────────────────────────────────────────────────
    def _draw_map_compare(self, mouse_pos):
        W, H    = self.screen.get_size()
        content_x = ANALYSIS_SW + 10
        content_w = W - ANALYSIS_SW - 20
        cx      = ANALYSIS_SW + (W - ANALYSIS_SW) // 2

        # ── Map selector bar ─────────────────────────────────────────────────
        sel_bar = pygame.Rect(content_x, 65, content_w, 44)
        draw_card(self.screen, sel_bar, color=(28, 28, 48))

        arr_l = pygame.Rect(content_x + 8,  73, 30, 28)
        arr_r = pygame.Rect(content_x + content_w - 38, 73, 30, 28)
        draw_arrow_btn(self.screen, arr_l, 'left',  self.fonts['sm'],
                       hover=arr_l.collidepoint(mouse_pos))
        draw_arrow_btn(self.screen, arr_r, 'right', self.fonts['sm'],
                       hover=arr_r.collidepoint(mouse_pos))

        name, path = self.map_list[self.cmp_idx]
        cpx = self.data.get(name, {}).get('complexity', '?')
        diff = self.data.get(name, {}).get('difficulty', '?')
        dlbl = self.data.get(name, {}).get('difficulty_label', '')
        draw_text(self.screen,
                  f"{name}   |   Difficulty: {diff} ({dlbl})   |   {self.cmp_idx+1} / {len(self.map_list)}",
                  cx, 87, self.fonts['sm'], WHITE, center=True)

        # ── Two-column layout: board left, table right ────────────────────────
        TOP     = 120
        BOT     = H - 20
        half_w  = content_w // 2 - 6
        board_rect = pygame.Rect(content_x,            TOP, half_w, BOT - TOP)
        table_rect = pygame.Rect(content_x + half_w + 12, TOP, half_w, BOT - TOP)

        # Board panel
        draw_card(self.screen, board_rect, color=(20, 20, 36))
        try:
            from utils.map_loader import load_map
            state = load_map(path)
            pad   = 12
            tile  = min(TILE,
                        (board_rect.width  - pad*2) // max(state.width,  1),
                        (board_rect.height - pad*2) // max(state.height, 1))
            ox = board_rect.x + (board_rect.width  - state.width  * tile) // 2
            oy = board_rect.y + (board_rect.height - state.height * tile) // 2
            draw_board(self.screen, state, None, ox, oy, tile)
        except Exception:
            pass

        # Table panel
        draw_card(self.screen, table_rect, color=(20, 20, 36))
        d = self.data.get(name, {})
        metrics = [
            ('Time (s)',       'time'),
            ('Moves',          'moves'),
            ('Nodes',          'nodes'),
            ('Efficiency n/m', 'efficiency'),
        ]

        col_metric = table_rect.x + 12
        col_g      = table_rect.x + table_rect.width * 52 // 100
        col_a      = table_rect.x + table_rect.width * 78 // 100

        # Header
        ty = table_rect.y + 14
        draw_card(self.screen,
                  pygame.Rect(table_rect.x + 6, ty - 4, table_rect.width - 12, 28),
                  color=(30, 30, 52))
        draw_text(self.screen, "Metric", col_metric, ty, self.fonts['xs'], ACCENT)
        draw_text(self.screen, "Greedy", col_g,      ty, self.fonts['xs'], CHART_G)
        draw_text(self.screen, "A*",     col_a,      ty, self.fonts['xs'], CHART_A)
        ty += 34

        for label, metric in metrics:
            gv = (self._eff(name, 'greedy') if metric == 'efficiency'
                  else d.get('greedy', {}).get(metric))
            av = (self._eff(name, 'astar')  if metric == 'efficiency'
                  else d.get('astar',  {}).get(metric))
            gf = d.get('greedy', {}).get('found', False)
            af = d.get('astar',  {}).get('found', False)

            g_better = a_better = False
            if gv is not None and av is not None and gf and af:
                g_better = gv <= av
                a_better = av <= gv

            row_rect = pygame.Rect(table_rect.x + 6, ty - 2,
                                   table_rect.width - 12, 32)
            draw_card(self.screen, row_rect, color=CARD_BG)
            draw_text(self.screen, label, col_metric, ty + 4,
                      self.fonts['sm'], TEXT)

            fmt = ((lambda v: f"{v:.4f}") if metric == 'time' else
                   (lambda v: f"{v:.2f}")  if metric == 'efficiency' else str)

            for cx2, val, found, better in [
                (col_g, gv, gf, g_better),
                (col_a, av, af, a_better),
            ]:
                if not found or val is None:
                    draw_text(self.screen, "N/A", cx2, ty + 4,
                              self.fonts['sm'], DANGER)
                else:
                    if better:
                        draw_rect_border(self.screen,
                                         pygame.Rect(cx2 - 5, ty - 1, 80, 26),
                                         SUCCESS, 1, 5)
                    draw_text(self.screen, fmt(val), cx2, ty + 4,
                              self.fonts['sm'], SUCCESS if better else TEXT)

            # Ratio bar
            if gv and av and gf and af:
                bx  = table_rect.x + 10
                by  = ty + 28
                bw  = table_rect.width - 20
                tot = gv + av
                gw  = int(bw * gv / tot)
                pygame.draw.rect(self.screen, CHART_G,
                                 pygame.Rect(bx,    by, gw,    5), border_radius=2)
                pygame.draw.rect(self.screen, CHART_A,
                                 pygame.Rect(bx+gw, by, bw-gw, 5), border_radius=2)

            ty += 48