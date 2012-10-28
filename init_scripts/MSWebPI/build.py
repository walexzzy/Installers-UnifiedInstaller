import sys
import os
import subprocess
import shutil
import logging

import distutils.sysconfig

from iiswsgi import options
from iiswsgi import install_msdeploy

logger = logging.getLogger('Plone.UnifiedInstaller')


def main():
    """
    Build Plone MSDeploy and Web PI package.

    Expects to be run with the system python with iiswsgi installed.

    >%SYSTEMDRIVE%\Python27\easy_install.exe -U iiswsgi[config,webpi]
    >cd init_scripts/MSWebPI
    >%SYSTEMDRIVE%\Python27\python.exe build.py

    Since the Unified installer and buildout-cache layouts can result
    in deep paths, it is best to place the UI checkout at the root of
    a drive.
    """
    UIDIR = os.path.dirname(os.path.dirname(os.getcwd()))

    # Copy the bits of UI that need to be included in the package
    for path in ('base_skeleton', 'buildout_templates', 'helper_scripts'):
        if os.path.exists(path):
            logger.info('Deleting old UI directory: {0}'.format(path))
            shutil.rmtree(path)
        logger.info('Copying UI directory: {0}'.format(path))
        shutil.copytree(os.path.join(UIDIR, path), path)

    # Clean up zeo, buildout
    cmd = [sys.executable, 'setup.py', '-v', 'clean_msdeploy']
    logger.info('Cleaning up: {0}'.format(' '.join(cmd)))
    subprocess.check_call(cmd)

    # Move old eggs aside
    clean_eggs()
    buildout_eggs = os.path.join('buildout-cache', 'eggs')
    old_eggs = buildout_eggs + '.old'

    # Build the package with iiswsgi_install
    installer = install_msdeploy.Installer(
        app_name='PloneIISApp', require_stamp=False,
        install_fcgi_app=False, virtualenv=True)
    installer(['develop', '--find-links={0}'.format(' '.join([
        os.path.abspath(old_eggs), 'http://dist.plone.org/thirdparty',
        'http://downloads.sourceforge.net/project/pywin32/pywin32'
        '/Build%20217/pywin32-217.win32-py2.7.exe'])),
               'bdist_msdeploy'])

    # use bdist_webpi to update the WebPI feed
    GITHUB_EXAMPLES = os.path.join(
        os.path.dirname(os.path.dirname(options.__file__)), 'examples')
    msdeploy_bdists = [os.path.join(GITHUB_EXAMPLES, 'sample.msdeploy'),
                       os.path.join(GITHUB_EXAMPLES, 'pyramid.msdeploy'),
                       os.curdir]
    cmd = [sys.executable, 'setup.py', '-v', 'bdist_webpi',
           '--msdeploy-bdists={0}'.format(' '.join(msdeploy_bdists)),
           'clean_webpi']
    logger.info('Building the WebPI feed: {0}'.format(
        ' '.join(cmd)))
    subprocess.check_call(cmd)


def clean_eggs():
    """
    Move old eggs aside to be used as --find-links.

    Thus the egg cache has only what's needed without downloading
    stuff that's already been installed.
    """
    virtualenv_eggs = distutils.sysconfig.get_python_lib(prefix=os.curdir)
    buildout_eggs = os.path.join('buildout-cache', 'eggs')
    old_eggs = buildout_eggs + '.old'
    if not os.path.exists(old_eggs):
        os.makedirs(old_eggs)
    for egg_cache in (virtualenv_eggs, buildout_eggs):
        if not os.path.exists(egg_cache):
            continue
        logger.info('Moving existing eggs aside: {0}'.format(egg_cache))
        for egg in os.listdir(egg_cache):
            old_egg = os.path.join(old_eggs, egg)
            while os.path.isdir(old_egg):
                cmd = 'rmdir /s /q {0}'.format(old_egg)
                subprocess.check_call(cmd, shell=True)
            else:
                if os.path.exists(old_egg):
                    os.remove(old_egg)
            os.rename(os.path.join(egg_cache, egg), old_egg)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
