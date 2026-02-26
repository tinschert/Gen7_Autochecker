#pragma once

#include <BaseApp.h>
#include <Config.h>

#include <functional>
#include <vector>
#include <memory>

/// @brief The AppManager class is responsible for managing the applications in the system.
class tAppManager {
public:

    /// @brief Constructs an instance of AppManager.
    tAppManager();

    /// @brief Handles the loading of an application.
    void handleAppOnLoad();

    /// @brief Handles the pre-start of measurement for an application.
    void handleAppOnMeasurementPreStart();

    /// @brief Handles the start of measurement for an application.
    void handleAppOnMeasurementStart();

    /// @brief Handles the stop of measurement for an application.
    void handleAppOnMeasurementStop();

    /// @brief Handles the unloading of an application.
    void handleAppOnUnload();

    /// @brief Handles a regular update of the application [interval of Config::APP_UPDATE_TIMER_PERIOD_MS]
    void handleUpdateTimer();

    /// @brief Registers an application.
    /// @param BaseAppPtr A pointer to the BaseApp object representing the application.
    void registerApp(tBaseApp& baseAppPtr);

private:

    /// @brief A vector of BaseApp pointers representing the applications
    std::vector<std::reference_wrapper<tBaseApp>> m_apps;

};