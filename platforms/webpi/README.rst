Building the Web Deploy Package
===============================

Install Python 2.6 from python.org

Install lxml from http://www.lfd.uci.edu/~gohlke/pythonlibs/4j5pfugm/lxml-2.3.3.win32-py2.6.exe

Install distribute from
http://python-distribute.org/distribute_setup.py

Install zc.buildout using easy_install

Make buildout-cache/eggs, buildout-cache/, and buildout-cache/

Copy distribute and zc.buildout eggs from site-packages to
buildout-cache/eggs

Run "C:\Installers-UnifiedInstaller>C:\Python26\python.exe helper_scripts\create_inst ance.py C:\Installers-UnifiedInstaller C:\Installers-UnifiedInstaller zeocluster xen xen act1v4t3 0 1 0 0 cluster C:\Installers-UnifiedInstaller\install.log 2 ߀"

It fails, cd to the zeocluster directory

C:\Python26\Scripts\buildout.exe bootstrap -d

bin\buildout.exe -N -c develop.cfg

Install 7zip http://downloads.sourceforge.net/project/sevenzip/7-Zip/9.20/7z920.msi

C:\Installers-UnifiedInstaller>"C:\Program Files\7-Zip\7z.exe" a -tzip ..\Installers-UnifiedInstaller.zip -r zeocluster buildout-cache manifest.xml -x!*.pyc -x!*.pyo -x!buildout-cache\downloads\dist 
