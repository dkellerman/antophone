import pygame
import random


class SnakeEnv:
    title = 'Ant Farm - Snake'
    square_size = (32, 32)
    action_map = {
        'up': (0, -1),
        'down': (0, 1),
        'left': (-1, 0),
        'right': (1, 0),
    }

    def __init__(self, size=(10, 10)):
        self.size = size
        self.reset()

    def reset(self):
        w, h = self.size
        self.snake = [(w // 4, h // 4)]
        # self.place_food()
        self.turn = 0
        self.last_step = None
        # self.health = 100

    # def place_food(self):
    #     loc = None
    #     while loc is None or loc in self.snake:
    #         loc = (random.randint(0, self.size[0] - 1), random.randint(0, self.size[1] - 1))
    #     self.food = loc

    @property
    def state(self):
        state = []
        w, h = self.size
        for y in range(h):
            row = []
            for x in range(w):
                sq = (x, y)
                # if sq == self.food:
                #     row.append(2)
                if sq in self.snake:
                    row.append(1)
                else:
                    row.append(0)
            state.append(row)
        return tuple(map(tuple, state))

    action_space = ['up', 'down', 'left', 'right']

    @property
    def reward(self):
        # if self.head == self.food:
        #     return 100
        if self.done:
            if self.full:
                return 100
            else:
                return -100
        else:
            return 1

    @property
    def head(self):
        return self.snake[-1]

    @property
    def full(self):
        return len(self.snake) == self.size[0] * self.size[1]

    @property
    def done(self):
        w, h = self.size
        x, y = self.head
        return x < 0 or x >= w or y < 0 or y >= h or self.head in self.snake[:-1] or self.full
               # or self.health <= 0

    def step(self, action):
        x, y = self.head
        dx, dy = self.action_map[action]
        sq = (x + dx, y + dy)
        self.snake.append(sq)
        # if sq == self.food:
        #     self.place_food()
        #     self.health += 100
        # else:
        if self.turn % 5 != 0:
            self.snake.pop(0)
        # self.health -= 1
        self.turn += 1
        val = self.state, self.reward, self.done
        self.last_step = (action, *val)
        return val

    def render(self):
        grid_width, grid_height = self.size
        sq_width, sq_height = self.square_size

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

                # if (x, y) == self.food:
                #     color = (255, 0, 0)
                if (x, y) in self.snake:
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 0) if not self.done else (128, 128, 128)

                pygame.draw.rect(self.surface, color, square)

        pygame.display.update()
        self.clock.tick(60)

    def handle_key(self, event):
        val = None

        if event.key == pygame.K_UP:
            val = self.step('up')
        elif event.key == pygame.K_DOWN:
            val = self.step('down')
        elif event.key == pygame.K_RIGHT:
            val = self.step('right')
        elif event.key == pygame.K_LEFT:
            val = self.step('left')
        if val:
            self.render()

    @property
    def agent(self):
        return self.snake
