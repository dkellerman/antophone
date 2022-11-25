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
    def __init__(self):
        layout = C.layout
        xcopies, ycopies = C.copies
        self.layout_width = len(layout[0])
        self.layout_height = len(layout)
        self.width = self.layout_width * xcopies
        self.height = self.layout_height * ycopies
        self.volumes = np.zeros((self.height, self.width))
        self.freq_vols = dict()
        self.audible_freqs = np.array([])
        self.sound_objs = []
        self.dissonance = 0.0
        self.mute = False
        self.audio_server = pyo.Server(buffersize=C.buffer_size).boot()

        for row in layout * ycopies:
            for note in row * xcopies:
                freq = float(hz(note))
                self.freq_vols[freq] = 0.0
                table = pyo.TriangleTable(order=C.partials).normalize()
                sound = pyo.Osc(table=table, freq=freq, mul=0.0)
                self.sound_objs.append(sound)

        self.max_freq = float(max(self.freq_vols.keys()))
        self.running = False

    def run(self):
        self.audio_server.start()
        for sound in self.sound_objs:
            sound.out()

        self.running = True
        while self.running:
            self.update()

        self.audio_server.shutdown()
        for sound in self.sound_objs:
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
        assert impact >= 0.0 and impact <= C.per_square_vol_cap

        self.volumes[y][x] += impact

        # apply sympathetic resonances
        for dx, dy in zip(*C.resonances):
            (rdecay_x, rdecay_y) = C.resonance_decay_factor
            dfx = impact / (rdecay_x*abs(dx))
            dfy = impact / (rdecay_y**abs(dy))
            xnext = x + dx
            ynext = y + dy
            if xnext < self.width and xnext >= 0:
                self.volumes[y][xnext] += dfx
            if ynext < self.height and ynext >= 0:
                self.volumes[ynext][x] += dfy

        self.update_sounds()

    def touch_freq(self, freq, impact, tolerance=0):
        '''tolerance: cents range'''

        for y in range(self.height):
            for x in range(self.width):
                f = self.freq_at(x, y)
                if (tolerance == 0 and freq == f) or (abs(utils.diff_cents(f, freq)) < tolerance):
                    self.touch(x, y, impact)

    def update(self):
        ts = utils.ts()

        # decay
        self.volumes *= (1 - C.decay_rate)
        self.update_sounds()

        ts_delta = utils.ts() - ts
        remaining = (C.update_cycle_time - ts_delta) % C.update_cycle_time
        time.sleep(max(remaining, 0))

    def update_sounds(self):
        self.volumes[self.volumes > C.per_square_vol_cap] = C.per_square_vol_cap
        self.volumes[self.volumes < C.per_square_vol_floor] = 0.0

        new_freq_vols = dict()
        for y in range(self.height):
            for x in range(self.width):
                freq = self.freq_at(x, y)
                vol = new_freq_vols.get(freq, 0.0) + self.volumes[y][x]
                new_freq_vols[freq] = vol

        audible_freqs = set()
        for freq, vol in new_freq_vols.items():
            vol = min(vol, C.per_freq_vol_cap)
            new_freq_vols[freq] = vol
            if vol > 0:
                audible_freqs.add(freq)

        # apply volumes
        for sound in self.sound_objs:
            vol = float(new_freq_vols[sound.freq])
            vol = vol if freq <= C.freq_cap else 0.0
            sound.mul = min(max(vol, 0.0), 1.0)

        self.audible_freqs = np.array(list(audible_freqs))
        self.freq_vols = new_freq_vols
        self.last_dissonance = self.dissonance
        self.dissonance = self.get_dissonance()

    def get_dissonance(self):        
        if len(self.audible_freqs):
            freqs, amps = harmonic_tone(self.audible_freqs, n_partials=C.partials)
            return dissonance(freqs, amps, model='sethares1993')
        return 0.0

    def get_grid_colors(self):
        colors = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                vol = self.volumes[y][x]
                freq = self.freq_at(x, y)
                color = self.freq_to_color(freq, vol)
                row.append(color)
            colors.append(row)
        return colors

    @cache
    def freq_to_color(self, freq, vol):
        if vol == 0:
            return C.bg_color
        return [min(255, int(val * 255)) for val in hls_to_rgb(
            freq / self.max_freq,
            vol,
            C.color_saturation,
        )]

    @cache
    def freq_at(self, x, y):
        return float(self.sound_objs[((y * self.width) + x) % len(self.sound_objs)].freq)
