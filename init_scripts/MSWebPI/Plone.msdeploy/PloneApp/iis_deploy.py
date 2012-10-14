#!/usr/bin/env python2.7

import sys
import os
import subprocess
import logging

logger = logging.getLogger('plone.iiswsgi')


def main():
    CWD = UIDIR = PLONE_HOME = os.getcwd()
    INSTANCE_HOME = os.path.join('zinstance')
    CLIENT_USER = os.environ['USERNAME']
    ZEO_USER = ROOT_INSTALL = OFFLINE = "0"
    RUN_BUILDOUT = "0"
    INSTALL_LXML = "no"
    ITYPE = ("__webpi_zeo_parameter__".lower() == "true" and "cluster"
             or "standalone")
    CLIENTS = "1"  # IIS controls number of instances
    LOG_FILE = os.path.join(PLONE_HOME, 'install.log')

    PASSWORD = '__webpi_password_parameter__'
    subprocess.check_call([
        sys.executable,
        os.path.join(UIDIR, 'helper_scripts', 'create_instance.py'),
        UIDIR, PLONE_HOME, INSTANCE_HOME, CLIENT_USER, ZEO_USER,
        PASSWORD, ROOT_INSTALL, RUN_BUILDOUT, INSTALL_LXML, OFFLINE,
        ITYPE, LOG_FILE, CLIENTS])

    try:
        os.chdir(INSTANCE_HOME)
        subprocess.check_call([sys.executable, 'bootstrap.py', '-d'])
        subprocess.check_call([os.path.join('bin', 'buildout.exe'), '-N'])
    finally:
        os.chdir(CWD)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
