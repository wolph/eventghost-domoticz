from __future__ import print_function

import sys
import eg_base


def error(message, *args, **kwargs):
    if args:
        message %= args
    if kwargs:
        message %= kwargs

    if eg_base.TESTING:
        print(message, file=sys.stderr)
    else:
        eg_base.eg.PrintError(message)
