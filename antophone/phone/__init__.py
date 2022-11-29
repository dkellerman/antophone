import numpy as np
import time
import random
import threading
import pygame
import importlib
from librosa import midi_to_hz
from .. import utils
from . import mic, midi, config, instrument, ant
from .instrument import Instrument
from .ant import Ant

C = config.Config


class Antophone:
    instr = Instrument()
    ants = []
    zoom = 1
    training = False

    def run(self):
        pygame.init()
        pygame.display.set_caption('Antophone')
        self.render_surface()

        # instrument thread
        self.instr_thread = threading.Thread(target=self.instr.run)
        self.instr_thread.start()

        # midi thread
        midi_cb = lambda *args: self.handle_midi_note(*args)
        self.midi_thread = threading.Thread(target=midi.listen, args=[midi_cb])
        self.midi_thread.start()

        # ant thread
        self.ants_thread = threading.Thread(target=self.run_ants)
        self.ants_thread.start()

        # run main gui loop
        self.clock = pygame.time.Clock()
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if not self.running:
                    break
                self.handle_event(event)
            self.render()
            pygame.display.update()
            self.clock.tick(C.frame_rate)

        self.quit()

    def stop(self):
        self.running = False
        self.ants_running = False

    def quit(self):
        print('quitting...')
        self.running = False
        self.ants_running = False
        mic.stop()
        midi.stop()
        self.instr.stop()
        pygame.quit()

    def run_ants(self):
        self.ants_running = True
        while self.ants_running:
            ts = utils.ts()
            self.update_ants()
            delta = utils.ts() - ts
            remaining = (C.ant_cycle_time - delta) % C.ant_cycle_time
            time.sleep(max(remaining, 0))

    def update_ants(self):
        for ant in self.ants:
            ant.update()

    def render(self):
        if self.training:
            return
        sqw, sqh = self.square_size

        grid = self.instr.get_grid_colors()
        for y, row in enumerate(grid):
            for x, rgb in enumerate(row):
                x1, y1 = x * sqw, y * sqh
                x2, y2 = x1 + sqw, y1 + sqh
                color = pygame.Color(*rgb)
                pygame.draw.rect(self.surface, color, pygame.Rect(x1, y1, x2, y2))

        for ant in self.ants:
            ax = (ant.x * sqw) + (sqw / 2) - (ant.img.get_width() / 2)
            ay = (ant.y * sqh) + (sqh / 2) - (ant.img.get_height() / 2)
            self.surface.blit(ant.img, (ax, ay))

    def remove_random_ants(self, n):
        for _ in range(min(len(self.ants), n)):
            del self.ants[random.randint(0, len(self.ants) - 1)]

    def add_random_ants(self, n):
        for _ in range(n):
            x = random.randint(0, self.instr.width - 1)
            y = random.randint(0, self.instr.height - 1)
            ant = Ant(self.instr, x, y)
            self.ants.append(ant)

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
        self.zoom = min(max(val, -5), 5)
        self.render_surface()

    def reload_config(self):
        importlib.reload(config)
        global C
        C = config.Config
        instrument.C = C.instr
        ant.C = C.ant

        # self.reload_instrument()
        self.render_surface()

    def reload_instrument(self):
        vols = np.array(self.instr.volumes)
        mute = self.instr.mute
        self.instr.stop()
        self.instr = Instrument()
        self.ants = [a for a in self.ants if a.x < self.instr.width and a.y < self.instr.height]
        vols.resize(self.instr.volumes.shape)
        self.instr.volumes = vols
        self.instr.mute = mute
        self.instr.freq_to_color.cache_clear()
        self.instr.freq_at.cache_clear()
        self.instr_thread = threading.Thread(target=self.instr.run)
        self.instr_thread.start()

    def handle_midi_note(self, note):
        hz = midi_to_hz(note.note)
        vol = min(max(note.velocity / 127, 0), C.user_impact)
        self.instr.touch_freq(hz, vol)

    def handle_audio_pitch(self, pitch, confidence):
        print('*', pitch, confidence)
        self.instr.touch_freq(pitch, C.user_impact / 2, tolerance=C.pitch_tolerance)

    def touch_instrument_at(self, pos, t=None):
        x, y = pos[0] // self.square_size[0], pos[1] // self.square_size[1]
        self.instr.touch(x, y, C.user_impact)

    def render_surface(self):
        sqw, sqh = self.square_size
        self.surface = pygame.display.set_mode((self.instr.width * sqw, self.instr.height * sqh))
        self.surface.fill(C.instr.bg_color)
        pygame.display.set_caption('Antophone' + (' [Recording]' if mic.running else ''))
        return self.surface

    @property
    def square_size(self):
        sqw, sqh = C.base_square_size
        return sqw * self.zoom, sqh * self.zoom

    def train(self):
        self.training = True
        self.instr.toggle_mute()
        ants = []
        x, y = random.randint(0, self.instr.width - 1), random.randint(0, self.instr.height - 1)
        a = Ant(self.instr, x, y)
        a.training = True
        ants.append(a)
        print('training...')
        from tqdm import tqdm
        for _ in tqdm(range(10000)):
            for ant in ants:
                ant.update()
        self.instr.toggle_mute()
        self.training = False
        print('done')

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.stop()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.touch_instrument_at(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                if event.mod & pygame.KMOD_SHIFT:
                    self.remove_random_ants(1)
                else:
                    self.add_random_ants(1)
            elif event.key == pygame.K_r:
                self.toggle_mic()
                self.render_surface()
            elif event.key == pygame.K_c:
                self.ants = []
            elif event.key == pygame.K_t:
                threading.Thread(target=self.train).start()
            elif event.key == pygame.K_SLASH:
                self.reload_config()
            elif event.key == pygame.K_z:
                if event.mod & pygame.KMOD_SHIFT:
                    self.set_zoom(self.zoom - 1)
                else:
                    self.set_zoom(self.zoom + 1)
            elif event.key == pygame.K_m:
                self.instr.toggle_mute()
            elif event.key == pygame.K_PERIOD and event.mod & pygame.KMOD_SHIFT:
                C.ant_cycle_time /= 2
                C.instr.update_cycle_time /= 2
                print('cycle time', C.ant_cycle_time, C.instr.update_cycle_time)
            elif event.key == pygame.K_COMMA and event.mod & pygame.KMOD_SHIFT:
                C.ant_cycle_time *= 2
                C.instr.update_cycle_time *= 2
                print('cycle time', C.ant_cycle_time, C.instr.update_cycle_time)
