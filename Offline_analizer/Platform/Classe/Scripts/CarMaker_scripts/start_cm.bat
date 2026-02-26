@echo off
setlocal enableextensions
:: Core Affinity and Priority changes for RT Rack
set /a cpu_number=%NUMBER_OF_PROCESSORS%
:: If the RT Rack has 8 CPUs Affinity of the RTK set to CPU5 and CPU7 and Priority to high
:: If the RT Rack has 12 CPUs Affinity of the RTK set to CPU9 and CPU11 and Priority to high
if %cpu_number% EQU 8 (
	 wmic process where name="RuntimeKernel.exe" CALL setpriority "high priority"
	 powershell.exe "$p = Get-Process RuntimeKernel; $p.ProcessorAffinity = 0x00A0"
	 echo CPU has 8 Processors) 
if %cpu_number% EQU 12 (
	 wmic process where name="RuntimeKernel.exe" CALL setpriority "high priority"
	 powershell.exe "$p = Get-Process RuntimeKernel; $p.ProcessorAffinity = 0x0A00"
	 echo CPU has 12 Processors)
if %cpu_number% EQU 20 (
	 wmic process where name="RuntimeKernel.exe" CALL setpriority "high priority"
	 powershell.exe "$p = Get-Process RuntimeKernel; $p.ProcessorAffinity = 0x007E"
	 echo CPU has 20 Processors)
		 
REM echo %errorlevel% >> affinity_check.txt :: Line not needed
start "InitCarmaker" X:\Tools\venv\Scripts\python.exe %~dp0\start_cm.py %*