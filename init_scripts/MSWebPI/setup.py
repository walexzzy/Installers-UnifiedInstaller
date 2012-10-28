import sys
import os
import subprocess
import logging
import sysconfig

from distutils import cmd

from setuptools import setup

from iiswsgi import install_msdeploy
from iiswsgi import fcgi
from iiswsgi import options

version = '0.1'

logger = logging.getLogger('plone.iiswsgi')


class install_plone_msdeploy(install_msdeploy.install_msdeploy):

    def initialize_options(self):
        install_msdeploy.install_msdeploy.initialize_options(self)
        self.find_links = None

    def finalize_options(self):
        install_msdeploy.install_msdeploy.finalize_options(self)
        self.set_undefined_options('develop', ('find_links', 'find_links'))

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
            PASSWORD='__msdeploy_password_parameter__',
            BUILDOUT_DIST=os.path.join(
                CWD, 'buildout-cache', 'downloads', 'dist'),
            ZEO_PORT="__msdeploy_zeo_parameter__",
            CLIENTS="__msdeploy_clients_parameter__",
            ITYPE="cluster", PART='client1', INSTANCE_HOME='zeocluster',
            BUILDOUT_CFG='develop.cfg', WSGI_CONFIG='development.ini',
            DEVELOP=str(int("__msdeploy_develop_parameter__".lower() == "true")))

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
            if int(os.environ['DEVELOP']):
                os.environ.update(CLIENTS="1")

        install_msdeploy.install_msdeploy.run(self)

        if not os.path.exists(os.environ['BUILDOUT_DIST']):
            os.makedirs(os.environ['BUILDOUT_DIST'])

        if not os.path.exists(os.environ['INSTANCE_HOME']):
            # IIS controls number of instances, so CLIENTS here is 1
            cmd = [sys.executable, os.path.join(
                os.environ['UIDIR'], 'helper_scripts', 'create_instance.py')]
            cmd.extend(os.environ[key] for key in (
                'UIDIR', 'PLONE_HOME', 'INSTANCE_HOME', 'CLIENT_USER',
                'ZEO_USER', 'PASSWORD', 'ROOT_INSTALL', 'RUN_BUILDOUT',
                'INSTALL_LXML', 'OFFLINE', 'ITYPE', 'LOG_FILE'))
            cmd.append("1")
            logger.info('Creating the buildout: {0}'.format(' '.join(cmd)))
            subprocess.check_call(cmd)
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

            cmd = [os.path.abspath(os.path.join(sysconfig.get_path(
                    'scripts', vars=dict(base=os.pardir)),
                    'buildout' + sysconfig.get_config_var('EXE')))]
            cmd.extend(buildout_args)
            cmd.extend(['bootstrap', '-d'])
            logger.info(
                'Bootstrapping the buildout: {0}'.format(' '.join(cmd)))
            subprocess.check_call(cmd)

            cmd = [os.path.join(
                'bin', 'buildout' + sysconfig.get_config_var('EXE')),
                    '-c', os.environ['BUILDOUT_CFG']]
            cmd.extend(buildout_args)
            logger.info('Setting up the buildout: {0}'.format(' '.join(cmd)))
            subprocess.check_call(cmd)

            if os.environ['ITYPE'] == 'cluster':
                service_script = os.path.join('bin', 'zeoserver_service' +
                                              sysconfig.get_config_var('EXE'))
                if os.path.exists(service_script):
                    cmd = [service_script, '--startup', 'auto', 'install']
                    logger.info('Installing the ZEO service: {0}'.format(
                        ' '.join(cmd)))
                    subprocess.check_call(cmd)
                    cmd = [service_script, 'start']
                    logger.info('Starting the ZEO service: {0}'.format(
                        ' '.join(cmd)))
                    subprocess.check_call(cmd)
                else:
                    logger.error(
                        'ZEO service script does not exist: {0}'.format(
                                     service_script))

        finally:
            os.chdir(CWD)


