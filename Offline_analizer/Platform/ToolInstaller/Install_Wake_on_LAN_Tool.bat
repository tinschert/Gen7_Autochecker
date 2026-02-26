@echo off
setlocal enableextensions
cd /d "%~dp0"
 
:: Source Path If the source path is changed, please change it here:
set src=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\WakeOnLAN

:: If the destination path is changed, please change it here:
set dst=C:\tools\WakeOnLAN

:: Destination path for the configuration file
set dcnf=C:\ProgramData\Aquila Technology\WakeOnLan

:: Desktop path as destination for the shortcut
set dsk=C:\Users\Public\Desktop

:: Check if the the tool is already installed and if the shortcut is on the public desktop folder, if not it'll install it and create the shortcut.
if exist %dst%\WakeOnLan.exe if exist %dsk%\WakeOnLan.lnk (
		echo WakeOnLAN Tool : Already installed - %date% %time:~0,5%>> output.log
		exit 0
)else (
		goto Copy_Tool
		)

:: The function "Copy_Tool" copies the zip file from the source to the destination, unzips the file and deletes it. 
:: The configuration file and a shorcut are copied to the destination PC. A Log file and the version text file are created 
:Copy_Tool
robocopy "%src%" "%dst%" WakeOnLan.zip
powershell -command "Expand-Archive "%dst%\WakeOnLan.zip" "%dst%" " -force
del %dst%\WakeOnLan.zip
robocopy "%dst%" "%dcnf%" machines.xml
robocopy "%dst%" "%dsk%" WakeOnLan.lnk
echo WakeOnLan Tool : OK - %date% %time:~0,5%>> output.log
exit 0