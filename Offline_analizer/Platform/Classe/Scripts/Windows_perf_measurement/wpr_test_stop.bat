@echo off
setlocal enableextensions
cd /d "%~dp0"
del /F wpr_trace_status.txt
set "status=wpr_trace_status.txt"

REM Search for folder name
FOR /F "delims=" %%i IN ('dir /b /ad /t:c /od') DO SET a=%%i
echo Most recent folder: %a%

REM Stop the measurement
wpr -stop "%~dp0%a: =0%\log.etl" [-compress]
if %errorlevel% equ 0 (echo 3 > %status%) else (echo 2 > %status%)
ping -n 3 localhost > Nul
del /F %status%
