import pygame
import time
from functools import cache
from colorsys import hls_to_rgb
from antophone import Instrument, Ant, FIFTHS_LAYOUT


class Game:
    instr = None
    padding = Ant.size
    square_size = (8, 8)
    delay = 0.05
    rnd_ant_ct = 100

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Antophone')
        self.clock = pygame.time.Clock()

    def init_instr(self):
        self.instr = Instrument(slots=FIFTHS_LAYOUT)
        self.instr.add_random_ants(self.rnd_ant_ct)
        # self.instr.randomize_volumes()
        w = self.instr.size[0] * self.square_size[0]
        h = self.instr.size[1] * self.square_size[1]
        self.surface = pygame.display.set_mode((w, h))
        return self.instr

    def run(self):
        self.running = True
        self.init_instr()
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.instr.update()
            for ant in self.instr.ants:
                ant.move()
            self.render()
            pygame.display.update()
            time.sleep(self.delay)
            self.clock.tick(60)
        pygame.quit()

    def render(self):
        sw, sh = self.surface.get_width(), self.surface.get_height()
        sqw, sqh = self.square_size
        for x, col in enumerate(self.instr.volumes):
            for y, vol in enumerate(col):
                freq = self.instr.pos_to_freq(x, y) / self.instr.max_freq
                color = self.freq_to_color(freq, vol)
                x1, y1 = x * sqw, y * sqh
                x2, y2 = x1 + sqw, y1 + sqh
                pygame.draw.rect(self.surface, color, pygame.Rect(x1, y1, x2, y2))

        for ant in self.instr.ants:
            ax, ay = ant.x * sqw, ant.y * sqh
            # x = min(max(self.padding[0], ax), sw - self.padding[0])
            # y = min(max(self.padding[1], ay), sh - self.padding[1])
            x, y = ax, ay
            self.surface.blit(ant.img, (x, y))

    def handle_event(self, event):
        print(event)
        if event.type == pygame.QUIT:
            self.running = False

    @cache
    def freq_to_color(self, freq, vol):
        r, g, b = [int(x * 255) for x in hls_to_rgb(freq, vol, 0.5)]
        return pygame.Color(r, g, b)
