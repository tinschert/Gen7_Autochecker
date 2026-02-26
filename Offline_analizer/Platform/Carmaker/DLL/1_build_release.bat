@echo off
conan install . --build=missing --settings=build_type=Release -s compiler.cppstd=20
cmake -S . -B build -G "Visual Studio 17 2022" -A x64 -DCMAKE_TOOLCHAIN_FILE="build/generators/conan_toolchain.cmake"
cmake --build ./build --parallel --config "Release"
pause