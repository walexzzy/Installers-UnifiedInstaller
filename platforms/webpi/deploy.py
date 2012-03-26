"""Deplpy as a Web Deploy package for Microsoft Web Platform Installer."""

import sys
import os
import logging
import subprocess

logger = logging.getLogger('plone.webdeploy')


def main():
    # Run bootstrap
    bootstrap = [sys.executable, os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'zeocluster', 'bootstrap.py'), '-d']
    logger.info('Running bootstrap: %r' % ' '.join(bootstrap))
    bootstrap_p = subprocess.Popen(bootstrap)
    bootstrap_p.communicate()
    assert bootstrap_p.returncode == 0, (
        'Bootstrap failed with returncode %s' % bootstrap_p.returncode)
    # Run buildout
    buildout = [os.path.join(
        os.path.dirname(__file__), 'bin', 'buildout.exe'), '-N']
    logger.info('Running buildout: %r' % ' '.join(buildout))
    buildout_p = subprocess.Popen(buildout)
    buildout_p.communicate()
    assert buildout_p.returncode == 0, (
        'Buildout failed with returncode %s' % buildout_p.returncode)
    

if __name__ == '__main__':
    main()
