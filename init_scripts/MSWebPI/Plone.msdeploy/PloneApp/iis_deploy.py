#!/usr/bin/env python2.7

import sys
import os
import subprocess
import logging
import pprint

logger = logging.getLogger('plone.iiswsgi')


def main():
    CWD = UIDIR = PLONE_HOME = os.getcwd()
    INSTANCE_HOME = os.path.join('zinstance')
    CLIENT_USER = os.environ['USERNAME']
    ZEO_USER = ROOT_INSTALL = OFFLINE = "0"
    RUN_BUILDOUT = "0"
    INSTALL_LXML = "no"
    CLIENTS = "1"  # IIS controls number of instances
    LOG_FILE = os.path.join(PLONE_HOME, 'install.log')
    PASSWORD = '__webpi_password_parameter__'

    ITYPE = "cluster"
    INSTANCE_HOME = os.path.join('zeocluster')
    if "__webpi_zeo_parameter__".lower() == "false":
        ITYPE = "standalone"
        INSTANCE_HOME = os.path.join('zinstance')

    args = [sys.executable,
            os.path.join(UIDIR, 'helper_scripts', 'create_instance.py'),
            UIDIR, PLONE_HOME, INSTANCE_HOME, CLIENT_USER, ZEO_USER,
            PASSWORD, ROOT_INSTALL, RUN_BUILDOUT, INSTALL_LXML, OFFLINE,
            ITYPE, LOG_FILE, CLIENTS]
    logger.info('Creating the buildout: {0}'.format(' '.join(args)))
    subprocess.check_call(args)

    try:
        os.chdir(INSTANCE_HOME)

        args = [sys.executable, 'bootstrap.py', '-d']
        logger.info('Bootstrapping the buildout: {0}'.format(' '.join(args)))
        subprocess.check_call(args)

        args = [os.path.join('bin', 'buildout.exe'), '-N']
        logger.info('Setting up the buildout: {0}'.format(' '.join(args)))
        subprocess.check_call(args)

        if ITYPE == 'cluster':
            args = [os.path.join('bin', 'zeoserver_service.exe'),
                    '--startup', 'auto', 'install']
            logger.info('Installing and starting the ZEO service: {0}'.format(
                ' '.join(args)))
            subprocess.check_call(args)
    finally:
        os.chdir(CWD)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
