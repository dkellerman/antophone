import pygame
import random


class Ant:
    img = pygame.image.load('images/ant.png')
    size = (img.get_width(), img.get_height())
    moves = ((0, 0), (0, 1), (0, -1), (1, 0), (-1, 0))
    randomness = .5
    last_move = None

    def __init__(self, instr, x, y):
        self.instr = instr
        self.set_loc(x, y)

    def set_loc(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        legal_moves = [
            m for m in list(self.moves) if
            (self.x + m[0] >= 0) and
            (self.x + m[0] < (self.instr.width - 1)) and
            (self.y + m[1] >= 0) and
            (self.y + m[1] < (self.instr.height - 1))
        ]
        if random.random() < self.randomness:
            move = random.choice(legal_moves)
        else:
            random.shuffle(legal_moves)
            move_scores = dict()
            for dx, dy in legal_moves:
                x2 = self.x + dx
                y2 = self.y + dy
                move_scores[(dx, dy)] = self.instr.volumes[y2][x2]
            move = max(move_scores, key=move_scores.get)
        self.last_move = move
        self.set_loc(self.x + move[0], self.y + move[1])
