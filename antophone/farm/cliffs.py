import pygame
from antophone.farm.ant import Ant


class CliffsEnv:
    size = (12, 4)
    square_size = (48, 48)
    action_map = {
        'up': (0, -1),
        'down': (0, 1),
        'left': (-1, 0),
        'right': (1, 0),
    }

    def __init__(self):
        self.reset()

    def reset(self):
        self.agent = (0, 3)
        self.goal = (11, 3)
        self.cliffs = [(i, 3) for i in range(1, 11)]
        self.turn = 0
        self.last_step = None

    @property
    def state(self):
        state = []
        w, h = self.size
        for y in range(h):
            row = []
            for x in range(w):
                if (x, y) == self.goal:
                    row.append(2)
                elif (x, y) == self.agent:
                    row.append(1)
                elif (x, y) in self.cliffs:
                    row.append(-1)
                else:
                    row.append(0)
            state.append(row)
        return tuple(map(tuple, state))

    @property
    def action_space(self):
        x, y = self.agent
        w, h = self.size
        return [k for k, v in self.action_map.items()
                if 0 <= x + v[0] < w
                and 0 <= y + v[1] < h]

    @property
    def reward(self):
        if self.agent == self.goal:
            return 0
        elif self.agent in self.cliffs:
            return -100
        else:
            return -1

    def step(self, action):
        x, y = self.agent
        dx, dy = self.action_map[action]
        self.agent = (x + dx, y + dy)
        self.turn += 1
        val = self.state, self.reward, self.done
        self.last_step = (action, *val)
        return val

    @property
    def done(self):
        return self.agent in (self.goal, *self.cliffs) or self.turn > 100

    def render(self):
        grid_width, grid_height = self.size
        sq_width, sq_height = self.square_size
        agent_img = Ant.img
        agent_width, agent_height = Ant.size

        if not getattr(self, 'initialized', False):
            pygame.display.set_caption('Ant Farm: Cliffs')
            board_size = (grid_width * sq_width, grid_height * sq_height)
            self.surface = pygame.display.set_mode(board_size)
            self.surface.fill((0, 0, 0))
            self.clock = pygame.time.Clock()
            self.initialized = True

        for y in range(grid_height):
            for x in range(grid_width):
                x1, y1 = x * sq_width, y * sq_height
                x2, y2 = x1 + sq_width, y1 + sq_height
                if (x, y) == self.goal:
                    color = (0, 255, 0)
                elif (x, y) in self.cliffs:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 0) if not self.done else (128, 128, 128)

                pygame.draw.rect(self.surface, color, pygame.Rect(x1, y1, x2, y2))
                ax = (self.agent[0] * sq_width) + (sq_width / 2) - (agent_width / 2)
                ay = (self.agent[1] * sq_height) + (sq_height / 2) - (agent_height / 2)
                self.surface.blit(agent_img, (ax, ay))

        pygame.display.update()
        self.clock.tick(60)

    def handle_key(self, event):
        val = None
        moves = self.action_space

        if event.key == pygame.K_UP:
            val = self.step('up') if 'up' in moves else None
        elif event.key == pygame.K_DOWN:
            val = self.step('down') if 'down' in moves else None
        elif event.key == pygame.K_RIGHT:
            val = self.step('right') if 'right' in moves else None
        elif event.key == pygame.K_LEFT:
            val = self.step('left') if 'left' in moves else None

        if val:
            q = Ant.Q.get((self.last_step[1], self.last_step[0]), 0)
            print(self.turn, self.agent, val[1], val[2], q)
            self.render()
