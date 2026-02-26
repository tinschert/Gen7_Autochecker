#pragma once

#include <array>
#include <cstdint>
#include <vector>

/// @brief The CRC section of the UDP packet
class tUdpPacketCRC
{
public:

    tUdpPacketCRC();

    /// @brief Deserialize the input data into the section
    /// @param data The data to deserialize
    void deserialize(const std::vector<char> data);

    /// @brief Serialize the class into a vector of bytes
    /// @return A std::vector of char bytes
    std::vector<char> serialize();

    /// @brief Updates the CRC32 for the packet based on the given data
    /// @param data The data to calculate the CRC32 with
    void update(const std::vector<char>& data);
    
    /// @brief Validates the existing CRC32 against the given data vector
    /// @param data The data to compare the CRC32 with
    /// @return true for matching CRC32 false for mismatch indicating corrupted or invalid data
    bool compare(const std::vector<char>& data) const;

    /// @brief The CRC32 value of the packet
    uint32_t m_crc32 {0U};

protected:

    /// @brief Generate a CRC32 number for a given data vector
    /// @param data A data vector reference to calculate the CRC32 of
    /// @return The calculated CRC32 of input data
    uint32_t generateCRC(const std::vector<char>& data) const;

};
