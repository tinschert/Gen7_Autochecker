:: EnvSim Tool Standalone Installation
:: 2023.01.13
:: Change: Destination folder will be now selected depending if D:\ Drive exists or not

@echo off
setlocal enableextensions
cd /d "%~dp0"
:: Source Path If the source path is changed, please change it here:
set src=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\EnvSim

:: Enter here the version number to install as follows:
set ver=Version_3_31_8

:: Selection of the destination path, depending of the existence of a D:\ drive. If the destination path is changed, please change it here:
if exist D:\ (set dst=D:\_RBS\Tool\EnvSim) else (set dst=C:\_RBS\Tool\EnvSim)

:: Check if the actual version is already installed, if not it'll install it.
if exist %dst%\EnvironmentSimulator.exe ( if exist %dst%\%ver%.txt ( 
		echo EnvSim Tool : Already installed - %date% %time:~0,5%>> output.log) 
		exit 0
)else (
		goto Copy_Tool
		)

:: The function "Copy_Tool" copies the zip file from the source to the destination, unzips the file and deletes it. A Log file and the version text file are created 
:Copy_Tool
robocopy "%src%" "%dst%" EnvSim.zip
powershell -command "Expand-Archive "%dst%\EnvSim.zip" "%dst%" " -force
echo %ver% Installed on %date% at %time:~0,5% >> %dst%\%ver%.txt
del %dst%\EnvSim.zip
echo EnvSim Tool : OK - %date% %time:~0,5%>> output.log
exit 0