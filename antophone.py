#!/usr/bin/env python

import sys
import traceback
from antophone.phone import Antophone

if __name__ == '__main__':
    a = Antophone()
    try:
        a.run()
    except Exception as ex:
        print(''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))
    finally:
        a.quit()
        sys.exit(0)
