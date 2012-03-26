"""Deplpy as a Web Deploy package for Microsoft Web Platform Installer."""

import sys
import os
import logging

logger = logging.getLogger('plone.webdeploy')


def main():
    # Run bootstrap
    bootstrap = [sys.executable, os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'zeocluster', 'bootstrap.py'), '-d']
    logger.info('Running bootstrap: %r' % ' '.join(bootstrap))
    assert os.system(' '.join(bootstrap)) == 0, 'Bootstrap failed'
    # Run buildout
    buildout = [os.path.join(
        os.path.dirname(__file__), 'bin', 'buildout.exe'), '-N']
    logger.info('Running buildout: %r' % ' '.join(buildout))
    assert os.system(' '.join(buildout)) == 0, 'Buildout failed'
    

if __name__ == '__main__':
    main()
