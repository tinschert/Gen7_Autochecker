cmake_minimum_required(VERSION 3.15)
project(CarMaker_APO CXX C)

# Include Package Libraries
find_package(asio REQUIRED)

# Setup DLL
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(LIBRARY_DIR ${CMAKE_CURRENT_SOURCE_DIR}/lib)

include_directories(
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/src
)

add_subdirectory(src)