/*
 * FILE:            fillTrafficSign.cpp
 * SW-COMPONENT:    fillTrafficSign
 * DESCRIPTION:     Source file for the fillTrafficSign component
 * COPYRIGHT:       © 2023 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#include "fillTrafficSignData.h"
#include "trafficSignDVAs.h"
#include <array>
#include <string>
#include "SimCore.h"

extern std::array<tTSignSensor, MAX_NUMBER_OF_TRAFFIC_SIGN_SENSORS> g_rbTrafficSignSensors;
extern std::array<std::string, MAX_NUMBER_OF_TRAFFIC_SIGN_SENSORS> g_sensor_name_to_find;

int fillTrafficSign()
{
    for (int i = 0; i < MAX_NUMBER_OF_TRAFFIC_SIGN_SENSORS; i++)
    {
        if(SimCore.State != SCState_Simulate)
        {
            g_rbTrafficSignSensors[i].nSign = 0;
            continue;
        }
        if(RB_TrafficSign_IsActive(i) == INT_ST_ON)
        {
            int sensorId = TSignSensor_FindIndexForName(g_sensor_name_to_find[i].c_str());

            const auto* const tSignSensor = TSignSensor_GetByIndex(sensorId);
            if (tSignSensor == NULL)
            {
                continue;
            }

            g_rbTrafficSignSensors[i] = *tSignSensor;
        }
    }
    
    return 0;
}