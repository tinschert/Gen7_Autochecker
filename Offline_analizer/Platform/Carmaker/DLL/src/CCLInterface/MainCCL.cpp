#include <AppManager.h>
#include <Config.h>
#include <UdpServerApp.h>

#include <CCL.h>

// Application Objects
tUdpServerApp g_UdpServerApp;

// Global Variables
tAppManager g_AppManager;

int32_t g_UpdateTimer;

void cclUpdateTimer(int64_t time, int32_t timerID)
{
    g_AppManager.handleUpdateTimer();
    cclTimerSet(g_UpdateTimer, cclTimeMilliseconds(Config::APP_UPDATE_TIMER_PERIOD_MS));
}

void cclMeasurementPreStartHandler()
{
    cclWrite("Info: onMeasurementPreStart");
    g_AppManager.handleAppOnMeasurementPreStart();
}

void cclMeasurementStartHandler()
{
    cclWrite("Info: onMeasurementStart");
    
    g_UpdateTimer = cclTimerCreate(cclUpdateTimer);
    cclTimerSet(g_UpdateTimer, cclTimeMilliseconds(Config::APP_UPDATE_TIMER_PERIOD_MS));

    g_AppManager.handleAppOnMeasurementStart();
}

void cclMeasurementStopHandler()
{
    cclWrite("Info: onMeasurementStop");
    g_AppManager.handleAppOnMeasurementStop();
}

void cclOnDllUnload()
{
    g_AppManager.handleAppOnUnload();
    cclWrite("Info: CCLInterface DLL unloaded");
}

void cclOnDllLoad() 
{
    cclSetMeasurementPreStartHandler(&cclMeasurementPreStartHandler);
    cclSetMeasurementStartHandler(&cclMeasurementStartHandler);
    cclSetMeasurementStopHandler(&cclMeasurementStopHandler);
    cclSetDllUnloadHandler(&cclOnDllUnload);

    // Register Applications
    g_AppManager.registerApp(g_UdpServerApp);
    
    g_AppManager.handleAppOnLoad();

    cclWrite("Info: CCLInterface DLL loaded");
}