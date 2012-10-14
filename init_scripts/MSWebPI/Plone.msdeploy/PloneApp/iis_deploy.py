#!/usr/bin/env python2.7

import sys
import os
import subprocess
import logging

logger = logging.getLogger('plone.iiswsgi')


def main():
    CWD = os.getcwd()
    INSTANCE_HOME = os.path.join('zinstance')

    try:
        os.chdir(INSTANCE_HOME)
        subprocess.check_call([sys.executable, 'bootstrap.py', '-d'])
        subprocess.check_call([os.path.join('bin', 'buildout.exe'), '-ND'])
    finally:
        os.chdir(CWD)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
