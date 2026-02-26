#pragma once

#include <CSysVar.h>
#include <RBSData.h>

#include <stdexcept>

/// @brief Checks if the passed ID matches any of the CCL errors and throws a matching exception
/// @param id The value to match to errors
/// @param context A string to inform the user of what context the error occurred in
/// @param name The name of the signal that caused this error
void processSysVarError(int32_t id, std::string context, std::string name)
{
    switch (id)
    {
    case CCL_SUCCESS:
        return;
    case CCL_WRONGSTATE:
        cclPrintf("Error: CCL_WRONGSTATE for signal \"%s\" in context %s", name.c_str(), context.c_str());
        throw std::runtime_error("CCL_WRONGSTATE");
    case CCL_INVALIDNAME:
        cclPrintf("Error: CCL_INVALIDNAME for signal \"%s\" in context %s", name.c_str(), context.c_str());
        throw std::runtime_error("CCL_INVALIDNAME");
    case CCL_SYSVARNOTDEFINED:
        cclPrintf("Error: CCL_SYSVARNOTDEFINED for signal \"%s\" in context %s", name.c_str(), context.c_str());
        throw std::runtime_error("CCL_SYSVARNOTDEFINED");
    case CCL_INTERNALERROR:
        cclPrintf("Error: CCL_INTERNALERROR for signal \"%s\" in context %s", name.c_str(), context.c_str());
        throw std::runtime_error("CCL_INTERNALERROR");
    default:
        cclPrintf("Error: unknown error for signal \"%s\" in context %s", name.c_str(), context.c_str());
        throw std::runtime_error("CANoe unimplemented/unknown error type");
    }
}

/// @brief A static method to return the CANoe SysVar ID from the SysVar Name
/// @param name The name of the CANoe SysVar
/// @return The CANoe SysVar ID for name
int32_t readSysVarID(std::string name)
{
    int32_t id = cclSysVarGetID(name.c_str());
    if (id < 0)
    {
        processSysVarError(id, "readSysVarID", name);
    }

    return id;
}

/// @brief A static method to return the CANoe SysVar Type from the SysVar Name
/// @param name The name of the CANoe SysVar
/// @return The CANoe SysVar Type for name
tSysVarType readSysVarType(std::string name)
{
    int32_t id = cclSysVarGetType(cclSysVarGetID(name.c_str()));
    if (id < 0)
    {
        processSysVarError(id, "readSysVarID", name);
    }

    switch (id)
    {
    case CCL_SYSVAR_INTEGER:
        return tSysVarType::INTEGER;
    case CCL_SYSVAR_FLOAT:
        return tSysVarType::FLOAT;
    case CCL_SYSVAR_STRING:
        return tSysVarType::STRING;
    case CCL_SYSVAR_STRUCT:
        return tSysVarType::STRUCT;
    default:
        cclPrintf("Error: UdpServer does not support SysVar Type of \"%s\" type %d", name.c_str(), id);
        throw std::runtime_error("UdpServer does not support current SysVar type");
    }
}

template <typename T>
tCSysVar<T>::tCSysVar(std::string name) : m_name(name)
{
    constexpr bool isTypeValid = std::disjunction<
        std::is_same<T, int32_t>,
        std::is_same<T, uint32_t>,
        std::is_same<T, int64_t>,
        std::is_same<T, uint64_t>,
        std::is_same<T, float>,
        std::is_same<T, std::string>,
        std::is_same<T, RBSData::ObjectData>,
        std::is_same<T, RBSData::RadarData>
    >::value;

    static_assert(isTypeValid, "Unsupported tCSysVar type");

    m_ID = readSysVarID(name);
    m_type = readSysVarType(name);
}

/// @brief Gets the int32_t value of a SysVar
/// @return A int32_t value
int32_t tCSysVar<int32_t>::getValue() const
{
    assert(m_ID < 0);
    int32_t value {0};
    const int32_t retval = cclSysVarGetInteger(m_ID, &value);
    processSysVarError(retval, "getValue", m_name);
    return value;
}

/// @brief Sets the int32_t value of a SysVar
/// @param The int32_t value to set
void tCSysVar<int32_t>::setValue(int32_t value) const
{
    assert(m_ID < 0);
    const int32_t retval = cclSysVarSetInteger(m_ID, value);
    processSysVarError(retval, "setValue", m_name);
}

/// @brief Gets the uint32_t value of a SysVar
/// @return A uint32_t value
uint32_t tCSysVar<uint32_t>::getValue() const
{
    assert(m_ID < 0);
    int32_t value {0};
    const int32_t retval = cclSysVarGetInteger(m_ID, &value);
    processSysVarError(retval, "getValue", m_name);
    return static_cast<uint32_t>(value);
}

/// @brief Sets the uint32_t value of a SysVar
/// @param The uint32_t value to set
void tCSysVar<uint32_t>::setValue(uint32_t value) const
{
    assert(m_ID < 0);
    const int32_t retval = cclSysVarSetInteger(m_ID, value);
    processSysVarError(retval, "setValue", m_name);
}

/// @brief Gets the int64_t value of a SysVar
/// @return A int64_t value
int64_t tCSysVar<int64_t>::getValue() const
{
    assert(m_ID < 0);
    int64_t value {0};
    const int32_t retval = cclSysVarGetInteger64(m_ID, &value);
    processSysVarError(retval, "getValue", m_name);
    return static_cast<uint32_t>(value);
}

/// @brief Sets the int64_t value of a SysVar
/// @param The int64_t value to set
void tCSysVar<int64_t>::setValue(int64_t value) const
{
    assert(m_ID < 0);
    const int32_t retval = cclSysVarSetInteger64(m_ID, value);
    processSysVarError(retval, "setValue", m_name);
}

