:: CarMaker Standalone Installation
:: Version 13.1.1
:: 2024.12.03
:: Change: Installation updated to CarMaker 13.1.1 and CANoe AddOn for CANoe 18.

@echo off
setlocal enableextensions
cd /d "%~dp0"

:: Source path for the shared Repo. 
:: Here please change the path to the source of the actual version.
set src=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\Carmaker\V13.1.1

:: Here please set the path and filename to the current CANoe Version AddOn for CarMaker
set pad1="C:\Program Files\Vector CANoe 17\Installer Additional Components\CarMaker\VectorCANoeCarMakerAddOn_2.8.2.exe"
set pad2="C:\Program Files\Vector CANoe 18\Installer Additional Components\CarMaker\VectorCANoeCarMakerAddOn_2.8.3.exe"


ECHO "Checking prerequisites, please wait..."
if exist C:\IPG\carmaker\win64-13.1.1 (ECHO CarMaker : OK>> output.log && exit 0) else (goto Download_CarMaker)

:Download_CarMaker
IF EXIST CD-CarMakerOffice-win-13.1.1\ goto Install_CarMaker
IF EXIST CD-CarMakerOffice-win-13.1.1.zip GOTO Extract_CarMaker
:: Source packet will be copied to the local folder and extracted. Zip file will be deleted after successful extraction.
echo "Downloading CarMaker, please wait..."
robocopy "%src%" .\ CD-CarMakerOffice-win-13.1.1.zip
:: Robocopy ERRORLEVEL must be o or 1 
IF %ERRORLEVEL% GTR 1 EXIT /b %ERRORLEVEL%
:Extract_CarMaker
powershell -command "Expand-Archive "CD-CarMakerOffice-win-13.1.1.zip" "." -Force"
IF %ERRORLEVEL% NEQ 0 EXIT /b %ERRORLEVEL%
del .\CD-CarMakerOffice-win-13.1.1.zip /F
EXIT /B 0

:Install_CarMaker
.\CD-CarMakerOffice-win-13.1.1\ipg-install.exe -usedir .\CD-CarMakerOffice-win-13.1.1\ -batch
:: Before finishing, if the installation was OK, the folder will be completely removed.
IF %ERRORLEVEL% EQU 0 ( IF EXIST .\CarMaker ( 
		RD /S /Q .\CarMaker) )
IF %ERRORLEVEL% EQU 0 (ECHO CarMaker : OK>> output.log) ELSE (ECHO CarMaker : NOT OK>> output.log)

:Install_CANoe_AddOn
IF EXIST %pad1% (%pad1% /S /v"/qn INSTALLDIR=\"c:\Program Files\Vector CANoe 17\"") ELSE (ECHO "Please verify the installation of Vector CANoe CarMaker AddOn for CANoe 17")
IF %ERRORLEVEL% EQU 0 (ECHO Vector CarMaker AddOn : OK>> output.log) ELSE (ECHO Vector CarMaker AddOn CANoe 17  : To be checked>> output.log)
IF EXIST %pad2% (%pad2% /S /v"/qn INSTALLDIR=\"c:\Program Files\Vector CANoe 18\"") ELSE (ECHO "Please verify the installation of Vector CANoe CarMaker AddOn for CANoe 18")
IF %ERRORLEVEL% EQU 0 (ECHO Vector CarMaker AddOn : OK>> output.log) ELSE (ECHO Vector CarMaker AddOn CANoe 18 : To be checked>> output.log)




