"""Vòng lặp chính."""
import pygame, sys
from ui.colors import *
from ui.screens import MenuScreen, GameScreen, AnalysisScreen

def build_fonts():
    pygame.font.init()
    try:
        return {
            'xs':  pygame.font.SysFont("segoeui", 13),
            'sm':  pygame.font.SysFont("segoeui", 17),
            'md':  pygame.font.SysFont("segoeui", 21, bold=True),
            'lg':  pygame.font.SysFont("segoeui", 28, bold=True),
            'xl':  pygame.font.SysFont("segoeui", 42, bold=True),
            'xxl': pygame.font.SysFont("segoeui", 56, bold=True),
        }
    except Exception:
        return {k: pygame.font.Font(None, s) for k, s in
                [('xs',15),('sm',19),('md',24),('lg',32),('xl',48),('xxl',64)]}

class SokobanApp:
    W, H = 960, 680
    FPS  = 60

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("Sokoban AI")
        self.clock  = pygame.time.Clock()
        self.fonts  = build_fonts()

        from utils.map_loader import get_map_list
        self.map_list   = get_map_list()
        self.cache_data = {}
        self.current_screen = MenuScreen(self.screen, self.fonts, self.map_list)

    def _load_cache(self):
        from utils.stats_cache import load_or_build_cache
        self.cache_data = load_or_build_cache(self.map_list)

    def run(self):
        import threading
        threading.Thread(target=self._load_cache, daemon=True).start()

        while True:
            dt        = self.clock.tick(self.FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self.current_screen.screen = self.screen
                self.current_screen.handle_event(event, mouse_pos)

            if isinstance(self.current_screen, GameScreen):
                self.current_screen.update(dt)

            result = getattr(self.current_screen, 'result', None)
            if result:
                self.current_screen.result = None
                self._transition(result)

            self.current_screen.draw(mouse_pos)

    def _transition(self, result):
        action = result[0]
        if action == 'play':
            _, path, algo = result
            self.current_screen = GameScreen(self.screen, self.fonts, path, algo)
        elif action == 'menu':
            self.current_screen = MenuScreen(self.screen, self.fonts, self.map_list)
        elif action == 'analysis':
            self.current_screen = AnalysisScreen(
                self.screen, self.fonts, self.cache_data, self.map_list)