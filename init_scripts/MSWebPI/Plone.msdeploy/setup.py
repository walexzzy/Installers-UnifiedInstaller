import os
import subprocess
import logging

from distutils.core import setup

from iiswsgi import install_msdeploy
from iiswsgi import fcgi
from iiswsgi import options

version = '0.1'

logger = logging.getLogger('plone.iiswsgi')


class install_plone_msdeploy(install_msdeploy.install_msdeploy):

    def run(self):
        """Reproduce UI behavior."""
        CWD = UIDIR = PLONE_HOME = os.getcwd()
        APP_NAME = self.distribution.get_name()
        APP_NAME  # pyflakes
        COUNT = self.count
        CLIENT_USER = os.environ.get('USERNAME')
        if CLIENT_USER is None:
            # Non-Windows compat for testing
            CLIENT_USER = os.environ['USER']
        ZEO_USER = ROOT_INSTALL = OFFLINE = "0"
        RUN_BUILDOUT = "0"
        INSTALL_LXML = "no"
        LOG_FILE = os.path.join(PLONE_HOME, 'install.log')
        PASSWORD = '__webpi_password_parameter__'
        BUILDOUT_DIST = os.path.join(
            PLONE_HOME, 'buildout-cache', 'downloads', 'dist')

        ZEO_PORT = "__webpi_zeo_parameter__"
        ITYPE = "cluster"
        PART = 'client1'
        INSTANCE_HOME = 'zeocluster'
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
            INSTANCE_HOME = 'zinstance'

        BUILDOUT_CFG = 'develop.cfg'
        WSGI_CONFIG = 'development.ini'
        DEVELOP = "__webpi_develop_parameter__".lower() == "false"
        if DEVELOP:
            # TODO uncomment when all auto-checkout dists in
            # base_skeleton/develop.cfg have been released
            # BUILDOUT_CFG = 'buildout.cfg'
            WSGI_CONFIG = 'production.ini'
        WSGI_CONFIG  # pyflakes, used web.config

        CLIENTS = "__webpi_clients_parameter__"
        try:
            CLIENTS = int(CLIENTS)
        except (ValueError, TypeError):
            CLIENTS = fcgi.app_attr_defaults_init['maxInstances']
            if DEVELOP:
                CLIIENTS = 1
                CLIIENTS  # pyflakes

        substitutions = locals()
        substitutions.pop('self', None)
        self.install(**substitutions)

        if not os.path.exists(BUILDOUT_DIST):
            os.makedirs(BUILDOUT_DIST)

        if not os.path.exists(INSTANCE_HOME):
            # IIS controls number of instances, so CLIENTS here is 1
            args = [
                self.executable,
                os.path.join(UIDIR, 'helper_scripts', 'create_instance.py'),
                UIDIR, PLONE_HOME, INSTANCE_HOME, CLIENT_USER, ZEO_USER,
                PASSWORD, ROOT_INSTALL, RUN_BUILDOUT, INSTALL_LXML, OFFLINE,
                ITYPE, LOG_FILE, "1"]
            logger.info('Creating the buildout: {0}'.format(' '.join(args)))
            subprocess.check_call(args)
        else:
            logger.warn(
                'The buildout already exists: {0}'.format(INSTANCE_HOME))

        # Set the ZEO port
        buildout_cfg = open(os.path.join(INSTANCE_HOME, 'buildout.cfg')).read()
        logger.info('Updating the ZEO port: {0}'.format(ZEO_PORT))
        open(os.path.join(INSTANCE_HOME, 'buildout.cfg'), 'w').write(
            buildout_cfg.replace(
                'zeo-address = 127.0.0.1:8100',
                'zeo-address = 127.0.0.1:{0}'.format(ZEO_PORT)))

        find_links = ['buildout:find-links+={0}'.format(link) for
                      link in self.find_links or ()]
        try:
            os.chdir(INSTANCE_HOME)

            args = [options.get_script_path('buildout', self.executable)]
            args.extend(find_links)
            args.extend(['bootstrap', '-d'])
            logger.info(
                'Bootstrapping the buildout: {0}'.format(' '.join(args)))
            subprocess.check_call(args)

            args = [os.path.join('bin', 'buildout' + options.script_ext), '-N',
                    '-c', BUILDOUT_CFG]
            args.extend(find_links)
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
                    logger.error(
                        'ZEO service script does not exist: {0}'.format(
                                     service_script))

        finally:
            os.chdir(CWD)

        self.test()

setup(name='PloneApp',
      version=version,
      description="""Plone application project.""",
      classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        ],
      keywords='python Plone IIS FastCGI WSGI',
      author='Plone Foundation',
      author_email='board@plone.org',
      url='http://plone.org',
      license='GPL version 3',
      setup_requires=['setuptools-git',
                      'iiswsgi'],
      cmdclass=dict(install_msdeploy=install_plone_msdeploy),
      )
