import random
import pyo
import numpy as np
from librosa import note_to_hz as hz
from antophone import Ant


CAP_VOL = 1.0
CAP_FREQ = 5000.0
LAYOUT = [
    ['F#5', 'C#5', 'G#5', 'D#5', 'A#5', 'F5', 'C5', 'G5', 'D5', 'A5', 'E5', 'B5'],
    ['F#4', 'C#4', 'G#4', 'D#4', 'A#4', 'F4', 'C4', 'G4', 'D4', 'A4', 'E4', 'B4'],
    ['F#3', 'C#3', 'G#3', 'D#3', 'A#3', 'F3', 'C3', 'G3', 'D3', 'A3', 'E3', 'B3'],
    ['F#2', 'C#2', 'G#2', 'D#2', 'A#2', 'F2', 'C2', 'G2', 'D2', 'A2', 'E2', 'B2'],
    ['F#1', 'C#1', 'G#1', 'D#1', 'A#1', 'F1', 'C1', 'G1', 'D1', 'A1', 'E1', 'B1'],
]


class Instrument:
    decay_rate = .9
    ant_impact = .1
    treshold = 0.4

    def __init__(self, layout=LAYOUT, copies=1):
        layout_width = len(layout[0])
        layout_height = len(layout)
        self.width = layout_width * copies
        self.height = layout_height * copies
        self.freqs = np.array([[hz(n) for n in row * copies] for row in layout * copies])
        self.max_freq = max([max(row) for row in self.freqs])
        self.volumes = np.zeros((self.height, self.width), np.float32)
        self.ants = []

        # initialize sounds
        self.sounds = []
        for y in range(layout_height):
            for x in range(layout_width):
                freq = float(self.freqs[y][x])
                sound = pyo.Sine(freq=freq if freq <= CAP_FREQ else 0, mul=0)
                self.sounds.append(sound)

    def start(self):
        for sound in self.sounds:
            sound.out()

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

    def adjust_freq(self, x, y, delta):
        self.volumes[y][x] += delta

        # sympathetic resonances
        w, h = self.width, self.height
        for i in range(1, 3):
            df = delta / (2**i)
            dx = dy = i
            xnext, xprev = x + dx, x - dx
            ynext, yprev = y + dy, y - dy
            if xnext < w - 1:
                self.volumes[y][xnext] += df
            if xprev > 0:
                self.volumes[y][xprev] += df
            if ynext < h - 1:
                self.volumes[ynext][x] += df
            if yprev > 0:
                self.volumes[yprev][x] += df

    def decay(self):
        self.volumes *= self.decay_rate

    def update(self):
        self.decay()

        for ant in self.ants:
            if ant.last_move != (0, 0):
                self.adjust_freq(ant.x, ant.y, self.ant_impact)

        self.volumes[self.volumes < 0.01] = 0
        self.volumes[self.volumes > 1.0] = 1.0

        # calculate and apply new volumes
        new_vols = np.zeros(len(self.sounds))
        for y in range(self.height):
            for x in range(self.width):
                i = ((y * self.width) + x) % len(self.sounds)
                new_vols[i] += self.volumes[y][x]
        for i in range(len(self.sounds)):
            new_vol = float(min(new_vols[i], CAP_VOL)) if new_vols[i] > self.treshold else 0
            self.sounds[i].mul = new_vol
