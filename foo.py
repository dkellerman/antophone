import mido
from mido import MidiFile, MidiTrack, Message

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

# Melody
track.append(Message('program_change', program=12, time=0))
track.append(Message('note_on', note=64, velocity=64, time=32))
track.append(Message('note_on', note=64, velocity=64, time=32))
track.append(Message('note_on', note=67, velocity=64, time=32))
track.append(Message('note_on', note=67, velocity=64, time=32))
track.append(Message('note_on', note=69, velocity=64, time=32))
track.append(Message('note_on', note=69, velocity=64, time=32))
track.append(Message('note_on', note=67, velocity=64, time=32))
track.append(Message('note_on', note=67, velocity=64, time=32))
track.append(Message('note_on', note=64, velocity=64, time=32))
track.append(Message('note_on', note=64, velocity=64, time=32))
track.append(Message('note_on', note=62, velocity=64, time=32))
track.append(Message('note_on', note=62, velocity=64, time=32))
track.append(Message('note_on', note=60, velocity=64, time=32))
track.append(Message('note_on', note=60, velocity=64, time=32))
track.append(Message('note_on', note=62, velocity=64, time=32))
track.append(Message('note_on', note=62, velocity=64, time=32))
track.append(Message('note_on', note=64, velocity=64, time=32))
track.append(Message('note_on', note=64, velocity=64, time=32))

# Bass
track.append(Message('program_change', program=34, time=0))
track.append(Message('note_on', note=48, velocity=64, time=64))
track.append(Message('note_on', note=48, velocity=64, time=64))
track.append(Message('note_on', note=55, velocity=64, time=64))
track.append(Message('note_on', note=55, velocity=64, time=64))
track.append(Message('note_on', note=60, velocity=64, time=64))
track.append(Message('note_on', note=60, velocity=64, time=64))
track.append(Message('note_on', note=55, velocity=64, time=64))
track.append(Message('note_on', note=55, velocity=64, time=64))
track.append(Message('note_on', note=48, velocity=64, time=64))
track.append(Message('note_on', note=48, velocity=64, time=64))

mid.save('test.mid')

