@echo off

:: Generate the CMake Config
call "0_configure_cmake.bat" --no-pause
if %ERRORLEVEL% GTR 0 (
    echo Error in configuration. Exiting with error level %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
)

echo --- Building the CarMaker Executable ---

rem Check if the first argument is --no-pause
if "%~1" == "--no-pause" (
    cmake --build ./buildx64 --config "Release" --target CarMakerFordAdasHil --parallel > CMakeBuildLog.txt
) else (
    cmake --build ./buildx64 --config "Release" --target CarMakerFordAdasHil --parallel
)

if %ERRORLEVEL% GTR 0 (
    echo *** Error was found during build process ***
    echo     _________    ______ 
    echo    / ____/   ^|  /  _/ / 
    echo   / /_  / /^| ^|  / // /  
    echo  / __/ / ___ ^|_/ // /___
    echo /_/   /_/  ^|_/___/_____/
) ELSE (
    echo *** CarMaker executable built without errors ***
    echo    _____ __  ______________________________
    echo   / ___// / / / ____/ ____/ ____/ ___/ ___/
    echo   \__ \/ / / / /   / /   / __/  \__ \\__ \ 
    echo  ___/ / /_/ / /___/ /___/ /___ ___/ /__/ / 
    echo /____/\____/\____/\____/_____//____/____/  
)

:: Check if "--no-pause" is present in the arguments
set "PAUSE_FLAG=1"
for %%i in (%*) do (
    if "%%i"=="--no-pause" set "PAUSE_FLAG=0"
)

:: Only pause if "--no-pause" is not provided
if %PAUSE_FLAG% EQU 1 pause
