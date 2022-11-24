import os
from antophone import layouts


class Config:
    base_square_size = (20, 20)
    ant_cycle_time = .1
    user_impact = .75
    initial_ant_count = 0
    frame_rate = 60
    pitch_tolerance = 30

    class instr:
        layout = layouts.FIFTHS
        copies = (3, 3)
        buffer_size = 2056
        update_cycle_time = .1
        decay_rate = .1
        threshold = 0.4
        resonances = ((-2, -1, 1, 2), (-2, -1, 1, 2))
        resonance_decay_factor = (3.0, 2.0)
        hue = .6
        bg_color = (10, 10, 10)
        freq_vol_cap = .5
        freq_cap = 5000.0

    class ant:
        img = os.path.join(os.path.dirname(__file__), '../images/ant.png')
        weight = 0.05
        weight_decay = .75
        moves = (
            (0, 0), (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1),
        )
