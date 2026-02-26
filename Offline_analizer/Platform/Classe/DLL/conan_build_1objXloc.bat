@echo off

REM Install Conan packages
conan profile detect --force
conan install conanfile.txt --output-folder=statistical_reflection_model --build=missing

REM Call conan build
call statistical_reflection_model\build\generators\conanbuild.bat

REM build the dll
cd object_calc
call build_object_calc.bat

REM Run the UnitTest
cd build\Release
UnitTests.exe

REM Plot the results of the UnitTest
cd ..\..\Sources
python loc_plot.py
cd ..\..\