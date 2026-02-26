:: Python and Libraries requierd for CarMaker - Standalone Installation for offline PCs 
:: Version 3.12.4
:: 2024.07.17
:: Zip and bat files must be manually copyied to the target PC.

@echo off
setlocal enableextensions
cd /d "%~dp0"
:: Path for the installation files
set src=.\Rendering_Libs
GOTO Extract_Python

:: Extract the installation files
:Extract_Python
IF EXIST .\Rendering_Libs GOTO Python_Init
ECHO Extracting files
powershell -command "Expand-Archive ".\Rendering_Libs.zip" "%src%" "
:: If extraction OK .zip file will be deleted.
IF %ERRORLEVEL% NEQ 0 EXIT /b %ERRORLEVEL%
del .\Rendering_Libs.zip /F
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
IF %ERRORLEVEL% EQU 0 (GOTO Check_Version) ELSE (GOTO Install_Python)

:: Check the installed version. If correct install libraries.
:Check_Version
X:\Tools\venv\Scripts\python.exe -V > python_version.txt
set last="0.0"
set xcmd="FIND "Python" python_version.txt"
for /f "tokens=* skip=2" %%I in ('%xcmd%') do for %%A in (%%~I) do set last=%%A
call :VerCompare "%last%","3.12.4",result
DEL python_version.txt
IF %result% EQU 1 GOTO Install_Lib


:: Install Python and delete the Exe file.
:Install_Python
ECHO "Installing Python, please wait..."
%src%\PythonSetup.exe /quiet InstallAllUsers=1 PrependPath=1
IF %ERRORLEVEL% EQU 0 (ECHO Python : OK>> output.log) ELSE (ECHO Python : NOT OK>> output.log)


:: Refreshing the path, so the libraries can be installed within this script using RefreshEnv.bat
:Refresh_Path
powershell ".\RefreshEnv.bat"

:Install_Lib
IF EXIST %PROGRAMDATA%\pip\pip.ini GOTO Start_Install_Lib
robocopy "pip" "%PROGRAMDATA%\pip"


:Start_Install_Lib
X:\Tools\venv\Scripts\python.exe -3.12 -m X:\Tools\venv\Scripts\pip.exe install --no-index --find-links %src% -r py-requirements_rendering.txt
IF %ERRORLEVEL% EQU 0 (ECHO Python lib : OK>> output.log) ELSE (ECHO Python lib : NOT OK>> output.log)