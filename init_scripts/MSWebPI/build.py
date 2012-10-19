import sys
import os
import subprocess
import shutil
import logging
import urllib2
import urlparse

from iiswsgi import options

logger = logging.getLogger('Plone.UnifiedInstaller')

lxml_url = 'http://dist.plone.org/thirdparty/lxml-2.3.4-py2.7-win32.egg'


def download_url(url, file):
    req = urllib2.urlopen(url)
    CHUNK = 16 * 1024
    with open(file, 'wb') as fp:
        chunk = req.read(CHUNK)
        while chunk:
            fp.write(chunk)
            chunk = req.read(CHUNK)


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

    if os.path.exists(INSTANCE_HOME):
        shutil.rmtree(INSTANCE_HOME)
    if os.path.exists(STANDALONE_HOME):
        shutil.rmtree(STANDALONE_HOME)

    # Manually add binary lxml egg since buildout doesn't seem to use
    # it even with find-links
    lxml_egg = os.path.join(
        BUILDOUT_DIST,
        urlparse.urlsplit(lxml_url).path.rsplit('/', 1)[-1])
    if os.path.exists(lxml_egg):
        logger.info('Deleting old lxml binary egg: {0}'.format(lxml_egg))
        os.remove(lxml_egg)
    logger.info('Downloading lxml binary egg: {0}'.format(lxml_url))
    download_url(lxml_url, lxml_egg)

    # Assumes sys.executable is a system python with iiswsgi installed
    args = [options.get_script_path('iiswsgi_deploy'), '-v', '-isd']
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
