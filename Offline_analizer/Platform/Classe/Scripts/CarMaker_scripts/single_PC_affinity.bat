@echo off
setlocal enableextensions
:: Core Affinity and Priority changes for Single PC Setup only
set /a cpu_number=%NUMBER_OF_PROCESSORS%

:: Current Performance PC has 20 CPUs (HP Z2 G9)
if %cpu_number% EQU 20 (
	 wmic process where name="RuntimeKernel.exe" CALL setpriority "high priority"
	 powershell.exe "$p = Get-Process RuntimeKernel; $p.ProcessorAffinity = 0x007E"
	 echo CPU has 20 Processors)