class clean_plone_msdeploy(cmd.Command):
    """Clean up/uninstall the Plone installation."""

    description = __doc__

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        self.PLONE_HOME = os.getcwd()
        self.INSTANCE_HOME = os.path.join(self.PLONE_HOME, 'zeocluster')
        self.STANDALONE_HOME = os.path.join(self.PLONE_HOME, 'zinstance')
        options.ensure_verbosity(self)

    def run(self):
        if os.path.exists(self.INSTANCE_HOME):
            self.clean_zeo(self.INSTANCE_HOME)
        for buildout in (self.INSTANCE_HOME, self.STANDALONE_HOME):
            if os.path.exists(buildout):
                self.clean_buildout(buildout)

    def clean_zeo(self, buildout):
        """Stop and remove ZEO service if present."""
        try:
            os.chdir(buildout)
            service_script = os.path.join('bin', 'zeoserver_service' +
                                          sysconfig.get_config_var('EXE'))
            if os.path.exists(service_script):
                cmd = [service_script, 'stop']
                logger.info('Stopping the ZEO service: {0}'.format(
                    ' '.join(cmd)))
                subprocess.check_call(cmd)
                cmd = [service_script, 'remove']
                logger.info('Removing the ZEO service: {0}'.format(
                    ' '.join(cmd)))
                subprocess.check_call(cmd)
        finally:
            os.chdir(self.PLONE_HOME)

    def clean_buildout(self, buildout):
        """Clean up an existing buildout."""
        # Have to clean up omelette ntfsutils.junction links before
        # removing the tree or egg contents will be deleted.
        # Best in general to let buildout recipes do their thing.
        buildout_script = os.path.join(
            'bin', 'buildout' + sysconfig.get_config_var('EXE'))
        if os.path.exists(os.path.join(buildout, buildout_script)):
            cmd = [buildout_script, '-N', '-o', 'buildout:parts=']
            logger.info('Cleanup buildout: {0}'.format(' '.join(cmd)))
            try:
                os.chdir(buildout)
                subprocess.check_call(cmd)
            finally:
                os.chdir(self.PLONE_HOME)
        cmd = 'rmdir /s /q {0}'.format(buildout)
        logger.info('Deleting existing buildout: {0}'.format(cmd))
        return subprocess.check_call(cmd, shell=True)


setup(name='PloneIISApp',
      version=version,
      title="Plone Application",
      description="""
      Leading open source CMS for Content Management, Document
      Management and Knowledge Management. Get your intranet, portal,
      web site or community site up and running in minutes!""",
      long_description="""
      Plone is powerful and flexible.

      It is ideal as an intranet and extranet server, as a document publishing system, a portal server and as a groupware tool for collaboration between separately located entities.
      
      Plone is easy to use.
      The Plone Team includes usability experts who have made Plone easy and attractive for content managers to add, update, and maintain content.
      
      Plone is easy to install.
      You can install Plone with a click-and-run installer, and have a content management system running on your computer in just a few minutes.
      
      Plone is international.
      The Plone interface has been translated into over 40 languages, and tools exist for managing multilingual content.
      
      Plone is standard.
      Plone carefully follows standards for usability and accessibility. Plone pages are compliant with US Section 508, and the W3C's AA rating for accessibility, in addition to using best-practice web standards like XHTML and CSS.
      
      Plone is Open Source.
      Plone is licensed under the GNU General Public License, the same license Linux uses. This gives you the right to use Plone without a license fee, and to improve upon the product.
      
      Plone is supported.
      There are over three hundred developers in the Plone Development Team around the world, and a multitude of companies specializing in Plone development and support.
      
      Plone is extensible.
      There are many add-on products for Plone that add new features and content types. In addition, Plone can be scripted using web standard solutions and Open Source languages.
      
      Plone is technology neutral.
      Plone can interoperate with most relational database systems, open source and commercial, and runs on a vast array of platforms, including Linux, Windows, Mac OS X, Solaris and BSD.
      
      Plone is protected.
      The nonprofit Plone Foundation was formed in 2004 to promote the use of Plone around the world and protect the Plone IP and trademarks.""",
      classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        ],
      keywords='ContentMgmt Plone Zope Python Server FrameworkRuntime WSGI',
      author='Plone Foundation',
      author_email='board@plone.org',
      author_url='http://plone.org',
      url='http://plone.org',
      help_url='http://plone.org/download',
      license='GPL version 3',
      license_url='http://www.gnu.org/licenses/gpl.txt',
      icon_url='http://www.sixfeetup.com/blog/plone.png',
      screenshot_url='http://plone.org/products/plone/screenshot',
      install_requires=['iiswsgi',
                        'nt_svcutils',
                        'pywin32',
                        'ntfsutils',
                        'lxml==2.3.4',
                        'zc.buildout==1.6.3'],
      setup_requires=['setuptools-git',
                      'iiswsgi'],
      extras_require=dict(webpi_eggs=['virtualenv', 'iiswsgi']),
      install_msdeploy=['WDeploy', 'virtualenv'],
      install_webpi=['IISManagementConsole'],
      cmdclass=dict(install_msdeploy=install_plone_msdeploy,
                    clean_msdeploy=clean_plone_msdeploy),
      )
