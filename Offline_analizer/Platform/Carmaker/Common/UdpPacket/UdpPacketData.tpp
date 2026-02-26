#pragma once

#include "UdpPacketData.h"

template <typename T>
tUdpPacketData<T>::tUdpPacketData()
{

}


/// @brief Override of the assignment operator for template type assignment
/// @param data The T to assign to m_data
template <typename T>
void tUdpPacketData<T>::operator=(const T &data)
{
    // TODO: Implement
}


/// @brief Deserialize the input data into the section
/// @param data The data to deserialize
template <typename T>
void tUdpPacketData<T>::deserialize(const std::vector<char> data)
{
    const tUdpPacketData *rawDataPacket = reinterpret_cast<const tUdpPacketData *>(data.data());
    m_data = rawDataPacket->m_data;
}

/// @brief Serialize the class into a vector of bytes
/// @param data The T to assign to m_data
/// @return A std::vector of char bytes
template <typename T>
std::vector<char> tUdpPacketData<T>::serialize() const
{
    std::vector<char> data(sizeof(tUdpPacketData));
    std::memcpy(data.data(), this, sizeof(tUdpPacketData));
    return data;
}
