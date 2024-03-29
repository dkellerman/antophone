import pygame
import random
from functools import cache
from antophone.utils import draw_border_rect
from antophone.farm.ant import Ant


class CliffsEnv:
    title = 'Ant Farm - Cliffs'
    square_size = (32, 32)
    action_map = {
        'up': (0, -1),
        'down': (0, 1),
        'left': (-1, 0),
        'right': (1, 0),
    }

    def __init__(self, size=(12, 4)):
        self.size = size
        self.font = pygame.font.SysFont(None, 24)
        self.reset()

    def reset(self):
        w, h = self.size
        self.agent = (0, 0)
        self.goal = (w - 1, h - 1)
        around_agent = [(self.agent[0] + dx, self.agent[1] + dy)
                        for dx, dy in self.action_map.values()]
        around_goal = [(self.goal[0] + dx, self.goal[1] + dy)
                       for dx, dy in self.action_map.values()]
        self.walls = []
        self.cliffs = []
        for x in range(0, w):
            for y in range(0, h):
                sq = (x, y)
                if (sq != self.agent) and (sq != self.goal) and (sq not in around_agent) \
                        and (sq not in around_goal):
                    if random.random() < .05:
                        self.cliffs.append(sq)
                    elif random.random() < .1:
                        self.walls.append(sq)
        self.walls = tuple(self.walls)
        self.cliffs = tuple(self.cliffs)
        self.turn = 0
        self.last_step = None

    @property
    def state(self):
        state = []
        w, h = self.size
        for y in range(h):
            row = []
            for x in range(w):
                sq = (x, y)
                if sq == self.goal:
                    row.append(2)
                elif sq == self.agent:
                    row.append(3)
                elif sq in self.walls:
                    row.append(1)
                elif sq in self.cliffs:
                    row.append(-1)
                else:
                    row.append(0)
            state.append(row)
        return tuple(map(tuple, state))

    @property
    def action_space(self):
        x, y = self.agent
        w, h = self.size
        actions = []
        for k, v in self.action_map.items():
            nx, ny = x + v[0], y + v[1]
            if (0 <= nx < w) and (0 <= ny < h) and ((nx, ny) not in self.walls):
                actions.append(k)
        return tuple(actions)

    @property
    def reward(self):
        if self.agent == self.goal:
            return 0
        elif self.agent in self.cliffs:
            return -100
        else:
            return -1

    @property
    def done(self):
        return self.agent in (self.goal, *self.cliffs) or self.turn > 200

    def step(self, action):
        x, y = self.agent
        dx, dy = self.action_map[action]
        self.agent = (x + dx, y + dy)
        self.turn += 1
        val = self.state, self.reward, self.done
        self.last_step = (action, *val)

        return val

    def render(self):
        grid_width, grid_height = self.size
        sq_width, sq_height = self.square_size
        agent_img = Ant.img
        agent_width, agent_height = Ant.size

        if not getattr(self, 'initialized', False):
            pygame.display.set_caption(self.title)
            board_size = (grid_width * sq_width, grid_height * sq_height)
            self.surface = pygame.display.set_mode(board_size)
            self.surface.fill((0, 0, 0))
            self.clock = pygame.time.Clock()
            self.initialized = True

        for y in range(grid_height):
            for x in range(grid_width):
                x1, y1 = x * sq_width, y * sq_height
                x2, y2 = x1 + sq_width, y1 + sq_height
                square = pygame.Rect(x1, y1, x2, y2)

                if (x, y) == self.goal:
                    color = (0, 255, 0)
                elif (x, y) in self.cliffs:
                    color = (255, 0, 0)
                elif (x, y) in self.walls:
                    color = (100, 100, 100)
                else:
                    color = (0, 0, 0) if not self.done else (128, 128, 128)

                draw_border_rect(self.surface, color, (60, 60, 60), square, border=1)

                ax = (self.agent[0] * sq_width) + (sq_width / 2) - (agent_width / 2)
                ay = (self.agent[1] * sq_height) + (sq_height / 2) - (agent_height / 2)
                self.surface.blit(agent_img, (ax, ay))

        pygame.display.update()
        self.clock.tick(60)

    def handle_key(self, event):
        val = None
        actions = self.action_space

        if event.key == pygame.K_UP:
            val = self.step('up') if 'up' in actions else None
        elif event.key == pygame.K_DOWN:
            val = self.step('down') if 'down' in actions else None
        elif event.key == pygame.K_RIGHT:
            val = self.step('right') if 'right' in actions else None
        elif event.key == pygame.K_LEFT:
            val = self.step('left') if 'left' in actions else None

        if val:
            self.render()


class SimpleCliffsEnv(CliffsEnv):
    title = 'Ant Farm - Simple Cliffs'

    def reset(self):
        self.size = (10, 4)
        super().reset()
        w, h = self.size
        self.agent = (0, h - 1)
        self.goal = (w - 1, h - 1)
        self.cliffs = [(x, h - 1) for x in range(1, w - 1)]
        self.walls = []
