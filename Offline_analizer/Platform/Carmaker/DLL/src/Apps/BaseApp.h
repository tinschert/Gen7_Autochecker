#pragma once

#include <string>

/// @brief A base class for all CANoe CCL applications
class tBaseApp
{
public:

    tBaseApp() {}

    /// @brief Called when CANoe loads the DLL
    void virtual onLoad() = 0;

    /// @brief Called right before the CANoe measurement starts 
    void virtual onMeasurementPreStart() = 0;

    /// @brief Called when the CANoe measurement starts
    void virtual onMeasurementStart() = 0;

    /// @brief Called when the CANoe measurement stops
    void virtual onMeasurementStop() = 0;

    /// @brief Called when the CANoe unloads the DLL
    void virtual onUnload() = 0;
    
    /// @brief Called every 5ms as defined by this CCL interface
    void virtual onUpdate() = 0;

private:

};