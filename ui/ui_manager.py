import pygame
import sys
from search.a_star import a_star_search
from search.greedy import greedy_search

TILE_SIZE = 64
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class SokobanUI:
    def __init__(self, game):
        pygame.init()
        self.game = game
        self.rows = len(game.map_data)
        self.cols = max(len(row) for row in game.map_data)
        self.screen = pygame.display.set_mode((self.cols * TILE_SIZE, self.rows * TILE_SIZE))
        pygame.display.set_caption("Sokoban AI - Ám Vân")
        self.font = pygame.font.SysFont('Arial', 24)

    def draw_text(self, text, y_offset, color=BLACK):
        text_surf = self.font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(self.cols * TILE_SIZE // 2, self.rows * TILE_SIZE // 2 + y_offset))
        self.screen.blit(text_surf, text_rect)

    def draw_menu(self):
        self.screen.fill(WHITE)
        self.draw_text("CHỌN THUẬT TOÁN", -60, (200, 0, 0))
        self.draw_text("put 'a' to A* search", 0)
        self.draw_text("put 'g' to greedy search", 40)
        pygame.display.flip()

    def run_menu(self):
        """Vòng lặp chính để chọn thuật toán ngay trên giao diện"""
        while True:
            self.draw_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        print("Đang giải bằng A*...")
                        solution = a_star_search(self.game)
                        self.run_solution(solution, "A* Search")
                    elif event.key == pygame.K_g:
                        print("Đang giải bằng Greedy...")
                        solution = greedy_search(self.game)
                        self.run_solution(solution, "Greedy Search")

    def draw_board(self, player_pos, boxes):
        self.screen.fill(WHITE)
        for r in range(self.rows):
            for c in range(len(self.game.map_data[r])):
                x, y = c * TILE_SIZE, r * TILE_SIZE
                pos = (r, c)
                if pos in self.game.walls:
                    pygame.draw.rect(self.screen, (50, 50, 50), (x, y, TILE_SIZE, TILE_SIZE))
                if pos in self.game.goals:
                    pygame.draw.circle(self.screen, (200, 0, 0), (x + TILE_SIZE//2, y + TILE_SIZE//2), 10)
                if pos in boxes:
                    color = (0, 200, 0) if pos in self.game.goals else (139, 69, 19)
                    pygame.draw.rect(self.screen, color, (x+5, y+5, TILE_SIZE-10, TILE_SIZE-10))
                if pos == player_pos:
                    pygame.draw.ellipse(self.screen, (0, 0, 255), (x+5, y+5, TILE_SIZE-10, TILE_SIZE-10))
        pygame.display.flip()

    def run_solution(self, solution, algo_name):
        if not solution:
            print("Không tìm thấy đường đi!")
            return

        pygame.display.set_caption(f"Sokoban - {algo_name}")
        curr_player = self.game.player_pos
        curr_boxes = self.game.boxes
        
        for action in solution:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

            pygame.time.delay(300)
            moves = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1)}
            res = self.game.get_next_state(curr_player, curr_boxes, moves[action])
            if res:
                curr_player, curr_boxes = res
                self.draw_board(curr_player, curr_boxes)