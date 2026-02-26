#pragma once

#include <CSysVar.h>

#include <array>
#include <optional>
#include <stdint.h>

/// @brief Handles the recording and subsequent alerting of all errors to the CANoe instance
/// @todo A future implementation goal could be the add in tCSysVars for each enum type to show counts 
class tErrorHandlerSingleton
{
public:

    /// @brief A collection of enums representing possible error conditions in the UdpServerApp
    /// @note  This order must control/match the order in `Platform\Carmaker\Nodes\cm_udp_error_handler.cin`
    enum class tErrorType : uint32_t
    {
        /// @brief Indicates no fault is present in the system (default state)
        /// @note Included below __COUNT_OF_ERRORS to prevent inclusion in error count array
        NO_FAULT,

        /// @brief Indicates the DLL server failed to startup
        CONNECTION_FAILURE,

        /// @brief Indicates a general failure of the UdpServerApp
        GENERAL_FAILURE,

        /// @brief Indicates the alive counter from the UDP packets is frozen indicating connection failure
        UDP_ALIVE_COUNTER_FROZEN, /// TODO: IMPLEMENT
        
        /// @brief Indicates a CRC mismatch on a received UDP packet
        UDP_CRC_MISMATCH,
        
        /// @brief Indicates a packet reception overflow ev2ent
        UDP_PACKET_OVERFLOW,

        /// @brief Indicates a general reception failure in the UDP reception procedure
        UDP_RECEPTION_FAILURE,

        /// @brief Indicates the packets sent from the CarMaker DLL were not received in order
        UDP_OUT_OF_ORDER_PACKETS,

        /// @brief Indicates the received UDP packet size does not match the tRBSData struct size
        /// @note This typically indicates a mismatch in DLL and EXE versions
        UDP_MESSAGE_SIZE_MISMATCH,

        /// @brief Indicates that the UDP tCSysVars were written to prior to initialization
        WRITE_TO_UNINITIALIZED_CSYSVAR,
        
        /// @brief Metadata for total count of errors in the enum
        /// @note Do not include any error enums after this member
        __COUNT_OF_ERRORS,
    };

    /// @brief Gets a reference to the instance of our tErrorHandlerSingleton
    /// @return A mutable reference to the tErrorHandleSingleton instance
    static tErrorHandlerSingleton& getInstance();

    static std::string getErrorTypeAsString(const tErrorType error);

    /// @brief Deleted Copy Constructor 
    tErrorHandlerSingleton(const tErrorHandlerSingleton&) = delete;

    /// @brief Deleted Assignment Operator
    tErrorHandlerSingleton& operator=(const tErrorHandlerSingleton&) = delete;

    /// @brief Handler all error reporting methods through checking error counters for anything above limit
    /// @note  All prints or sysvar writes must be in the main thread context (not in a server thread)
    void handleErrorReporting();

    /// @brief Reset the error handler
    /// @note This should be called at each measurement stop to reinitialize the sysvar and counts
    void reset();

    /// @brief Get the error count for a given tErrorType enum
    /// @param errorType The error type to read the value of 
    /// @return The current count of errors
    uint32_t getErrorCount(const tErrorType errorType) const;

    /// @brief Set the error count for a given tErrorType enum
    /// @param errorType The error type to set the value of
    /// @param count The count to set the value to
    void setErrorCount(const tErrorType errorType, const uint32_t count);

    /// @brief Increment the error count for a given tErrorType enum
    /// @param errorType The error type to increment the value of
    void incrementErrorCount(const tErrorType errorType);

protected:

    /// @brief Set the value of m_errorReportSysVar to the value specified
    /// @param value The error type to set the error sysvar to
    /// @note This method will lazy initialize m_errorReportSysVar upon first call of the measurement
    void setReportSysVar(tErrorType value);

private:

    /// @brief Default Constructor
    tErrorHandlerSingleton() = default;

    /// @brief Default Destructor
    ~tErrorHandlerSingleton() = default;

    /// @brief An optional containing a tCSysVar connected to a CANoe SysVar used to transmit error enums
    /// @note This member is lazy initialized and will be initialized upon the first call to setReportSysVar
    std::optional<tCSysVar<uint32_t>> m_errorReportSysVar;

    /// @brief An array with size matching total size of the tErrorType where the enum indexes its value
    /// @note  Enforce that this is only ever accessed through the "getErrorCount" or "setErrorCount" method \ 
    ///        prevent OOB error
    std::array<volatile uint32_t, static_cast<size_t>(tErrorType::__COUNT_OF_ERRORS)> m_errorCountArray;
};
