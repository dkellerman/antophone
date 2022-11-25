import numpy as np
import pygame
import random
from antophone.config import Config

C = Config.ant


class Ant:
    img = pygame.image.load(C.img)
    size = (img.get_width(), img.get_height())
    G = dict()

    def __init__(self, instr, x, y):
        self.instr = instr
        self.steps = 0
        self.last_action = None
        self.set_loc(x, y)

    def set_loc(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        state = self.get_state()

        legal_actions = [
            a for a in list(C.actions) if
            (self.x + a[0] >= 0) and
            (self.x + a[0] < (self.instr.width)) and
            (self.y + a[1] >= 0) and
            (self.y + a[1] < (self.instr.height))
        ]

        antsiness = C.base_antsiness + (self.instr.dissonance / 1000.0)

        if random.random() < antsiness:
            action = random.choice(legal_actions)
        else:
            random.shuffle(legal_actions)
            action_scores = np.zeros(len(legal_actions))
            for i, (dx, dy) in enumerate(legal_actions):
                try_action = (self.x + dx, self.y + dy)
                action_scores[i] = self.get_expected_reward(state, try_action)

            action = legal_actions[np.argmax(action_scores)]

        dx, dy = action
        self.set_loc(self.x + dx, self.y + dy)
        self.update_instr()

        # update rewards table
        reward = self.get_current_reward()
        print('\t', reward)
        self.update_rewards(state, action, reward)

        self.last_action = action
        self.steps += 1

    def update_instr(self):
        impact = C.weight
        if self.last_action == (0, 0):
            impact *= C.weight_decay
        self.instr.touch(self.x, self.y, impact)

    def get_state(self):
        state = []
        for y in range(self.instr.height):
            row = []
            for x in range(self.instr.width):
                if (x, y) == (self.x, self.y):
                    row.append(2)
                row.append(1 if self.instr.volumes[y][x] > 0 else 0)
            state.append(tuple(row))
        return tuple(state)

    def update_rewards(self, state, action, reward):
        expected_reward = self.get_expected_reward(state, action)
        self.G[(state, action)] += (C.learning_rate * (reward - expected_reward))

    def get_expected_reward(self, state, action):
        sa = (state, action)
        if self.G.get(sa, None) is None:
            self.G[sa] = np.random.uniform(high=1.0, low=.1)
        return self.G[sa]

    def get_current_reward(self):
        return max(0, (20.0 - (self.instr.dissonance))) # + self.instr.volumes[self.y][self.x]
