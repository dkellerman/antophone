#!/usr/bin/env python

import sys
import argparse
import traceback
from antophone.farm import Farm

parser = argparse.ArgumentParser()
parser.add_argument('-g', '--game', type=str, default="cliffs", help="Game type")
args = parser.parse_args()

if __name__ == '__main__':
    farm = Farm(env_type=args.game)
    try:
        farm.run_user_session()
    except Exception as ex:
        print(''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))
    finally:
        farm.quit()
        sys.exit(0)
