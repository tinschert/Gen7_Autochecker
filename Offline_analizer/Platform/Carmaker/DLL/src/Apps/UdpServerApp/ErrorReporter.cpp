#include <ErrorReporter.h>

#include <Config.h>

#include <algorithm>
#include <array>
#include <functional>
#include <map>

/// @brief Gets a reference to the instance of our tErrorHandlerSingleton
/// @return A mutable reference to the tErrorHandleSingleton instance
tErrorHandlerSingleton& tErrorHandlerSingleton::getInstance()
{
    static tErrorHandlerSingleton instance;
    return instance;
}

std::string tErrorHandlerSingleton::getErrorTypeAsString(const tErrorType error)
{
    const std::map<tErrorType, std::string> errorToStringMap = {
            {tErrorType::CONNECTION_FAILURE, "CONNECTION_FAILURE"},
            {tErrorType::GENERAL_FAILURE, "GENERAL_FAILURE"},
            {tErrorType::UDP_ALIVE_COUNTER_FROZEN, "UDP_ALIVE_COUNTER_FROZEN"},
            {tErrorType::UDP_CRC_MISMATCH, "UDP_CRC_MISMATCH"},
            {tErrorType::UDP_PACKET_OVERFLOW, "UDP_PACKET_OVERFLOW"},
            {tErrorType::UDP_RECEPTION_FAILURE, "UDP_RECEPTION_FAILURE"},
            {tErrorType::UDP_OUT_OF_ORDER_PACKETS, "UDP_OUT_OF_ORDER_PACKETS"},
            {tErrorType::UDP_MESSAGE_SIZE_MISMATCH, "UDP_MESSAGE_SIZE_MISMATCH"},
            {tErrorType::WRITE_TO_UNINITIALIZED_CSYSVAR, "WRITE_TO_UNINITIALIZED_CSYSVAR"}
    };

    if (errorToStringMap.contains(error))
    {
        return errorToStringMap.at(error);
    }

    return "ERRORTYPE_TO_STRING_MISSING";
}

