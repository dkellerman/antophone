#!/usr/bin/env python

import sys
import traceback
from antophone import Game

if __name__ == '__main__':
    game = Game()
    try:
        game.run()
    except Exception as ex:
        print(''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))
    finally:
        game.quit()
        sys.exit(0)
