#pragma once

#include <cstdint>
#include <vector>

/// @brief The header of the UDP packet
class tUdpPacketHeader
{
public:

    tUdpPacketHeader();

    /// @brief Updates the header based on the given data
    /// @param data The data to calculate the CRC32 with
    void update(const uint32_t dataLength);

    /// @brief Serialize the class into a vector of bytes
    /// @return A std::vector of char bytes
    std::vector<char> serialize() const;

    /// @brief Deserialize the input data into the section
    /// @param data The data to deserialize
    void deserialize(const std::vector<char> data);

    /// @brief The magic number of the packet
    uint32_t m_magicNumber {0x55555555U};

    /// @brief The counter variable for the packet
    /// @note This is incremented every time the packet is compiled to send
    uint32_t m_counter {0U};

    /// @brief The length of the data section of the packet
    uint32_t m_dataLength {0U};

    /// @brief A UNIX Timestamp of when the packet was sent
    uint64_t m_timestamp {0U};

};