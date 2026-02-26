@echo off

@REM :: Alles in output.log umleiten
@REM set LOGFILE=D:\CarMaker_Shared\batch_output.log
@REM echo Logging to %LOGFILE%
@REM echo ------------------------- >> %LOGFILE%
@REM date /t >> %LOGFILE%
@REM time /t >> %LOGFILE%
@REM echo ------------------------- >> %LOGFILE%
@REM :: Starte die Umleitung
@REM (
@REM     call :MAIN
@REM ) > "%LOGFILE%" 2>&1
@REM exit /b

@REM :MAIN

REM Check if D: drive exists
if not exist D:\ (
    echo D: drive does not exist. Mapping to C:\CarMaker_Shared
    subst D: C:\CarMaker_Shared
) else (
    echo D: drive already exists.
)

::::::::::::::::::::::: Mount X Drive :::::::::::::::::::::::::::
:: Define the share path and network drive letter
set "SHARE_PATH=\\%COMPUTERNAME%\Carmaker_shared"
set "DRIVE_LETTER=X:"
set "error_in_venv=0"

:: Check if the network drive is already mapped
if exist %DRIVE_LETTER%\ (
    echo Network drive %DRIVE_LETTER% is already connected.
)

:: Ensure the shared folder exists
if not exist "D:\Carmaker_shared" (
    echo Error: The folder D:\Carmaker_shared does not exist.
)

:: Create the share if it doesn't exist
net share Carmaker_shared >nul 2>&1
if %errorlevel% neq 0 (
    echo Creating network share...
    net share Carmaker_share=D:\Carmaker_shared /GRANT:Everyone,FULL >nul 2>&1
)

:: Wait for the share to be active
timeout /t 2 /nobreak >nul

:: Connect the network drive
net use %DRIVE_LETTER% %SHARE_PATH% /PERSISTENT:YES >nul 2>&1

:: Verify if the connection was successful
if %errorlevel% neq 0 (
    echo Error: Failed to connect the network drive.
)

echo Network drive successfully mapped as %DRIVE_LETTER%.

REM Clean all TXT flag-handlers
DEL D:\CarMaker_Shared\*.txt /F

echo 0 > D:\CarMaker_Shared\canoe_start_ready.txt

::::::::::::::::::::::::::::::: check venv version against SW BOM and download and extract ::::::::::::::::::::::::::::::::
REM Extract installation source path from YAML using Python
for /f "tokens=1,2 delims=," %%a in ('python .\Platform\Classe\Scripts\CarMaker_scripts\get_yaml_path.py') do (
    set VERSION_venv=%%a
    set INSTALLATION_SOURCE=%%b
)

echo YAML Version: %VERSION_venv%
echo Installation Source: %INSTALLATION_SOURCE%

REM Ensure installation source is valid
if "%INSTALLATION_SOURCE%"=="Not Found" (
    echo Installation source not found in YAML. Exiting...
    set "error_in_venv=1"
)

REM Check if version.txt exists and compare versions
set "version_file_venv=D:\CarMaker_Shared\tools\venv\version.txt"
set "LOCAL_VERSION=Not Found"

if exist "%version_file_venv%" (
    for /f "delims=" %%v in (%version_file_venv%) do set LOCAL_VERSION=%%v
)

echo Local Version from version.txt: %LOCAL_VERSION%
set "LOCAL_VERSION=%LOCAL_VERSION: =%"
set "VERSION_venv=%VERSION_venv: =%"
if "%VERSION_venv%"=="%LOCAL_VERSION%" (
    echo Virtual environment is up to date. Skipping installation.
    set "SKIP_VENV_INSTALL_var=1"
    goto SKIP_VENV_INSTALL
) else (
    echo Virtual environment is outdated or missing. Installing new version...
)

REM Define destination path
set "destination_file_venv=D:\CarMaker_Shared\tools\venv.zip"
set "extract_folder_venv_temp=D:\CarMaker_Shared\tools\venvtemp"
set "destination_folder_venv=D:\CarMaker_Shared\tools" 
set "destination_folder_venv_venv=D:\CarMaker_Shared\tools\venv" 

