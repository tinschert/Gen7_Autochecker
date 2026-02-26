:: Generate/ Copy installation files requierd for CarMaker - Standalone Installation for offline PCs 
:: CarMaker Version 12.0.2
:: 2023.12.14
:: All contents in the folder (Zip and bat files) must be manually copyied to the target PC. 
:: An instruction will be printed on the terminal and the script waits for a key to be pressed before exiting.

@echo off
setlocal enableextensions
cd /d "%~dp0"
:: Here please change the path to the source of the actual version. Exe file-name must be always "PythonSetup.exe"
set src=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\Carmaker\V12.0.2


:: Download Python from the shared folder.
:Download_CarMaker
IF EXIST CD-CarMakerOffice-win-12.0.2.zip (GOTO Instruction)
ECHO Downloading CarMaker 12.0.2
	robocopy "%src%" .\ CD-CarMakerOffice-win-12.0.2.zip
	
:Instruction
ECHO ############################################################################## 
ECHO:
ECHO Please copy the folder to the offline PC and run the "Install_CM_Offline.bat" there. & ECHO:
pause
