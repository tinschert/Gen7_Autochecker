cmake_minimum_required(VERSION 3.15)
project(CarMaker_APO CXX C)

# Setup DLL
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(LIBRARY_DIR ${CMAKE_CURRENT_SOURCE_DIR}/lib)

include_directories(
    ${PROJECT_SOURCE_DIR}
)

add_subdirectory(${CMAKE_SOURCE_DIR}/../UdpPacket ${CMAKE_SOURCE_DIR}/build/common)

add_executable(UdpTestApp
    UdpClient.cpp
)

target_link_libraries(UdpTestApp PUBLIC UdpPacket)

target_include_directories(UdpTestApp PUBLIC
    ${CMAKE_SOURCE_DIR}/../
)

add_custom_command(TARGET UdpTestApp POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:UdpTestApp> ${CMAKE_SOURCE_DIR}
    COMMENT "Copying CCLInterface executable to the root directory"
)