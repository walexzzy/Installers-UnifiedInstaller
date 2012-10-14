import sys
import os
import subprocess


def main():
    PLONE_HOME = os.path.abspath(os.path.dirname(__file__))
    UIDIR = os.path.dirname(os.path.dirname(PLONE_HOME))
    INSTANCE_HOME = os.path.join(
        UIDIR, 'init_scripts', 'MSWebPI', 'Plone.msdeploy', 'zinstance')
    CLIENT_USER = os.environ['USERNAME']
    ZEO_USER = ROOT_INSTALL = OFFLINE = CLIENTS = "0"
    RUN_BUILDOUT = "1"
    INSTALL_LXML = "no"
    ITYPE = "standalone"
    LOG_FILE = os.path.join(PLONE_HOME, 'install.log')

    PASSWORD = subprocess.check_output([
        sys.executable,
        os.path.join(UIDIR, 'helper_scripts', 'generateRandomPassword.py')])

    subprocess.check_call([
        sys.executable,
        os.path.join(UIDIR, 'helper_scripts', 'create_instance.py'),
        UIDIR, PLONE_HOME, INSTANCE_HOME, CLIENT_USER, ZEO_USER,
        PASSWORD, ROOT_INSTALL, RUN_BUILDOUT, INSTALL_LXML, OFFLINE,
        ITYPE, LOG_FILE, CLIENTS])

if __name__ == '__main__':
    main()
