import pygame
import numpy as np
import random
import time
from antophone.farm.ant import Ant


class Farm:
    def __init__(self):
        pass

    def train(self):
        self.board = Board(12, 4)
        self.ants = self.make_ants(self.board, 1)

        pygame.init()
        pygame.display.set_caption('Ant Farm')
        sqw, sqh = 48, 48
        self.surface = pygame.display.set_mode((self.board.width * sqw, self.board.height * sqh))
        self.surface.fill((50, 50, 50))
        clock = pygame.time.Clock()

        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            for ant in self.ants:
                ant.update()
                self.board.render(self.ants, self.surface, sqw, sqh)
            pygame.display.update()
            time.sleep(.1)
            clock.tick(60)

    def make_ants(self, board, n):
        ants = []
        for _ in range(n):
            x = random.randint(0, board.width - 1)
            y = random.randint(0, board.height - 1)
            ant = Ant(board, (x, y))
            ants.append(ant)
        return ants

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.quit()

    def quit(self):
        self.running = False


class Board:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.grid = np.zeros((height, width), dtype=np.float32)
        self.place_food()

    def get_state(self, ant):
        state = np.array(self.grid)
        state[ant.loc] = 2

    def get_legal_actions(self, ant):
        x, y = ant.loc
        return [
            a for a in list(ant.actions) if
            (x + a[0] >= 0) and
            (x + a[0] < (self.width)) and
            (y + a[1] >= 0) and
            (y + a[1] < (self.height))
        ]

    def render(self, ants, surface, sqw, sqh):
        surface.fill((0, 0, 0))
        for y, row in enumerate(self.grid):
            for x, _ in enumerate(row):
                x1, y1 = x * sqw, y * sqh
                x2, y2 = x1 + sqw, y1 + sqh
                fx, fy = self.food
                if fx == x and fy == y:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 0)
                pygame.draw.rect(surface, color, pygame.Rect(x1, y1, x2, y2))

        for ant in ants:
            ax = (ant.loc[0] * sqw) + (sqw / 2) - (ant.img.get_width() / 2)
            ay = (ant.loc[1] * sqh) + (sqh / 2) - (ant.img.get_height() / 2)
            surface.blit(ant.img, (ax, ay))

    def place_food(self):
        self.food = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))

    def update(self, ant):
        if ant.loc == self.food:
            self.place_food()
