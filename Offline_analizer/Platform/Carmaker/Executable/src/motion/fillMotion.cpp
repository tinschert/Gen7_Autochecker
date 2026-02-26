/*
 * FILE:            fillMotion.cpp
 * SW-COMPONENT:    fillMotion
 * DESCRIPTION:     Source file for the fillMotion component
 * COPYRIGHT:       © 2024 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */
#include <string>
#include <cmath>
#include "fillMotion.h"
#include "motionDVAs.h"
#include "common/commonDefinitions.h"
#include "Vehicle/Sensor_Inertial.h"
#include "Vehicle.h"
#include "SimCore.h"
#include "Car/Car.h"

extern RbInertialSensors g_inertialSensors;
extern RbRoadAttributes g_road;
//tRadarSensor * RbRadarSensor;
tBdySensor * RbBdySensor;

int GetSensorIdx(char * sensor_name)
{
    int retIdx;
    int i;

    retIdx = -1;

    for(i=0;i<MAX_NBR_OF_SUSPENSION_SENSORS;i++)
    {
        if(strcmp(sensor_name, gStrSuspSensors[i]) == 0)
        {
            retIdx = i;
            break;
        }
    }

    return retIdx;
}

int fillMotion()
{
    int i_Sensor;
    int nSensors;
    int sensorIdx;

    if (SimCore.State != SCState_Simulate)
    {
        for(i_Sensor=0;i_Sensor<MAX_NBR_OF_SUSPENSION_SENSORS;i_Sensor++)
        {
            g_inertialSensors.Susp_Sensors[i_Sensor].isActive = 0;
            g_inertialSensors.Susp_Sensors[i_Sensor].mount_pos_xyz_in_m[COORD_Z] = 0;
            g_inertialSensors.Susp_Sensors[i_Sensor].actl_pos_xyz_in_m[COORD_Z] = 0;
            g_inertialSensors.Susp_Sensors[i_Sensor].delta_pos_xyz_in_m[COORD_Z] = 0;
        }
        
        g_road.steepness_roll_in_rad = 0;
        g_road.steepness_pitch_in_rad = 0;

    }
    else
    {
        g_road.steepness_pitch_in_rad = 
            (
                asin(
                    (Car.Tire[WHL_FL].P_0[COORD_Z] - Car.Tire[WHL_RL].P_0[COORD_Z])
                    / sqrt(
                        pow(Car.Tire[WHL_FL].P_0[COORD_X] - Car.Tire[WHL_RL].P_0[COORD_X], 2)
                        + pow(Car.Tire[WHL_FL].P_0[COORD_Y] - Car.Tire[WHL_RL].P_0[COORD_Y], 2)
                        + pow(Car.Tire[WHL_FL].P_0[COORD_Z] - Car.Tire[WHL_RL].P_0[COORD_Z], 2)
                    )
                )
                + asin(
                    (Car.Tire[WHL_FR].P_0[COORD_Z] - Car.Tire[WHL_RR].P_0[COORD_Z])
                    / sqrt(
                        pow(Car.Tire[WHL_FR].P_0[COORD_X] - Car.Tire[WHL_RR].P_0[COORD_X], 2)
                        + pow(Car.Tire[WHL_FR].P_0[COORD_Y] - Car.Tire[WHL_RR].P_0[COORD_Y], 2)
                        + pow(Car.Tire[WHL_FR].P_0[COORD_Z] - Car.Tire[WHL_RR].P_0[COORD_Z], 2)
                    )
                )
            ) / 2;

            g_road.steepness_roll_in_rad = 
            (
                asin(
                    (Car.Tire[WHL_FL].P_0[COORD_Z] - Car.Tire[WHL_FR].P_0[COORD_Z])
                    / sqrt(
                        pow(Car.Tire[WHL_FL].P_0[COORD_X] - Car.Tire[WHL_FR].P_0[COORD_X], 2)
                        + pow(Car.Tire[WHL_FL].P_0[COORD_Y] - Car.Tire[WHL_FR].P_0[COORD_Y], 2)
                        + pow(Car.Tire[WHL_FL].P_0[COORD_Z] - Car.Tire[WHL_FR].P_0[COORD_Z], 2)
                    )
                )
                + asin(
                    (Car.Tire[WHL_RL].P_0[COORD_Z] - Car.Tire[WHL_RR].P_0[COORD_Z])
                    / sqrt(
                        pow(Car.Tire[WHL_RL].P_0[COORD_X] - Car.Tire[WHL_RR].P_0[COORD_X], 2)
                        + pow(Car.Tire[WHL_RL].P_0[COORD_Y] - Car.Tire[WHL_RR].P_0[COORD_Y], 2)
                        + pow(Car.Tire[WHL_RL].P_0[COORD_Z] - Car.Tire[WHL_RR].P_0[COORD_Z], 2)
                    )
                )
            ) / 2;
        
        // Suspension travel (inertial sensor)

        nSensors = InertialSensorCount;

        if(nSensors > 0)
        {
            for(i_Sensor=0;i_Sensor<nSensors;i_Sensor++)
            {   
                RbBdySensor = InertialSensor_GetByIndex(i_Sensor);

                sensorIdx = GetSensorIdx(RbBdySensor->Name);

                if(sensorIdx != -1)
                {
                    g_inertialSensors.Susp_Sensors[sensorIdx].isActive = 1;
                    g_inertialSensors.Susp_Sensors[sensorIdx].mount_pos_xyz_in_m[COORD_X] = RbBdySensor->Pos_B[COORD_X];
                    g_inertialSensors.Susp_Sensors[sensorIdx].mount_pos_xyz_in_m[COORD_Y] = RbBdySensor->Pos_B[COORD_Y];
                    g_inertialSensors.Susp_Sensors[sensorIdx].mount_pos_xyz_in_m[COORD_Z] = RbBdySensor->Pos_B[COORD_Z];
                    g_inertialSensors.Susp_Sensors[sensorIdx].actl_pos_xyz_in_m[COORD_X] = RbBdySensor->Pos_0[COORD_X];
                    g_inertialSensors.Susp_Sensors[sensorIdx].actl_pos_xyz_in_m[COORD_Y] = RbBdySensor->Pos_0[COORD_Y];
                    g_inertialSensors.Susp_Sensors[sensorIdx].actl_pos_xyz_in_m[COORD_Z] = RbBdySensor->Pos_0[COORD_Z];
                    g_inertialSensors.Susp_Sensors[sensorIdx].delta_pos_xyz_in_m[COORD_Z] = // Fr1
                        sqrt(
                            pow(g_inertialSensors.Susp_Sensors[sensorIdx].actl_pos_xyz_in_m[COORD_X] - Car.Tire[sensorIdx].P_0[COORD_X], 2)
                            + pow(g_inertialSensors.Susp_Sensors[sensorIdx].actl_pos_xyz_in_m[COORD_Y] - Car.Tire[sensorIdx].P_0[COORD_Y], 2)
                            + pow(g_inertialSensors.Susp_Sensors[sensorIdx].actl_pos_xyz_in_m[COORD_Z] - Car.Tire[sensorIdx].P_0[COORD_Z], 2)
                        ) // Fr0
                         - g_inertialSensors.Susp_Sensors[sensorIdx].mount_pos_xyz_in_m[COORD_Z]; // Fr1
                }
            }
        }
    }

    return 0;
}