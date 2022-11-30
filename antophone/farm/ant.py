import os
import pygame
import random
import pprint
import numpy as np
from antophone.utils import rnd_softmax


class Ant:
    img = pygame.image.load(os.path.join(os.path.dirname(__file__), '../../images/ant.png'))
    size = (img.get_width(), img.get_height())
    Q = dict()

    # RL config
    learning_rate = .5
    discount_rate = .99
    antsiness = 0.1
    q_delay = 10
    no_random = False
    use_softmax = False
    log = False

    def __init__(self, env):
        self.env = env

    def update(self):
        state = self.env.state
        action = self.get_next_action(state)
        qval = self.get_qval(state, action)

        observation, reward, done = self.env.step(action)
        if not done:
            next_action = self.get_next_action(observation, antsy=False)
            next_qval = self.get_qval(observation, next_action)
        else:
            next_qval = 0

        discount = self.discount_rate ** self.env.turn
        self.Q[(state, action)] = qval + (self.learning_rate * (
            reward + ((discount * next_qval) - qval)
        ))

        return done, reward

    def get_next_action(self, state, antsy=True):
        actions = self.env.action_space

        if self.log and getattr(self.env, 'last_step', None):
            self.log_qvals()

        if (antsy
            and (not self.no_random)
            and (random.random() <= self.antsiness)
            and (self.env.turn > self.q_delay)
            ):
            action = random.choice(actions)
        else:
            scores = [self.get_qval(state, a) for a in actions]
            if self.use_softmax:
                score = rnd_softmax(scores)
            else:
                score = max(scores)
            action = actions[scores.index(score)]
        return action

    def get_qval(self, state, action):
        return self.Q.get((state, action), 0)

    def log_qvals(self):
        '''log action values from current state'''
        vals = dict()
        for a in self.env.action_space:
            vals[a] = self.get_qval(self.env.state, a)
        last = self.env.last_step
        q = self.Q.get((last[1], last[0]), 0)
        print('\n', self.env.turn, self.env.agent, last[2], last[3], q)
        pprint.pprint(vals)
