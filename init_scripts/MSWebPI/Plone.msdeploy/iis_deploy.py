#!/usr/bin/env python2.7

import os
import subprocess
import logging
import re

from iiswsgi import options
from iiswsgi import deploy

logger = logging.getLogger('plone.iiswsgi')

app_name_pattern = re.compile(r'^(.*?)([0-9]*)$')


def main(install_fcgi_app=True):
    CWD = UIDIR = PLONE_HOME = os.getcwd()
    INSTANCE_HOME = os.path.join('zinstance')
    APP_NAME, COUNT = app_name_pattern.match(PLONE_HOME).groups()
    if COUNT:
        COUNT = int(COUNT)
    else:
        COUNT = 0
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

    ZEO_PORT = "__webpi_zeo_parameter__"
    ITYPE = "cluster"
    PART = 'client1'
    INSTANCE_HOME = os.path.join('zeocluster')
    if ZEO_PORT:
        try:
            ZEO_PORT = int(ZEO_PORT)
        except (ValueError, TypeError):
            # Automatic port choosing
            ZEO_PORT = 8100 + COUNT
    else:
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

    # Set the ZEO port
    buildout_cfg = open(os.path.join(INSTANCE_HOME, 'buildout.cfg')).read()
    open(os.path.join(INSTANCE_HOME, 'buildout.cfg'), 'w').write(
        buildout_cfg.replace('zeo-address = 127.0.0.1:8100',
                             'zeo-address = 127.0.0.1:{0}'.format(ZEO_PORT)))

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

    finally:
        os.chdir(CWD)

    deployer.test()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args, remaining = deploy.deploy_parser.parse_known_args()
    main(args.install_fcgi_app)
