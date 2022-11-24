import threading
import time
import datetime
import math


def ts():
    return datetime.datetime.now().microsecond / 1000000.0


def diff_cents(f1, f2):
    return 1200 * math.log2(f1 / f2)


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