if not exist "%extract_folder_venv_temp%" (
    mkdir "%extract_folder_venv_temp%"
    echo "%extract_folder_venv_temp%" has been created
)

if not exist "%destination_folder_venv_venv%" (
    mkdir "%destination_folder_venv_venv%"
    icacls "%destination_folder_venv_venv%" /grant Everyone:F /T
    echo "%destination_folder_venv_venv%" has been created
)

REM Copy the venv.zip file
echo Copying virtual environment from %INSTALLATION_SOURCE% to %destination_file_venv%...
copy /Y "%INSTALLATION_SOURCE%" "%destination_file_venv%"

REM Check if copying was successful
if %errorlevel% neq 0 (
    echo Error copying venv.zip. Exiting...
    set "error_in_venv=2"

)
echo venv.zip successfully copied.

:::::::::::::::::::::::::::::::::::::: Unzip venv.zip ::::::::::::::::::::::::::::::::
echo Extracting virtual environment...

REM Falls 7-Zip nicht im Standardpfad ist, suchen
set "ZIP7_Path=%ProgramFiles%\7-Zip\7z.exe"
if not exist "%ZIP7_Path%" (
    echo Error: 7-Zip not found. Please install 7-Zip.
    set "error_in_venv=3"
) else (
    echo 7-Zip found at "%ZIP7_Path%".
)

"%ZIP7_Path%" x "%destination_file_venv%" -o"%extract_folder_venv_temp%" -y
ECHO extract done

if %errorlevel% neq 0 (
    echo Error extracting venv.zip. Exiting...
    set "error_in_venv=4"

)

echo "%extract_folder_venv_temp%"  extract_folder_venv_temp
echo "%destination_folder_venv%" destination_folder_venv

@REM robocopy "%extract_folder_venv_temp%" "%destination_folder_venv%" /W:1 /NP /MIR
robocopy "D:\CarMaker_Shared\tools\venvtemp\venv" "D:\CarMaker_Shared\tools\venv" /W:1 /NP /MIR

if %errorlevel% gtr 7 (
    echo Error extracting venv.zip. Exiting...
    set "error_in_venv=5"
)

REM Remove the zip file after extraction
rmdir /S /Q "%extract_folder_venv_temp%"

REM Remove the zip file after extraction
del /Q "%destination_file_venv%"

REM Save new version to version.txt
echo %VERSION_venv% > "%version_file_venv%"
echo Updated version.txt with %VERSION_venv%


:SKIP_VENV_INSTALL

REM Continue with the rest of the script
set "source_path2=.\Platform\Classe\Scripts\CarMaker_scripts\CarMakerScripts"
set "destination_folder2=D:\CarMaker_Shared\CarMakerScripts"



REM Create the destination folders if they don't exist
if not exist "%destination_folder2%" mkdir "%destination_folder2%"

REM Copy files and directories from source to destination using robocopy
robocopy "%source_path2%" "%destination_folder2%" /W:1 /NP /MIR
echo CM Project has been successfully copied to the shared folder.

cd "%~dp0"

X:\Tools\venv\Scripts\python.exe -W ignore modify_CAN_ini.py

X:\Tools\venv\Scripts\python.exe -W ignore rpyc_client.py check_connection copy_server
if %errorlevel% EQU 0 (
    echo Copy OK				
) else (
    echo:
    echo ###############################################################################################
    echo # Rendering PC cannot access shared drive X:\ If this is needed please check the shared drive #
    echo ###############################################################################################
    echo:
    ping -n 10 localhost > Nul
)
if %error_in_venv% equ 0 (
    echo write 1 to canoe_start_ready.txt file
    echo 1 > D:\CarMaker_Shared\canoe_start_ready.txt
) else (
    echo:
		echo:
		echo ######################################################################################################
		echo # Script ended with error! Please check. error_in_venv variable is %error_in_venv%                   #
		echo ######################################################################################################
		echo:
		ping -n 10 localhost > Nul
)
exit /b 0
