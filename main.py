#!/usr/bin/env python

import sys
from antophone import Game

if __name__ == '__main__':
    game = Game()
    try:
        game.run()
    finally:
        game.quit()
        sys.exit(0)
