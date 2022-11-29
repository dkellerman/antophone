import os
import pygame
import random


class Ant:
    img = pygame.image.load(os.path.join(os.path.dirname(__file__), '../../images/ant.png'))
    size = (img.get_width(), img.get_height())
    Q = dict()
    learning_rate = .5
    discount_rate = .99
    antsiness = 0.1
    no_random = False

    def __init__(self, env):
        self.env = env

    def update(self):
        state = self.env.state
        action = self.get_policy_action(state)
        qval = self.get_qval(state, action)

        observation, reward, done = self.env.step(action)
        next_action = self.get_policy_action(observation, antsy=False)
        next_qval = self.get_qval(observation, next_action)
        discount = self.discount_rate ** self.env.turn

        self.Q[(state, action)] = qval + (self.learning_rate * (
            reward + ((discount * next_qval) - qval)
        ))

        return done, reward

    def get_policy_action(self, state, antsy=True):
        actions = self.env.action_space
        if antsy and (not self.no_random) and (random.random() <= self.antsiness):
            action = random.choice(actions)
        else:
            scores = [self.get_qval(state, a) for a in actions]
            action = actions[scores.index(max(scores))]

        return action

    @classmethod
    def get_qval(cls, state, action):
        return cls.Q.get((state, action), 0)
