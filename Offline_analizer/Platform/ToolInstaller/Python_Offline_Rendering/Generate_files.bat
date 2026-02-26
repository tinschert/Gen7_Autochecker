:: Generate/ Copy Python and Libraries requierd for CarMaker - Standalone Installation for offline PCs 
:: Python Version 3.12.4
:: 2024.07.17
:: All contents in the folder (Zip and bat files) must be manually copyied to the target PC. 
:: An instruction will be printed on the terminal and the script waits for a key to be pressed before exiting.

@echo off
setlocal enableextensions
cd /d "%~dp0"
:: Here please change the path to the source of the actual version. Exe file-name must be always "PythonSetup.exe"
set src=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\Python\Libraries\Libs_3.12
GOTO Download_Python

:: Download Python from the shared folder.
:Download_Python
IF EXIST Rendering_Libs.zip (GOTO Download_RefreshEnv)
ECHO Downloading Python
	robocopy "%src%" .\ Rendering_Libs.zip
	
:Download_RefreshEnv
IF EXIST RefreshEnv.bat (GOTO Instruction)
robocopy ..\ .\ RefreshEnv.bat

:Instruction
ECHO ############################################################################## 
ECHO:
ECHO Please copy the folder to the offline PC and run the "Install_Py_Offline.bat" there. & ECHO:
pause
