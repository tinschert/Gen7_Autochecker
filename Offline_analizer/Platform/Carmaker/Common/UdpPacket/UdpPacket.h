#pragma once

#include <UdpPacketCRC.h>
#include <UdpPacketData.h>
#include <UdpPacketHeader.h>

#include <vector>

/// @brief Definition of a UDP Packet as expected by the UdpServerApp
/// @tparam T The data type of the data to transmit in the packet
template <typename T> 
class tUdpPacket
{
public:

    tUdpPacket();

    /// @brief Construct a packet from a raw packet
    /// @param rawPacket The raw packet to construct from
    tUdpPacket(const std::vector<char> rawPacket);

    /// @brief Getter Method for the packet data section
    /// @return A reference to the data section of the packet
    tUdpPacketData<T>& getDataSection() { return m_dataSection; }

    /// @brief Construct a Raw Packet from the current tUdpPacket
    /// @return A Raw Packet based on the current tUdpPacket data sections
    std::vector<char> constructRawPacket();
    
    /// @brief Construct a new Raw Packet based on the input data
    /// @param data The data to use in the new packet
    /// @return An updated Raw Packet based on the new data with updated data sections
    std::vector<char> constructRawPacket(const T& data);

    /// @brief Update the packet from the packet datatype
    /// @param data The data to use for the update
    void update(const T& data);

    /// @brief Update the Packet from a raw packet input
    /// @param rawPacket A vector containing the raw packet bytes
    void updateFromRawPacket(const std::vector<char>& rawPacket);

    /// @brief The UDP Packet Header Section
    tUdpPacketHeader m_headerSection; 

    /// @brief The UDP Packet Data Section
    tUdpPacketData<T> m_dataSection;

    /// @brief The UDP Packet CRC Section
    tUdpPacketCRC m_crcSection;

};

#include <UdpPacket.tpp>