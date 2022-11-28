import aubio
import numpy as np
import sounddevice as sd

running = False


def listen(callback):
    pitch_o = aubio.pitch("yin", 4096, 512, 44100)
    pitch_o.set_unit("Hz")
    pitch_o.set_tolerance(0.8)

    global running
    running = True
    while running:
        audiobuffer = sd.rec(512, samplerate=44100, channels=1, dtype='float32')
        sd.wait()
        signal = np.fromstring(audiobuffer, dtype=np.float32)
        pitch = pitch_o(signal)[0]
        confidence = pitch_o.get_confidence()
        if pitch > 0 and confidence > 0.5:
            callback(pitch, confidence)


def stop():
    global running
    running = False
