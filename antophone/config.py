from antophone import layouts


class Config:
    instr_layout = layouts.FIFTHS
    instr_copies = (3, 3)
    instr_hue = .6
    base_square_size = (20, 20)
    bg_color = (0, 0, 0)
    vol_decay_rate = .9
    vol_treshold = 0.4
    resonance_decay_factor = (3.0, 2.0)
    sympathies = ((-2, -1, 1, 2), (-2, -1, 1, 2))
    ant_randomness = .1
    ant_antsiness = .1
    ant_img = 'images/ant.png'
    ant_weight = 0.06
    user_impact = .8
    initial_ant_count = 0
    frame_rate = 60
    engine_delay = .05
    buffer_size = 2056
