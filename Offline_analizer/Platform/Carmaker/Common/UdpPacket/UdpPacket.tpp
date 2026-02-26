#pragma once

#include <UdpPacket.h>

#include <cstdint>

#include <stdexcept>
#include <vector>

template <typename T>
tUdpPacket<T>::tUdpPacket()
{
}

template <typename T>
tUdpPacket<T>::tUdpPacket(const std::vector<char> rawPacket)
{
    updateFromRawPacket(rawPacket);
}

/// @brief Construct a Raw Packet from the current tUdpPacket
/// @return A Raw Packet based on the current tUdpPacket data sections
template <typename T>
std::vector<char> tUdpPacket<T>::constructRawPacket()
{
    std::vector<char> rawPacketData;

    const std::vector<char> rawHeaderSection = m_headerSection.serialize();
    const std::vector<char> rawDataSection = m_dataSection.serialize();
    const std::vector<char> rawCRCSection = m_crcSection.serialize();

    rawPacketData.reserve(rawHeaderSection.size() + rawDataSection.size() + rawCRCSection.size());
    rawPacketData.insert(rawPacketData.end(), rawHeaderSection.begin(), rawHeaderSection.end());
    rawPacketData.insert(rawPacketData.end(), rawDataSection.begin(), rawDataSection.end());
    rawPacketData.insert(rawPacketData.end(), rawCRCSection.begin(), rawCRCSection.end());

    return rawPacketData;
}

/// @brief Construct a new Raw Packet based on the input data
/// @param data The data to use in the new packet
/// @return An updated Raw Packet based on the new data with updated data sections
template <typename T>
std::vector<char> tUdpPacket<T>::constructRawPacket(const T &data)
{   
    this->update(data);
    return constructRawPacket();
}

/// @brief Update the packet from the packet datatype
/// @param data The data to use for the update
template <typename T>
void tUdpPacket<T>::update(const T& data)
{
    m_dataSection.setData(data);
    m_headerSection.update(sizeof(data));
    m_crcSection.update(m_dataSection.serialize());
}

/// @brief Update the Packet from a raw packet input
/// @param rawPacket A vector containing the raw packet bytes
template <typename T>
void tUdpPacket<T>::updateFromRawPacket(const std::vector<char> &rawPacket)
{
    const size_t headerSize = sizeof(tUdpPacketHeader);
    const size_t dataSize = sizeof(tUdpPacketData<T>);
    const size_t crcSize = sizeof(tUdpPacketCRC);

    if (rawPacket.size() < headerSize + dataSize + crcSize)
    {
        char errorMessage[256];
        sprintf(
            errorMessage, 
            "Packet size is too small to contain all sections [recv: %d, expect: %d]", 
            rawPacket.size(), 
            headerSize + dataSize + crcSize
        );
        throw std::runtime_error(errorMessage);
    }

    std::vector<char> rawHeaderSection(headerSize);
    std::vector<char> rawDataSection(dataSize);
    std::vector<char> rawCRCSection(crcSize);

    const size_t dataSectionStart = headerSize;
    const size_t crcSectionStart = dataSectionStart + dataSize;

    std::copy(rawPacket.begin(), rawPacket.begin() + dataSectionStart, rawHeaderSection.begin());
    std::copy(rawPacket.begin() + dataSectionStart, rawPacket.begin() + crcSectionStart, rawDataSection.begin());
    std::copy(rawPacket.begin() + crcSectionStart, rawPacket.end(), rawCRCSection.begin());

    m_headerSection.deserialize(rawHeaderSection);
    m_dataSection.deserialize(rawDataSection);
    m_crcSection.deserialize(rawCRCSection);
}