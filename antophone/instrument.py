import random
import pyo
import numpy as np
from librosa import note_to_hz as hz
from antophone import Ant, Config


CAP_VOL = 1.0
CAP_FREQ = 5000.0

class Instrument:
    def __init__(self):
        layout = Config.instr_layout
        copies = Config.instr_copies
        self.layout_width = len(layout[0])
        self.layout_height = len(layout)
        self.width = self.layout_width * copies
        self.height = self.layout_height * copies
        self.freqs = np.array([[hz(n) for n in row * copies] for row in layout * copies])
        self.max_freq = max([max(row) for row in self.freqs])
        self.volumes = np.zeros((self.height, self.width), np.float32)
        self.ants = []

    def start(self):
        # initialize sounds
        self.sounds = []
        for y in range(self.layout_height):
            for x in range(self.layout_width):
                freq = float(self.freqs[y][x])
                freq = freq if freq <= CAP_FREQ else 0
                table = pyo.TriangleTable(order=2).normalize()
                sound = pyo.Osc(table=table, freq=freq, mul=0).out()
                self.sounds.append(sound)

    def stop(self):
        for sound in self.sounds:
            sound.stop()

    def remove_random_ants(self, n):
        for _ in range(min(len(self.ants), n)):
            del self.ants[random.randint(0, len(self.ants) - 1)]

    def add_random_ants(self, n):
        for _ in range(n):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            ant = Ant(self, x, y)
            self.ants.append(ant)

    def adjust_freq(self, x, y, dfreq):
        self.volumes[y][x] += dfreq

        # apply sympathetic resonances
        for dx, dy in zip(*Config.sympathies):
            (rdecay_x, rdecay_y) = Config.resonance_decay_factor
            dfx = dfreq / (rdecay_x*abs(dx))
            dfy = dfreq / (rdecay_y**abs(dy))
            xnext = x + dx
            ynext = y + dy
            if xnext < self.width - 1 and xnext > 0:
                self.volumes[y][xnext] += dfx
            if ynext < self.height - 1 and ynext > 0:
                self.volumes[ynext][x] += dfy

    def decay(self):
        self.volumes *= Config.vol_decay_rate

    def update(self):
        self.decay()

        for ant in self.ants:
            if ant.last_move != (0, 0):
                self.adjust_freq(ant.x, ant.y, Config.ant_weight)

        self.volumes[self.volumes < 0.01] = 0
        self.volumes[self.volumes > 1.0] = 1.0

        # calculate and apply new volumes
        new_vols = np.zeros(len(self.sounds))
        for y in range(self.height):
            for x in range(self.width):
                i = ((y * self.width) + x) % len(self.sounds)
                new_vols[i] += self.volumes[y][x]
        for i in range(len(self.sounds)):
            new_vol = float(min(new_vols[i], CAP_VOL)) if new_vols[i] > Config.vol_treshold else 0
            self.sounds[i].mul = new_vol
