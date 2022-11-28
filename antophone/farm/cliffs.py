import pygame
from antophone.farm.ant import Ant


class CliffsEnv:
    size = (12, 4)
    square_size = 48, 48
    actions = {
        'up': (0, -1),
        'down': (0, 1),
        'left': (-1, 0),
        'right': (1, 0),
    }

    def __init__(self):
        self.width, self.height = self.size
        self.reset()

    def reset(self):
        self.agent = (0, 3)
        self.goal = (11, 3)
        self.cliffs = [(i, 3) for i in range(1, 11)]
        self.turn = 0

    def get_state(self):
        state = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
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

    def get_legal_actions(self):
        x, y = self.agent
        return [k for k, v in self.actions.items()
                if 0 <= x + v[0] < self.width
                and 0 <= y + v[1] < self.height]

    def get_reward(self):
        if self.agent == self.goal:
            return 0
        elif self.agent in self.cliffs:
            return -100
        else:
            return -1

    def step(self, action):
        x, y = self.agent
        dx, dy = self.actions[action]
        self.agent = (x + dx, y + dy)
        reward = self.get_reward()
        self.turn += 1
        return self.get_state(), reward, self.is_done
    
    @property
    def is_done(self):
        return self.agent in (self.goal, *self.cliffs) or self.turn > 100

    def render(self):
        sqw, sqh = self.square_size

        if not getattr(self, 'initialized', False):
            pygame.display.set_caption('Ant Farm: Cliffs')
            self.surface = pygame.display.set_mode((self.width * sqw, self.height * sqh))
            self.surface.fill((0, 0, 0))
            self.clock = pygame.time.Clock()
            self.initialized = True

        for y in range(self.height):
            for x in range(self.width):
                x1, y1 = x * sqw, y * sqh
                x2, y2 = x1 + sqw, y1 + sqh
                if (x, y) == self.goal:
                    color = (0, 255, 0)
                elif (x, y) in self.cliffs:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 0) if not self.is_done else (128, 128, 128)

                pygame.draw.rect(self.surface, color, pygame.Rect(x1, y1, x2, y2))
                ax = (self.agent[0] * sqw) + (sqw / 2) - (Ant.img.get_width() / 2)
                ay = (self.agent[1] * sqh) + (sqh / 2) - (Ant.img.get_height() / 2)
                self.surface.blit(Ant.img, (ax, ay))

        pygame.display.update()
        self.clock.tick(60)

    def handle_key(self, event):
        val = None
        moves = self.get_legal_actions()
        if event.key == pygame.K_UP:
            val = self.step('up') if 'up' in moves else None
        elif event.key == pygame.K_DOWN:
            val = self.step('down') if 'down' in moves else None
        elif event.key == pygame.K_RIGHT:
            val = self.step('right') if 'right' in moves else None
        elif event.key == pygame.K_LEFT:
            val = self.step('left') if 'left' in moves else None
        if val:
            print(self.agent, val[1], val[2])
            self.render()
