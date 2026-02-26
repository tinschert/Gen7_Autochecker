@echo off
setlocal enableextensions

set "tool=SW_Versions_Extractor"
echo Generating EXE file, please wait...
goto :generate_exe 

:delete_temp_files
if exist %~dp0\build (rd /S /Q %~dp0\build)
if exist %~dp0\*.spec (del %~dp0\*.spec /F /Q)
exit /b 

:generate_exe
X:\Tools\venv\Scripts\python.exe -m PyInstaller --onefile -n %tool% --distpath .\%tool% --clean sw_ex_gui.py
if %errorlevel% neq 0 (echo Generation failed, please verify all Python libraries are available in the PC!
		call :delete_files
		timeout /T 15 /nobreak
		exit /b) else (
		call :delete_temp_files
		call :copy_files
		exit /b)

:copy_files
if exist ..\..\..\..\Release\*.yml (robocopy ..\..\..\..\Release .\%tool% *.yml /W:1 /IS /NP /NFL /NDL) else (echo No YAML found)
if exist D:\CarMaker_Shared (robocopy .\%tool% D:\CarMaker_Shared\%tool%\ /W:1 /IS /NP /NFL /NDL) else (echo Network drive X:\ not found, please copy manually the folder %tool% to the destination PC!)
if exist Y:\ (robocopy .\%tool% Y:\%tool%\ /W:1 /IS /NP /NFL /NDL) else (echo Network drive Y:\ not found, please copy manually the folder %tool% to the destination PC!)
echo EXE file generated successfully...
echo Find it in %~dp0%tool%\
timeout /T 10 /nobreak