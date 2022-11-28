import numpy as np
import os
import pygame
import random


class Ant:
    img = pygame.image.load(os.path.join(os.path.dirname(__file__), '../../images/ant.png'))
    size = (img.get_width(), img.get_height())
    Q = dict()
    learning_rate = .5
    discount_rate = .9
    no_random = False

    def __init__(self, env):
        self.env = env

    def update(self):
        state = self.env.get_state()
        action = self.get_action(state)
        qval = self.get_qval(state, action)

        next_state, reward, done = self.env.step(action)
        if done:
            return done

        next_action = self.get_action(next_state)
        next_qval = self.get_qval(next_state, next_action)
        discount = 1 - (self.discount_rate ** self.env.turn)

        self.Q[(state, action)] = qval + (self.learning_rate * (
            reward + ((discount * next_qval) - qval)
        ))

        return done

    def get_action(self, state):
        legal_actions = self.env.get_legal_actions()
        antsiness = 0 if self.no_random else .5

        if random.random() < antsiness:
            action = random.choice(legal_actions)
        else:
            action_scores = [self.Q.get((state, a), 0) for a in legal_actions]
            choice = max(action_scores)
            action = legal_actions[action_scores.index(choice)]

        return action

    def get_qval(self, state, action):
        return self.Q.get((state, action), 0)
