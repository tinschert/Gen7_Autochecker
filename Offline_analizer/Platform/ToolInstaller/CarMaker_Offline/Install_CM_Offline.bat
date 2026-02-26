:: CarMaker Standalone Installation
:: Version 12.0
:: 2023.07.12
:: Installation updated to CarMaker 12. Zip and bat files must be manually copyied to the target PC.

@echo off
setlocal enableextensions
cd /d "%~dp0"

:: Source path for the shared Repo. 
:: Here please change the path to the source of the actual version.
set src=.\CD-CarMakerOffice-win-12.0.2.zip

ECHO "Checking prerequisites, please wait..."
if exist C:\IPG\carmaker\win64-12.0.2 (ECHO CarMaker : OK>> output.log && exit 0) else (goto Download_CarMaker)

:Download_CarMaker
IF EXIST CD-CarMakerOffice-win-12.0.2\ goto Install_CarMaker
IF EXIST CD-CarMakerOffice-win-12.0.2.zip GOTO Extract_CarMaker
ECHO Please download the installation files using the script "Generate_files.bat" on the GUI PC
:: Source packet will be copied to the local folder and extracted. Zip file will be deleted after successful extraction.
REM echo "Downloading CarMaker, please wait..."
REM robocopy "%src%" .\ CD-CarMakerOffice-win-12.0.zip
:: Robocopy ERRORLEVEL must be o or 1 
REM IF %ERRORLEVEL% GTR 1 EXIT /b %ERRORLEVEL%
:Extract_CarMaker
powershell -command "Expand-Archive "CD-CarMakerOffice-win-12.0.2.zip" "." -Force"
IF %ERRORLEVEL% NEQ 0 EXIT /b %ERRORLEVEL%
del .\CD-CarMakerOffice-win-12.0.2.zip /F
EXIT /B 0

:Install_CarMaker
.\CD-CarMakerOffice-win-12.0.2\ipg-install.exe -usedir .\CD-CarMakerOffice-win-12.0.2\ -batch
:: Before finishing, if the installation was OK, the folder will be completely removed.
IF %ERRORLEVEL% EQU 0 ( IF EXIST .\CarMaker ( 
		RD /S /Q .\CarMaker) )
IF %ERRORLEVEL% EQU 0 (ECHO CarMaker : OK>> output.log) ELSE (ECHO CarMaker : NOT OK>> output.log)
EXIT /B 0