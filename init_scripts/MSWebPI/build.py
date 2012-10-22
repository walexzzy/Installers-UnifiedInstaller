import os
import subprocess
import shutil
import logging

from distutils import core

from iiswsgi import options

logger = logging.getLogger('Plone.UnifiedInstaller')

requirements = dict(
    pywin='http://downloads.sourceforge.net/project/pywin32/pywin32/Build%20217/pywin32-217.win32-py2.7.exe',
    lxml='http://dist.plone.org/thirdparty/lxml-2.3.4-py2.7-win32.egg')


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
    PLONE_HOME = os.getcwd()
    INSTANCE_HOME = os.path.join(PLONE_HOME, 'zeocluster')
    STANDALONE_HOME = os.path.join(PLONE_HOME, 'zinstance')

    environ = os.environ.copy()
    environ['APPL_PHYSICAL_PATH'] = PLONE_HOME

    # Copy the bits of UI that need to be included in the package
    for path in ('base_skeleton', 'buildout_templates', 'helper_scripts'):
        if os.path.exists(path):
            logger.info('Deleting old UI directory: {0}'.format(path))
            shutil.rmtree(path)
        logger.info('Copying UI directory: {0}'.format(path))
        shutil.copytree(os.path.join(UIDIR, path), path)

    if os.path.exists(INSTANCE_HOME):
        # Stop and remove ZEO service if present
        try:
            os.chdir(INSTANCE_HOME)
            service_script = os.path.join(
            'bin', 'zeoserver_service' + options.script_ext)
            if os.path.exists(service_script):
                args = [service_script, 'stop']
                logger.info('Stopping the ZEO service: {0}'.format(
                    ' '.join(args)))
                subprocess.check_call(args)
                args = [service_script, 'remove']
                logger.info('Removing the ZEO service: {0}'.format(
                    ' '.join(args)))
                subprocess.check_call(args)
        finally:
            os.chdir(PLONE_HOME)

    # Clean up any existing buildouts
    for buildout in (INSTANCE_HOME, STANDALONE_HOME):
        if not os.path.exists(buildout):
            continue
        if os.path.exists(os.path.join(buildout, 'parts', 'omelette')):
            # Have to clean up ntfsutils.junction links before
            # removing the tree or egg contents will be deleted
            try:
                os.chdir(buildout)
                args = [os.path.join('bin', 'buildout' + options.script_ext),
                        '-N', '-o', 'buildout:parts=']
                logger.info(
                    'Running non-development buildout to cleanup omelette: {0}'
                    .format(' '.join(args)))
                subprocess.check_call(args)
            finally:
                os.chdir(PLONE_HOME)
        args = 'rmdir /s /q {0}'.format(buildout)
        logger.info('Deleting existing buildout: {0}'.format(args))
        subprocess.check_call(args, shell=True)

    # Install dependencies that can't be found correctly by normal easy_install
    dist = core.run_setup('setup.py')
    install = dist.get_command_obj('install_msdeploy')
    install.executable = install.setup_virtualenv()
    reqs = tuple(
        url for req, url in requirements.iteritems() if subprocess.call(
            [install.executable, '-c', 'import {0}'.format(req)]))
    if reqs:
        install.easy_install_requirements(requirements=reqs)

    old_eggs = os.path.join('buildout-cache.old', 'eggs')
    if os.path.exists('buildout-cache'):
        cache_eggs = os.path.join('buildout-cache', 'eggs')
        # Move old buildout-cache aside and use as --find-links so that
        # the new buildout-cache has only what's needed without
        # downloading stuff that's already been installed
        if not os.path.exists(old_eggs):
            os.makedirs(old_eggs)

        logger.info('Moving buildout-cache eggs aside')
        for egg in os.listdir(cache_eggs):
            old_egg = os.path.join(old_eggs, egg)
            while os.path.isdir(old_egg):
                cmd = 'rmdir /s /q {0}'.format(old_egg)
                subprocess.check_call(cmd, shell=True)
            else:
                if os.path.exists(old_egg):
                    os.remove(old_egg)
            os.rename(os.path.join(cache_eggs, egg), old_egg)

    # Use iiswsgi.build to make the packages and update the WebPI feed
    GITHUB_EXAMPLES = os.path.join(
        os.path.dirname(os.path.dirname(options.__file__)), 'examples')
    args = [options.get_script_path('iiswsgi_webpi'),
            '-v', '-f', os.path.join(WEBPI_DIR, 'web-pi.xml'),
            '-p', os.path.join(GITHUB_EXAMPLES, 'sample.msdeploy'),
            '-p', os.path.join(GITHUB_EXAMPLES, 'pyramid.msdeploy'),
            '-p', os.path.join(WEBPI_DIR, 'Plone.msdeploy'),
            'bdist_msdeploy', '--index={0}'.format(
                os.path.join(os.pardir, old_eggs)),
            '--find-links=http://pypi.python.org/simple']
    logger.info('Delegating to `iiswsgi.build`: {0}'.format(' '.join(args)))
    subprocess.check_call(args)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
