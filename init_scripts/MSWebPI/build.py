import sys
import os
import subprocess
import shutil
import logging

from iiswsgi import options
from iiswsgi import install_msdeploy

logger = logging.getLogger('Plone.UnifiedInstaller')


def main():
    """
    Build Plone MSDeploy and Web PI package.

    Expects to be run with the system python with iiswsgi installed in
    the PloneApp directory.

    >cd Plone.msdeploy
    >%SYSTEMDRIVE%\Python27\python.exe ..\build.py

    Since the Unified installer and buildout-cache layouts can result
    in deep paths, it is best to place the UI checkout at the root of
    a drive.
    """
    WEBPI_DIR = os.path.dirname(os.path.abspath(__file__))
    UIDIR = os.path.dirname(os.path.dirname(WEBPI_DIR))

    # Copy the bits of UI that need to be included in the package
    for path in ('base_skeleton', 'buildout_templates', 'helper_scripts'):
        if os.path.exists(path):
            logger.info('Deleting old UI directory: {0}'.format(path))
            shutil.rmtree(path)
        logger.info('Copying UI directory: {0}'.format(path))
        shutil.copytree(os.path.join(UIDIR, path), path)

    # Clean up zeo, buildout, eggs
    cmd = [sys.executable, 'setup.py', '-v', 'clean_msdeploy']
    logger.info('Cleaning up: {0}'.format(' '.join(cmd)))
    subprocess.check_call(cmd)
    buildout_eggs = os.path.join('buildout-cache', 'eggs')
    old_eggs = buildout_eggs + '.old'

    # Build the package with iiswsgi_install
    installer = install_msdeploy.Installer(
        app_name='PloneApp', require_stamp=False,
        install_fcgi_app=False, virtualenv=True)
    installer(['develop', '--find-links={0} {1}'.format(
        os.path.abspath(old_eggs), 'http://dist.plone.org/thirdparty'),
               'bdist_msdeploy'])

    # use bdist_webpi to update the WebPI feed
    GITHUB_EXAMPLES = os.path.join(
        os.path.dirname(os.path.dirname(options.__file__)), 'examples')
    msdeploy_bdists = [os.path.join(GITHUB_EXAMPLES, 'sample.msdeploy'),
                       os.path.join(GITHUB_EXAMPLES, 'pyramid.msdeploy'),
                       os.path.join(WEBPI_DIR, 'Plone.msdeploy')]
    cmd = [sys.executable, 'setup.py', '-v', 'bdist_webpi',
           '--msdeploy-bdists={0}'.format(' '.join(msdeploy_bdists)),
           'clean_webpi']
    logger.info('Building the WebPI feed: {0}'.format(
        ' '.join(cmd)))
    subprocess.check_call(cmd)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
