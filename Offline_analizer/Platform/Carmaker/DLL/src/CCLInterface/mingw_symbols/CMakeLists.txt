# ------------------------------------------------------------------------------------------------------------
# MinGW Compatability Symbol Library
# ------------------------------------------------------------------------------------------------------------

add_library(MinGW_Symbols STATIC
    MinGW_Symbols.cpp
)

target_include_directories(MinGW_Symbols PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)