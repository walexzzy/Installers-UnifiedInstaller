import sys
import os
import subprocess
import shutil
import logging

from iiswsgi import options
from iiswsgi import deploy

logger = logging.getLogger('Plone.UnifiedInstaller')

requirements = (
    'http://downloads.sourceforge.net/project/pywin32/pywin32/Build%20217/pywin32-217.win32-py2.7.exe',
    'http://dist.plone.org/thirdparty/lxml-2.3.4-py2.7-win32.egg')


def main():
    """
    Expects to be run with the system python in the PloneApp directory.

    >cd Plone.msdeploy\PloneApp
    >%SYSTEMDRIVE%\Python27\python.exe ..\..\build.py

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

    for path in ('base_skeleton', 'buildout_templates', 'helper_scripts'):
        if os.path.exists(path):
            logger.info('Deleting old UI directory: {0}'.format(path))
            shutil.rmtree(path)
        logger.info('Copying UI directory: {0}'.format(path))
        shutil.copytree(os.path.join(UIDIR, path), path)

    for buildout in (INSTANCE_HOME, STANDALONE_HOME):
        if not os.path.exists(buildout):
            continue
        if os.path.exists(os.path.join(buildout, 'parts', 'omelette')):
            # Have to clean up ntfsutils.junction links before
            # removing the tree or egg contents will be deleted
            try:
                os.chdir(INSTANCE_HOME)
                args = [os.path.join(
                    'bin', 'buildout' + options.script_ext), '-N']
                logger.info(
                    'Running non-development buildout to cleanup omelette: {0}'
                    .format(' '.join(args)))
                subprocess.check_call(args)
            finally:
                os.chdir(PLONE_HOME)
        logger.info('Deleting existing buildout: {0}'.format(buildout))
        shutil.rmtree(buildout)

    deployer = deploy.Deployer(app_name='PloneApp')
    deployer.setup_virtualenv()
    deployer.easy_install_requirements(requirements=requirements)

    # Assumes sys.executable is a system python with iiswsgi installed
    args = [sys.executable, 'iis_deploy.py', '-v', '-isd']
    logger.info('Delegating to `iiswsgi.deploy`: {0}'.format(' '.join(args)))
    subprocess.check_call(args, env=environ)

    try:
        os.chdir(INSTANCE_HOME)

        # Use the `develop.cfg` config to get all the eggs the install
        args = [os.path.join('bin', 'buildout' + options.script_ext),
                '-N', '-c', 'develop.cfg']
        logger.info('Setting up the development buildout: {0}'.format(
            ' '.join(args)))
        subprocess.check_call(args)
    finally:
        os.chdir(PLONE_HOME)

    # Assumes sys.executable is a system python with iiswsgi installed
    GITHUB_EXAMPLES = os.path.join(
        os.path.dirname(os.path.dirname(options.__file__)), 'examples')
    args = [options.get_script_path('iiswsgi_build'),
            '-v', '-f', os.path.join(WEBPI_DIR, 'web-pi.xml'),
            os.path.join(GITHUB_EXAMPLES, 'sample.msdeploy'),
            os.path.join(GITHUB_EXAMPLES, 'pyramid.msdeploy'),
            os.path.join(WEBPI_DIR, 'Plone.msdeploy')]
    logger.info('Delegating to `iiswsgi.build`: {0}'.format(' '.join(args)))
    subprocess.check_call(args)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
