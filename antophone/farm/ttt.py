import pygame
import random
from enum import Enum
from antophone.utils import draw_border_rect
from antophone.farm.ant import Ant

Tile = Enum('Tile', ['BLANK', 'X', 'O'])


class TTTEnv:
    title = 'Ant Farm - Tic Tac Toe'
    square_size = (128, 128)

    def __init__(self, size=3, opponent=None):
        self.size = size
        self.opponent = opponent
        self.font = pygame.font.SysFont(None, 64)
        self.win_slots = [[(x, y) for y in range(self.size)] for x in range(self.size)]
        self.win_slots += [[(x, y) for x in range(self.size)] for y in range(self.size)]
        self.win_slots += [[(i, i) for i in range(self.size)]]
        self.win_slots += [[(self.size - i - 1, i) for i in range(self.size)]]
        self.reset()

    def reset(self):
        self.agent = random.choice([Tile.X, Tile.O])
        self.player2 = Tile.O if self.agent == Tile.X else Tile.X
        self.turn = 0
        self.grid = [[Tile.BLANK for _ in range(self.size)] for _ in range(self.size)]
        if random.random() > .5:
            self.opponent_move()

    @property
    def state(self):
        return tuple(map(tuple, self.grid))

    @property
    def action_space(self):
        empty = []
        for y in range(self.size):
            for x in range(self.size):
                if self.grid[y][x] == Tile.BLANK:
                    empty.append((x, y))
        return tuple(empty)

    @property
    def winner(self):
        winner = None
        for slots in self.win_slots:
            vals = [self.grid[y][x] for x, y in slots]
            if all(v == vals[0] and (v != Tile.BLANK) for v in vals):
                winner = vals[0]
                break
        return winner

    @property
    def reward(self):
        winner = self.winner
        if winner == self.agent:
            return 100
        elif winner == self.player2:
            return -100
        elif self.full:
            return 1
        else:
            return 0

    def step(self, action):
        x, y = action
        self.grid[y][x] = self.agent
        self.turn += 1
        if not self.done:
            self.opponent_move()
        val = self.state, self.reward, self.done
        self.last_step = (action, *val)
        return val

    def opponent_move(self):
        if not self.opponent:
            return None, None
        x, y = self.opponent.get_next_action(self.state)
        self.grid[y][x] = self.player2
        return x, y

    @property
    def full(self):
        for y in range(self.size):
            for x in range(self.size):
                if self.grid[y][x] == Tile.BLANK:
                    return False
        return True

    @property
    def done(self):
        return self.winner or self.full

    def render(self):
        sq_width, sq_height = self.square_size

        if not getattr(self, 'initialized', False):
            pygame.display.set_caption(self.title)
            board_size = (self.size * sq_width, self.size * sq_height)
            self.surface = pygame.display.set_mode(board_size)
            self.surface.fill((0, 0, 0))
            self.clock = pygame.time.Clock()
            self.initialized = True

        for y in range(self.size):
            for x in range(self.size):
                x1, y1 = x * sq_width, y * sq_height
                x2, y2 = x1 + sq_width, y1 + sq_height
                square = pygame.Rect(x1, y1, x2, y2)

                if self.grid[y][x] == self.agent:
                    img = self.font.render(self.agent.name, True, (255, 255, 255))
                elif self.grid[y][x] == self.player2:
                    img = self.font.render(self.player2.name, True, (255, 0, 0))
                else:
                    img = self.font.render('', True, (0, 0, 0))

                bg = (0, 0, 0) if not self.done else (100, 100, 100)
                draw_border_rect(self.surface, bg, (60, 60, 60), square, border=1)

                imgx = (x * sq_width) + (sq_width / 2) - (img.get_width() / 2)
                imgy = (y * sq_height) + (sq_height / 2) - (img.get_height() / 2)
                self.surface.blit(img, (imgx, imgy))

        pygame.display.update()
        self.clock.tick(60)

    def handle_key(self, event):
        val = None
        actions = self.action_space

        if event.unicode.isdigit():
            d = int(event.unicode) - 1
            x, y = d % self.size, d // self.size
            val = self.step((x, y)) if (x, y) in actions else None
            print('* result:', val)

        if val:
            self.render()
