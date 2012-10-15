import sys
import os
import subprocess
import shutil
import logging
import urllib2
import urlparse

logger = logging.getLogger('Plone.UnifiedInstaller')

lxml_url = 'http://dist.plone.org/thirdparty/lxml-2.3.4-py2.7-win32.egg'


def main():
    """
    Expects to be run with the system python in the PloneApp directory.

    >cd Plone.msdeploy\PloneApp
    >%SYSTEMDRIVE%\Python27\python.exe ..\..\build.py
    """
    WEBPI_DIR = os.path.dirname(os.path.abspath(__file__))
    UIDIR = os.path.dirname(os.path.dirname(WEBPI_DIR))
    PLONE_HOME = os.getcwd()
    INSTANCE_HOME = os.path.join(PLONE_HOME, 'zinstance')
    BUILDOUT_DIST = os.path.join(
        PLONE_HOME, 'buildout-cache', 'downloads', 'dist')

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

    if not os.path.exists(BUILDOUT_DIST):
        os.makedirs(BUILDOUT_DIST)
    # Manually add binary lxml egg since buildout doesn't seem to use
    # it even with find-links
    lxml_egg = os.path.join(
        BUILDOUT_DIST,
        urlparse.urlsplit(lxml_url).path.rsplit('/', 1)[-1])
    if not os.path.exists(lxml_egg):
        open(lxml_egg, 'w').write(urllib2.urlopen(lxml_url).read())

    # Assumes sys.executable is a system python with iiswsgi installed
    args = [os.path.join(os.path.dirname(sys.executable), 'Scripts',
                         'iiswsgi_deploy.exe'), '-vvis']
    logger.info('Delegating to `iiswsgi.deploy`: {0}'.format(' '.join(args)))
    subprocess.check_call(args, env=environ)

    # Assumes sys.executable is a system python with iiswsgi installed
    args = [os.path.join(os.path.dirname(sys.executable), 'Scripts',
                         'iiswsgi_build.exe'),
            '-vv', '-f', os.path.join(WEBPI_DIR, 'web-pi.xml'),
            os.path.join(WEBPI_DIR, 'Plone.msdeploy')]
    logger.info('Delegating to `iiswsgi.build`: {0}'.format(' '.join(args)))
    subprocess.check_call(args)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
