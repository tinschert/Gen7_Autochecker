#include <UdpServerApp.h>

#include <Config.h>
#include <ErrorReporter.h>
#include <UdpPacket.h>

#include <iostream>

/// @brief A external g_DebugValue to debug the threaded instance
extern int32_t g_DebugValue;

tUdpServerApp::tUdpServerApp() : m_socket(m_context)
{
}

/// @brief Called when CANoe loads the DLL
void tUdpServerApp::onLoad()
{
}

/// @brief Called right before the CANoe measurement starts
void tUdpServerApp::onMeasurementPreStart()
{
}

/// @brief Called when the CANoe measurement starts
void tUdpServerApp::onMeasurementStart()
{
    cclPrintf("Info: RBSData size = %d", sizeof(RBSData::tRBSData));
    cclPrintf("Info: RadarData size = %d", sizeof(RBSData::RadarData));
    cclPrintf("Info: ObjectData size = %d", sizeof(RBSData::ObjectData));
    initSysVarReferences();
    startUdpServer();
}

/// @brief Called when the CANoe measurement stops
void tUdpServerApp::onMeasurementStop()
{
    deinitSysVarReferences();
    stopUdpServer();
}

/// @brief Called when the CANoe unloads the DLL
void tUdpServerApp::onUnload()
{
    stopUdpServer();
}

/// @brief Called every timer update cycle [5ms]
void tUdpServerApp::onUpdate()
{
    if (!m_receivedPackets.isEmpty())
    {
        tUdpPacket<RBSData::tRBSData> packet = m_receivedPackets.dequeue();
        try
        {
            mapPacketToCANoe(packet);
        }
        catch (std::exception &e)
        {
            // Map Packet to CANoe Error
            tErrorHandlerSingleton::getInstance()
            .incrementErrorCount(tErrorHandlerSingleton::tErrorType::GENERAL_FAILURE);
        }
    }

    tErrorHandlerSingleton::getInstance().handleErrorReporting();
}

/// @brief start the applications UDP server if it is open
void tUdpServerApp::startUdpServer()
{
    if (m_socket.is_open())
    {
        m_socket.close();
    }

    cclWrite("Info: UdpServer starting...");

    try
    {
        m_socket.open(asio::ip::udp::v4());
        m_socket.bind(asio::ip::udp::endpoint(asio::ip::udp::v4(), Config::UdpServerApp::LISTENING_PORT));
    }
    catch (asio::system_error &e)
    {
        cclPrintf("Error: Failed to start UdpServer: %s", e.what());
        tErrorHandlerSingleton::getInstance()
            .incrementErrorCount(tErrorHandlerSingleton::tErrorType::CONNECTION_FAILURE);
        return;
    }

    cclPrintf("Info: UdpServer started at port %s", std::to_string(Config::UdpServerApp::LISTENING_PORT));

    // Spawn the UDP Server Thread
    m_isThreadRunning = true;
    m_serverThread = std::thread(&tUdpServerApp::threadUdpServer, this);

    cclWrite("Info: UdpServer thread spawned");
}

/// @brief stop the applications UDP server if it is open
void tUdpServerApp::stopUdpServer()
{
    // Close the UDP Server Thread
    m_isThreadRunning = false;

    // Shutdown the UDP Socket
    if (m_socket.is_open())
    {
        m_socket.cancel();
        m_socket.close();
    }

    if (m_serverThread.joinable())
    {
        m_serverThread.join();
    }
}

/// @brief Receives a UDP packet from a client
/// @return A std::vector containing the raw serialized bytes of the packet
/// @note This function will block until a packet arrives
std::vector<char> tUdpServerApp::receiveUdpPacket()
{
    std::error_code error;
    asio::ip::udp::endpoint senderEndpoint;

    const size_t bufferSize = 2 * sizeof(RBSData::tRBSData);
    std::array<char, bufferSize> recvBuffer;

    // wait for a packet to be received
    size_t len = m_socket.receive_from(asio::buffer(recvBuffer), senderEndpoint, 0, error);

    if (error && error != asio::error::message_size)
    {
        throw std::system_error(error);
    }

    // Copy the raw data packet data into a vector
    std::vector<char> packetData(len);
    std::copy(recvBuffer.begin(), recvBuffer.begin() + len, packetData.begin());

    return packetData;
}

/// @brief Initialize the tCSysVars inside of member m_sysvars
/// @note Should be called at each measurement start prior to internal UDP CANoe communication logic
void tUdpServerApp::initSysVarReferences()
{
    m_sysvars = std::move(tLocalSysVars());
}

/// @brief Deinitialize the tCSysVars inside of member m_sysvars
/// @note Should be called after/during each measurement stop
void tUdpServerApp::deinitSysVarReferences()
{
    m_sysvars = std::nullopt;
}

/// @brief Maps the data members of the packet to the CANoe variables
/// @param packet A tUdpPacket to write to CANoe SysVars
void tUdpServerApp::mapPacketToCANoe(tUdpPacket<RBSData::tRBSData> &packet)
{
    if (!m_sysvars.has_value())
    {
        tErrorHandlerSingleton::getInstance()
            .incrementErrorCount(tErrorHandlerSingleton::tErrorType::WRITE_TO_UNINITIALIZED_CSYSVAR);
        return;
    }

    tLocalSysVars& localSysVars = m_sysvars.value();

    // Set the UdpPacket specific data
    localSysVars.m_timestamp.setValue(packet.m_headerSection.m_timestamp);
    localSysVars.m_packetCounter.setValue(packet.m_headerSection.m_counter);

    // Set the radar data in CANoe from the packet
    localSysVars.m_radars[RBSData::Radar::FC]
        .setValue(packet.m_dataSection.m_data.m_radars[RBSData::Radar::FC]);

    localSysVars.m_radars[RBSData::Radar::FR]
        .setValue(packet.m_dataSection.m_data.m_radars[RBSData::Radar::FR]);

    localSysVars.m_radars[RBSData::Radar::FL]
        .setValue(packet.m_dataSection.m_data.m_radars[RBSData::Radar::FL]);

    localSysVars.m_radars[RBSData::Radar::RR]
        .setValue(packet.m_dataSection.m_data.m_radars[RBSData::Radar::RR]);

    localSysVars.m_radars[RBSData::Radar::RL]
        .setValue(packet.m_dataSection.m_data.m_radars[RBSData::Radar::RL]);
}

