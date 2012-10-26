import os
import subprocess
import logging
import sysconfig

from distutils.core import setup

from iiswsgi import install_msdeploy
from iiswsgi import fcgi

version = '0.1'

logger = logging.getLogger('plone.iiswsgi')


class install_plone_msdeploy(install_msdeploy.install_msdeploy):

    def run(self):
        """Reproduce UI behavior."""
        CWD = os.getcwd()
        os.environ.update(
            CWD=CWD, UIDIR=CWD, PLONE_HOME=CWD,
            CLIENT_USER=os.environ.get('USERNAME', os.environ.get('USER', '')),
            APP_NAME=self.distribution.get_name(), COUNT=str(self.count),
            ZEO_USER="0", ROOT_INSTALL="0", OFFLINE="0", RUN_BUILDOUT="0",
            INSTALL_LXML="no",
            LOG_FILE=os.path.join(CWD, 'install.log'),
            PASSWORD='__webpi_password_parameter__',
            BUILDOUT_DIST=os.path.join(
                CWD, 'buildout-cache', 'downloads', 'dist'),
            ZEO_PORT="__webpi_zeo_parameter__",
            CLIENTS="__webpi_clients_parameter__",
            ITYPE="cluster", PART='client1', INSTANCE_HOME='zeocluster',
            BUILDOUT_CFG='develop.cfg', WSGI_CONFIG='development.ini',
            DEVELOP=str(int("__webpi_develop_parameter__".lower() == "false")))

        if os.environ['ZEO_PORT']:
            try:
                os.environ.update(ZEO_PORT=str(int(os.environ['ZEO_PORT'])))
            except (ValueError, TypeError):
                # Automatic port choosing
                os.environ.update(ZEO_PORT=str(8100 + self.count))
        else:
            os.environ.update(ITYPE="standalone",
                              PART='instance',
                              INSTANCE_HOME='zinstance')

        if int(os.environ['DEVELOP']):
            # TODO uncomment when all auto-checkout dists in
            # base_skeleton/develop.cfg have been released
            os.environ.update(
                # BUILDOUT_CFG='buildout.cfg',
                WSGI_CONFIG='production.ini')

        try:
            os.environ.update(CLIENTS=int(os.environ['CLIENTS']))
        except (ValueError, TypeError):
            os.environ.update(
                CLIENTS=str(fcgi.app_attr_defaults_init['maxInstances']))
            if os.environ['DEVELOP']:
                os.environ.update(CLIIENTS="1")

        self.install()

        if not os.path.exists(os.environ['BUILDOUT_DIST']):
            os.makedirs(os.environ['BUILDOUT_DIST'])

        if not os.path.exists(os.environ['INSTANCE_HOME']):
            # IIS controls number of instances, so CLIENTS here is 1
            args = [self.executable, os.path.join(
                os.environ['UIDIR'], 'helper_scripts', 'create_instance.py')]
            args.extend(os.environ[key] for key in (
                'UIDIR', 'PLONE_HOME', 'INSTANCE_HOME', 'CLIENT_USER',
                'ZEO_USER', 'PASSWORD', 'ROOT_INSTALL', 'RUN_BUILDOUT',
                'INSTALL_LXML', 'OFFLINE', 'ITYPE', 'LOG_FILE'))
            args.append("1")
            logger.info('Creating the buildout: {0}'.format(' '.join(args)))
            subprocess.check_call(args)
        else:
            logger.warn('The buildout already exists: {INSTANCE_HOME}'.format(
                **os.environ))

        # Set the ZEO port
        buildout_cfg = open(os.path.join(
            os.environ['INSTANCE_HOME'], 'buildout.cfg')).read()
        logger.info('Updating the ZEO port: {ZEO_PORT}'.format(**os.environ))
        open(os.path.join(
            os.environ['INSTANCE_HOME'], 'buildout.cfg'), 'w').write(
            buildout_cfg.replace(
                'zeo-address = 127.0.0.1:8100',
                'zeo-address = 127.0.0.1:{ZEO_PORT}'.format(**os.environ)))

        buildout_args = ['-N']
        if self.find_links:
            # Use find-links as a local cache to simulate offline
            # access with fallback to online retrieval
            buildout_args.extend('buildout:find-links+={0}'.format(link)
                                 for link in self.find_links)
        else:
            # default to offline
            buildout_args.append('-o')
        try:
            os.chdir(os.environ['INSTANCE_HOME'])

            args = [self.get_script_path('buildout', base=os.pardir)]
            args.extend(buildout_args)
            args.extend(['bootstrap', '-d'])
            logger.info(
                'Bootstrapping the buildout: {0}'.format(' '.join(args)))
            subprocess.check_call(args)

            args = [os.path.join(
                'bin', 'buildout' + sysconfig.get_config_var('EXE')),
                    '-c', os.environ['BUILDOUT_CFG']]
            args.extend(buildout_args)
            logger.info('Setting up the buildout: {0}'.format(' '.join(args)))
            subprocess.check_call(args)

            if os.environ['ITYPE'] == 'cluster':
                service_script = os.path.join('bin', 'zeoserver_service' +
                                              sysconfig.get_config_var('EXE'))
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
      install_requires=['iiswsgi',
                        'nt_svcutils',
                        'pywin32',
                        'ntfsutils',
                        'lxml==2.3.4',
                        'zc.buildout==1.6.3'],
      setup_requires=['setuptools-git',
                      'iiswsgi'],
      cmdclass=dict(install_msdeploy=install_plone_msdeploy),
      )
