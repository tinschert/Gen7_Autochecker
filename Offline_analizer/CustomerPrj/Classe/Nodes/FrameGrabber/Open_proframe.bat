:: Frame Grabber starting and screnshots script
:: Author: Pablo Forchino
:: 2023.04.26
:: Description: Starts the proFrame SW on the PC where the software is connected and executes 4 different tasks,
:: depending on the recieved input (screen_0, screen_1, screen_2, screen_3, channel_0, channel_1, channel_2 and if needed channel_3).
:: Return codes as follow: 0 = OK, 1 = error, 2 = running, 3 = no connection to ECU.
:: When a screenshot is taken, the filename (only the latest name) will be printed to the file: filename.txt,
:: this will be then used by VTStudio to add the screenshot to the report.

@echo off
setlocal enableextensions

set rtm=%~2
set pth=D:\Tools\FrameGrabber\proFRAME\src\win64\x64\Release\
cd /d "%~dp0"
set ret="%CD%\returncode.txt"

:: Checking for the Output Folder if not there it will be created. Should the output folder change, please update here
cd /d "..\..\..\..\"
set out=%CD%\Screenshots\
if not exist "%out%" (mkdir "%out%")

:: Set status to running
echo 2 > %ret%

:: Get current date
for /F "tokens=1,2,3 delims=_" %%i in ('PowerShell -Command "& {Get-Date -format "yyyy_MM_dd"}"') do (set _date=%%i.%%j.%%k)
echo %_date%

:: Function selection
if /I "%~1"==""                 goto abort
if /I "%~1"=="-h"				goto help
if /I "%~1"=="screen_0"			goto screen_0
if /I "%~1"=="screen_1"			goto screen_1
if /I "%~1"=="screen_2"			goto screen_2
if /I "%~1"=="screen_3"			goto screen_3			
if /I "%~1"=="channel_0"		goto channel_0
if /I "%~1"=="channel_1"		goto channel_1
if /I "%~1"=="channel_2"		goto channel_2
if /I "%~1"=="channel_3"		goto channel_3

:: Initializing FG
:init
%pth%sxpf-init-sequence.exe /dev/sxpf0 -port 0 -ini "D:\Tools\FrameGrabber\SXPF_V3_Minimal_Config_Quad_TI9702_Ver2.ini" --execute 0
%pth%rb-dvreg.exe 0 0 "D:\Tools\FrameGrabber\Ford_Toliman_TI_SerDes_FPD4_20221025_sync_static_values.dvreg"
exit /b 0

:: Checking connection to ECU
:connection_status
:: checks the connection status and return the variable "sta". If this one ends with "3" it's connected otherwise it ends with "0"
set tmp=%pth%sxpfi2c.exe 0 0 0x7a 1 0x4d
for /F "tokens=* usebackq" %%F in (`%tmp%`) do (set sta=%%F)
set sta=%sta:~-1%
echo %sta%
exit /b 0

:: Taking 1 screenshot of channel 0 "Main View"
:screen_0
echo 1 screenshot of channel 0
call :init
call :connection_status
set img=%_date%_%TIME:~0,2%.%TIME:~3,2%.%TIME:~6,2%_img_main
set pthimg=%out%\%img%
if %sta%==3 (
%pth%sxpfapp.exe --card 0 --channel 3 -d 0x1E -l8 -g 1920x1248@0x0 -O1 -n"%pthimg%" --output-format png -T1
) else (
echo 3 > %ret% && exit /b 0
)
echo %img%.png > %out%\filename.txt
if %ERRORLEVEL% NEQ 0 (echo 1 > %ret%) else (echo 0 > %ret%)
exit /b 0

:: Taking 1 screenshot of channel 1 "360 View"
:screen_1
echo 1 screenshot of channel 1 
call :init
call :connection_status
set img=%_date%_%TIME:~0,2%.%TIME:~3,2%.%TIME:~6,2%_img_360
set pthimg=%out%\%img%
if %sta%==3 (
%pth%sxpfapp.exe --card 0 --channel 3 -d 0x5E -l8 -g 1920x1248@0x0 -O1 -n"%pthimg%" --output-format png -T1
) else (
echo 3 > %ret% && exit /b 0
)
echo %img%.png > %out%\filename.txt
if %ERRORLEVEL% NEQ 0 (echo 1 > %ret%) else (echo 0 > %ret%)
exit /b 0

