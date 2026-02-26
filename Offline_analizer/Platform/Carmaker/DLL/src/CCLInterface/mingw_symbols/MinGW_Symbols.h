//============================================================================================================
// C O P Y R I G H T
//============================================================================================================
/// @file       MinGW_Symbols.h
/// @brief      Declaration of methods for to define missing MinGW symbols in an MSVC enviornment
/// @details    Includes declaration of all missing MinGW symbols when linking the libAPO library file to the
///             application. The libAPO file is compiled using MinGW so these methods are required to resolve
///             the symbol names declared by MinGW for the below methods.
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

#ifdef _MSC_VER // Only include this code when compiling with MSVC

#include <cstdio>
#include <cstdarg>

extern "C" int __mingw_vfprintf(FILE *stream, const char *format, va_list argptr);

extern "C" int __mingw_vsscanf(const char* buffer, const char *format, va_list argptr);

extern "C" int __mingw_vsprintf(char* buffer, const char *format, va_list argptr);

extern "C" int __mingw_vsnprintf(char* buffer, size_t buffer_count, const char *format, va_list argptr);

extern "C" void __cdecl ___chkstk_ms();

#endif // _MSC_VERc