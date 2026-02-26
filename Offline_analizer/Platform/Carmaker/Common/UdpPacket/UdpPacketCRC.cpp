#include <UdpPacketCRC.h>

/// @brief The CRC32 polynomial used for calculation
static constexpr uint32_t g_polynomialCRC = 0xEDB88320;

/// @brief Calculate the CRC32 for a specific byte
/// @param byte The byte to calculate CRC for
/// @return a uint32_t containing the CRC32 value
constexpr uint32_t calculateCRC32ForByte(uint8_t byte)
{
    uint32_t crc = byte;
    for (uint8_t i = 0; i < 8; i++)
    {
        if (crc & 1)
        {
            crc = (crc >> 1) ^ g_polynomialCRC;
        }
        else
        {
            crc = crc >> 1;
        }
    }
    return crc;
}

/// @brief Generate a CRC table for the CRC32 calculation
/// @return An array of size 256 containing the precalculated CRC bytes for each byte
constexpr const std::array<uint32_t, 256> generateCRCTable()
{
    std::array<uint32_t, 256> table{};
    for (uint32_t i = 0; i < 256; i++)
    {
        table[i] = calculateCRC32ForByte(static_cast<uint8_t>(i));
    }
    return table;
}

tUdpPacketCRC::tUdpPacketCRC()
{
}

/// @brief Deserialize the input data into the section
/// @param data The data to deserialize
void tUdpPacketCRC::deserialize(const std::vector<char> data)
{
    const tUdpPacketCRC *rawDataPacket = reinterpret_cast<const tUdpPacketCRC *>(data.data());
    m_crc32 = rawDataPacket->m_crc32;
}

/// @brief Serialize the class into a vector of bytes
/// @return A std::vector of char bytes
std::vector<char> tUdpPacketCRC::serialize()
{
    std::vector<char> crcData(sizeof(m_crc32));
    std::memcpy(crcData.data(), &m_crc32, sizeof(m_crc32));
    return crcData;
}

/// @brief Calculates the new CRC32 for the packet
/// @param data The data to calculate the CRC32 with
void tUdpPacketCRC::update(const std::vector<char> &data)
{
    m_crc32 = generateCRC(data);
}

/// @brief Validates the existing CRC32 against the given data vector
/// @param data The data to compare the CRC32 with
/// @return true for matching CRC32 false for mismatch indicating corrupted or invalid data
bool tUdpPacketCRC::compare(const std::vector<char>& data) const
{
    const uint32_t comparisionCRC32 = generateCRC(data);
    return m_crc32 == comparisionCRC32;
}

/// @brief Generate a CRC32 number for a given data vector
/// @param data A data vector reference to calculate the CRC32 of
/// @return The calculated CRC32 of input data
uint32_t tUdpPacketCRC::generateCRC(const std::vector<char>& data) const
{
    uint32_t crc = 0xFFFFFFFF;
    static constexpr const std::array<uint32_t, 256> CRCTable{generateCRCTable()};

    for (const auto &byte : data)
    {
        crc = (crc >> 8) ^ CRCTable[(crc ^ byte) & 0xFF];
    }

    return crc;
}