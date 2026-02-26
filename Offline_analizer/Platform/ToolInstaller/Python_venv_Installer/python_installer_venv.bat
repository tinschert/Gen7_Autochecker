@echo off
setlocal enabledelayedexpansion

:: Determine the directory of the script
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..\..") do set "RELEASE_DIR=%%~fI\Release"

echo SCRIPT_DIR: %SCRIPT_DIR%
echo RELEASE_DIR: %RELEASE_DIR%

:: Check if the release directory exists
if not exist "%RELEASE_DIR%" (
    echo Error: The release directory does not exist.
    PAUSE
    exit /b 1
)

:: Search for the first .yml file in the release folder
set "YML_FILE="
for %%F in ("%RELEASE_DIR%\*.yml") do (
    set "YML_FILE=%%F"
    goto :found
)

echo No .yml file found.
PAUSE
exit /b 1

:found
echo Found YAML file: %YML_FILE%

:: Check if version argument is provided
if "%1"=="" (
    :: If no argument is provided, pass "no_version_argument" to the Python script
    set "VERSION=no_version_argument"
) else (
    :: If version argument is provided, use it
    set "VERSION=%1"
)

:: Start the Python script with the found .yml file and version argument
python.exe "%SCRIPT_DIR%python_installer_venv.py" "%YML_FILE%" %VERSION%
PAUSE
