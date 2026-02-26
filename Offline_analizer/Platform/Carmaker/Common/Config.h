#pragma once

#include <stdint.h>
#include <string>

/// @brief Project specific configuration parameters
namespace Config
{

    /// @brief The period of the update timer in milliseconds.
    /// @note This controls the update period of the Apps based of AppManager. Changing this value directly \
    ///       affects how often each app is updated. Decreasing the period may result in a performance impact to \
    ///       CANoe. This should be less than Config::UdpClient::TRANSMIT_UDP_DATA_CYCLE_TIME_MS
    const int64_t APP_UPDATE_TIMER_PERIOD_MS = 5;

    /// @brief The configuration parameters for the Radar Model
    namespace Radar
    {
        /// @brief The max amount of radar objects configured in the RBS
        /// @note  Modifying this value will require increasing the ClasseDatabase.xslx file to match the \
        ///        The new increased size. This will require a SysVar.xml regeneration for CANoe
        const int32_t MAX_RADAR_OBJECTS = 40;

        /// @brief The total amount of radars in the RBS to send data for
        /// @note  Modifying this value will require increasing the ClasseDatabase.xslx file to match the \
        ///        The new increased size. This will require a SysVar.xml regeneration for CANoe
        const int32_t TOTAL_RADAR_COUNT = 5;
    }

    /// @brief The configuration parameters for the CANoe UdpServerApp UDP Server
    namespace UdpServerApp
    {
        /// @brief The UDP socket listening port for the UDP Server
        /// @note  This port is used by the UDP Server to listen for incoming packets from the CarMaker EXE
        const int32_t LISTENING_PORT = 25565;

        /// @brief The maximum number of packets that can be stored in the received packets queue
        /// @note  This value controls the maximum number of packets that can be stored in the queue before \
        ///        packets are dropped
        const int32_t MAX_PACKETS_IN_QUEUE = 16;

    }

    /// @brief The configuration parameters for the CarMaker Executable UDP Client
    namespace UdpClient
    {
        /// @brief The UDP socket sending port for the UDP Client
        /// @note  This port is used by the UDP Client to send packets to the CarMaker EXE
        const int32_t SENDING_PORT = Config::UdpServerApp::LISTENING_PORT;

        /// @brief The IP address of the CANoe UDP Server
        /// @note  This IP address is used by the UDP Client to send packets to the UDP Server
        const std::string CARMAKER_UDP_TARGET_IP_ADDRESS = "127.0.0.1";

        /// @brief The CarMaker Executable UDP Update Cycle in milliseconds
        /// @note  This controls how quickly CarMaker sends UDP Packets to the UDP Server on CANoe
        const int64_t TRANSMIT_UDP_DATA_CYCLE_TIME_MS = 25;
    }

    /// @brief Definitions of all error limits in the UdpServerApp
    namespace UdpServerApp::ErrorLimits
    {
        /// @brief The name of the UDP Server App Error count number sysvar in CANoe
        const std::string ERROR_SYSVAR_NAME_CANOE = "RBSData::udpServerAppErrorNumber";

        /// @brief Enables the CANoe write window printing of errors
        const bool ERROR_HANDLER_CANOE_WRITE_PRINT_ENABLED = true;

        /// @brief The max amount of alive counter failures
        const uint32_t MAX_ALIVE_COUNTER_FAILURES = 3;

        /// @brief The max amount of connection failures
        const uint32_t MAX_CONNECTION_FAILURES = 1;

        /// @brief The max amount of CRC mismatches
        const uint32_t MAX_CRC_MISMATCHES = 3;

        /// @brief The max amount of packet overflows
        const uint32_t UDP_PACKET_OVERFLOW = 3;
    }

}

// -----------------------------------------------------------------------------------------------------------
// Parameter Validation Section
// -----------------------------------------------------------------------------------------------------------

// Validate we are polling packets on CANoe faster than we send them on CarMaker
static_assert(Config::UdpClient::TRANSMIT_UDP_DATA_CYCLE_TIME_MS > Config::APP_UPDATE_TIMER_PERIOD_MS, 
    "Config::UdpClient::TRANSMIT_UDP_DATA_CYCLE_TIME_MS must be greater than Config::APP_UPDATE_TIMER_PERIOD_MS");

// Validate CarMaker is sending packets on the same port the UDP Server is listening on
static_assert(Config::UdpClient::SENDING_PORT == Config::UdpServerApp::LISTENING_PORT, 
    "Config::UdpClient::SENDING_PORT must be the same as Config::UdpServerApp::LISTENING_PORT");