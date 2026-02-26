echo off
cls


echo ***********************************************************************
echo REBOOT VX DEVICE
echo ***********************************************************************
echo IP_ADDRESS: %1
echo PATH OF SCRIPT:%~dp0

::if "%~1"=="" goto READ_IP_ADDRESS
::set VX_DASY_IP_ADDRESS=%1
set ERRORCOUNT=0

if [%1%] == [] goto READ_IP_ADDRESS
SET VX_DASY_IP_ADDRESS=%1
goto TCC_VX_TOOL_PATH

:READ_IP_ADDRESS
findstr /l "DEVICE_0_IP_ADDRESS:" %~dp0\06_RB_MT_Project_config.ini 
if %errorlevel%==1 goto ERROR_MISSING_DASY_IP_ADDRESS
for /F "delims=" %%a in ( 'findstr /l "DEVICE_0_IP_ADDRESS:" %~dp0\06_RB_MT_Project_config.ini' ) do set "VX_DASY_IP_ADDRESS=%%a"
echo FLASHFILE NAME RAW:%VX_DASY_IP_ADDRESS%
echo ERROR:%errorlevel%
call set VX_DASY_IP_ADDRESS=%%VX_DASY_IP_ADDRESS:DEVICE_0_IP_ADDRESS:=%EMPTY%%%
echo FLASHFILE NAME FINAL:%VX_DASY_IP_ADDRESS%

:TCC_VX_TOOL_PATH
echo *********************************
echo CHECK FOR JETTA/TCC ENVIRONMENT
echo *********************************

::CHECK IF JETTA ENVVARS ARE EXISTING -->IF YES ASSUME JETTA IS AVAILABLE
if "%JETTA_GET_CONFIG_DATA%" == "" echo [INFO] JETTA ENVIRONEMT NOT DETECTED, TRY TO USE SETTINGS FROM LOCAL INSTALLATION
if "%JETTA_GET_CONFIG_DATA%" == "" goto VX_TOOLS_FROM_LOCAL_INSTALLATION

::READ VECTOR HW LABEL FROM CONFIG FILE TO DECIDE FOR TCC TOOLSET FITTING INSIDE JETTA
findstr /l "VECTOR_HW_CONFIG_LABEL:" %~dp0\06_RB_MT_Project_config.ini >NUL
if %errorlevel%==1 goto ERROR_DEVICE_NAME
for /F "delims=" %%a in ( 'findstr /l "VECTOR_HW_CONFIG_LABEL:" %~dp0\06_RB_MT_Project_config.ini' ) do set "VECTOR_HW_CONFIG_LABEL=%%a"
echo ERROR:%errorlevel%
call set VECTOR_HW_CONFIG_LABEL=%%VECTOR_HW_CONFIG_LABEL:VECTOR_HW_CONFIG_LABEL:=%EMPTY%%%
echo VECTOR_HW_CONFIG_LABEL:%VECTOR_HW_CONFIG_LABEL%

::GET TCC TOOLPATHS PATH BATCH FILE FROM TCC FOR THE VARIANT WITH VECTOR HW LABEL
powershell %JETTA_GET_CONFIG_DATA% %VECTOR_HW_CONFIG_LABEL% JETTA_TCC_INITALIZE_PATHS BAT >%~dp0TCC_SETTING
SET /p TCC_TOOLPATHS=<%~dp0TCC_SETTING
del %~dp0TCC_SETTING

if "%TCC_TOOLPATHS%" == "" echo [INFO] COULD NOT RECEIVE TCC TOOLPATHS FOR VARIANT %VECTOR_HW_CONFIG_LABEL%. USING VX TOOLS FROM LOCAL CONFIGURATION
if "%TCC_TOOLPATHS%" == "" goto VX_TOOLS_FROM_LOCAL_INSTALLATION
echo TCC TOOLPATHS:%TCC_TOOLPATHS%
::CALL TCC TOOLPATHS FILE RECIEVED FROM JETTA TO GET TCC PATHS
call %TCC_TOOLPATHS%

