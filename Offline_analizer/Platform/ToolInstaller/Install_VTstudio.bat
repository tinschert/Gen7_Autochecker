:: vTESTstudio Standalone Installation
:: Version 6 SP4 (6.4.1.0)
:: 2022.11.07
:: Change: Source packet now in sharefolder. 

@echo off
setlocal enableextensions
cd /d "%~dp0"
ECHO "Checking prerequisites, please wait..."
wmic product get name,version > prerequisites.txt

:: Source path for the shared Repo. 
:: Here please change the path to the source of the actual version. Zip file-name must be always "vTESTstudio.zip"
set src=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\vTESTstudio\V6_SP4

GOTO Install_VT_studio

:VerCompare
powershell -command "&{exit(([version]$args[0]).CompareTo([version]$args[1]))}" "%~1" "%~2"
IF ERRORLEVEL 1 (ECHO "%~1" is newer than "%~2"
SET "%~3=1")  ELSE (IF ERRORLEVEL 0 (
ECHO "%~1" is the same as "%~2"
SET "%~3=1") ELSE (ECHO "%~1" is older than "%~2"
SET "%~3=0"))
EXIT /B 0
:NameSearch
set last="0.0"
set xcmd="FIND "%~1" prerequisites.txt"
for /f "tokens=* skip=2" %%I in ('%xcmd%') do for %%A in (%%~I) do set last=%%A
call :VerCompare "%last%","%~3",result
IF %result% EQU 1 EXIT /B 0
ECHO "Installing %~1"
REM "%~2"
set "command=%~2"
set "command=%command:""="%"
call :Download_vTestStudio
%command%
EXIT /B 0

:Download_vTestStudio
IF EXIST vTESTstudio\ EXIT /b %ERRORLEVEL%
IF EXIST vTESTstudio.zip GOTO Extract_VT_studio
:: Source packet will be copied to the local folder and extracted. Zip file will be deleted after successful extraction.
echo "Downloading vTESTstudio, please wait..."
robocopy "%src%" .\ vTESTstudio.zip
:: Robocopy ERRORLEVEL must be o or 1 
IF %ERRORLEVEL% GTR 1 EXIT /b %ERRORLEVEL%
:Extract_VT_studio
powershell -command "Expand-Archive ".\vTESTstudio.zip" ".\vTESTstudio" -Force"
IF %ERRORLEVEL% NEQ 0 EXIT /b %ERRORLEVEL%
del .\vTESTstudio.zip /F
EXIT /B 0

:Install_VT_studio
call :NameSearch "Vector vTESTstudio 6 ","""vTESTstudio\vTESTstudio_V6.0\Application\setup.exe"" /s /v"/qn"","6.4.1.0"
:: Before finishing, if the installation was OK, the folder will be completely removed.
IF %ERRORLEVEL% EQU 0 ( IF EXIST .\vTESTstudio ( 
		RD /S /Q .\vTESTstudio) )
IF %ERRORLEVEL% EQU 0 (ECHO vTESTstudio : OK>> output.log) ELSE (ECHO vTESTstudio : NOT OK>> output.log)