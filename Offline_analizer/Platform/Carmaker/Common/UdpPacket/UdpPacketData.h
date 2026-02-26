#pragma once

#include <cstdint>
#include <vector>

/// @brief The data section of the UDP packet
template <typename T>
class tUdpPacketData
{
public:

    tUdpPacketData();

    /// @brief Override of the assignment operator for template type assignment
    /// @param data The T to assign to m_data
    void operator=(const T& data);

    /// @brief Deserialize the input data into the section
    /// @param data The data to deserialize
    void deserialize(const std::vector<char> data);

    /// @brief Serialize the class into a vector of bytes
    /// @return A std::vector of char bytes
    std::vector<char> serialize() const;

    /// @brief Getter Method for size of data
    /// @return The size of the current data type stored
    size_t getDataSize() const { return sizeof(T); }

    /// @brief Getter Method for the stored data
    /// @return A reference to the data stored
    T& getData() { return m_data; }

    /// @brief Setter Method for the stored data
    /// @param data A reference to data to copy to the stored data variable
    void setData(const T& data) { m_data = data; }

    /// @brief The data to be sent in the packet
    T m_data;

};


#include <UdpPacketData.tpp>