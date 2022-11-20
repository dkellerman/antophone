import pygame
from functools import cache
from colorsys import hls_to_rgb
from antophone import Instrument, Ant, FIFTHS_LAYOUT


class Game:
    instr = Instrument(slots=FIFTHS_LAYOUT)
    padding = Ant.size

    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode(self.instr.size)
        pygame.display.set_caption('Antophone')
        self.clock = pygame.time.Clock()
        self.instr.add_random_ants(10)
        self.instr.randomize_volumes()

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            for ant in self.instr.ants:
                ant.move()
            self.instr.update()
            self.render()
            pygame.display.update()
            self.clock.tick(60)
        pygame.quit()

    def render(self):
        for x, col in enumerate(self.instr.volumes):
            for y, vol in enumerate(col):
                freq = self.instr.pos_to_freq(x, y) / self.instr.max_freq
                color = self.freq_to_color(freq, vol)
                self.surface.set_at((x, y), color)

        for ant in self.instr.ants:
            x = min(max(self.padding[0], ant.x), self.instr.size[0] - self.padding[0])
            y = min(max(self.padding[1], ant.y), self.instr.size[1] - self.padding[1])
            self.surface.blit(ant.img, (x, y))

    def handle_event(self, event):
        print(event)
        if event.type == pygame.QUIT:
            self.running = False

    @cache
    def freq_to_color(self, freq, vol):
        r, g, b = [int(x * 255) for x in hls_to_rgb(freq, vol, 0.5)]
        return pygame.Color(r, g, b)
