#!/usr/bin/env python2.7

import os
import subprocess
import logging

from iiswsgi import options
from iiswsgi import deploy

logger = logging.getLogger('plone.iiswsgi')


def main(install_fcgi_app=True):
    CWD = UIDIR = PLONE_HOME = os.getcwd()
    INSTANCE_HOME = os.path.join('zinstance')
    CLIENT_USER = os.environ.get('USERNAME')
    if CLIENT_USER is None:
        # Non-Windows compat for testing
        CLIENT_USER = os.environ['USER']
    ZEO_USER = ROOT_INSTALL = OFFLINE = "0"
    RUN_BUILDOUT = "0"
    INSTALL_LXML = "no"
    CLIENTS = "1"  # IIS controls number of instances
    LOG_FILE = os.path.join(PLONE_HOME, 'install.log')
    PASSWORD = '__webpi_password_parameter__'
    BUILDOUT_DIST = os.path.join(
        PLONE_HOME, 'buildout-cache', 'downloads', 'dist')

    ITYPE = "cluster"
    PART = 'client1'
    INSTANCE_HOME = os.path.join('zeocluster')
    if "__webpi_zeo_parameter__".lower() == "false":
        ITYPE = "standalone"
        PART = 'instance'
        PART  # pyflakes, used in web.config
        INSTANCE_HOME = os.path.join('zinstance')

    BUILDOUT_CFG = 'develop.cfg'
    WSGI_CONFIG = 'development.ini'
    if "__webpi_develop_parameter__".lower() == "false":
        BUILDOUT_CFG = 'buildout.cfg'
        WSGI_CONFIG = 'production.ini'
    WSGI_CONFIG  # pyflakes, used web.config

    logger.info('Delegate to "iiswsgi.deploy" for the normal deployment')
    deployer = deploy.Deployer(
        app_name='PloneApp', install_fcgi_app=install_fcgi_app,
        find_links=(
            os.path.join(PLONE_HOME, 'buildout-cache', 'eggs'),))
    deployer.deploy(**locals())

    if not os.path.exists(BUILDOUT_DIST):
        os.makedirs(BUILDOUT_DIST)

    if not os.path.exists(INSTANCE_HOME):
        args = [deployer.executable,
                os.path.join(UIDIR, 'helper_scripts', 'create_instance.py'),
                UIDIR, PLONE_HOME, INSTANCE_HOME, CLIENT_USER, ZEO_USER,
                PASSWORD, ROOT_INSTALL, RUN_BUILDOUT, INSTALL_LXML, OFFLINE,
                ITYPE, LOG_FILE, CLIENTS]
        logger.info('Creating the buildout: {0}'.format(' '.join(args)))
        subprocess.check_call(args)
    else:
        logger.warn('The buildout already exists: {0}'.format(INSTANCE_HOME))

    try:
        os.chdir(INSTANCE_HOME)

        args = [options.get_script_path(
                'buildout', deployer.executable), 'bootstrap', '-d']
        logger.info('Bootstrapping the buildout: {0}'.format(' '.join(args)))
        subprocess.check_call(args)

        args = [os.path.join('bin', 'buildout' + options.script_ext), '-N',
                '-c', BUILDOUT_CFG]
        logger.info('Setting up the buildout: {0}'.format(' '.join(args)))
        subprocess.check_call(args)

        if ITYPE == 'cluster':
            service_script = os.path.join(
                'bin', 'zeoserver_service' + options.script_ext)
            if os.path.exists(service_script):
                args = [service_script, '--startup', 'auto', 'install']
                logger.info('Installing the ZEO service: {0}'.format(
                    ' '.join(args)))
                subprocess.check_call(args)
                args = [service_script, 'start']
                logger.info('Starting the ZEO service: {0}'.format(
                    ' '.join(args)))
                subprocess.check_call(args)
            else:
                logger.error('ZEO service script does not exist: {0}'.format(
                                 service_script))

        args = [os.path.join('bin', 'iiswsgi' + options.script_ext),
                '--test', '-c', WSGI_CONFIG]
        logger.info('Testing the Zope WSGI app: {0}'.format(
            ' '.join(args)))
        subprocess.check_call(args)
    finally:
        os.chdir(CWD)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args, remaining = deploy.deploy_parser.parse_known_args()
    main(args.install_fcgi_app)
