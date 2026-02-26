:: Python and its Libraries Standalone Installation
:: Version 3.12.4
:: 2024.10.02
:: Change: added new lib requirement file.
:: Added RefreshEnv.bat script to refresh the nvironment variables. With this change, the libraries will be installed without issues.

@echo off
setlocal enableextensions
cd /d "%~dp0"
:: Here please change the path to the source of the actual version. Exe file-name must be always "PythonSetup.exe"
set src=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\Python\V3.12.4
GOTO Python_Init

:VerCompare
powershell -command "&{exit(([version]$args[0]).CompareTo([version]$args[1]))}" "%~1" "%~2"
IF ERRORLEVEL 1 (ECHO "%~1" is newer than "%~2"
SET "%~3=1")  ELSE (IF ERRORLEVEL 0 (
ECHO "%~1" is the same as "%~2"
SET "%~3=1") ELSE (ECHO "%~1" is older than "%~2"
SET "%~3=0"))
EXIT /B 0

:: Initialise Python to check the version
:Python_Init
X:\Tools\venv\Scripts\python.exe -V
IF %ERRORLEVEL% EQU 0 (GOTO Check_Version) ELSE (GOTO Download_Python)

:: Check the installed version. If correct install libraries.
:Check_Version
X:\Tools\venv\Scripts\python.exe -V > python_version.txt
set last="0.0"
set xcmd="FIND "Python" python_version.txt"
for /f "tokens=* skip=2" %%I in ('%xcmd%') do for %%A in (%%~I) do set last=%%A
call :VerCompare "%last%","3.12.4",result
DEL python_version.txt
IF %result% EQU 1 GOTO Install_Lib

:: Download Python from the shared folder.
:Download_Python
IF EXIST PythonSetup.exe GOTO Install_Python
ECHO "Downloading Python"
robocopy "%src%" .\ PythonSetup.exe

:: Install Python and delete the Exe file.
:Install_Python
ECHO "Installing Python"
PythonSetup.exe /quiet InstallAllUsers=1 PrependPath=1
IF %ERRORLEVEL% EQU 0 (ECHO Python : OK>> output.log) ELSE (ECHO Python : NOT OK>> output.log)
del .\PythonSetup.exe /F

:: Refreshing the path, so the libraries can be installed within this script using RefreshEnv.bat
:Refresh_Path
powershell ".\RefreshEnv.bat"

:Install_Lib
echo "Installing libraries"
X:\Tools\venv\Scripts\python.exe -m X:\Tools\venv\Scripts\pip.exe install --upgrade pip
X:\Tools\venv\Scripts\pip.exe install --no-index --find-links \\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\Python\Libraries\Libs_3.12 -r GUI_PC_py_requirements.txt
IF %ERRORLEVEL% EQU 0 (ECHO Python lib : OK>> output.log) ELSE (ECHO Python lib : NOT OK>> output.log)