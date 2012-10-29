Releasing Plone MSDeploy and Web PI packages
============================================

Expects to be run in a virtualenv with iiswsgi installed::

    >cd init_scripts/MSWebPI
    >C:\Python27\Scripts\virtualenv --distribute --clear .
    >Scripts\easy_install.exe -U iiswsgi
    >Scripts\python.exe setup.py release

Since the Unified installer and buildout-cache layouts can result
in deep paths, it is best to place the UI checkout at the root of
a drive.
