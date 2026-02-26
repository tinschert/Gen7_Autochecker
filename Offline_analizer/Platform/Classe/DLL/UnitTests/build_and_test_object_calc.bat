@echo off
cd ..\
cd object_calc
call build_object_calc.bat
cd build\Release
UnitTests.exe
cd ..\..\Sources
python loc_plot.py
cd ..\..\