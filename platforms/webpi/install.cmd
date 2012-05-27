set APPL_PHYSICAL_PATH=%~dp0
cd "%APPL_PHYSICAL_PATH%zinstance"
"%SystemDrive%\Python27\python.exe" bootstrap.py -d
bin\buildout.exe -N
"%IIS_BIN%\appcmd.exe" set config -section:system.webServer/fastCgi /+"[fullPath='%SystemDrive%\Python27\python.exe',arguments='-u %APPL_PHYSICAL_PATH%zinstance\bin\iisfcgi-script.py -c %APPL_PHYSICAL_PATH%zinstance\production.ini',maxInstances='1',monitorChangesTo='%APPL_PHYSICAL_PATH%zinstance\production.ini']" /commit:apphost
