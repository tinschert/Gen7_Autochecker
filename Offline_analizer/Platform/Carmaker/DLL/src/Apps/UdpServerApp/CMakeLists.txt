add_subdirectory(${CMAKE_SOURCE_DIR}/../Common/UdpPacket ${CMAKE_SOURCE_DIR}/build/common)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# ApoApplication Library Target
add_library(UdpServerApp
    CSysVar.cpp
    ErrorReporter.cpp
    UdpServerApp.cpp
)

target_link_libraries(UdpServerApp
    asio::asio
    UdpPacket
    CCL
)

target_include_directories(UdpServerApp PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/../Common/
)