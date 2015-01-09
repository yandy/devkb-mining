#!/usr/bin/env python
import sys
import os.path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    from devkb import cmdline
    cmdline.execute()
