import random
import numpy as np
import pyo
from librosa import note_to_hz as hz
from antophone import Ant


CAP_VOL = 1.0
CAP_FREQ = 4000.0
COPIES = 4
LAYOUT = [
    ['F#2', 'C#2', 'G#2', 'D#2', 'A#2', 'F2', 'C2', 'G2', 'D2', 'A2', 'E2', 'B2'] * COPIES,
    ['F#3', 'C#3', 'G#3', 'D#3', 'A#3', 'F3', 'C3', 'G3', 'D3', 'A3', 'E3', 'B3'] * COPIES,
    ['F#4', 'C#4', 'G#4', 'D#4', 'A#4', 'F4', 'C4', 'G4', 'D4', 'A4', 'E4', 'B4'] * COPIES,
    ['F#5', 'C#5', 'G#5', 'D#5', 'A#5', 'F5', 'C5', 'G5', 'D5', 'A5', 'E5', 'B5'] * COPIES,
] * COPIES

class Instrument:
    decay_rate = .9
    ant_impact = .1
    treshold = 0.4

    def __init__(self, layout=LAYOUT):
        self.width = len(layout[0])
        self.height = len(layout)
        self.freqs = np.array([[hz(n) for n in row] for row in layout])
        self.max_freq = max([max(row) for row in self.freqs])
        self.volumes = np.zeros((self.height, self.width), np.float32)
        self.ants = []
        
        # initialize outputs
        self.outputs = []
        for y in range(self.height):
            outrow = []
            for x in range(self.width):
                freq = float(self.freqs[y][x])
                sound = pyo.Sine(freq=freq if freq <= CAP_FREQ else 0, mul=0)
                outrow.append(sound)
            self.outputs.append(outrow)

    def start(self):
        for row in self.outputs:
            for sound in row:
                sound.out()

    def stop(self):
        for row in self.outputs:
            for sound in row:
                sound.stop()

    def add_random_ants(self, n):
        for _ in range(n):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            ant = Ant(self, x, y)
            self.ants.append(ant)

    def adjust_freq(self, x, y, delta):
        self.volumes[y][x] += delta

        # sympathetic resonance
        w, h = self.width, self.height
        for i in range(1, 3):
            df = delta / (2 ** i)
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
        for y in range(self.height):
            for x in range(self.width):
                sound = self.outputs[y][x]
                vol = self.volumes[y][x]
                sound.mul = float(min(vol, CAP_VOL)) if vol > self.treshold else 0
                    
