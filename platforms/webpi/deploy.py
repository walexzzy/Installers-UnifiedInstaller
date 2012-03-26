"""Deplpy as a Web Deploy package for Microsoft Web Platform Installer."""

import sys
import os
import logging
import subprocess

logger = logging.getLogger('plone.webdeploy')


def main():
    # Run bootstrap
    bootstrap = [sys.executable, '-S', os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'zeocluster', 'bootstrap.py'), '-d']
    logger.info('Running bootstrap: %r' % ' '.join(bootstrap))
    subprocess.check_call(bootstrap)
    # Run buildout
    buildout = [os.path.join(
        os.path.dirname(__file__), 'bin', 'buildout.exe'), '-N']
    logger.info('Running buildout: %r' % ' '.join(buildout))
    subprocess.check_call(buildout)
    

if __name__ == '__main__':
    main()
