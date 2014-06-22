=========================
Plone  Installer for OSX
=========================


Mac OS X
~~~~~~~~

OS X users will generally need to install XCode and XCode Command Line Tools.
Some have had luck using Homebrew to provide GNU build tools.
We only test with XCode.

XCode command-line tools have a separate step in recent versions of XCode.
If you seem to be missing gcc, you've missed that install step.

Building Python libraries with C-language components requires an extra step in XCode 5.1+.
See Apple's release notes for 5.1. https://developer.apple.com/library/mac/releasenotes/DeveloperTools/RN-Xcode/xc5_release_notes/xc5_release_notes.html#//apple_ref/doc/uid/TP40001051-CH2-SW1
The Unified Installer takes care of this for you when building the initial Plone, but you need to supply the environment flags when adding new Python eggs that have C-language components.

MacPorts
~~~~~~~~

If you're using MacPorts, it's probably best to follow an all-or-nothing
strategy: either use ports to pre-install all the dependencies (Python-2.7,
libxml2, libxslt, readline and libjpg), or don't use it at all.

Uninstall instructions
======================
1) Stop Plone
2) Remove folder Hombrew and the Plone folder, or run the uninstall script


Backup instructions
===================
1) Stop Plone
2) Back up folder ``$HOME/Plone``::

   >> tar -zcvf Plone-backup.tgz /usr/local/Plone

Live backup is possible.
See `Backup Plone <https://plone.org/documentation/kb/backup-plone>`_


Coexistence with System Python
==============================
The Python installed by the Unified Installer should *not* interfere with
any other Python on your system.  The Installer bundles Python 2.7.6,
placing it at ``/usr/local/Plone/Python-2.7`` or ``$HOME/Plone/Python-2.7``


Developer Options
=================
After installation, read the instructions at the top of the ``develop.cfg``
file at the top of the instance directory. This provides support for building
a development environment.


Custom buildout.cfg Template
============================

You may specify ``--template=`` to pick a file to use as a template for the
``buildout.cfg`` file. The file must be located in buildout_templates,
and should be generally modified on the ``buildout.cfg`` included with the
installer.
The safest customizations will be to add eggs, parts or version pinnings.

The purpose of this option is to allow for feature packaging for particular
use cases with common add-on needs.


Installer Bug reports
=====================
Please use the Plone issue tracker at https://dev.plone.org for all
bug reports. Specify the "Installer (Unified)" component.


Credits
=======
The Unified Installer was originally developed for Plone 2.5 by Kamal Gill.
Adaptation to Plone 3.x, 4.x and buildout: Steve McMahon (steve@dcn.org)
Maintainer for Plone 3.x, 4.x: Steve McMahon

Thanks to Martin Aspeli and Wichert Akkerman for vital hints and suggestions
with the buildout version.

Thanks for Naotaka Jay Hotta for suggesting -- and offering an initial
implementation for -- stand-alone and cluster configuration options.

Thanks to Larry T of the Davis Plone Group for the first implementation
of the rootless install.

Thanks to Barry Page and Larry Pitcher for their work on the init scripts.
