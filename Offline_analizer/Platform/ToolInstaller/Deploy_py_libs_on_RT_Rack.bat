@echo off
setlocal enabledelayedexpansion
set "directoryPath=D:\UserFiles\py_libs_install_status.txt"
set "libsPath=X:\py_libs"
set "status="
set COUNTER=0
ECHO 0 > %directoryPath%
:start
set "status="
timeout 3
for %%A in (X:\py_libs\py_deploy_status.txt) DO (if %%~zA==0 GOTO start)

cd /d %libsPath%
set "currentDir=%cd%"
echo %currentDir%
:Check_status
FOR /F "tokens=* delims=" %%x in (X:\py_libs\py_deploy_status.txt) DO (set "status=!status!%%x")
echo %status%
IF %status% EQU 0 ( IF %COUNTER% GTR 20 (ECHO 2 > %directoryPath% && exit /b) ELSE (set /A COUNTER=%COUNTER%+1 && GOTO start) )
IF %status% EQU 1 (X:\Tools\venv\Scripts\pip.exe install --no-index --find-links X:\py_libs -r X:\py_libs\py_requirements_rt_rack.txt)
IF %ERRORLEVEL% EQU 1 (ECHO 2 > %directoryPath% && exit /b) ELSE (ECHO 1 > %directoryPath%)
pause

