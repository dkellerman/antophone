import pygame
from tqdm import tqdm
import time
from antophone.farm.cliffs import CliffsEnv
from antophone.farm.ant import Ant


class Farm:
    def __init__(self):
        pygame.init()

    def train(self, episode_ct=10000, ant_ct=1):
        self.env = CliffsEnv()
        self.ants = self.make_ants(ant_ct)
        self.running = True

        print('training...')
        for _ in tqdm(range(episode_ct)):
            self.run_episode()

        print('demoing...')
        Ant.no_random = True
        for _ in tqdm(range(100)):
            self.run_episode(render=True, delay=.5)

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

    def quit(self):
        self.running = False