/// @brief Gets the int64_t value of a SysVar
/// @return A int64_t value
uint64_t tCSysVar<uint64_t>::getValue() const
{
    assert(m_ID < 0);
    int64_t value {0};
    const int32_t retval = cclSysVarGetInteger64(m_ID, &value);
    processSysVarError(retval, "getValue", m_name);
    return static_cast<uint64_t>(value);
}

/// @brief Sets the int64_t value of a SysVar
/// @param The int64_t value to set
void tCSysVar<uint64_t>::setValue(uint64_t value) const
{
    assert(m_ID < 0);
    const int32_t retval = cclSysVarSetInteger64(m_ID, value);
    processSysVarError(retval, "setValue", m_name);
}

/// @brief Gets the float value of a SysVar
/// @return A float value
double tCSysVar<double>::getValue() const
{
    assert(m_ID < 0);
    double value {0};
    const int32_t retval = cclSysVarGetFloat(m_ID, &value);
    processSysVarError(retval, "getValue", m_name);
    return value;
}

/// @brief Sets the float value of a SysVar
/// @param The float value to set
void tCSysVar<double>::setValue(double value) const
{
    assert(m_ID < 0);
    const int32_t retval = cclSysVarSetFloat(m_ID, value);
    processSysVarError(retval, "setValue", m_name);
}

/// @brief Gets the string value of a SysVar
/// @return A string value
std::string tCSysVar<std::string>::getValue() const
{
    assert(m_ID < 0);
    char tempString[256] = {0};
    const int32_t retval = cclSysVarGetString(m_ID, tempString, sizeof(tempString));
    processSysVarError(retval, "getValue", m_name);
    return std::string(tempString);
}

/// @brief Sets the string value of a SysVar
/// @param The string value to set
void tCSysVar<std::string>::setValue(std::string value) const
{
    assert(m_ID < 0);
    const int32_t retval = cclSysVarSetString(m_ID, value.c_str());
    processSysVarError(retval, "setValue", m_name);
}

/// @brief Gets the string value of a SysVar
/// @return A string value
RBSData::ObjectData tCSysVar<RBSData::ObjectData>::getValue() const
{
    assert(m_ID < 0);
    uint8_t buffer[sizeof(RBSData::ObjectData)] = {0};
    const int32_t retval = cclSysVarGetData(m_ID, buffer, sizeof(RBSData::ObjectData));

    processSysVarError(retval, "getValue", m_name);
    return *reinterpret_cast<RBSData::ObjectData*>(buffer);
}

/// @brief Sets the string value of a SysVar
/// @param The string value to set
void tCSysVar<RBSData::ObjectData>::setValue(RBSData::ObjectData value) const
{
    assert(m_ID < 0);
    const uint8_t* pointer = reinterpret_cast<uint8_t*>(&value);
    const int32_t retval = cclSysVarSetData(m_ID, pointer, sizeof(RBSData::ObjectData));
    processSysVarError(retval, "setValue", m_name);
}

/// @brief Gets the string value of a SysVar
/// @return A string value
RBSData::RadarData tCSysVar<RBSData::RadarData>::getValue() const
{
    assert(m_ID < 0);
    uint8_t buffer[sizeof(RBSData::RadarData)] = {0};
    const int32_t retval = cclSysVarGetData(m_ID, buffer, sizeof(RBSData::RadarData));

    processSysVarError(retval, "getValue", m_name);
    return *reinterpret_cast<RBSData::RadarData*>(buffer);
}

/// @brief Sets the string value of a SysVar
/// @param The string value to set
void tCSysVar<RBSData::RadarData>::setValue(RBSData::RadarData value) const
{
    assert(m_ID < 0);
    const uint8_t* pointer = reinterpret_cast<uint8_t*>(&value);
    const int32_t retval = cclSysVarSetData(m_ID, pointer, sizeof(RBSData::RadarData));
    processSysVarError(retval, "setValue", m_name);
}

/// ----------------------------------------------------------------------------------------------------------
/// Explicit Initializations of Template Methods
/// ----------------------------------------------------------------------------------------------------------

// Constructors
template class tCSysVar<int32_t>;
template class tCSysVar<uint32_t>;
template class tCSysVar<int64_t>;
template class tCSysVar<uint64_t>;
template class tCSysVar<float>;
template class tCSysVar<std::string>;
template class tCSysVar<RBSData::ObjectData>;
template class tCSysVar<RBSData::RadarData>;

// Getters
template int32_t tCSysVar<int32_t>::getValue() const;
template uint32_t tCSysVar<uint32_t>::getValue() const;
template int64_t tCSysVar<int64_t>::getValue() const;
template uint64_t tCSysVar<uint64_t>::getValue() const;
template float tCSysVar<float>::getValue() const;
template std::string tCSysVar<std::string>::getValue() const;
template RBSData::ObjectData tCSysVar<RBSData::ObjectData>::getValue() const;
template RBSData::RadarData tCSysVar<RBSData::RadarData>::getValue() const;

// Setters
template void tCSysVar<int32_t>::setValue(int32_t value) const;
template void tCSysVar<uint32_t>::setValue(uint32_t value) const;
template void tCSysVar<int64_t>::setValue(int64_t value) const;
template void tCSysVar<uint64_t>::setValue(uint64_t value) const;
template void tCSysVar<float>::setValue(float value) const;
template void tCSysVar<std::string>::setValue(std::string value) const;
template void tCSysVar<RBSData::ObjectData>::setValue(RBSData::ObjectData value) const;
template void tCSysVar<RBSData::RadarData>::setValue(RBSData::RadarData value) const;