@echo off
setlocal enableextensions

set /a cpu_number=%NUMBER_OF_PROCESSORS%
:: If the RT Rack has 8 CPUs Affinity set to avoid CPU5 and CPU7 and Priority to high or normal
:: If the RT Rack has 12 CPUs Affinity set to avoid CPU9 and CPU11 and Priority to high or normal

if /I "%~1"=="MovieNX"          goto set_affinity_movienx

if %cpu_number% EQU 8 (
	set value=0x005C
	call :set_affinity
	echo CPU has 8 Processors
	exit /b 0) 
	
if %cpu_number% EQU 12 (
	set value=0x05FC
	call :set_affinity
    echo CPU has 12 Processors
	exit /b 0)

if %cpu_number% EQU 20 (
	set value=0xFFF80
	call :set_affinity
    echo CPU has 20 Processors
	exit /b 0)
	
:set_affinity
wmic process where name="apobrokerd.exe" CALL setpriority "high priority"
powershell.exe "$p = Get-Process apobrokerd; $p.ProcessorAffinity = %value%"
wmic process where name="python.exe" CALL setpriority "normal"
ping -n 1 localhost > nul
powershell.exe "$p = Get-Process python; $p.ProcessorAffinity = %value%"
wmic process where name="HIL.exe" CALL setpriority "high priority"
powershell.exe "$p = Get-Process HIL; $p.ProcessorAffinity = %value%"
wmic process where name="Movie.exe" CALL setpriority "high priority"
powershell.exe "$p = Get-Process Movie; $p.ProcessorAffinity = %value%"
wmic process where name="CarMaker.win64.exe" CALL setpriority "high priority"
powershell.exe "$p = Get-Process CarMaker.win64; $p.ProcessorAffinity = %value%"
exit /b 0

:set_affinity_movienx
wmic process where name="MovieNX.exe" CALL setpriority "high priority"
powershell.exe "$p = Get-Process MovieNX; $p.ProcessorAffinity = 0xFFFD4"
exit /b 0