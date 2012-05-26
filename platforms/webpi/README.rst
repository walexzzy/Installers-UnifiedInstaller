Building the Web Deploy Package
===============================

#. Install the `Microsoft Web Platform Installer  (WebPI)
   <http://www.microsoft.com/web/downloads/platform.aspx>`_.

   Skip this if you've already done it and haven't changed anything since.

#. Use the WebPI to install dependencies.

   Skip this if you've already done it and haven't changed anything since.

   Install the ``PyPI`` package for ``pip`` and all of it's
   dependencies including Python and distribute.  Also install Web
   Matrix.  Note that you can install multiple packages at once so no
   need to do this in two steps.

#. Clone `Installers-UnifiedInstaller
   <https://github.com/plone/Installers-UnifiedInstaller>`_

   Use a `windows git client
   <http://help.github.com/win-set-up-git/>`_. Skip this if you've
   already done it and haven't changed anything since.

#. TODO Create the buildout::

     > cd Installers-UnifiedInstaller
     > C:\Python2.7\python.exe platforms\webpi\TODO.py PloneWebDeployPackage

   Make buildout-cache/eggs, buildout-cache/downloads

   Run::

     >C:\Python27\python.exe helper_scripts\create_inst ance.py C:\Installers-UnifiedInstaller C:\Installers-UnifiedInstaller zeocluster xen xen act1v4t3 0 1 0 0 cluster C:\Installers-UnifiedInstaller\install.log 2

#. Run the buildout::

     > cd PloneWebDeployPackage
     > C:\Python2.7\python.exe bootstrap.py -d
     > bin\buildout.exe -N -c develop.cfg

   We use develop.cfg to make sure we have all the eggs the user may
   need including develop tools.

#. Create the Web Deploy zip package::

     > C:\Python2.7\python.exe setup.py sdist --formats=tar -k

   Then open a file browser, select ``Manifest.xml``,
   ``Parameters.xml`` and ``PloneInstaller-4-2``, then right-click and
   Select "Send to -> Compressed (zipped) Folder".

     TODO> C:\Python2.7\python.exe setup.py bdist_msdeploy

#. TODO Test with msdeploy

#. Update the Web PI atom feed

   #. Update the SHA1 hash

      Install `fciv.exe
      <http://download.microsoft.com/download/c/f/4/cf454ae0-a4bb-4123-8333-a1b6737712f7/windows-kb841290-x86-enu.exe>`_
      (skip this if you've already done it and know where ``fciv.exe``
      is).
  
      Then use it to `display the SHA1 hash
      <http://learn.iis.net/page.aspx/1082/web-deploy-parameterization/>`_::

        > fciv.exe -sha1 Parameters.zip

      Copy the printed hash and replace the existing one in
      ``Installers-UnifiedInstaller\platforms\webpi\web-pi.xml`` at
      (xpath) ``installers/installer/installerFile/sha1`` inside the
      ``entry/productId`` for ``Plone_4_2``.

   #. Update the package size

      Use use the file browser to get the package size in KB replace
      the existing one in
      ``Installers-UnifiedInstaller\platforms\webpi\web-pi.xml`` at
      ``installers/installer/installerFile/fileSize``.

#. Test with WebPI
 
   #. Point WebPI to the local feed

      Skip this if you've already done it and haven't changed anything since.
  
      Force WebPI to use the modified feed.  Use the WebPI options screen
      to remove any previous Plone installer feeds and adding
      ``file:///C:/...Installers-UnifiedInstaller/platforms/webpi/web-pi.xml``
      replacing ``...`` with the appropriate path.  Then delete it's cache
      of feeds by deleting all ``*.xml`` files in
      ``%LOCALAPPDATA%\xen\Local Settings\Application Data\Microsoft\Web
      Platform Installer`` (``%USERPROFILE%\Local Settings\Application
      Data\Microsoft\Web Platform Installer`` on Windows XP).

   #. Point WebPI to the local package

      You can skip this if you've done it before and the new package is
      in the same place as the file URL points to.
  
      Replace the URL in
      ``Installers-UnifiedInstaller\platforms\webpi\web-pi.xml`` at
      ``installers/installer/installerFile/installerURL`` with
      ``file:///C:/.../Parameters.zip`` replacing ``...`` with the
      appropriate path.  This will make the WebPI install your archive
      and not the current one online.

   #. TODO Install the new package with WebPI

   #. TODO Test with WebMatrix

#. Release the package

   #. Restore the ``<installerURL>`` element contents.

   #. Commit the SHA1 and file size changes to
      ``Installers-UnifiedInstaller\platforms\webpi\web-pi.xml``

   #. Upload ``Parameters.zip`` to ``dist.plone.org`` as
      ``PloneInstaller-4-2.zip``

   #. upload
      ``Installers-UnifiedInstaller\platforms\webpi\web-pi.xml`` to
      ``dist.plone.org``
   
   #. Ask Windows users to test by installing from WebPI
