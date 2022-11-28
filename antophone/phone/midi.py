import mido

running = False


def listen(cb):
    global running
    running = True
    with mido.open_input() as inport:
        while running:
            for msg in inport.iter_pending():
                if msg.type == 'note_on' and msg.velocity > 0:
                    cb(msg)


def stop():
    global running
    running = False
