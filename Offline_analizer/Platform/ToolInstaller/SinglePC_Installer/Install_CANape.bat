:: CANape Standalone Installation
:: Version 19SP5 (19.0.50.1172)
:: 2022.11.30
:: Change: Standalone Installation implemented. Source packet now in sharefolder (corrected).

@echo off
setlocal enableextensions
cd /d "%~dp0"

:: Source path for the shared Repo. 
:: Here please change the path to the source of the actual version. Zip file-name must be always "CANape.zip"
set src=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\CANape\V19_SP5
ECHO "Checking prerequisites, please wait..."
wmic product get name,version > prerequisites.txt
GOTO :Precheck

:: Version Check ::
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
IF %result% EQU 1 (EXIT /B 0) ELSE (call :Download_CANape)
ECHO "Installing %~1"
REM "%~2"
set "command=%~2"
set "command=%command:""="%"
%command%
EXIT /B 0

:: Download / Extraction / Cleaning zip file ::
:Download_CANape
IF EXIST CANape\ EXIT /b %ERRORLEVEL%
IF EXIST CANape.zip GOTO Extract_CANape
echo "Downloading CANape, please wait..."
robocopy "%src%" .\ CANape.zip
:: Robocopy ERRORLEVEL must be o or 1 
IF %ERRORLEVEL% GTR 1 EXIT /b %ERRORLEVEL%
:Extract_CANape
powershell -command "Expand-Archive ".\CANape.zip" ".\CANape" "
:: If extraction OK .zip file will be deleted.
IF %ERRORLEVEL% NEQ 0 EXIT /b %ERRORLEVEL%
del .\CANape.zip /F
EXIT /B 0
:: PREREQUISITES ::

:: Check Prerequisites for changes or updates in the "AdminManualAll.html" file inside the Software folder (Point 5.2.1). If changes are needed please update the functions acordingly

:Install_VS2015_x64
REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" | FINDSTR /I /C:"{F20396E5-D84E-3505-A7A8-7358F0155F6C}" > nul
IF %ERRORLEVEL% EQU 0 GOTO Install_LDF
call :Download_CANape
ECHO "Installing Microsoft Visual C++ 2015 Update 3 Redistributable Package (x64)"
"CANape\ISSetupPrerequisites\VC 2015-2019 Redist (x64)\vc_redist.x64.exe" /q /norestart
:: Checked -> yes

:Install_LDF
call :NameSearch "Vector LDF Explorer","""CANape\ISSetupPrerequisites\Vector LDF Explorer\LDFExplorer.msi"" /qn /l*v %TEMP%\PMCBundleInstallLDFExplorer.log ARPCOMMENTS=""Bundled with Vector Product like CANape, CANdito, vSignalyzer. DO NOT REMOVE if you are using one them""","1.5.14"
:: Checked -> yes

:Install_MSXML
REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" | FINDSTR /I /C:"{A43BF6A5-D5F0-4AAA-BF41-65995063EC44}" > nul
IF %ERRORLEVEL% EQU 0 GOTO Install_CANapeRecordingService
call :Download_CANape
ECHO "Installing MSXML 6.10.1129.0"
"CANape\ISSetupPrerequisites\{726F97A8-63B9-4A58-ACFB-B8A56B383740}\msxml6_x86.msi" /qn
:: Checked -> yes

:Install_CANapeRecordingService
REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" | FINDSTR /I /C:"{97580C70-CAF9-4449-BEB2-D609AD71DC19}" > nul
IF %ERRORLEVEL% EQU 0 GOTO Install_VS2015_x86
call :Download_CANape
ECHO "Installing Vector CANape Recording Service"
"CANape\ISSetupPrerequisites\Vector CANape Recording Service\Vector CANape Recording Service.msi" /qn /l*v %TEMP%\PMCBundleInstalllRecordingServiceLog.log SERVICELOCAL=1 ARPCOMMENTS="Bundled with Vector Product CANape"
:: Checked -> yes

:Install_VS2015_x86
REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" | FINDSTR /I /C:"{37B55901-995A-3650-80B1-BBFD047E2911}" > nul
IF %ERRORLEVEL% EQU 0 GOTO Install_SecurityManager
call :Download_CANape
ECHO "Installing Microsoft Visual C++ 2015 Update 3 Redistributable Package (x86)"
"CANape\ISSetupPrerequisites\VC 2015-2019 Redist (x86)\vc_redist.x86.exe" /q /norestart
:: Checked -> yes

