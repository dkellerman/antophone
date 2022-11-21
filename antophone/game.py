import sys
import time
import threading
from functools import cache
from colorsys import hls_to_rgb
import pygame
import pyo
from antophone import Instrument, Ant

class Game:
    instr = None
    square_size = Ant.size
    initial_ant_count = 1
    frame_rate = 60
    bg_color = (0, 0, 0)
    delay = .1

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Antophone')
        self.clock = pygame.time.Clock()
        self.audio_server = pyo.Server().boot()

    def init_instr(self):
        self.audio_server.start()
        self.instr = Instrument()
        self.instr.add_random_ants(self.initial_ant_count)
        sqw, sqh = self.square_size
        self.surface = pygame.display.set_mode((self.instr.width * sqw, self.instr.height * sqh))

    def run(self):
        self.running = True
        self.init_instr()
        self.engine_thread = threading.Thread(target=self.run_engine)
        self.engine_thread.start()
        
        self.instr.start()
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.render()
            pygame.display.update()
            self.clock.tick(self.frame_rate)
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
        # print(event)
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


    @cache
    def freq_to_color(self, freq, vol):
        r, g, b = [min(255, int(x * 255)) for x in hls_to_rgb(freq, (vol ** 2), 0.5)]
        return pygame.Color(r, g, b)
