import threading
import time
import datetime
import math
import numpy as np


def draw_border_rect(surface, fill_color, outline_color, rect, border=1):
    surface.fill(outline_color, rect)
    surface.fill(fill_color, rect.inflate(-border * 2, -border * 2))


def rolling_avg(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)


def ts():
    return datetime.datetime.now().microsecond / 1000000.0


def diff_cents(f1, f2):
    return 1200 * math.log2(f1 / f2)


def softmax(x):
    return (np.exp(x - np.max(x)) / np.exp(x - np.max(x)).sum())


def rnd_softmax(x):
    return np.random.choice(x, p=softmax(x))


class PygameShell:
    pass


class TimedCycleThread():
    running = False

    def __init__(self, cycle_time=None):
        self.cycle_time = cycle_time

    def setup(self):
        pass

    def start(self, *args, **kwargs):
        self.thread = threading.Thread(target=self.run, args=args, kwargs=kwargs)
        self.thread.start()

    def run(self):
        self.setup()
        self.running = True
        while self.running:
            ts = datetime.datetime.now().microsecond / 1000000
            self.cycle()
            if self.cycle_time:
                delta = (datetime.datetime.now().microsecond / 1000000) - ts
                remaining = (self.cycle_time - delta) % self.cycle_time
                time.sleep(max(remaining, 0))
        self.quit()

    def cycle(self):
        pass

    def stop(self):
        self.running = False

    def quit(self):
        pass
