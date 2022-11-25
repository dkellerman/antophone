import numpy as np
import pygame
import random
from antophone.config import Config

C = Config.ant


class Ant:
    img = pygame.image.load(C.img)
    size = (img.get_width(), img.get_height())
    actions = (
        (0, 0), (0, 1), (0, -1), (1, 0), (-1, 0),
        (1, 1), (1, -1), (-1, 1), (-1, -1),
    )
    G = dict()

    def __init__(self, env, loc):
        self.env = env
        self.loc = loc
        self.steps = 0
        self.history = []

    def update(self):
        legal_actions = self.env.get_legal_actions(self)
        action = random.choice(legal_actions)
        dx, dy = action
        self.loc = (self.loc[0] + dx, self.loc[1] + dy)
        self.steps += 1
        self.env.update(self)

        # state = self.env.get_state()
        # legal_actions = self.env.get_legal_actions(self)
        # antsiness = .99 ** self.steps

        # if random.random() < antsiness:
        #     action = random.choice(legal_actions)
        # else:
        #     random.shuffle(legal_actions)
        #     action_scores = np.array([reward for _, reward in legal_actions])
        #     action, reward = legal_actions[np.argmax(action_scores)]

        # self.loc = action(self)
        # expected_reward = self.get_expected_reward(state, action)
        # self.G[(state, action)] += (C.learning_rate * (reward - expected_reward))

        # # self.history.append(action)
        # self.steps += 1
