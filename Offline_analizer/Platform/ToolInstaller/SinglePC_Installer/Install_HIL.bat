:: Tool Installer 
:: 2024.10.02
:: Change: Standalone Installations implemented. CarMaker installation added.

@echo off
setlocal enableextensions
cd /d "%~dp0"
powershell ".\Popup.bat | tee answer.txt"
REM ECHO DOWNLOADING
REM powershell ".\downloader.bat | tee log_download.log"
REM IF %ERRORLEVEL% NEQ 0 (ECHO Download failed. Please check your share permits or the source packets>>output.log
REM start output.log
REM EXIT /b %ERRORLEVEL%)
set xcmd="FIND "output" answer.txt"
for /f "tokens=* skip=2" %%I in ('%xcmd%') do for %%A in (%%~I) do set usa=%%A
del answer.txt
powershell ".\Install_Python.bat | tee log_Python.log"
IF EXIST CANoe\ (powershell ".\Install_CANoe.bat %usa%| tee log_CANoe.log")
IF EXIST CANape\ (powershell ".\Install_CANape.bat | tee log_CANape.log")
IF EXIST VXtoolsSetup\ IF EXIST Vector_Driver_Setup\ (powershell ".\VectorDrivers.bat | tee log_Drivers.log")
powershell ".\Install_CarMaker.bat | tee CarMaker.log"
ECHO Installation done>>output.log
start output.log
pause