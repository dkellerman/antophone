import pygame
import random


class Ant:
    img = pygame.image.load('images/ant.png')
    size = (img.get_width(), img.get_height())
    moves = ((0, 0), (0, 1), (0, -1), (1, 0), (-1, 0))
    last_move = None
    wildness = .05

    def __init__(self, instr, x, y):
        self.instr = instr
        self.set_loc(x, y)

    def set_loc(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        moves = list(self.moves)
        random.shuffle(moves)
        if self.last_move and (self.last_move != (0, 0)) and (random.random() > self.wildness):
            moves.insert(0, self.last_move)
        for i, (dx, dy) in enumerate(moves):
            x2 = self.x + dx
            y2 = self.y + dy
            if x2 < 0 or x2 >= self.instr.width or y2 < 0 or y2 >= self.instr.height:
                continue
            self.last_move = (dx, dy)
            self.set_loc(x2, y2)
            break