:: Taking 1 screenshot of channel 2 "Supplementary View"
:screen_2
echo 1 screenshot of channel 2 
call :init
call :connection_status
set img=%_date%_%TIME:~0,2%.%TIME:~3,2%.%TIME:~6,2%_img_supp
set pthimg=%out%\%img%
if %sta%==3 (
%pth%sxpfapp.exe --card 0 --channel 3 -d 0x9E -l8 -g 1920x1248@0x0 -O1 -n"%pthimg%" --output-format png -T1
) else (
echo 3 > %ret% && exit /b 0
)
echo %img%.png > %out%\filename.txt
if %ERRORLEVEL% NEQ 0 (echo 1 > %ret%) else (echo 0 > %ret%)
exit /b 0

:: Taking 1 screenshot of channel 3 "not used atm"
:screen_3
echo 1 screenshot of channel 3 
call :init
call :connection_status
set img=%_date%_%TIME:~0,2%.%TIME:~3,2%.%TIME:~6,2%_img_ch3
set pthimg=%out%\%img%
if %sta%==3 (
%pth%sxpfapp.exe --card 0 --channel 3 -d 0xDE -l8 -g 1920x1248@0x0 -O1 -n"%pthimg%" --output-format png -T1
) else (
echo 3 > %ret% && exit /b 0
)
echo %img%.png > %out%\filename.txt
if %ERRORLEVEL% NEQ 0 (echo 1 > %ret%) else (echo 0 > %ret%)
exit /b 0

:: Live view of channel 0	
:channel_0
echo Channel 0 live
call :init
call :connection_status
if %sta%==3 (%pth%sxpfapp.exe --card 0 --channel 3 -d 0x1E -l8 -g 1920x1248@0x0 -T%rtm%) else (echo 3 > %ret% && exit /b 0)
if %ERRORLEVEL% NEQ 0 (echo 1 > %ret%) else (echo 0 > %ret%)
exit /b 0

:: Live view of channel 1
:channel_1
echo Channel 1 live
call :init
call :connection_status
if %sta%==3 (%pth%sxpfapp.exe --card 0 --channel 3 -d 0x5E -l8 -g 1920x1248@0x0 -T%rtm%) else (echo 3 > %ret% && exit /b 0)
if %ERRORLEVEL% NEQ 0 (echo 1 > %ret%) else (echo 0 > %ret%)
exit /b 0

:: Live view of channel 2
:channel_2
echo Channel 2 live
call :init
call :connection_status
if %sta%==3 (%pth%sxpfapp.exe --card 0 --channel 3 -d 0x9E -l8 -g 1920x1248@0x0 -T%rtm%) else (echo 3 > %ret% && exit /b 0)
if %ERRORLEVEL% NEQ 0 (echo 1 > %ret%) else (echo 0 > %ret%)
exit /b 0

:: Live view of channel 3
:channel_3
echo Channel 3 live
call :init
call :connection_status
if %sta%==3 (%pth%sxpfapp.exe --card 0 --channel 3 -d 0xDE -l8 -g 1920x1248@0x0 -T%rtm%) else (echo 3 > %ret% && exit /b 0)
if %ERRORLEVEL% NEQ 0 (echo 1 > %ret%) else (echo 0 > %ret%)
exit /b 0

:abort
echo "Error: no argument entered for mode option"
echo 1 > %ret%
exit /b 0

:help
echo  ******************************************************************************
echo  * This script takes eight different arguments that perform the following tasks:
echo  * 
echo  * use "screen_0" to take one screenshot of channel_0
echo  * 
echo  * use "screen_1" to take one screenshot of channel_1
echo  * 
echo  * use "screen_2" to take one screenshot of channel_2
echo  * 
echo  * use "screen_3" to take one screenshot of channel_3
echo  *  
echo  * use "channel_0" to start the live view on the virtual channel 0
echo  *  
echo  * use "channel_1" to start the live view on the virtual channel 1
echo  * 
echo  * use "channel_2" to start the live view on the virtual channel 2
echo  * 
echo  * use "channel_3" to start the live view on the virtual channel 3
echo  ******************************************************************************
echo 1 > %ret%
exit /b 0