#include "UdpPacketHeader.h"
#include <chrono>

tUdpPacketHeader::tUdpPacketHeader()
{
}

/// @brief Deserialize the input data into the section
/// @param data The data to deserialize
void tUdpPacketHeader::deserialize(const std::vector<char> data)
{
    const tUdpPacketHeader *rawDataPacket = reinterpret_cast<const tUdpPacketHeader *>(data.data());
    m_counter = rawDataPacket->m_counter;
    m_dataLength = rawDataPacket->m_dataLength;
    m_magicNumber = rawDataPacket->m_magicNumber;
    m_timestamp = rawDataPacket->m_timestamp;
}

/// @brief Serialize the class into a vector of bytes
/// @return A std::vector of char bytes
std::vector<char> tUdpPacketHeader::serialize() const
{
    std::vector<char> headerData(sizeof(tUdpPacketHeader));
    std::memcpy(headerData.data(), this, sizeof(tUdpPacketHeader));
    return headerData;
}

/// @brief Updates the header based on the given data
/// @param data The data to calculate the CRC32 with
void tUdpPacketHeader::update(const uint32_t dataLength)
{
    auto now = std::chrono::system_clock::now();
    uint64_t millis = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();

    m_counter++;
    m_dataLength = dataLength;
    m_timestamp = static_cast<uint64_t>(millis);
}