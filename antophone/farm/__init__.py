import pygame
from tqdm import tqdm
import numpy as np
import time
import matplotlib.pyplot as plt
from antophone.utils import rolling_avg
from antophone.farm.cliffs import CliffsEnv, SimpleCliffsEnv
from antophone.farm.ant import Ant

Envs = {
    'simple_cliffs': SimpleCliffsEnv,
    'cliffs': CliffsEnv,
}


class Farm:
    def __init__(self, env_type='simple_cliffs'):
        pygame.init()
        Env = Envs[env_type]
        print(Env)
        self.env = Env((5, 5))
        self.is_user_session = False
        self.running = True

    def train(self, episode_ct=100000, ant_ct=1):
        self.ants = self.make_ants(ant_ct)
        Ant.no_random = False
        self.rewards = []
        for _ in tqdm(range(episode_ct)):
            rtotal = self.run_episode()
            self.rewards.append(rtotal)

    def run_user_session(self):
        self.ants = self.make_ants(1)
        self.env.reset()
        self.env.render()
        Ant.no_random = True
        self.is_user_session = True
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
        self.is_user_session = False

    def run_episode(self, delay=0, render=False):
        self.env.reset()
        done = [False for _ in self.ants]
        rtotal = 0
        while self.running and not all(done):
            for event in pygame.event.get():
                self.handle_event(event)
            for i, ant in enumerate(self.ants):
                d, r = ant.update()
                done[i] = d
                rtotal += r
                if render:
                    self.env.render()
            if render and delay:
                time.sleep(delay)
        return rtotal

    def make_ants(self, n):
        ants = []
        for _ in range(n):
            ant = Ant(self.env)
            ants.append(ant)
        return ants

    def show_training_stats(self):
        y = np.array(self.rewards)
        y = np.average(y.reshape(-1, len(y) // 10), axis=1)
        x = np.arange(len(y)) * 10

        plt.plot(x, y)
        plt.xlabel('episode')
        plt.ylabel('rewards')
        plt.show()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.quit()
        elif self.is_user_session:
            ant = self.ants[0]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PERIOD and not self.env.done:
                    ant.update()
                    self.env.render()
                elif event.key == pygame.K_n:
                    self.env.reset()
                    self.env.render()
                elif event.key == pygame.K_s:
                    self.show_training_stats()
                elif not self.env.done:
                    self.env.handle_key(event)

    def quit(self):
        self.running = False
