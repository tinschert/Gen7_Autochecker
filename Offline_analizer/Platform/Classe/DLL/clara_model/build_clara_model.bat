
@echo off
if exist build\ (
    echo Removing build folder
    rmdir build /s /q
)

if exist Debug64\ (
    echo Removing Debug64 folder
    rmdir /s /q Debug64
)

if exist Debug\ (
    echo Removing Debug folder
    rmdir /s /q Debug
)

if exist Release64\ (
    echo Removing release64 folder
    rmdir Release64 /q /s
)

if exist Release\ (
    echo Removing release folder
    rmdir Release /q /s
)

mkdir build
cd build

@REM cmake .. -G "Visual Studio 15 2017" -A Win32
cmake .. -G "Visual Studio 16 2019" -A x64
cmake --build . --config Release

cd ..