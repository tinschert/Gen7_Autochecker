@echo off

REM Install Conan packages
REM conan profile detect --force
conan install conanfile.txt --output-folder=statistical_reflection_model --build=missing

REM Call conan build
call statistical_reflection_model\build\generators\conanbuild.bat

REM build the dll
cd clara_model
call build_clara_model.bat

REM Run the UnitTest
cd build\Release
UnitTests.exe

REM Plot the results of the UnitTest
cd ..\..\Sources
python loc_plot.py
cd ..\..\