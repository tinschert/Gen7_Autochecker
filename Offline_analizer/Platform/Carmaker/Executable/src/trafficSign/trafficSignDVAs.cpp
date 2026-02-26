/*
 * FILE:            trafficSignDVAs.cpp
 * SW-COMPONENT:    trafficSignDVAs
 * DESCRIPTION:     Source file for the trafficSignDVAs component
 * COPYRIGHT:       © 2023 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#include "trafficSignDVAs.h"
#include "common/commonDefinitions.h"

#include <array>
#include <string>

std::array<tTSignSensor, MAX_NUMBER_OF_TRAFFIC_SIGN_SENSORS> g_rbTrafficSignSensors;
std::array<std::string, MAX_NUMBER_OF_TRAFFIC_SIGN_SENSORS> g_sensor_name_to_find = {"TS1"};

int RB_TrafficSign_IsActive(int sensor)
{
    return (TSignSensor_FindIndexForName(g_sensor_name_to_find[sensor].c_str()) != -1) ? (INT_ST_ON) : (INT_ST_OFF);
}

int RB_TrafficSign_DeclQuants()
{
    for (int j = 0; j < MAX_NUMBER_OF_TRAFFIC_SIGN_SENSORS; j++)
    {
#if defined(RB_INT_VARIANT_HANDLING_ON)
        if(RB_TrafficSign_IsActive(j) == INT_ST_ON)
#endif
        {
            std::string sensor_name = g_sensor_name_to_find[j];
            auto &rbTrafficSignSensor = g_rbTrafficSignSensors[j];

            static_assert(MAX_NUMBER_OF_TRAFFIC_SIGNS < ROAD_MAX_TRFSIGNS, "MAX_NUMBER_OF_TRAFFIC_SIGNS shall be smaller than what is configured in Carmaker as ROAD_MAX_TRFSIGNS");
            for (int i = 0; i < MAX_NUMBER_OF_TRAFFIC_SIGNS; i++)
            {
                std::string sign_obj_ds_x = "RB.TrafficSign." + sensor_name + ".object" + std::to_string(i) + ".ds.x";
                std::string sign_obj_ds_y = "RB.TrafficSign." + sensor_name + ".object" + std::to_string(i) + ".ds.y";
                std::string sign_obj_ds_z = "RB.TrafficSign." + sensor_name + ".object" + std::to_string(i) + ".ds.z";
                std::string sign_obj_main_val0 = "RB.TrafficSign." + sensor_name + ".object" + std::to_string(i) + ".Main.val0";
                std::string sign_obj_main_val1 = "RB.TrafficSign." + sensor_name + ".object" + std::to_string(i) + ".Main.val1";
                std::string sign_obj_obj_id = "RB.TrafficSign." + sensor_name + ".object" + std::to_string(i) + ".ObjId";

                // Build the DVAs
                DDefDouble(NULL, sign_obj_ds_x.c_str(), "m", &rbTrafficSignSensor.Sign[i].ds[0], DVA_None);
                DDefDouble(NULL, sign_obj_ds_y.c_str(), "m", &rbTrafficSignSensor.Sign[i].ds[1], DVA_None);
                DDefDouble(NULL, sign_obj_ds_z.c_str(), "m", &rbTrafficSignSensor.Sign[i].ds[2], DVA_None);
                DDefFloat(NULL, sign_obj_main_val0.c_str(), "-", &rbTrafficSignSensor.Sign[i].main.val[0], DVA_None);
                DDefFloat(NULL, sign_obj_main_val1.c_str(), "-", &rbTrafficSignSensor.Sign[i].main.val[1], DVA_None);
                DDefInt(NULL, sign_obj_obj_id.c_str(), "-", &rbTrafficSignSensor.Sign[i].objId, DVA_None);
            }

            std::string sensor_n_sign = "RB.TrafficSign." + sensor_name + ".nSign";
            std::string sensor_timeStamp = "RB.TrafficSign." + sensor_name + ".TimeStamp";

            DDefInt(NULL, sensor_n_sign.c_str(), "-", &rbTrafficSignSensor.nSign, DVA_None);
            DDefDouble(NULL, sensor_timeStamp.c_str(), "s", &rbTrafficSignSensor.TimeStamp, DVA_None);
        }
    }

    return 0;
}