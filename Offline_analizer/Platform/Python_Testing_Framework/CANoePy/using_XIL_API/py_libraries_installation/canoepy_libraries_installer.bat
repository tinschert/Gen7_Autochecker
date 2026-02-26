echo "Installing libraries"
X:\Tools\venv\Scripts\python.exe -m X:\Tools\venv\Scripts\pip.exe install --upgrade pip
X:\Tools\venv\Scripts\pip.exe install --no-index --find-links \\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\Python\Libraries\Libs_3.12\CANoePy_Libs -r canoepy_python_libraries_requirements_file.txt
IF %ERRORLEVEL% EQU 0 (ECHO Python lib : OK>> output.log) ELSE (ECHO Python lib : NOT OK>> output.log)