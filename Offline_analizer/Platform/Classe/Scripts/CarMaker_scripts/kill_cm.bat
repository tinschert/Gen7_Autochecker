@echo off
taskkill /f /im HIL.exe
taskkill /f /im HIL.exe
taskkill /f /im Movie.exe
taskkill /f /im Movie.exe
taskkill /f /im MovieNX.exe
taskkill /f /im MovieNX.exe
taskkill /f /fi "WINDOWTITLE eq InitCarmaker"
taskkill /f /fi "WINDOWTITLE eq InitCarmaker"
taskkill /f /im CarMaker.win64.exe
taskkill /f /im CarMaker.win64.exe
taskkill /f /fi "WINDOWTITLE eq CANoePy_GUI"
taskkill /f /fi "WINDOWTITLE eq CANoePy_CLI"
taskkill /f /fi "WINDOWTITLE eq CANoePy_GUI"
taskkill /f /fi "WINDOWTITLE eq CANoePy_CLI"

set error_file=D:\\UserFiles\\apps_status.txt

rem Check if the error log file exists
if exist %error_file% (
    rem Delete the error log file
    del %error_file%
    echo Error log file "%error_file%" has been deleted.
) else (
    echo Error log file "%error_file%" does not exist.     
)

rem Define the processes to check
set processes=HIL.exe Movie.exe

rem Loop through the processes and check if they are running
for %%p in (%processes%) do (
    tasklist /FI "IMAGENAME eq %%p" | findstr /i %%p > nul
    if errorlevel 1 (
        echo %%p is not running
	set app_status=1
    ) else (
        echo Error!!! %%p is still running
        set app_status=2
    )
)

rem Define the window title to search for
set window_title=InitCarmaker

rem Check if the window with the specified title is running
tasklist /FI "WINDOWTITLE eq %window_title%" | findstr /i cmd.exe > nul
if errorlevel 1 (
    echo Command Prompt window with title "%window_title%" is not running
    set window_status=1
    
) else (
    echo Command Prompt window with title "%window_title%" is running
    set window_status=2
)

if %app_status% == 1 (
    if %window_status% == 1  (
    	echo 1 > %error_file%
    	echo Exit code written to %error_file% )
) else (
    echo 2 > %error_file%
    echo Exit code written to %error_file%
)