::GET TCC TOOL INTENDED TO BE USED FOR THE VARIANT WITH VECTOR HW LABEL
powershell %JETTA_GET_CONFIG_DATA% %VECTOR_HW_CONFIG_LABEL% JETTA_TCC_VX_TOOL_SELECTOR BAT >%~dp0TCC_SETTING
SET /p VX_TOOLS_PATH=<%~dp0TCC_SETTING
del %~dp0TCC_SETTING


::BUILD TOOLPATH FOC VX TOOL SELECTED
set VX_TOOLS_PATH=!%VX_TOOLS_PATH%!
echo DETECTED VX TOOLS INSTALLATION PATH:%VX_TOOLS_PATH%
set VX_TOOLS_EXE="%VX_TOOLS_PATH%\VXconfig.exe"
echo DETECTED VX TOOLS EXE:%VX_TOOLS_EXE%
goto EXECUTE_RESET
:VX_TOOLS_FROM_LOCAL_INSTALLATION
echo *********************************
echo GET CONFIGURED VX TOOLS PATH [NORMAL INSTALLED TOOL FROM OFFICIAL WEBSITE]
echo *********************************
findstr /l /c:"VXTOOLS_APPLICATION_ID:" %~dp0\07_RB_MT_Platform_config.ini
rem if %errorlevel%==1 goto ERROR_MISSING_POD_PARAMETER_FILE
for /F "delims=" %%a in ( 'findstr /l /c:"VXTOOLS_APPLICATION_ID:" 07_RB_MT_Platform_config.ini' ) do set "VX_APPLICATION=%%a"
::echo CANAPE PATH RAW:%VX_APPLICATION%

call set VX_APPLICATION=%%VX_APPLICATION:VXTOOLS_APPLICATION_ID:=%EMPTY%%%
::echo CANAPE Application FINAL:%VX_APPLICATION%

set VX_APPLICATION=HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VX_APPLICATION%
                      :: HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\VXtools3.8
::reg export %CANAPE_APPLICATION% CanapeApplication.txt
Set Reg.Key=%VX_APPLICATION%
Set Reg.Val=InstallLocation

For /F "Tokens=2*" %%A In ('Reg Query "%Reg.Key%" /v "%Reg.Val%" ^| Find /I "%Reg.Val%"' ) Do Call Set VX_TOOLS_PATH=%%B
::if %errorlevel% goto VXTOOLS_VERSION_ERROR
if exist %VX_TOOLS_PATH% ( echo PATH EXISTS ) ELSE ( goto VXTOOLS_VERSION_ERROR )

if %errorlevel% ==1 goto VXTOOLS_VERSION_ERROR
set VX_TOOLS_EXE="%VX_TOOLS_PATH%\VXconfig.exe"
echo DETECTED VX TOOLS INSTALLATION PATH:%VX_TOOLS_PATH%
echo DETECTED VX TOOLS EXE:%VX_TOOLS_EXE%
echo *********************************


goto EXECUTE_RESET
:ERROR_MISSING_DASY_IP_ADDRESS
ECHO ERROR! NO IP ADDRESS DEFINED IN CONFIGURATION FILE !
sleep 10
goto END


:EXECUTE_RESET
Call %VX_TOOLS_EXE% -net %VX_DASY_IP_ADDRESS% -r
if %ERRORLEVEL% ==0 GOTO SUCCESS
echo
echo
echo
echo ***********************************************************************
echo ERROR: CANAPE STILL IN ONLINE MODE ! SET CANAPE TO OFFLINE MODE TO REBOOT VX DEVICE AND RESTART THIS BATCH
echo ***********************************************************************
sleep 5
echo RETRY %ERRORCOUNT%
@echo RETRYING VX RESET %ERRORCOUNT% >> .\DATA_OUT\VX_RESET.txt
set /A ERRORCOUNT=%ERRORCOUNT%+1
if %ERRORCOUNT% EQU "5" GOTO END
goto EXECUTE_RESET


:SUCCESS
echo ***********************************************************************
echo REBOOT SUCCESSFULLY DONE , THIS WINDOW WILL CLOSE IN 7s
echo ***********************************************************************
::sleep 7

) 
:END