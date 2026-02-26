add_subdirectory(ccl_lib)
add_subdirectory(mingw_symbols)

# ------------------------------------------------------------------------------------------------------------
# CCL Testing Library
# ------------------------------------------------------------------------------------------------------------

add_library(CCLInterface SHARED
    MainCCL.cpp
)

target_include_directories(CCLInterface PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(CCLInterface
    CCLApps
    CCL
)

add_custom_command(TARGET CCLInterface POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:CCLInterface> ${CMAKE_SOURCE_DIR}/../
    COMMENT "Copying CCLInterface executable to the root directory"
)