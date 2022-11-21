import sys
import time
import threading
import pygame
import pyo
from functools import cache
from colorsys import hls_to_rgb
from antophone import Instrument, Ant


class Game:
    instr = None
    base_square_size = Ant.size
    zoom = 1
    initial_ant_count = 1
    frame_rate = 60
    bg_color = (0, 0, 0)
    delay = .1
    instr_copies = 3

    @property
    def square_size(self):
        return self.base_square_size[0] * self.zoom, self.base_square_size[1] * self.zoom

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Antophone')
        self.clock = pygame.time.Clock()
        self.audio_server = pyo.Server().boot()

    def init_instr(self):
        self.audio_server.start()
        self.instr = Instrument(copies=self.instr_copies)
        self.render_surface()
        self.instr.add_random_ants(self.initial_ant_count)
        self.instr.start()

    def run(self):
        self.running = True
        self.init_instr()

        # instrument/ant thread
        self.engine_thread = threading.Thread(target=self.run_engine)
        self.engine_thread.start()

        # gui thread
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.render()
            pygame.display.update()
            self.clock.tick(self.frame_rate)
        self.quit()

    def quit(self):
        self.running = False
        self.engine_running = False
        self.instr.stop()
        self.audio_server.shutdown()
        pygame.quit()
        sys.exit()

    def run_engine(self):
        self.engine_running = True
        while self.engine_running:
            for ant in self.instr.ants:
                ant.move()
            self.instr.update()
            time.sleep(self.delay)

    def render(self):
        sqw, sqh = self.square_size
        self.surface.fill(self.bg_color)

        for y in range(self.instr.height):
            for x in range(self.instr.width):
                freq = self.instr.freqs[y][x] / self.instr.max_freq
                vol = self.instr.volumes[y][x]
                color = self.freq_to_color(freq, vol)
                x1, y1 = x * sqw, y * sqh
                x2, y2 = x1 + sqw, y1 + sqh
                pygame.draw.rect(self.surface, color, pygame.Rect(x1, y1, x2, y2))

        for ant in self.instr.ants:
            ax = (ant.x * sqw) + (sqw / 2) - (ant.img.get_width() / 2)
            ay = (ant.y * sqh) + (sqh / 2) - (ant.img.get_height() / 2)
            self.surface.blit(ant.img, (ax, ay))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                if event.mod & pygame.KMOD_SHIFT:
                    self.instr.remove_random_ants(1)
                else:
                    self.instr.add_random_ants(1)
            elif event.key == pygame.K_c:
                self.instr.ants = []
            elif event.key == pygame.K_z:
                if event.mod & pygame.KMOD_SHIFT:
                    self.zoom = max(self.zoom - 1, 1)
                else:
                    self.zoom = min(self.zoom + 1, 5)
                self.render_surface()

    def render_surface(self):
        sqw, sqh = self.square_size
        self.surface = pygame.display.set_mode((self.instr.width * sqw, self.instr.height * sqh))
        return self.surface

    @cache
    def freq_to_color(self, freq, vol):
        r, g, b = [min(255, int(x * 255)) for x in hls_to_rgb(freq, (vol ** 2), 0.5)]
        return pygame.Color(r, g, b)
