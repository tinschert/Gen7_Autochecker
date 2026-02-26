//============================================================================================================
// C O P Y R I G H T
//============================================================================================================
/// @file       MinGW_Symbols.cpp
/// @brief      Definition of methods for to define missing MinGW symbols in an MSVC enviornment
/// @details    Includes definition of all missing MinGW symbols when linking the libAPO library file to the
///             application. The libAPO file is compiled using MinGW so these methods are required to resolve
///             the symbol names defined by MinGW for the below methods.
/// @author     Lucas Ringe <Lucas.Ringe@us.bosch.com>
///
/// @copyright  Copyright (c) 2024 by Robert Bosch GmbH. All rights reserved. \n
///             The reproduction, distribution and utilization of this file as well as the communication of its \n
///             contents to others without express authorization is prohibited. Offenders will be held liable for \n
///             the payment of damages. \n
///             All rights reserved in the event of the grant of a patent, utility model or design. \n
///             @b Disclaimer: Any modification or usage outside of the intended purpose is not under authors 
///                            liability. \n
///             @b Usage: Further use of source code files or code snippets is under full liability of the user.
///
/// @attention N/A
/// @todo      N/A
//============================================================================================================

#include <MinGW_Symbols.h>
#include <iostream>

extern "C" int __mingw_vfprintf(FILE *stream, const char *format, va_list argptr) {
    // Implement a compatible version of __mingw_vfprintf for MSVC
    return vfprintf(stream, format, argptr);
}

extern "C" int __mingw_vsscanf(const char* buffer, const char *format, va_list argptr) {
    // Implement a compatible version of __mingw_vfprintf for MSVC
    return vsscanf(buffer, format, argptr);
}

extern "C" int __mingw_vsprintf(char* buffer, const char *format, va_list argptr) {
    // Implement a compatible version of __mingw_vfprintf for MSVC
    return vsprintf(buffer, format, argptr);
}

extern "C" int __mingw_vsnprintf(char* buffer, size_t buffer_count, const char *format, va_list argptr) {
    // Implement a compatible version of __mingw_vfprintf for MSVC
    return vsnprintf(buffer, buffer_count, format, argptr);
}

extern "C" void __cdecl ___chkstk_ms() {
    std::cerr << "Warning: ___chkstk_ms called (dummy implementation)" << std::endl;
    // Optionally, you can provide an implementation here to perform stack checking
    // or other necessary operations for MSVC, but it may not be necessary for compatibility.
}