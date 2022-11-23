import os
from antophone import layouts


class Config:
    instr_layout = layouts.FIFTHS
    instr_copies = (3, 3)
    instr_hue = .6
    base_square_size = (20, 20)
    bg_color = (10, 10, 10)
    vol_decay_rate = .9
    vol_threshold = 0.4
    resonance_decay_factor = (3.0, 2.0)
    sympathies = ((-2, -1, 1, 2), (-2, -1, 1, 2))
    ant_randomness = .1
    ant_antsiness = .08
    ant_img = os.path.join(os.path.dirname(__file__), '../images/ant.png')
    ant_weight = 0.05
    ant_moves = (
        (0, 0), (0, 1), (0, -1), (1, 0), (-1, 0),
        # (1, 1), (1, -1), (-1, 1), (-1, -1),
        # (0, 2), (0, -2), (2, 0), (-2, 0),
        # (2, 2), (2, -2), (-2, 2), (-2, -2),
    )
    user_impact = .8
    initial_ant_count = 0
    frame_rate = 60
    cycle_time = .09
    buffer_size = 2056
