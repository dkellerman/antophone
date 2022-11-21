import numpy as np
import time
import threading
import pygame
import pyo
from librosa import midi_to_hz
from functools import cache
from colorsys import hls_to_rgb
from antophone import Instrument, Ant, mic, midi, layouts


class Game:
    instr = None
    base_square_size = Ant.size
    zoom = 1
    initial_ant_count = 0
    frame_rate = 60
    bg_color = (0, 0, 0)
    delay = .1
    instr_copies = 3
    user_impact = .5
    dragging = False
    layout = layouts.FIFTHS

    @property
    def square_size(self):
        return self.base_square_size[0] * self.zoom, self.base_square_size[1] * self.zoom

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Antophone')
        self.audio_server = pyo.Server(buffersize=1024).boot()
        self.clock = pygame.time.Clock()

    def init_instr(self):
        self.audio_server.start()
        self.instr = Instrument(layout=self.layout, copies=self.instr_copies)
        self.render_surface()
        self.instr.add_random_ants(self.initial_ant_count)
        self.instr.start()

    def run(self):
        self.running = True
        self.init_instr()

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
            self.clock.tick(self.frame_rate)

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
            for ant in self.instr.ants:
                ant.move()
            self.instr.update()
            time.sleep(self.delay)

    def render(self):
        sqw, sqh = self.square_size
        self.surface.fill(self.bg_color)
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
            self.surface.blit(ant.img, (ax, ay))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            t = int(time.time())
            self.dragging = t
            self.touch(event.pos, t)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.touch(event.pos, int(time.time()))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                if event.mod & pygame.KMOD_SHIFT:
                    self.instr.remove_random_ants(1)
                else:
                    self.instr.add_random_ants(1)
            elif event.key == pygame.K_r:
                if mic.running:
                    print('stopping mic')
                    mic.stop()
                else:
                    print('starting mic')
                    cb = lambda *args: self.handle_audio_pitch(*args)
                    self.mic_thread = threading.Thread(target=mic.listen, args=[cb])
                    self.mic_thread.start()
            elif event.key == pygame.K_c:
                self.instr.ants = []
            elif event.key == pygame.K_z:
                if event.mod & pygame.KMOD_SHIFT:
                    self.zoom = max(self.zoom - 1, 1)
                else:
                    self.zoom = min(self.zoom + 1, 5)
                self.render_surface()

    def handle_midi_note(self, note):
        hz = midi_to_hz(note.note)
        vol = min(max(note.velocity / 127, 0), self.user_impact)
        hits = np.where(self.instr.freqs == hz)
        for y, x in zip(*hits):
            self.instr.adjust_freq(x, y, vol)

    def handle_audio_pitch(self, pitch, confidence):
        for y, row in enumerate(self.instr.freqs):
            for x, freq in enumerate(row):
                if freq >= pitch - 5 and freq <= pitch + 5:
                    self.instr.adjust_freq(x, y, self.user_impact)

    def touch(self, pos, t=None):
        x, y = pos[0] // self.square_size[0], pos[1] // self.square_size[1]
        if not self.dragging:
            impact = self.user_impact
        else:
            dt = t - self.dragging
            impact = self.user_impact / (4**dt)
            if impact < .01:
                self.dragging = False
                return
        self.instr.adjust_freq(x, y, impact)

    def render_surface(self):
        sqw, sqh = self.square_size
        self.surface = pygame.display.set_mode((self.instr.width * sqw, self.instr.height * sqh))
        return self.surface

    @cache
    def freq_to_color(self, freq, vol):
        r, g, b = [min(255, int(x * 255)) for x in hls_to_rgb(freq, (vol ** 2), 0.5)]
        return pygame.Color(r, g, b)
