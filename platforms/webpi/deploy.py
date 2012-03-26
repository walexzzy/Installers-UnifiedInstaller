"""Deplpy as a Web Deploy package for Microsoft Web Platform Installer."""

import sys
import os
import subprocess

def main():
    # Run bootstrap
    subprocess.check_call([sys.executable, os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'zeocluster', 'bootstrap.py'), '-d'])
    # Run buildout
    subprocess.check_call([os.path.join(
        os.path.dirname(__file__), 'bin', 'buildout.exe'), '-N'])
    

if __name__ == '__main__':
    main()
