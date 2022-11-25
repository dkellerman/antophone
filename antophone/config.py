import os
from antophone import layouts


class Config:
    base_square_size = (50, 50)
    ant_cycle_time = .1
    user_impact = .1
    frame_rate = 60
    pitch_tolerance = 30

    class instr:
        layout = layouts.FIFTHS
        copies = (1, 1)
        buffer_size = 1024
        update_cycle_time = 0.05
        decay_rate = .3
        threshold = 1.0
        resonances = ((1,), (1,)) # ((-2, -1, 1, 2), (-2, -1, 1, 2))
        resonance_decay_factor = (3.0, 3.0)
        color_saturation = .6
        bg_color = (10, 10, 10)
        per_square_vol_cap = .1
        per_square_vol_floor = 0.000001
        per_freq_vol_cap = .1
        freq_cap = 5000.0
        partials = 2

    class ant:
        img = os.path.join(os.path.dirname(__file__), '../images/ant.png')
        weight = 0.05
        weight_decay = .01
        learning_rate = .5
        base_antsiness = .05
        actions = (
            # (0, 0),
            (0, 0), (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1),
        )
