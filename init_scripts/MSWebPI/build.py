"""
Build Plone MSDeploy and Web PI package.

Expects to be run in a virtualenv with iiswsgi installed.

>cd init_scripts/MSWebPI
>C:\Python27\Scripts\virtualenv --distribute --clear .
>Scripts\easy_install.exe -U iiswsgi
>Scripts\python.exe build.py release
>Scripts\python.exe build.py release_feed

Since the Unified installer and buildout-cache layouts can result
in deep paths, it is best to place the UI checkout at the root of
a drive.
"""

import os
import subprocess
import shutil
import logging

import setuptools

# setup script
import setup

logger = logging.getLogger('Plone.UnifiedInstaller')


class clean_plone_msdeploy(setup.clean_plone_msdeploy):
    """Do additional cleaning beyond what's in the distributed setup.py."""

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
    kw['cmdclass'] = dict(install_msdeploy=setup.install_plone_msdeploy,
                          clean_msdeploy=clean_plone_msdeploy)
    setuptools.setup(**kw)

if __name__ == '__main__':
    kw = setup.setup_kw.copy()
    # Explicit versions of the packages needed both in the virtualenv
    # and in buildout so that buildout will run without complainging
    # about version conflicts.
    kw['install_requires'] += [
        'virtualenv',
        'zope.interface==3.6.7',
        'zope.pagetemplate==3.5.2',
        'pytz==2012c',
        'RestrictedPython==3.6.0',
        'zope.browser==1.3',
        'zope.component==3.9.5',
        'zope.configuration==3.7.4',
        'zope.contenttype==3.5.5',
        'zope.event==3.5.2',
        'zope.exceptions==3.6.2',
        'zope.i18n==3.7.4',
        'zope.i18nmessageid==3.5.3',
        'zope.location==3.9.1',
        'zope.proxy==3.6.1',
        'zope.publisher==3.12.6',
        'zope.schema==4.2.0',
        'zope.security==3.7.4',
        'zope.tal==3.5.2',
        'zope.tales==3.5.2',
        'zope.traversing==3.13.2']
    # Package the release setup.py, not this script
    kw['script_name'] = 'setup.py'
    main(**kw)


# TODO use aliases
