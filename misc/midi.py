#!/usr/bin/env python

import mido

print('listening for midi events...')
out_port = mido.open_output()
with mido.open_input() as in_port:
    for msg in in_port:
        print(msg)
        if msg.type == 'note_on':
            out_msg = msg.copy(note=msg.note + 4)
            print('=>', out_msg)
            out_port.send(out_msg)
