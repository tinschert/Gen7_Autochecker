:: Vector Drivers and VXTools Standalone Installation
:: 2023.09.05
:: Change: update to Vector Drivers V.23.10.0

@echo off
setlocal enableextensions
cd /d "%~dp0"
:: Here please change the path to the source of the actual version of the vector drivers. Zip file-name must be equal to "Vector_Driver_Setup.zip"
set src1=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\Vector_Driver_Setup\V.23.10.0

:: Here please change the path to the source of the actual version of VX Tools. Zip file-name must be equal to "VXtoolsSetup.zip"
set src2=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\VXtools\V4.4_SP2

:: New path for the source file added. SW won't be downloaded anymore, it will be copied from the network share. Change path according to new version
:Download_Vector_Drivers
IF EXIST Vector_Driver_Setup\ echo Vector_Drivers downloaded && GOTO :Download_VX_Tools
IF EXIST Vector_Driver_Setup.zip GOTO Extract_Vector_Drivers
robocopy "%src1%" .\ Vector_Driver_Setup.zip
:: Robocopy ERRORLEVEL must be o or 1 
IF %ERRORLEVEL% GTR 1 EXIT /b %ERRORLEVEL%
:Extract_Vector_Drivers
powershell -command "Expand-Archive ".\Vector_Driver_Setup.zip" ".\Vector_Driver_Setup" "
:: If extraction OK .zip file will be deleted.
IF %ERRORLEVEL% NEQ 0 EXIT /b %ERRORLEVEL%
del .\Vector_Driver_Setup.zip /F

:: New path for the source file added. SW won't be downloaded anymore, it will be copied from the network share. Change path according to new version
:Download_VX_Tools
IF EXIST VXtoolsSetup\ echo VX_Tools downloaded && GOTO :Install_VX_Tools
IF EXIST VXtoolsSetup.zip GOTO Extract_VX_tools
robocopy "%src2%" .\ VXtoolsSetup.zip
:: Robocopy ERRORLEVEL must be o or 1 
IF %ERRORLEVEL% GTR 1 EXIT /b %ERRORLEVEL%
:Extract_VX_tools
powershell -command "Expand-Archive ".\VXtoolsSetup.zip" ".\VXtoolsSetup" "
:: If extraction OK .zip file will be deleted.
IF %ERRORLEVEL% NEQ 0 EXIT /b %ERRORLEVEL%
dir "%cd%\VXtoolsSetup" /b > temp.txt
for /f %%A in ('FIND ".exe" temp.txt') do set VXtoolsName=%%A
ren "%cd%\VXtoolsSetup\%VXtoolsName%" "VXtoolsSetup.exe"
del temp.txt
del .\VXtoolsSetup.zip /F

:Install_VX_Tools
echo "Installing VX Tools"
REM start taskkiller.bat
"VXtoolsSetup\VXtoolsSetup.exe" /s
IF %ERRORLEVEL% EQU 0 ( IF EXIST ".\VXtoolsSetup" ( 
		 RD /S /Q ".\VXtoolsSetup") )
IF %ERRORLEVEL% EQU 0 (ECHO VX Tools : OK>> output.log) ELSE (ECHO VX Tools : NOT OK>> output.log)		 
echo "Installing Vector Drivers"
"Vector_Driver_Setup\Drivers\setup.exe" /s /installCert /i all
IF %ERRORLEVEL% EQU 0 ( IF EXIST ".\Vector_Driver_Setup" ( 
		 RD /S /Q ".\Vector_Driver_Setup") )
IF %ERRORLEVEL% EQU 0 (ECHO Vector Drivers : OK>> output.log) ELSE (ECHO Vector Drivers : NOT OK>> output.log)