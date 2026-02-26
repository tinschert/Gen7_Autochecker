@echo off
setlocal enabledelayedexpansion

echo --- CMake Configure for Visual Studio 17 2022 ---

rem Define variables
set "buildDir=./buildx64"
set "generatorFile=%buildDir%/generator.txt"
set "currentGenerator=Visual Studio 17 2022"

rem Check if the build directory exists and recreate if generator changes
if exist "%buildDir%" (
    rem Read the stored generator from the file
    if exist "%generatorFile%" (
        set /p storedGenerator=<"%generatorFile%"
        if "!storedGenerator!" neq "!currentGenerator! " (
            echo Generator has changed. Deleting the build directory...
            rmdir /s /q "%buildDir%"
        )
    ) else (
        echo No previous generator found. Deleting build directory...
        rmdir /s /q "%buildDir%"
    )
) else (
    echo Build directory does not exist. Creating it...
)

rem Create the build directory if it does not exist
mkdir "%buildDir%"

rem Check if the first argument is --no-pause
if "%~1" == "--no-pause" (
    cmake -G "%currentGenerator%" -A x64 -B "%buildDir%" -S . > CMakeConfigLog.txt 2>&1
) else (
    cmake -G "%currentGenerator%" -A x64 -B "%buildDir%" -S .
)

:: Store the current generator in the file
echo %currentGenerator% > "%generatorFile%"

if %ERRORLEVEL% GTR 0 (
    echo *** Error was found during configuration process ***
    echo     _________    ______ 
    echo    / ____/   ^|  /  _/ / 
    echo   / /_  / /^| ^|  / // /  
    echo  / __/ / ___ ^|_/ // /___
    echo /_/   /_/  ^|_/___/_____/
    set /A ERRORLEVEL=1
) ELSE (
    echo *** CMake was configured successfully ***
    set /A ERRORLEVEL=0
)

:: Check if "--no-pause" is present in the arguments
set "PAUSE_FLAG=1"
for %%i in (%*) do (
    if "%%i"=="--no-pause" set "PAUSE_FLAG=0"
)

:: Only pause if "--no-pause" is not provided
if %PAUSE_FLAG% EQU 1 pause

:: Return the error level
exit /b %ERRORLEVEL%
