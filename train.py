#!/usr/bin/env python

import sys
import argparse
import traceback
from antophone.farm import Farm


parser = argparse.ArgumentParser()
parser.add_argument('-e', '--episodes', type=int, default=10000, help="Number of episodes")
parser.add_argument('-g', '--game', type=str, default="simple_cliffs", help="Game type")
parser.add_argument('-u', '--user', action='store_true', help="Launch a user session")
args = parser.parse_args()

if __name__ == '__main__':
    farm = Farm(env_type=args.game)
    try:
        farm.train(episode_ct=args.episodes)
        farm.show_training_stats()
        if args.user:
            farm.run_user_session()
    except Exception as ex:
        print(''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))
    finally:
        farm.quit()
        sys.exit(0)
