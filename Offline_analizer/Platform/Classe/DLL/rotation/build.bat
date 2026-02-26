
@echo off
if exist build\ (
    echo Removing build folder
    rmdir build /s /q
)

if exist Release64\ (
    echo Removing release64 folder
    rmdir Release64 /q /s
)

mkdir build
cd build

@REM cmake .. -G "Visual Studio 15 2017" -A x64
cmake .. -G "Visual Studio 16 2019" -A x64
cmake --build . --config Release

cd ..