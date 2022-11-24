import numpy as np
import pygame
import random
from antophone.config import Config as C


class Ant:
    img = pygame.image.load(C.ant_img)
    size = (img.get_width(), img.get_height())
    last_move = None

    def __init__(self, instr, x, y):
        self.instr = instr
        self.set_loc(x, y)

    def set_loc(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        legal_moves = [
            m for m in list(C.ant_moves) if
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

        self.last_move = move
        self.set_loc(self.x + move[0], self.y + move[1])
