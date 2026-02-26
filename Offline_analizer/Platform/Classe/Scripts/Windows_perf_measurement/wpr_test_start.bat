@echo off
setlocal enableextensions
cd /d "%~dp0"
del /F wpr_trace_status.txt
set "status=wpr_trace_status.txt"

REM Set folder name
set timestamp=%date:~-4%%date:~-7,2%%date:~-10,2%-%time:~-11,2%%time:~-8,2%%time:~-5,2%

echo Starting Windows performance mesurement
echo Log can be found in folder %timestamp%

REM Create directory for log file
mkdir "%~dp0%timestamp: =0%

REM Start the measurement
wpr -start cpu
if %errorlevel% equ 0 (echo 1 > %status%) else (echo 2 > %status%)
ping -n 3 localhost > Nul
del /F %status%