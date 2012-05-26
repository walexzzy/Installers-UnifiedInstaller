from distutils.core import setup
from distutils.command import build

version = '4.2'


class MSDeployBuild(build.build):
    """Build an MSDeploy zip packages for installation into IIS."""

    def initialize_options(self):
        """Be more discriminating about what to prune."""
        build.build.initialize_options(self)
        self.build_base = 'build/'


setup(name='PloneInstaller',
      version=version,
      description="Installer for the Plone Content Management System",
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        ],
      keywords='Plone CMF python Zope',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://plone.org/',
      license='GPL version 2',
      cmdclass={'build': MSDeployBuild},
      )