/// @brief Handler all error reporting methods through checking error counters for anything above limit
/// @note  All prints or sysvar writes must be in the main thread context (not in a server thread)
void tErrorHandlerSingleton::handleErrorReporting()
{
    const uint32_t DEFAULT_ERROR_COUNT = 1;
    static uint64_t handlerCycleCountTracker = 0;
    
    /// @brief Lambda to handle errors based on the error type, limit, and decay rate
    /// @param type The error type to handle
    /// @param limit The maximum number of errors to allow before handling
    /// @param errorDecayRateMillis The rate at which to decay the error count [0 = no decay]
    /// @param handler and addition void method to call for each error for any error specific implementation
    auto handleError = [this]
        (tErrorType type, const uint32_t limit, const uint32_t errorDecayRateMillis, std::function<void(tErrorType)> handler) 
    {
        if (this->getErrorCount(type) >= limit)
        {
            if (Config::UdpServerApp::ErrorLimits::ERROR_HANDLER_CANOE_WRITE_PRINT_ENABLED)
            {
                cclPrintf("Error: CANoe DLL max error count of %s exceeded [limit = %d]",
                    tErrorHandlerSingleton::getErrorTypeAsString(type).c_str(),
                    limit
                );
            }
            handler(type);
            this->setErrorCount(type, 0);
        }

        const uint64_t currentCycleCountTimeMilliseconds 
            = Config::APP_UPDATE_TIMER_PERIOD_MS * handlerCycleCountTracker;
        if (
            errorDecayRateMillis > 0 
            && (currentCycleCountTimeMilliseconds % errorDecayRateMillis) < Config::APP_UPDATE_TIMER_PERIOD_MS)
        {
            this->setErrorCount(type, std::max(0, static_cast<int>(this->getErrorCount(type)) - 1));
        }
    };

    handleError(
        tErrorType::CONNECTION_FAILURE, 
        Config::UdpServerApp::ErrorLimits::MAX_CONNECTION_FAILURES, 
        0,
        [this](tErrorType type) { this->setReportSysVar(type); }
    );

    handleError(
        tErrorType::GENERAL_FAILURE,
        DEFAULT_ERROR_COUNT,
        0,
        [this](tErrorType type) { this->setReportSysVar(type); }
    );

    handleError(
        tErrorType::UDP_ALIVE_COUNTER_FROZEN,
        Config::UdpServerApp::ErrorLimits::MAX_ALIVE_COUNTER_FAILURES,
        0,
        [this](tErrorType type) { this->setReportSysVar(type); }
    );

    handleError(
        tErrorType::UDP_CRC_MISMATCH,
        Config::UdpServerApp::ErrorLimits::MAX_CRC_MISMATCHES,
        0,
        [this](tErrorType type) { this->setReportSysVar(type); }
    );

    handleError(
        tErrorType::UDP_PACKET_OVERFLOW,
        Config::UdpServerApp::ErrorLimits::UDP_PACKET_OVERFLOW,
        0,
        [this](tErrorType type) { this->setReportSysVar(type); }
    );

    handleError(
        tErrorType::UDP_RECEPTION_FAILURE,
        DEFAULT_ERROR_COUNT,
        0,
        [this](tErrorType type) { this->setReportSysVar(type); }
    );

    handleError(
        tErrorType::UDP_OUT_OF_ORDER_PACKETS,
        DEFAULT_ERROR_COUNT,
        0,
        [this](tErrorType type) { this->setReportSysVar(type); }
    );

    handleError(
        tErrorType::UDP_MESSAGE_SIZE_MISMATCH,
        DEFAULT_ERROR_COUNT,
        0,
        [this](tErrorType type) { this->setReportSysVar(type); }
    );

    handleError(
        tErrorType::WRITE_TO_UNINITIALIZED_CSYSVAR,
        DEFAULT_ERROR_COUNT,
        0,
        [this](tErrorType type) { this->setReportSysVar(type); }
    );

    // Increment cycle counter
    handlerCycleCountTracker++;
}

/// @brief Reset the error handler
/// @note This should be called at each measurement stop to reinitialize the sysvar and counts
void tErrorHandlerSingleton::reset()
{
    m_errorReportSysVar = std::nullopt;

    for (volatile uint32_t& count : m_errorCountArray)
    {
        count = 0;
    }
}

/// @brief Get the error count for a given tErrorType enum
/// @param errorType The error type to read the value of 
/// @return The current count of errors
uint32_t tErrorHandlerSingleton::getErrorCount(const tErrorType errorType) const
{
    return m_errorCountArray[static_cast<const size_t>(errorType)];
}

/// @brief Set the error count for a given tErrorType enum
/// @param errorType The error type to set the value of
/// @param count The count to set the value to
void tErrorHandlerSingleton::setErrorCount(const tErrorType errorType, const uint32_t count)
{
    m_errorCountArray[static_cast<const size_t>(errorType)] = count;
}

/// @brief Increment the error count for a given tErrorType enum
/// @param errorType The error type to increment the value of
void tErrorHandlerSingleton::incrementErrorCount(const tErrorType errorType)
{
    m_errorCountArray[static_cast<const size_t>(errorType)] += 1;
}

/// @brief Set the value of m_errorReportSysVar to the value specified
/// @param value The error type to set the error sysvar to
/// @note This method will lazy initialize m_errorReportSysVar upon first call of the measurement
void tErrorHandlerSingleton::setReportSysVar(tErrorType value)
{
    // Lazy Initialization
    if(!m_errorReportSysVar.has_value())
    {
        m_errorReportSysVar = tCSysVar<uint32_t>(Config::UdpServerApp::ErrorLimits::ERROR_SYSVAR_NAME_CANOE);
    }

    m_errorReportSysVar.value().setValue(static_cast<uint32_t>(value));
}