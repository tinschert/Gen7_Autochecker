@echo off
setlocal enableextensions

REM Run wmic command and save the result in a string
wmic PATH Win32_VideoController GET Name > gpu.txt

REM Find if the RT Rack has an NVIDIA GPU if so it is a BYO RT Rack
FIND "NVIDIA" gpu.txt > Nul

echo %errorlevel%
if %errorlevel% equ 0 (
		echo 1 > %~dp0\BYO_RT_Rack.txt
		echo BYO RT Rack available.
		) else (
		echo 2 > %~dp0\BYO_RT_Rack.txt
		echo BYO RT Rack not available.)
del /F gpu.txt
exit /b 0