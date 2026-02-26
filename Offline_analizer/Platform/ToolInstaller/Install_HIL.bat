:: Tool Installer 
:: 2023.10.02
:: Change: Deleted downloader script.

@echo off
setlocal enableextensions
cd /d "%~dp0"
powershell ".\Popup.bat | tee answer.txt"
set xcmd="FIND "output" answer.txt"
for /f "tokens=* skip=2" %%I in ('%xcmd%') do for %%A in (%%~I) do set usa=%%A
del answer.txt
powershell ".\Install_Python.bat | tee log_Python.log"
powershell ".\Install_EnvSim_Tool.bat | tee log_EnvSim.log"
IF EXIST CANoe\ (powershell ".\Install_CANoe.bat %usa%| tee log_CANoe.log")
IF EXIST CANape\ (powershell ".\Install_CANape.bat | tee log_CANape.log")
IF EXIST "Remote Power Pro_V2.1\" (powershell ".\Install_Power_Remote.bat | tee log_Power.log")
IF EXIST VXtoolsSetup\ IF EXIST Vector_Driver_Setup\ (powershell ".\VectorDrivers.bat | tee log_Drivers.log")
IF EXIST vTESTstudio\ (powershell ".\Install_VTstudio.bat | tee log_VTstudio.log")
powershell ".\Install_CarMaker.bat | tee CarMaker.log"
ECHO Installation done>>output.log
start output.log
pause