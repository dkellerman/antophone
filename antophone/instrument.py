import pyo
import numpy as np
import time
from functools import cache
from colorsys import hls_to_rgb
from librosa import note_to_hz as hz
from dissonant import harmonic_tone, dissonance
from antophone import utils
from antophone.config import Config

C = Config.instr


class Instrument:
    mute = False
    running = False

    def __init__(self):
        layout = C.layout
        xcopies, ycopies = C.copies
        self.layout_width = len(layout[0])
        self.layout_height = len(layout)
        self.width = self.layout_width * xcopies
        self.height = self.layout_height * ycopies
        self.freqs = np.array([[hz(n) for n in row * xcopies] for row in layout * ycopies])
        self.max_freq = max([max(row) for row in self.freqs])
        self.volumes = np.zeros((self.height, self.width), np.float32)
        self.dissonance = 0

    def run(self):
        self.audio_server = pyo.Server(buffersize=C.buffer_size).boot()
        self.audio_server.start()

        # initialize sounds
        self.sounds = []
        for y in range(self.layout_height):
            for x in range(self.layout_width):
                freq = float(self.freqs[y][x])
                freq = freq if freq <= C.freq_cap else 0
                table = pyo.TriangleTable(order=2).normalize()
                sound = pyo.Osc(table=table, freq=freq, mul=0).out()
                self.sounds.append(sound)

        self.running = True
        while self.running:
            self.update()

        self.audio_server.shutdown()
        for sound in self.sounds:
            sound.stop()

    def stop(self):
        self.running = False

    def toggle_mute(self):
        if self.mute:
            self.audio_server.amp = self._last_amp
            self.mute = False
            self._amp = None
        else:
            self._last_amp = self.audio_server.amp
            self.audio_server.amp = 0
            self.mute = True

    def touch(self, x, y, impact):
        assert impact >= 0.0 and impact <= 1.0

        dfreq = impact  # impact=dB currently
        self.volumes[y][x] += dfreq

        # apply sympathetic resonances
        for dx, dy in zip(*C.resonances):
            (rdecay_x, rdecay_y) = C.resonance_decay_factor
            dfx = dfreq / (rdecay_x*abs(dx))
            dfy = dfreq / (rdecay_y**abs(dy))
            xnext = x + dx
            ynext = y + dy
            if xnext < self.width - 1 and xnext > 0:
                self.volumes[y][xnext] += dfx
            if ynext < self.height - 1 and ynext > 0:
                self.volumes[ynext][x] += dfy

    def touch_freq(self, freq, impact, tolerance=None):
        '''tolerance = cents range fudge factor'''
        if not tolerance:
            hits = np.where(self.freqs == freq)
        else:
            hits = [[], []]
            for y in range(self.height):
                for x in range(self.width):
                    if abs(utils.diff_cents(self.freqs[y][x], freq)) < tolerance:
                        hits[0].append(y)
                        hits[1].append(x)
        for y, x in zip(*hits):
            self.touch(x, y, impact)

    def update(self):
        ts = utils.ts()

        # decay
        self.volumes *= (1 - C.decay_rate)
        self.volumes[self.volumes < 0.01] = 0
        self.volumes[self.volumes > 1.0] = 1.0

        # calculate and apply new volumes
        new_vols = np.zeros(len(self.sounds))
        audible_freqs = set()
        for y in range(self.height):
            for x in range(self.width):
                i = ((y * self.width) + x) % len(self.sounds)
                new_vols[i] += self.volumes[y][x]
                new_vols[i] = min(new_vols[i], C.freq_vol_cap)
                if new_vols[i] >= C.threshold:
                    audible_freqs.add(self.freqs[y][x])
        for i in range(len(self.sounds)):
            new_vol = float(new_vols[i]) if new_vols[i] >= C.threshold else 0.0
            self.sounds[i].mul = new_vol

        # calculate dissonance
        self.last_dissonance = self.dissonance
        if len(audible_freqs):
            freqs, amps = harmonic_tone(list(audible_freqs), n_partials=2)
            self.dissonance = dissonance(freqs, amps, model='sethares1993')
        else:
            self.dissonance = 0

        ts_delta = utils.ts() - ts
        remaining = (C.update_cycle_time - ts_delta) % C.update_cycle_time
        time.sleep(max(remaining, 0))

    def get_grid_colors(self):
        colors = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                freq = self.freqs[y][x] / self.max_freq
                vol = self.volumes[y][x]
                color = self._freq_to_color(freq, vol)
                row.append(color)
            colors.append(row)
        return colors

    @cache
    def _freq_to_color(self, freq, vol):
        if vol == 0:
            return C.bg_color
        return [min(255, int(val * 255)) for val in hls_to_rgb(
            freq,
            (vol ** 2),
            C.hue,
        )]