:Install_SecurityManager
call :NameSearch "Vector Security Manager","""CANape\ISSetupPrerequisites\Vector Security Manager\VectorSecurityManager.msi"" /qn /l*v %TEMP%\SecurityManagerBundle.log","2.10.16.0"
:: Checked -> yes

:Install_ODXStudio
call :NameSearch "Vector ODXStudio","""CANape\ISSetupPrerequisites\Vector ODXStudio\ODXStudio.msi"" /qn /l*v %TEMP%\CANapeBundleInstallODXStudio.log DESKTOP_SHORTCUTS=FALSE DESKTOPSHORTCUT=0 ODXSTUDIO_ADDDESKTOPICON=0","4.1"
:: Checked -> yes

REM :Install_NETFramework462
REM ECHO "TODO: Add installation check"
REM ECHO "Installing Microsoft .NET Framework 4.6.2 Full"
REM "CANape\ISSetupPrerequisites\{79322030-9447-4BE5-BF26-F2E5B6529F09}\NDP462-KB3151800-x86-x64-AllOS-ENU.exe" /q /norestart
:: Deprecated

:Install_CANdelaStudio
call :NameSearch "Vector CANdelaStudio","""CANape\ISSetupPrerequisites\Vector CANdelaStudio\CANdelaStudio.msi"" /qn /l*v %TEMP%\CANapeBundleInstallCANdelaStudio.log CANDELASTUDIO_ADDDESKTOPICON=0 REBOOTREQUIRED=0 CS_ADDDESKTOPICON_EN=0 CS_ADDDESKTOPICON_DE=0 CS_ADDDESKTOPICON_JA=0 INSTALLASBUNDLEDPRODUCT=1","9.1"
:: Checked -> yes

:Install_VS2017_x86
REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" | FINDSTR /I /C:"{7258184A-EC44-4B1A-A7D3-68D85A35BFD0}" > nul
IF %ERRORLEVEL% EQU 0 GOTO Install_ASAP
call :Download_CANape
ECHO "Installing Microsoft Visual C++ 2017 Redistributable Package (x86)"
"CANape\ISSetupPrerequisites\VC 2015-2019 Redist (x86)\vc_redist.x86.exe" -q -norestart
:: Checked -> yes

:Install_ASAP
call :NameSearch "Vector ASAP2 Studio CANape","""CANape\ISSetupPrerequisites\Vector ASAP2 Studio\Vector ASAP2 Studio Service 2.2.msi"" /qn /l*v %TEMP%\ASAP2StudioBundle.log","1.2"
:: Checked -> yes

:Install_SupportAssistant
call :NameSearch "Vector Support Assistant","""CANape\ISSetupPrerequisites\Vector Support Assistant\Vector Support Assistant.msi"" /qn /l*v %TEMP%\VectorSupportAssistant.log","3.7.2"
:: Checked -> yes

:Install_AUTOSAR23
call :NameSearch "Vector AUTOSAR Explorer 1","""CANape\ISSetupPrerequisites\Vector AUTOSAR Explorer\AUTOSARExplorer2.msi"" /qn /l*v %TEMP%\\PMCBundleInstallAUTOSARExplorer.log ARPCOMMENTS=""Bundled with Vector Product like CANape, CANdito, vSignalyzer. DO NOT REMOVE if you are using one them""","2.1.0"
:: Checked -> yes

:Install_VS2017_x64
REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" | FINDSTR /I /C:"{9D29FC96-9EEE-4253-943F-96B3BBFDD0B6}" > nul
IF %ERRORLEVEL% EQU 0 GOTO Install_VS2013_x86
call :Download_CANape
ECHO "Installing Microsoft Visual C++ 2017 Redistributable Package (x64)"
"CANape\ISSetupPrerequisites\VC 2015-2019 Redist (x64)\vc_redist.x64.exe" -q -norestart
:: Checked -> yes

:Install_VS2013_x86
REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" | FINDSTR /I /C:"{577ff5ba-39aa-4d8c-a3a9-f95012763438}" > nul
IF %ERRORLEVEL% EQU 0 GOTO Install_CANdelaPersistors
call :Download_CANape
ECHO "Installing Microsoft Visual C++ 2013 Update Redistributable Package (x86)"
"CANape\ISSetupPrerequisites\VC 2013 SP1 Redist\vcredist_x86.exe" /q
:: Checked -> yes

:Install_CANdelaPersistors
call :NameSearch "Vector CANdelaPersistors","""CANape\ISSetupPrerequisites\Vector CANdela Persistors\CANdelaPersistors.msi"" /qn /l*v %TEMP%\CANapeBundleInstallPersistors.log","17.0.00102"
:: Checked -> yes

