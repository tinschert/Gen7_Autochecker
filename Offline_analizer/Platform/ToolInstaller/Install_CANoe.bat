:: CANoe Standalone Installation
:: Version 18SP3 (18.2.65.2)
:: 03.12.2024
:: Change: Update to V.18SP3 (18.3.118)

@echo off
setlocal enableextensions
cd /d "%~dp0"

:: Source path for the shared Repo. 
:: Here please change the path to the source of the actual version. Zip file-name must be always "CANoe.zip"
set src=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\CANoe\V18_SP3
:: Here please set the path and filename to the current CANoe Version AddOn for CarMaker
set pad="C:\Program Files\Vector CANoe 18\Installer Additional Components\CarMaker\VectorCANoeCarMakerAddOn_2.8.3.exe"
ECHO "Checking prerequisites, please wait..."
powershell -Command "Get-Package | Where-Object { $_.Name -like 'Vector CANoe Family 18' } | Select-Object Name, Version" > prerequisites.txt

:: USA Condition
IF [%1]==[] (GOTO :noparam) ELSE (set "usa=%1" && GOTO :Install_CANoe_USA)
:noparam
powershell ".\Popup.bat | tee answer.txt"
set xcmd="FIND "output" answer.txt"
for /f "tokens=* skip=2" %%I in ('%xcmd%') do for %%A in (%%~I) do set usa=%%A
IF %usa% EQU 0 (GOTO :Install_CANoe) ELSE (GOTO :Install_CANoe_USA)
EXIT /B 0

:: Download / Extraction / Cleaning zip file. 
:VerCompare
powershell -command "&{exit(([version]$args[0]).CompareTo([version]$args[1]))}" "%~1" "%~2"
IF ERRORLEVEL 1 (ECHO "%~1" is newer than "%~2"
SET "%~3=1")  ELSE (IF ERRORLEVEL 0 (
ECHO "%~1" is the same as "%~2"
SET "%~3=1") ELSE (ECHO "%~1" is older than "%~2"
SET "%~3=0"))
EXIT /B 0
:NameSearch
set last="0.0"
set xcmd="FIND "%~1" prerequisites.txt"
for /f "tokens=* skip=2" %%I in ('%xcmd%') do for %%A in (%%~I) do set last=%%A
call :VerCompare "%last%","%~3",result
IF %result% EQU 1 EXIT /B 0
ECHO "Installing %~1"
REM "%~2"
set "command=%~2"
set "command=%command:""="%"
call :Download_CANoe
%command%
EXIT /B 0

:: New path for the source file added. SW won't be downloaded anymore, it will be copied from the network share. 
:Download_CANoe
IF EXIST CANoe\ echo CANoe downloaded && EXIT /b %ERRORLEVEL%
IF EXIST CANoe.zip GOTO :Extract_CANoe
robocopy "%src%" .\ CANoe.zip
:: Robocopy ERRORLEVEL must be o or 1 
IF %ERRORLEVEL% GTR 1 EXIT /b %ERRORLEVEL%
:Extract_CANoe
powershell -command "Expand-Archive ".\CANoe.zip" ".\CANoe" "
:: If extraction OK .zip file will be deleted.
IF %ERRORLEVEL% NEQ 0 EXIT /b %ERRORLEVEL%
del .\CANoe.zip /F
EXIT /B 0

:Install_CANoe_USA
ECHO "USA"
call :NameSearch "Vector CANoe Family 18","CANoe\CANoeFamily\SetupCANoeFamily.exe /noGui /noReboot","18.3.118"
:: Check installation and remove CANoe folder
IF %ERRORLEVEL% EQU 0 ( IF EXIST .\CANoe ( 
		 RD /S /Q ".\CANoe") )
IF %ERRORLEVEL% EQU 0 (ECHO CANoe : OK>> output.log) ELSE (ECHO CANoe : NOT OK>> output.log)
call :Install_CANoe_AddOn
EXIT /B 0

:Install_CANoe
ECHO "NOT USA"
call :NameSearch "Vector CANoe Family 18","CANoe\CANoeFamily\SetupCANoeFamily.exe /noGui /noReboot /userSettings "%cd%/CANoe_config.xml"","18.3.118"
:: Check installation and remove CANoe folder
IF %ERRORLEVEL% EQU 0 ( IF EXIST .\CANoe ( 
		 RD /S /Q ".\CANoe") )
IF %ERRORLEVEL% EQU 0 (ECHO CANoe : OK>> output.log) ELSE (ECHO CANoe : NOT OK>> output.log)
call :Install_CANoe_AddOn
EXIT /B 0

:Install_CANoe_AddOn
IF EXIST %pad% (%pad% /v"/qn INSTALLDIR=\"c:\Program Files\Vector CANoe 18\"") ELSE (ECHO "Please verify the installation of Vector CANoe CarMaker AddOn")
IF %ERRORLEVEL% EQU 0 (ECHO Vector CarMaker AddOn : OK>> output.log) ELSE (ECHO Vector CarMaker AddOn  : NOT OK>> output.log)
EXIT /B 0