/// @brief Waits for an incoming packet to be received
/// @return A tUdpPacket that was received or an empty optional
/// @note Must be called in the server thread context
std::optional<tUdpPacket<RBSData::tRBSData>> tUdpServerApp::waitForIncomingPacket()
{
    try
    {
        const std::vector<char> rawPacket = receiveUdpPacket();
        return tUdpPacket<RBSData::tRBSData>(rawPacket);
    }
    catch (std::exception &e)
    {
        tErrorHandlerSingleton::getInstance()
            .incrementErrorCount(tErrorHandlerSingleton::tErrorType::UDP_RECEPTION_FAILURE);
        return std::nullopt;
    }
}

/// @brief Check if a packets data length is mismatched
/// @param packet A tUdpPacket to validate
/// @return A boolean true indicating a fault condition or false for no fault
bool tUdpServerApp::checkPacketDataLengthMismatch(const tUdpPacket<RBSData::tRBSData>& packet)
{
    if (packet.m_headerSection.m_dataLength != sizeof(RBSData::tRBSData))
    {
        tErrorHandlerSingleton::getInstance()
            .incrementErrorCount(tErrorHandlerSingleton::tErrorType::UDP_MESSAGE_SIZE_MISMATCH);
        return true;
    }
    return false;
}

/// @brief Check if a packet was received out of order
/// @param packet A tUdpPacket to validate
/// @return A boolean true indicating a fault condition or false for no fault
bool tUdpServerApp::checkPacketOutOfOrder(const tUdpPacket<RBSData::tRBSData>& packet)
{
    static uint32_t lastPacketCount {0};
    
    /// @note This will catch situations where carmaker executable restarts and reset the state of this method
    const bool isPacketFirstPacket = packet.m_headerSection.m_counter == 1;
    if (isPacketFirstPacket)
    {
        lastPacketCount = 0;
    }
    
    const uint32_t recvPacketCountDifference = packet.m_headerSection.m_counter - lastPacketCount;
    if (recvPacketCountDifference != 1U && lastPacketCount != 0)
    {
        tErrorHandlerSingleton::getInstance()
            .incrementErrorCount(tErrorHandlerSingleton::tErrorType::UDP_OUT_OF_ORDER_PACKETS);
        return true;
    }

    lastPacketCount = packet.m_headerSection.m_counter;
    return false;
}

/// @brief Check if the packets calculated CRC does not receive the transmitted one
/// @param packet A tUdpPacket to validate
/// @return A boolean true indicating a fault condition or false for no fault
bool tUdpServerApp::checkPacketCRCMismatch(const tUdpPacket<RBSData::tRBSData>& packet)
{
    if(!packet.m_crcSection.compare(packet.m_dataSection.serialize()))
    {
        tErrorHandlerSingleton::getInstance()
            .incrementErrorCount(tErrorHandlerSingleton::tErrorType::UDP_CRC_MISMATCH);
        return true;
    }
    return false;
}

/// @brief Check if the packet queue is full and the packet will be dropped
/// @param packet A tUdpPacket to validate
/// @return A boolean true indicating a fault condition or false for no fault
bool tUdpServerApp::checkPacketQueueIsFull(const tUdpPacket<RBSData::tRBSData>& packet)
{
    if (m_receivedPackets.isFull())
    {
        tErrorHandlerSingleton::getInstance()
            .incrementErrorCount(tErrorHandlerSingleton::tErrorType::UDP_PACKET_OVERFLOW);
        return true;
    }

    return false;
}

/// @brief Add the given packet into the internal packet queue to be processed in the main thread context
/// @param packet A tUdpPacket to add to the queue
/// @return A boolean true indicating success or false for failure
bool tUdpServerApp::addPacketToQueue(const tUdpPacket<RBSData::tRBSData>& packet)
{
    try
    {
        m_receivedPackets.enqueue(packet);
        return true;
    }
    catch (std::exception &e)
    {
        tErrorHandlerSingleton::getInstance()
            .incrementErrorCount(tErrorHandlerSingleton::tErrorType::GENERAL_FAILURE);
        return false;
    }
}

/// @brief The function spawned by the UDP Server Thread
void tUdpServerApp::threadUdpServer()
{
    std::vector<char> rawPacket;
    tUdpPacket<RBSData::tRBSData> packet;

    while (m_isThreadRunning)
    {
        std::optional<tUdpPacket<RBSData::tRBSData>> packetOptional = waitForIncomingPacket();
        if (!packetOptional.has_value())
        {
            continue;
        }
        tUdpPacket<RBSData::tRBSData> packet = packetOptional.value();

        bool hasErrorOccurred = false;
        hasErrorOccurred = checkPacketCRCMismatch(packet)        | hasErrorOccurred;
        hasErrorOccurred = checkPacketDataLengthMismatch(packet) | hasErrorOccurred;
        hasErrorOccurred = checkPacketOutOfOrder(packet)         | hasErrorOccurred;
        hasErrorOccurred = checkPacketQueueIsFull(packet)        | hasErrorOccurred;

        if (hasErrorOccurred) 
        { 
            continue; 
        }

        addPacketToQueue(packet);
    }
}