:Install_ShellExt_32bit
call :NameSearch "Vector ShellExtensions 32-bit","""CANape\ISSetupPrerequisites\Vector Shell Extensions\Vector ShellExtensions 32-bit.msi"" /qn REBOOT=ReallySuppress ADDLOCAL=ALL /l*v %TEMP%\VectorShellExtension32Install.log","5.0.13260"
:: Checked -> yes

REM :Install_VS2008_x64 :: Deprecated
REM ECHO "TODO: Add installation VS2008 x64 check"
REM ECHO "Installing Microsoft Visual C++ 2008 SP1 Redistributable Package (x64)"
REM "CANape\ISSetupPrerequisites\{8D61397C-2AD6-4210-8E43-C2793010DC35}\vcredist_x64.exe" /q

:Install_ASAPViewer
call :NameSearch "Vector ASAP2 Studio Viewer","""CANape\SSetupPrerequisites\Vector ASAP2 Studio\Vector ASAP2 Studio Service 2.2.msi"" /qn /l*v %TEMP%\ASAP2StudioViewBundle.log","2.2.52.10934"
:: Checked -> yes

:Install_VS2010_x86
REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" | FINDSTR /I /C:"{F0C3E5D1-1ADE-321E-8167-68EF0DE699A5}" > nul
IF %ERRORLEVEL% EQU 0 GOTO Install_CSMConfig
call :Download_CANape
ECHO "Installing Microsoft Visual C++ 2010 SP1 Redistributable Package (x86)"
"CANape\ISSetupPrerequisites\VC 2013 SP1 Redist\vcredist_x86.exe" /q
:: Checked -> yes

:Install_CSMConfig
REG QUERY "HKEY_LOCAL_MACHINE\SOFTWARE\CSM GmbH\xx-Scan\x.y.z"
IF %ERRORLEVEL% EQU 0 GOTO Install_LicenseClient
call :Download_CANape
ECHO "Installing CSMconfig"
"CANape\ISSetupPrerequisites\xx-Scan\CSMconfig.exe" /VERYSILENT /TASKS="startmode0" /NORESTART /LOG=%TEMP%\CSMconfig.log
:: Checked -> yes

:Install_LicenseClient
call :NameSearch "Vector License Client","""CANape\ISSetupPrerequisites\Vector License Client\VectorLicenseClientInstaller.msi"" /qn /l*v %TEMP%\VectorLicenseClientInstaller.log","6.1.0"
:: Checked -> yes

REM :Install_LicenseManager
REM call :NameSearch "Vector License Manager","""CANape\ISSetupPrerequisites\Vector License Manager\VectorLicenseManagerInstaller.msi"" /quiet /l*v %TEMP%\CANapeBundleInstallLicenseManager.log","1.4.1100.0"

:Install_vMDM
call :NameSearch "Vector vMDM","""CANape\ISSetupPrerequisites\Vector vMDM\Vector vMDM.msi"" /qn REBOOT=ReallySuppress ADDLOCAL=ALL ISVMDMLOCAL=[VMDMLOCAL] /l*v %TEMP%\VectorvMDM.log","3.5.55.0"
:: Checked -> yes

REM :Install_VS2008_x86 :: Deprecated
REM ECHO "TODO: Add installation check"
REM ECHO "Installing Microsoft Visual C++ 2008 SP1 Redistributable Package (x86)"
REM "CANape\ISSetupPrerequisites\{0BE9572E-8558-404f-B0A5-8C347D145655}\vcredist_x86.exe" /q

:Install_CodeMeter
set last="0.0"
REG QUERY "HKEY_LOCAL_MACHINE\SOFTWARE\WIBU-SYSTEMS\CodeMeter" > nul
REM MIN REQUIRED 7.21
IF %errorlevel% equ 1 GOTO Start_Install_CodeMeter
FOR /F "tokens=2* skip=2" %%a in ('REG QUERY "HKEY_LOCAL_MACHINE\SOFTWARE\WIBU-SYSTEMS\CodeMeter" /v RuntimeVersion') do set last=%%b
call :VerCompare "%last%","7.21",result
IF %result% EQU 1 GOTO Install_NETFramework48
:: Checked -> yes

:Start_Install_CodeMeter
call :Download_CANape
ECHO "Installing CodeMeter Runtime 7.21b"
"CANape\ISSetupPrerequisites\Vector Driver\x64\CodeMeterRuntime.exe" /componentargs "*":"/qn ADDLOCAL=Complete,DotNET_Modules,AutomaticServerSearch REMOVE=WibuShellExtension,EnableNetworkServer,AccessToWebAdmin /l*v "C:\windows\temp\keyinst.log" /norestart PROP_CMCC=""none"""
:: Checked -> yes

:Install_NETFramework48
REG QUERY "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\.NETFramework\v4.0.30319\SKUs\.NETFramework" > nul
IF %ERRORLEVEL% EQU 1 GOTO Start_Install_NET_Framework48
FOR /F "tokens=2* skip=2" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\.NETFramework\v4.0.30319\SKUs\.NETFramework" /v Version') do set VreleaseNETp=%%b
REM ECHO %VreleaseNETp%
call :VerCompare "%VreleaseNETp%","4.8",result
IF %result% EQU 1 GOTO Install_VS2010_x64

