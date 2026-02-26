:: ASAM XIL Standalone Installation
:: Version 2.1
:: 17.12.2024

@echo off
setlocal

rem Set the path to the .msi file
set "msiFile=\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\ASAM_XIL\Vector CANoe XIL API.msi"

rem Check if the .msi file exists
if exist "%msiFile%" (
    echo The MSI file exists. Proceeding with installation...
    
    rem Execute the msiexec command to install the MSI file silently
    msiexec /i "%msiFile%" /quiet /qn"
    
    rem Check the exit code to see if the installation was successful
    if %ERRORLEVEL%==0 (
        echo Installation completed successfully.
		echo ASAM_XIL : OK>> output.log
    ) else (
        echo Installation failed with error code %ERRORLEVEL%.
		echo Vector ASAM_XIL : NOK >> output.log
    )
) else (
    echo The MSI file does not exist. Please check the path.
)

endlocal