import random
import time
import numpy as np
from functools import cache
from librosa import note_to_hz as hz
from antophone import Ant


FIFTHS_LAYOUT = (
    ('F#2', 'C#2', 'G#2', 'D#2', 'A#2', 'F2', 'C2', 'G2', 'D2', 'A2', 'E2', 'B2'),
    ('F#3', 'C#3', 'G#3', 'D#3', 'A#3', 'F3', 'C3', 'G3', 'D3', 'A3', 'E3', 'B3'),
    ('F#4', 'C#4', 'G#4', 'D#4', 'A#4', 'F4', 'C4', 'G4', 'D4', 'A4', 'E4', 'B4'),
    ('F#5', 'C#5', 'G#5', 'D#5', 'A#5', 'F5', 'C5', 'G5', 'D5', 'A5', 'E5', 'B5'),
)

CONTINUOUS_LAYOUT = (
    ('C2', 'C#2', 'D2', 'D#2', 'E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'A#2', 'B2'),
    ('C3', 'C#3', 'D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3'),
    ('C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4'),
    ('C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5'),
)


class Instrument:
    cents_per_square = 10
    size = (12 * cents_per_square, 4 * cents_per_square)
    volumes = np.zeros(size, np.float32)
    ants = []
    threshold = 0.5
    decay_rate = .9

    def __init__(self, slots=CONTINUOUS_LAYOUT):
        self.slots = np.array([[hz(n) for n in s] for s in slots])
        self.max_freq = max([max(row) for row in self.slots])
        self.row_ct = len(self.slots)
        self.col_ct = len(self.slots[0])
    
    def randomize_volumes(self, min=.1, max=.2):
        self.volumes = np.random.uniform(low=min, high=max, size=self.size)
        # self.volumes = np.random.random(size=self.size)

    def add_random_ants(self, n):
        for i in range(n):
            self.ants.append(Ant(self, random.randint(
                0, self.size[0] - 1), random.randint(0, self.size[1] - 1)))

    @cache
    def pos_to_freq(self, x, y):
        w, h = self.size
        col = int((x / w) * self.col_ct)
        row = int((y / h) * self.row_ct)
        return self.slots[row][col]

    def adjust_freq(self, x, y, delta):
        self.volumes[x][y] += delta

        # sympathetic resonance
        w, h = self.volumes.shape
        for i in range(1, 3):
            df = delta / (2 ** i)
            dx = dy = i * self.cents_per_square
            xnext, xprev = x + dx, x - dx
            ynext, yprev = y + dy, y - dy
            if xnext < w - 1:
                self.volumes[xnext][y] += df
            if xprev > 0:
                self.volumes[xprev][y] += df
            if ynext < h - 1:
                self.volumes[x][ynext] += df
            if yprev > 0:
                self.volumes[x][yprev] += df

    def decay(self):
        self.volumes *= self.decay_rate

    def update(self):
        self.decay()
        for ant in self.ants:
            if ant.last_move != (0, 0):
                self.adjust_freq(ant.x, ant.y, .1)
        self.volumes[self.volumes < 0.01] = 0
        self.volumes[self.volumes > 1.0] = 1.0
