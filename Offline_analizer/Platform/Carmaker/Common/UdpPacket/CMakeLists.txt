include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# ApoApplication Library Target
add_library(UdpPacket
    UdpPacketCRC.cpp
    UdpPacketHeader.cpp
)

target_link_libraries(UdpPacket
    
)

target_include_directories(UdpPacket PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)