:Start_Install_NET_Framework48
call :Download_CANape
ECHO "Installing Microsoft .NET Framework 4.8 Full"
"CANape\ISSetupPrerequisites\{06D565DC-042E-4F1B-8702-2E0BD0F22805}\ndp48-x86-x64-allos-enu.exe" -q -norestart
rem environ 3 apres crash - why?
:: Checked -> yes

:Install_VS2010_x64
REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" | FINDSTR /I /C:"{1D8E6291-B0D5-35EC-8441-6616F567A0F7}" > nul
IF %ERRORLEVEL% EQU 0 GOTO Install_FunctionLibrary
call :Download_CANape
ECHO "Installing Microsoft Visual C++ 2010 SP1 Redistributable Package (x64)"
"CANape\ISSetupPrerequisites\VC 2013 SP1 Redist\vcredist_x86.exe" /q
:: Checked -> yes

:Install_FunctionLibrary
call :NameSearch "Vector Function Library","""CANape\ISSetupPrerequisites\Vector Global Function Packages Library\Vector Global Function Package Library 1.0.msi"" /qn /l*v %TEMP%\CANapeBundleInstallGlobalFunctionLib.log","1.0.20.00"
:: Checked -> yes

:Install_VS2013_x64
REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" | FINDSTR /I /C:"{5740BD44-B58D-321A-AFC0-6D3D4556DD6C}" > nul
IF %ERRORLEVEL% EQU 0 GOTO Install_FIBEX
call :Download_CANape
ECHO "Installing Microsoft Visual C++ 2013 Update Redistributable Package (x64)"
"CANape\ISSetupPrerequisites\VC 2013 SP1 Redist\vcredist_x64.exe" /q
:: Checked -> yes

:Install_FIBEX
call :NameSearch "Vector FIBEX Explorer","""CANape\ISSetupPrerequisites\Vector FIBEX Explorer\FIBEXExplorer.msi"" /qn /l*v %TEMP%\PMCBundleInstallFIBEXExplorer.log ARPCOMMENTS=""Bundled with Vector Product like CANape, CANdito, vSignalyzer. DO NOT REMOVE if you are using one them""","3.2.26"
:: Checked -> yes

:Install_vFlash
call :NameSearch "Vector vFlash","""CANape\ISSetupPrerequisites\Vector vFlash\vFlash.msi"" /qn /l*v %TEMP%\CANapeBundleInstallvFlash.log VECTOR_HARDWARE_INSTALLED=1 VFLASH_EXITDIALOGSTARTVFLASHNOW=0 VFLASH_EXITDIALOGOPENRELEASENOTES=0 VFLASH_USERNAME=""CANape Tool"" VFLASH_COMPANYNAME=""Vector""","3.5"
:: Checked -> yes

:Install_ShellExt_64bit
call :NameSearch "Vector ShellExtensions 64-bit","""CANape\ISSetupPrerequisites\Vector Shell Extensions\Vector ShellExtensions 64-bit.msi"" /qn REBOOT=ReallySuppress ADDLOCAL=ALL /l*v %TEMP%\VectorShellExtension64Install.log","5.0.13206"
:: Checked -> yes

:Install_AUTOSAR2
call :NameSearch "Vector AUTOSAR Explorer 2","""CANape\ISSetupPrerequisites\Vector AUTOSAR Explorer\AUTOSARExplorer2.msi"" /qn /l*v %TEMP%\\PMCBundleInstallAUTOSARExplorer.log ARPCOMMENTS=""Bundled with Vector Product like CANape, CANdito, vSignalyzer. DO NOT REMOVE if you are using one them""","2.3.13"
:: Checked -> yes

:: CANape Installation ::

:Install_CANape
call :NameSearch "Vector CANape 19","start /w CANape\Setup.exe /s /v""VPROGRAM_LANGUAGE=01 /qn""","19.0.50.1172"
:: Before finishing, if the installation was OK, the folder will be completely removed.
IF %ERRORLEVEL% EQU 0 ( IF EXIST .\CANape ( 
		RD /S /Q ".\CANape") )
EXIT /B %ERRORLEVEL% 

:: Check if the Version is already installed.
:Precheck
call :NameSearch "Vector CANape 19","GOTO :Install_VS2015_x64","19.0.50.1172"
GOTO :END

:: End of script. Check error level and print output log
:END
IF %ERRORLEVEL% EQU 0 (ECHO CANape : OK>> output.log) ELSE (ECHO CANape : NOT OK>> output.log)
EXIT /B 0