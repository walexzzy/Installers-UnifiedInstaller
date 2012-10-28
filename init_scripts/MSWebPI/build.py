"""
Build Plone MSDeploy and Web PI package.

Expects to be run in a virtualenv with iiswsgi installed.

>cd init_scripts/MSWebPI
>C:\Python27\Scripts\virtualenv --distribute --clear .
>Scripts\easy_install.exe -U iiswsgi
>Scripts\python.exe build.py

Since the Unified installer and buildout-cache layouts can result
in deep paths, it is best to place the UI checkout at the root of
a drive.
"""

import sys
import os
import subprocess
import shutil
import logging

import setuptools

from iiswsgi import options

# setup script
import setup

logger = logging.getLogger('Plone.UnifiedInstaller')


class clean_plone_msdeploy(setup.clean_plone_msdeploy):

    def run(self):
        setup.clean_plone_msdeploy.run(self)

        # Copy the bits of UI that need to be included in the package
        UIDIR = os.path.dirname(os.path.dirname(os.getcwd()))
        for path in ('base_skeleton', 'buildout_templates', 'helper_scripts'):
            if os.path.exists(path):
                logger.info('Deleting old UI directory: {0}'.format(path))
                shutil.rmtree(path)
            logger.info('Copying UI directory: {0}'.format(path))
            shutil.copytree(os.path.join(UIDIR, path), path)

        # Move old eggs aside
        self.clean_eggs()

    def clean_eggs(self):
        """
        Move old eggs aside to be used as --find-links.

        Thus the egg cache has only what's needed without downloading
        stuff that's already been installed.
        """
        egg_cache = os.path.join('buildout-cache', 'eggs')
        if not os.path.exists(egg_cache):
            return
        old_eggs = egg_cache + '.old'
        if not os.path.exists(old_eggs):
            os.makedirs(old_eggs)
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


def main(**kw):
    buildout_eggs = os.path.join('buildout-cache', 'eggs')
    old_eggs = buildout_eggs + '.old'

    GITHUB_EXAMPLES = os.path.join(
        os.path.dirname(os.path.dirname(options.__file__)), 'examples')
    msdeploy_bdists = [os.path.join(GITHUB_EXAMPLES, 'sample.msdeploy'),
                       os.path.join(GITHUB_EXAMPLES, 'pyramid.msdeploy'),
                       os.curdir]

    kw['cmdclass'] = dict(install_msdeploy=setup.install_plone_msdeploy,
                          clean_msdeploy=clean_plone_msdeploy)
    if not sys.argv[1:]:
        kw['script_args'] = [
            # global options
            '-v',

            # Start with a clean environment
            'clean_msdeploy',

            # Install dependencies using old eggs and special sources
            'develop', '--find-links={0}'.format(' '.join([
                os.path.abspath(old_eggs), 'http://dist.plone.org/thirdparty',
                'http://downloads.sourceforge.net/project/pywin32/pywin32'
                '/Build%20217/pywin32-217.win32-py2.7.exe'])),

            # Build the MSDeploy package files from templates
            # Have to put it here to ensure it gets run before install_msdeploy
            'bdist_msdeploy',

            # Populate the build and test the install process
            'install_msdeploy', '--skip-fcgi-app-install',

            # Create the MSDeploy package zip file
            'bdist_msdeploy',

            # Build the WebPI feed and clear the WebPI caches
            'bdist_webpi', '--msdeploy-bdists={0}'.format(
                ' '.join(msdeploy_bdists)),
            'clean_webpi',
            ]

    setuptools.setup(
        **kw)

if __name__ == '__main__':
    kw = setup.setup_kw.copy()
    main(**kw)
