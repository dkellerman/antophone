#!/usr/bin/env python

import sys
import traceback
from antophone.farm import Farm

if __name__ == '__main__':
    farm = Farm()
    try:
        farm.train()
    except Exception as ex:
        print(''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))
    finally:
        farm.quit()
        sys.exit(0)