@echo off

REM Install Conan packages
conan profile detect --force
conan install conanfile.txt --output-folder=statistical_reflection_model --build=missing

REM Call conan build
call statistical_reflection_model\build\generators\conanbuild.bat

REM build the dll
call build_road_obj.bat

REM Run the UnitTest
cd build\Release
UnitTests.exe

REM Plot the results of the UnitTest
cd ..\..\Tests
python loc_plot.py
cd ..\