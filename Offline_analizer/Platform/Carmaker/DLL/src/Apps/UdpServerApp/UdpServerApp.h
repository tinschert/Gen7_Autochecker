#pragma once

#include <BaseApp.h>
#include <Config.h>
#include <CSysVar.h>
#include <FixedSizeQueue.h>
#include <RBSData.h>
#include <UdpPacket/UdpPacket.h>

#include <asio.hpp>

#include <array>
#include <atomic>
#include <optional>
#include <thread>
#include <vector>

/// @brief A collection of tCSysVar instances for interfacing with CANoe
/// @note  Add all required SysVars to this structure and it's initialization list
struct tLocalSysVars
{
    /// @brief Construct a tLocalSysVar with the defined tCSysVars
    /// @note Fully initialize all members in the initialization list
    tLocalSysVars () :
        m_timestamp(tCSysVar<uint64_t>("RBSData::packetTimestamp")),
        m_packetCounter(tCSysVar<uint32_t>("RBSData::packetCounter")),
        m_radars({
            tCSysVar<RBSData::RadarData>("RBSData::FC"),
            tCSysVar<RBSData::RadarData>("RBSData::FL"),
            tCSysVar<RBSData::RadarData>("RBSData::FR"),
            tCSysVar<RBSData::RadarData>("RBSData::RR"),
            tCSysVar<RBSData::RadarData>("RBSData::RL")
        })
    { 
        // Do Nothing
    }

    /// @brief A timestamp from the CarMaker instance of when the UDP packet was sent
    tCSysVar<uint64_t> m_timestamp;

    /// @brief A counter that increments for each received packet
    tCSysVar<uint32_t> m_packetCounter;

    /// @brief A array containing a instance of RadarData for each configured radar 
    std::array<tCSysVar<RBSData::RadarData>, Config::Radar::TOTAL_RADAR_COUNT> m_radars;
};

class tUdpServerApp : public tBaseApp
{
public:

    tUdpServerApp();

    /// @brief Called when CANoe loads the DLL
    void onLoad();

    /// @brief Called right before the CANoe measurement starts 
    void onMeasurementPreStart();

    /// @brief Called when the CANoe measurement starts
    void onMeasurementStart();

    /// @brief Called when the CANoe measurement stops
    void onMeasurementStop();

    /// @brief Called when the CANoe unloads the DLL
    void onUnload();

    /// @brief Called every timer update cycle [Config::APP_UPDATE_TIMER_PERIOD_MS]
    void onUpdate();
    
protected:

    /// @brief Start the applications UDP server if it is open
    void startUdpServer();

    /// @brief Stop the applications UDP server if it is open
    void stopUdpServer();

    /// @brief The function spawned by the UDP Server Thread
    void threadUdpServer();

    /// @brief Receives a UDP packet from a client
    /// @return A std::vector containing the raw serialized bytes of the packet
    /// @note This function will block until a packet arrives
    std::vector<char> receiveUdpPacket();

    /// @brief Initialize the tCSysVars inside of member m_sysvars
    /// @note Should be called at each measurement start prior to internal UDP CANoe communication logic
    void initSysVarReferences();

    /// @brief Deinitialize the tCSysVars inside of member m_sysvars
    /// @note Should be called after/during each measurement stop
    void deinitSysVarReferences();

    /// @brief Maps the data members of the packet to the CANoe variables
    /// @param packet A tUdpPacket to write to CANoe SysVars
    void mapPacketToCANoe(tUdpPacket<RBSData::tRBSData>& packet);

    /// @brief Waits for an incoming packet to be received
    /// @return A tUdpPacket that was received or an empty optional
    /// @note Must be called in the server thread context
    std::optional<tUdpPacket<RBSData::tRBSData>> waitForIncomingPacket();

    /// @brief Check if a packets data length is mismatched
    /// @param packet A tUdpPacket to validate
    /// @return A boolean true indicating a fault condition or false for no fault
    bool checkPacketDataLengthMismatch(const tUdpPacket<RBSData::tRBSData>& packet);

    /// @brief Check if a packet was received out of order
    /// @param packet A tUdpPacket to validate
    /// @return A boolean true indicating a fault condition or false for no fault
    bool checkPacketOutOfOrder(const tUdpPacket<RBSData::tRBSData>& packet);

    /// @brief Check if the packets calculated CRC does not receive the transmitted one
    /// @param packet A tUdpPacket to validate
    /// @return A boolean true indicating a fault condition or false for no fault
    bool checkPacketCRCMismatch(const tUdpPacket<RBSData::tRBSData>& packet);

    /// @brief Check if the packet queue is full and the packet will be dropped
    /// @param packet A tUdpPacket to validate
    /// @return A boolean true indicating a fault condition or false for no fault
    bool checkPacketQueueIsFull(const tUdpPacket<RBSData::tRBSData>& packet);

    /// @brief Add the given packet into the internal packet queue to be processed in the main thread context
    /// @param packet A tUdpPacket to add to the queue
    /// @return A boolean true indicating success or false for failure
    bool addPacketToQueue(const tUdpPacket<RBSData::tRBSData>& packet);

private:

    /// @brief An optional collection of sysvars for interfacing with CANoe once the interface is valid
    std::optional<tLocalSysVars> m_sysvars {std::nullopt};

    /// @brief The IO context for the ASIO socket
    asio::io_context m_context;

    /// @brief  The socket instance for the UDP Server
    asio::ip::udp::socket m_socket;

    /// @brief The thread object for the running UDP server
    std::thread m_serverThread;

    /// @brief The atomic flag used to signify the UDP thread status
    std::atomic<bool> m_isThreadRunning;

    /// @brief A queue of received packets
    FixedSizeQueue<tUdpPacket<RBSData::tRBSData>, Config::UdpServerApp::MAX_PACKETS_IN_QUEUE> m_receivedPackets;

};
