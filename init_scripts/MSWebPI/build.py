import sys
import os
import subprocess
import shutil
import logging

logger = logging.getLogger('Plone.UnifiedInstaller')


def main():
    """
    Expects to be run with the system python in the PloneApp directory.

    >cd Plone.msdeploy\PloneApp
    >%SYSTEMDRIVE%\Python27\python.exe ..\..\build.py
    """
    UIDIR = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    PLONE_HOME = os.getcwd()
    INSTANCE_HOME = os.path.join(PLONE_HOME, 'zinstance')
    BUILDOUT_DIST = os.path.join(
        PLONE_HOME, 'buildout-cache', 'downloads', 'dist')

    for path in ('base_skeleton', 'buildout_templates', 'helper_scripts'):
        if os.path.exists(path):
            logger.info('Deleting old UI directory: {0}'.format(path))
            shutil.rmtree(path)
        logger.info('Copying UI directory: {0}'.format(path))
        shutil.copytree(os.path.join(UIDIR, path), path)

    if os.path.exists(INSTANCE_HOME):
        shutil.rmtree(INSTANCE_HOME)

    if not os.path.exists(BUILDOUT_DIST):
        os.makedirs(BUILDOUT_DIST)

    # Assumes sys.executable is a system python with iiswsgi installed
    args = [os.path.join(os.path.dirname(sys.executable), 'Scripts',
                         'iiswsgi_deploy.exe'), '-vvis']
    logger.info('Delegating to `iiswsgi.deploy`: {0}'.format(' '.join(args)))
    subprocess.check_call(args)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
