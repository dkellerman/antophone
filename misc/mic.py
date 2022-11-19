#!/usr/bin/env python

import pyaudio
import sys
import numpy as np
import aubio
import mido

p = pyaudio.PyAudio()
buffer_size = 1024
pyaudio_format = pyaudio.paFloat32
n_channels = 1
samplerate = 44100
stream = p.open(format=pyaudio_format,
                channels=n_channels,
                rate=samplerate,
                input=True,
                frames_per_buffer=buffer_size)

# setup pitch
tolerance = 0.8
win_s = 4096 # fft size
hop_s = buffer_size # hop size
pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)

# out_port = mido.open_output()
msg = None

print("*** starting recording")

while True:
    try:
        audiobuffer = stream.read(buffer_size)
        signal = np.fromstring(audiobuffer, dtype=np.float32)

        pitch = pitch_o(signal)[0]
        confidence = pitch_o.get_confidence()

        print("{} / {}".format(pitch,confidence))

        # if msg:
        #     # msg = mido.Message('note_on', velocity=3, note=pitch, time)
        #     out_port.send(msg.copy(velocity=0))
        #     msg = None
        # if pitch > 0:
        #     msg = mido.Message('note_on', velocity=0, note=pitch)
        #     out_port.send(msg)
    except KeyboardInterrupt:
        print("*** Ctrl+C pressed, exiting")
        break

print("*** done recording")
stream.stop_stream()
stream.close()
p.terminate()
