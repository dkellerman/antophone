import pygame
from tqdm import tqdm
import time
from antophone.farm.cliffs import CliffsEnv
from antophone.farm.ant import Ant


class Farm:
    def __init__(self):
        self.env = CliffsEnv()
        self.is_user_session = False
        self.running = True
        pygame.init()

    def train(self, episode_ct=10000, ant_ct=1):
        self.ants = self.make_ants(ant_ct)
        Ant.no_random = False
        for _ in tqdm(range(episode_ct)):
            self.run_episode()

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
        while self.running and not all(done):
            for event in pygame.event.get():
                self.handle_event(event)
            for i, ant in enumerate(self.ants):
                done[i] = ant.update()
                if render:
                    self.env.render()
            if render and delay:
                time.sleep(delay)

    def make_ants(self, n):
        ants = []
        for _ in range(n):
            ant = Ant(self.env)
            ants.append(ant)
        return ants

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
                elif not self.env.done:
                    self.env.handle_key(event)

    def quit(self):
        self.running = False
