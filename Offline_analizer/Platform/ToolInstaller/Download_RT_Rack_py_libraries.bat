@echo off
GOTO Main:

:Error
echo Critical Error!!!
IF %ERRORLEVEL% EQU 1 (ECHO 0 > D:\CarMaker_Shared\py_libs\py_deploy_status.txt && exit /b)

:Main
:: Delete and create D:\CarMaker_Shared\py_libs\py_libs as a python libs download location
set "directoryPath=D:\CarMaker_Shared\py_libs"
set "reqFilePath=%cd%\Platform\ToolInstaller\py_requirements_rt_rack.txt"

if exist "%directoryPath%" (
    rmdir /s /q "%directoryPath%"
    mkdir "%directoryPath%"
	ECHO 0 > D:\CarMaker_Shared\py_libs\py_deploy_status.txt
    echo Directory and its contents removed at %directoryPath%
    echo Directory created at %directoryPath%
) else (
    mkdir "%directoryPath%"
    echo Directory created at %directoryPath%
)
IF %ERRORLEVEL% EQU 1 (GOTO Error)

:: Download required py libs based on py_requirements_rt_rack.txt file
echo Start collecting RT rack python libraries
X:\Tools\venv\Scripts\python.exe -m X:\Tools\venv\Scripts\pip.exe download --no-cache-dir -r %reqFilePath% -d D:\CarMaker_Shared\py_libs
IF %ERRORLEVEL% EQU 1 (GOTO Error) 

:: Copy py_requirements_rt_rack.txt to shared drive
copy "%reqFilePath%" "%directoryPath%"

if errorlevel 1 (
    echo Failed to copy "%reqFilePath%" to "%directoryPath%"
) else (
    echo File "%reqFilePath%" copied to "%directoryPath%" successfully.
)
IF %ERRORLEVEL% EQU 1 (GOTO Error) 

ECHO 1 > D:\CarMaker_Shared\py_libs\py_deploy_status.txt






