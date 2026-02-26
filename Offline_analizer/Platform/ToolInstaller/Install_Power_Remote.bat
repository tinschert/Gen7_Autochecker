:: Remote Power Pro Standalone Installation
:: 2022.11.09
:: Change: Standalone Installations implemented. Source packets are now in a sharefolder. Zip file and installator folder will be deleted after install.

@echo off
setlocal enableextensions
cd /d "%~dp0"

:: Here please change the path to the source of the actual version. Zip file-name must be similar to "Remote_Power_Pro_V2.1.zip"
set src=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\Remote_Power_Pro_V2.1

:Download_RemotePowerPro
IF EXIST "Remote Power Pro_V2.1\" goto :Install_RemotePowerPro
IF EXIST Remote_Power_Pro_V2.1.zip GOTO Extract_RemotePowerPro
robocopy "%src%" .\ Remote_Power_Pro_V2.1.zip
:: Robocopy ERRORLEVEL must be o or 1 
IF %ERRORLEVEL% GTR 1 EXIT /b %ERRORLEVEL%
:Extract_RemotePowerPro
powershell -command "Expand-Archive ".\Remote_Power_Pro_V2.1.zip" .\ -Force"
:: If extraction OK .zip file will be deleted.
IF %ERRORLEVEL% NEQ 0 EXIT /b %ERRORLEVEL%
del .\Remote_Power_Pro_V2.1.zip /F

:Install_RemotePowerPro
robocopy "Remote Power Pro_V2.1" "%PUBLIC%\Documents\Remote Power Pro_V2.1" /s
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%PUBLIC%\Desktop\Remote Power Pro.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%PUBLIC%\Documents\Remote Power Pro_V2.1\Remote Power Pro.exe" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs
IF %ERRORLEVEL% EQU 0 ( IF EXIST ".\Remote Power Pro_V2.1\" ( 
		 RD /S /Q ".\Remote Power Pro_V2.1\") )
ECHO Remote Power Pro : OK>> output.log