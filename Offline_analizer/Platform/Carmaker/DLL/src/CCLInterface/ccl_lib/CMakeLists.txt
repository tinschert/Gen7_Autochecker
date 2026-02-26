add_library(CCL STATIC
    CCL.cpp
)

target_include_directories(CCL PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(CCL

)