#!/usr/bin/env python2.7

import sys
import os
import subprocess
import logging
import pprint

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

    logger.info('Delegate to "iiswsgi.deploy" for the normal deployment')
    deployer = deploy.Deployer(app_name='PloneApp',
                               install_fcgi_app=install_fcgi_app)
    deployer.deploy(**locals())

    if not os.path.exists(BUILDOUT_DIST):
        os.makedirs(BUILDOUT_DIST)

    if not os.path.exists(INSTANCE_HOME):
        args = [sys.executable,
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

        args = [sys.executable, 'bootstrap.py', '-d']
        logger.info('Bootstrapping the buildout: {0}'.format(' '.join(args)))
        subprocess.check_call(args)

        args = [os.path.join(
            options.scripts_name, 'buildout' + options.script_ext), '-N']
        logger.info('Setting up the buildout: {0}'.format(' '.join(args)))
        subprocess.check_call(args)

        if ITYPE == 'cluster':
            service_script = os.path.join(
                options.scripts_name, 'zeoserver_service' + options.script_ext)
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

            args = [os.path.join(
            options.scripts_name, 'iiswsgi' + options.script_ext), '--test']
            logger.info('Testing the Zope WSGI app: {0}'.format(
                ' '.join(args)))
            subprocess.check_call(args)
    finally:
        os.chdir(CWD)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args, remaining = deploy.deploy_parser.parse_known_args()
    main(args.install_fcgi_app)
