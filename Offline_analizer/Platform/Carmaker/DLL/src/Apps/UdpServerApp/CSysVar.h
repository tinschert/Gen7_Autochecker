#pragma once

#include <CSysVar.h>

#include <CCL.h>

#include <cassert>
#include <cstdint>
#include <string>

/// @brief The CANoe System Variable Type as C++ Enum Class
enum class tSysVarType : int32_t
{
    INTEGER = CCL_SYSVAR_INTEGER,
    FLOAT = CCL_SYSVAR_FLOAT,
    STRING = CCL_SYSVAR_STRING,
    INTEGERARRAY = CCL_SYSVAR_INTEGERARRAY,
    FLOATARRAY = CCL_SYSVAR_FLOATARRAY,
    DATA = CCL_SYSVAR_DATA,
    STRUCT = CCL_SYSVAR_STRUCT,
    GENERICARRAY = CCL_SYSVAR_GENERICARRAY
};


/// @brief Implementation of CANoe SysVar interface
/// @tparam T The type of the SysVar [int32_t, uint32_t, float, string]
/// @note This class only supports SysVar compatible types. It will throw an assertion if the type is not \
///       not supported in CANoe. The expected types are defined through specializations in CSysVar.tpp
template <typename T>
class tCSysVar
{
public:

    /// @brief Default Constructor is deleted
    tCSysVar() = delete;

    /// @brief Construct a tCSysVar from a CANoe SysVar name
    /// @param name The CANoe SysVar Name
    tCSysVar(std::string name);

    /// @brief Get the current value of the CANoe SysVar
    /// @return The value of the SysVar
    T getValue() const;

    /// @brief Set the value of the CANe SysVar
    /// @param value The value to set the SysVar to
    void setValue(T value) const;

private:

    /// @brief The name of the SysVar in CANoe
    std::string m_name {""};

    /// @brief The ID of the System Variable the object refers to
    int32_t m_ID {-1};

    /// @brief The CANoe Type Enum of the System Variable the object refers to
    tSysVarType m_type {-1};

};