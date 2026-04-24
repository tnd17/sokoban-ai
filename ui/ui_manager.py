import pygame
import sys
from search.search_algo import a_star_search, greedy_search
from state.state import State

TILE_SIZE = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (50, 150, 255)
YELLOW = (255, 215, 0)
GREEN = (46, 204, 113)
RED = (231, 76, 60)

class SokobanUI:
    def __init__(self, game):
        pygame.init()
        self.game = game
        self.rows = len(game.map_data)
        self.cols = max(len(row) for row in game.map_data)
        self.screen = pygame.display.set_mode((self.cols * TILE_SIZE, self.rows * TILE_SIZE + 50))
        pygame.display.set_caption("Sokoban AI: A* vs Greedy - Am Van")
        self.font = pygame.font.SysFont(None, 24)

    def draw_board(self, player_pos, boxes, info_text=""):
        self.screen.fill(WHITE)
        # Vẽ bản đồ
        for r in range(self.rows):
            for c in range(len(self.game.map_data[r])):
                x, y = c * TILE_SIZE, r * TILE_SIZE
                pos = (r, c)
                if pos in self.game.walls:
                    pygame.draw.rect(self.screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE))
                if pos in self.game.goals:
                    pygame.draw.circle(self.screen, RED, (x + TILE_SIZE//2, y + TILE_SIZE//2), TILE_SIZE//4, 2)
                if pos in boxes:
                    color = GREEN if pos in self.game.goals else YELLOW
                    pygame.draw.rect(self.screen, color, (x+5, y+5, TILE_SIZE-10, TILE_SIZE-10))
                if pos == player_pos:
                    pygame.draw.ellipse(self.screen, BLUE, (x+10, y+10, TILE_SIZE-20, TILE_SIZE-20))
        
        # Vẽ dòng chữ hướng dẫn ở dưới cùng
        info_surf = self.font.render(info_text, True, BLACK)
        self.screen.blit(info_surf, (10, self.rows * TILE_SIZE + 15))
        pygame.display.flip()

    def run(self):
        initial_state = State(self.game.player_pos, self.game.boxes)
        running = True
        msg = "Press 'A' for A* | 'G' for Greedy"

        while running:
            self.draw_board(self.game.player_pos, self.game.boxes, msg)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    path = None
                    if event.key == pygame.K_a:
                        msg = "Running A*..."
                        self.draw_board(self.game.player_pos, self.game.boxes, msg)
                        path, nodes = a_star_search(self.game, initial_state)
                        algo = "A*"
                    elif event.key == pygame.K_g:
                        msg = "Running Greedy..."
                        self.draw_board(self.game.player_pos, self.game.boxes, msg)
                        path, nodes = greedy_search(self.game, initial_state)
                        algo = "Greedy"

                    if path:
                        msg = f"{algo}: {len(path)} steps | {nodes} nodes"
                        self.animate_solution(path, msg)
                    else:
                        msg = "No solution found!"

    def animate_solution(self, path, final_msg):
        curr_p = self.game.player_pos
        curr_b = self.game.boxes
        
        for action in path:
            pygame.time.delay(200)
            moves = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1)}
            res = self.game.get_next_state(curr_p, set(curr_b), moves[action])
            if res:
                curr_p, curr_b = res
                self.draw_board(curr_p, curr_b, final_msg)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()