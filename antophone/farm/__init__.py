import pygame
from tqdm import tqdm
import numpy as np
import time
import matplotlib.pyplot as plt
from antophone.farm.cliffs import CliffsEnv, SimpleCliffsEnv
from antophone.farm.ttt import TTTEnv
from antophone.farm.ant import Ant

Envs = {
    'simple_cliffs': SimpleCliffsEnv,
    'cliffs': CliffsEnv,
    'ttt': TTTEnv,
}


class Farm:
    def __init__(self, env_type='simple_cliffs'):
        pygame.init()
        Env = Envs[env_type]
        self.env_type = env_type
        self.env = Env()
        self.is_user_session = False

    def train(self, episode_ct=100000, ant_ct=1):
        self.ants = self.make_ants(ant_ct)
        self.env.opponent = self.ants[0]
        Ant.no_random = False
        self.rewards = []
        self.running = True
        for _ in tqdm(range(episode_ct)):
            rtotal = self.run_episode()
            self.rewards.append(rtotal)

    def run_user_session(self):
        self.ants = self.make_ants(1)
        self.env.opponent = self.ants[0]
        self.env.reset()
        self.env.render()
        Ant.no_random = True
        Ant.log = True
        self.is_user_session = True
        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
        self.is_user_session = False
        if getattr(self, 'on_stop', None):
            self.on_stop()

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

    def make_ants(self, n, **kwargs):
        ants = []
        for _ in range(n):
            ant = Ant(self.env, **kwargs)
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
                elif event.key == pygame.K_g:
                    envs = [e for e in Envs.keys()]
                    i = envs.index(self.env_type)
                    next_env = envs[(i + 1) % len(envs)]
                    self.env_type = next_env
                    self.env = Envs[next_env]()
                    self.running = False
                    self.on_stop = self.relaunch
                elif event.key == pygame.K_n:
                    self.env.reset()
                    self.env.render()
                elif event.key == pygame.K_s:
                    self.show_training_stats()
                elif not self.env.done:
                    self.env.handle_key(event)

    def quit(self):
        self.running = False

    def relaunch(self):
        del self.on_stop
        self.run_user_session()
