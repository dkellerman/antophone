from antophone import layouts

class Config:
    instr_layout = layouts.FIFTHS
    instr_copies = 3
    instr_hue = .6
    bg_color = (0, 0, 0)
    vol_decay_rate = .9
    vol_treshold = 0.4
    resonance_decay_factor = (4.0, 2.0)
    sympathies = ((-2, -1, 1, 2), (-2 , -1, 1, 2))
    ant_randomness = .45
    ant_img = 'images/ant.png'
    ant_weight = 0.06
    user_impact = .8
    initial_ant_count = 0
    frame_rate = 60
    engine_delay = .05
    buffer_size = 2056
    base_square_size = (16, 16)
