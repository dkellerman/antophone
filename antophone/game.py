import numpy as np
import time
import threading
import pygame
import pyo
import importlib
import datetime
from librosa import midi_to_hz
from functools import cache
from colorsys import hls_to_rgb
import antophone
from antophone import Instrument, Ant, mic, midi

Config = antophone.config.Config


class Game:
    instr = Instrument()
    zoom = 1
    mute = False

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Antophone')
        self.render_surface()
        self.clock = pygame.time.Clock()
        self.audio_server = pyo.Server(buffersize=Config.buffer_size).boot()
        self.audio_server.start()
        self.instr.add_random_ants(Config.initial_ant_count)
        self.instr.start()

    def run(self):
        self.running = True

        # instrument/ant thread
        self.engine_thread = threading.Thread(target=self.run_engine)
        self.engine_thread.start()

        # midi thread
        midi_cb = lambda *args: self.handle_midi_note(*args)
        self.midi_thread = threading.Thread(target=midi.listen, args=[midi_cb])
        self.midi_thread.start()

        # gui thread
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.render()
            pygame.display.update()
            self.clock.tick(Config.frame_rate)

    def quit(self):
        print('quitting...')
        self.running = False
        self.engine_running = False
        mic.stop()
        midi.stop()
        self.instr.stop()
        self.audio_server.shutdown()
        pygame.quit()

    def run_engine(self):
        self.engine_running = True
        while self.engine_running:
            ts = datetime.datetime.now().microsecond / 1000000
            for ant in self.instr.ants:
                ant.move()
            self.instr.update()
            delta = (datetime.datetime.now().microsecond / 1000000) - ts
            rem = (Config.cycle_time - delta) % Config.cycle_time
            time.sleep(max(rem, 0))

    def render(self):
        sqw, sqh = self.square_size
        self.surface.fill(Config.bg_color)
        pygame.display.set_caption('Antophone' + (' [Recording]' if mic.running else ''))

        for y in range(self.instr.height):
            for x in range(self.instr.width):
                freq = self.instr.freqs[y][x] / self.instr.max_freq
                vol = self.instr.volumes[y][x]
                color = self.freq_to_color(freq, vol)
                x1, y1 = x * sqw, y * sqh
                x2, y2 = x1 + sqw, y1 + sqh
                pygame.draw.rect(self.surface, color, pygame.Rect(x1, y1, x2, y2))

        for ant in self.instr.ants:
            ax = (ant.x * sqw) + (sqw / 2) - (ant.img.get_width() / 2)
            ay = (ant.y * sqh) + (sqh / 2) - (ant.img.get_height() / 2)
            self.surface.blit(Ant.img, (ax, ay))

    def toggle_mic(self):
        if mic.running:
            print('stopping mic')
            mic.stop()
        else:
            print('starting mic')
            cb = lambda *args: self.handle_audio_pitch(*args)
            self.mic_thread = threading.Thread(target=mic.listen, args=[cb])
            self.mic_thread.start()

    def set_zoom(self, val):
        self.zoom = min(max(val, -3), 3)
        self.render_surface()

    def toggle_mute(self):
        if self.mute:
            self.audio_server.amp = self._amp
            self.mute = False
            self._amp = None
        else:
            self._amp = self.audio_server.amp
            self.audio_server.amp = 0
            self.mute = True

    def reload_config(self):
        global Config
        old_attrs = set(vars(Config).items())
        importlib.reload(antophone.config)
        Config = antophone.config.Config
        antophone.instrument.Config = Config

        new_attrs = set(vars(Config).items())
        keys = [pair[0] for pair in old_attrs ^ new_attrs if '__' not in pair[0]]
        print('updating config', keys)
        if len([k for k in keys if k.startswith('instr_')]) > 0:
            self.reload_instrument()
        self.render_surface()

    def reload_instrument(self):
        ants = list(self.instr.ants)
        vols = np.array(self.instr.volumes)
        self.instr.stop()
        self.instr = Instrument()
        self.instr.ants = [a for a in ants if a.x < self.instr.width and a.y < self.instr.height]
        vols.resize(self.instr.volumes.shape)
        self.instr.volumes = vols
        self.instr.start()

    def handle_midi_note(self, note):
        hz = midi_to_hz(note.note)
        vol = min(max(note.velocity / 127, 0), Config.user_impact)
        hits = np.where(self.instr.freqs == hz)
        for y, x in zip(*hits):
            self.instr.adjust_freq(x, y, vol)

    def handle_audio_pitch(self, pitch, confidence):
        for y, row in enumerate(self.instr.freqs):
            for x, freq in enumerate(row):
                if freq >= pitch - 5 and freq <= pitch + 5:
                    self.instr.adjust_freq(x, y, Config.user_impact / 2)

    def touch(self, pos, t=None):
        x, y = pos[0] // self.square_size[0], pos[1] // self.square_size[1]
        self.instr.adjust_freq(x, y, Config.user_impact)

    def render_surface(self):
        sqw, sqh = self.square_size
        self.surface = pygame.display.set_mode((self.instr.width * sqw, self.instr.height * sqh))
        return self.surface

    @cache
    def freq_to_color(self, freq, vol):
        if vol == 0:
            return Config.bg_color
        r, g, b = [min(255, int(val * 255)) for val in hls_to_rgb(
            freq,
            (vol ** 2),
            Config.instr_hue,
        )]
        return pygame.Color(r, g, b)

    @property
    def square_size(self):
        return Config.base_square_size[0] * self.zoom, Config.base_square_size[1] * self.zoom

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.touch(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                if event.mod & pygame.KMOD_SHIFT:
                    self.instr.remove_random_ants(1)
                else:
                    self.instr.add_random_ants(1)
            elif event.key == pygame.K_r:
                self.toggle_mic()
            elif event.key == pygame.K_c:
                self.instr.ants = []
            elif event.key == pygame.K_SLASH:
                self.reload_config()
            elif event.key == pygame.K_z:
                if event.mod & pygame.KMOD_SHIFT:
                    self.set_zoom(self.zoom - 1)
                else:
                    self.set_zoom(self.zoom + 1)
            elif event.key == pygame.K_m:
                self.toggle_mute()
            elif event.key == pygame.K_PERIOD and event.mod & pygame.KMOD_SHIFT:
                Config.cycle_time /= 2
                print('cycle time', Config.cycle_time)
            elif event.key == pygame.K_COMMA and event.mod & pygame.KMOD_SHIFT:
                Config.cycle_time *= 2
                print('cycle time', Config.cycle_time)
