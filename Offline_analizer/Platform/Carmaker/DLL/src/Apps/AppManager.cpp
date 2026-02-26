#include <AppManager.h>


tAppManager::tAppManager()
{
}


void tAppManager::registerApp(tBaseApp& baseAppPtr)
{
    m_apps.push_back(baseAppPtr);
}


void tAppManager::handleAppOnLoad()
{
    for (tBaseApp& app : m_apps)
    {
        app.onLoad();
    }
}


void tAppManager::handleAppOnMeasurementPreStart()
{
    for (tBaseApp& app : m_apps)
    {
        app.onMeasurementPreStart();
    }
}


void tAppManager::handleAppOnMeasurementStart()
{
    for (tBaseApp& app : m_apps)
    {
        app.onMeasurementStart();
    }
}


void tAppManager::handleAppOnMeasurementStop()
{
    for (tBaseApp& app : m_apps)
    {
        app.onMeasurementStop();
    }
}


void tAppManager::handleAppOnUnload()
{
    for (tBaseApp& app : m_apps)
    {
        app.onUnload();
    }
}

void tAppManager::handleUpdateTimer()
{
    for (tBaseApp& app : m_apps)
    {
        app.onUpdate();
    }
}