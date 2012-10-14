from distutils.core import setup

try:
    from iiswsgi.setup import cmdclass
    cmdclass  # pyflakes
except ImportError:
    cmdclass = dict()

version = '0.1'

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
      # TODO get the custom commands to work without iiswsgi installed
      # in the python
      setup_requires=['setuptools-git',
                      'iiswsgi'],
      cmdclass=cmdclass,
      )
