
# Include the App files
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# Add ApoSignalApp
add_subdirectory(UdpServerApp)

# Define CCLApps library
add_library(CCLApps
    AppManager.cpp
)

target_include_directories(CCLApps PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(CCLApps
    UdpServerApp
)
