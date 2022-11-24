import numpy as np
import pygame
import random
from antophone.config import Config

C = Config.ant


class Ant:
    img = pygame.image.load(C.img)
    size = (img.get_width(), img.get_height())
    last_move = None

    def __init__(self, instr, x, y):
        self.instr = instr
        self.set_loc(x, y)

    def set_loc(self, x, y):
        self.x = x
        self.y = y

    def move(self, update_instr=True):
        legal_moves = [
            m for m in list(C.moves) if
            (self.x + m[0] >= 0) and
            (self.x + m[0] < (self.instr.width)) and
            (self.y + m[1] >= 0) and
            (self.y + m[1] < (self.instr.height))
        ]

        antsiness = self.instr.dissonance / 100.0
        if random.random() < antsiness:
            move = random.choice(legal_moves)
        else:
            random.shuffle(legal_moves)
            move_scores = dict()
            for dx, dy in legal_moves:
                x2 = self.x + dx
                y2 = self.y + dy
                move_scores[(dx, dy)] = self.instr.volumes[y2][x2]
            scores = list(move_scores.values())
            if sum(scores) == 0:
                move = random.choice(legal_moves)
            else:
                val = np.random.choice(scores, p=[s/sum(scores) for s in scores])
                move = list(move_scores.keys())[scores.index(val)]

        dx, dy = move
        self.set_loc(self.x + dx, self.y + dy)
        self.last_move = move

        if update_instr:
            self.update_instr()

    def update_instr(self):
        impact = C.weight
        if self.last_move == (0, 0):
            impact *= C.weight_decay
        self.instr.touch(self.x, self.y, impact)
