/*
 * FILE:            fillCarParameters.cpp
 * SW-COMPONENT:    fillCarParameters
 * DESCRIPTION:     Source file for the fillCarParameters component
 * COPYRIGHT:       © 2024 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */
#include <string>
#include "fillCarParameters.h"
#include "carParametersDVAs.h"
#include "common/commonDefinitions.h"
#include "Vehicle.h"
#include "SimCore.h"
//#include "Vehicle/Sensor_Radar.h"
#include "Vehicle/Sensor_Object.h"
//#include "ipgdriver.h"

extern RbCarParameters g_carParameters;
//tRadarSensor * RbRadarSensor;
tObjectSensor * RbObjectSensor;

int GetRadarIdx(char * sensor_name)
{
    int retIdx;
    int i;

    retIdx = -1;

    for(i=0;i<MAX_NBR_OF_RADARS;i++)
    {
        if(strcmp(sensor_name, gStrRadars[i]) == 0)
        {
            retIdx = i;
            break;
        }
    }

    return retIdx;
}

bool IsFVideo(char * sensor_name)
{
    return (strcmp(sensor_name, gStrFVideo) == 0);
}

int fillCarParameters()
{
    int i_Whl, i_Sensor;
    int radarIdx;
    int nSensors, nRadars;

    if (SimCore.State != SCState_Simulate)
    {
        g_carParameters.drivenDistance = 0;
        g_carParameters.massTotal = 0;
        g_carParameters.nbrOfBGears = 0;
        g_carParameters.nbrOfFGears = 0;
        g_carParameters.nbrOfWheels = 0;
        g_carParameters.overhangFront = 0;
        g_carParameters.overhangRear = 0;
        g_carParameters.trackWidth = 0;
        g_carParameters.velocityMax = 0;
        g_carParameters.wheelBase = 0;
        //g_carParameters.wheelRadius = 0;
        
        for(i_Whl=0;i_Whl<MAX_NBR_OF_WHEELS;i_Whl++)
        {
            g_carParameters.Wheel[i_Whl].radiusBelt = 0;
            g_carParameters.Wheel[i_Whl].radiusRim = 0;
            g_carParameters.Wheel[i_Whl].width = 0;
        }

        for(i_Sensor=0;i_Sensor<MAX_NBR_OF_RADARS;i_Sensor++)
        {
            g_carParameters.Radars[i_Sensor].isActive = 0;
            // g_carParameters.Radars[i_Sensor].Mounting.ori_xyz_in_rad[COORD_X] = 0;
            // g_carParameters.Radars[i_Sensor].Mounting.ori_xyz_in_rad[COORD_Y] = 0;
            g_carParameters.Radars[i_Sensor].Mounting.ori_xyz_in_rad[COORD_Z] = 0;
            g_carParameters.Radars[i_Sensor].Mounting.pos_xyz_in_m[COORD_X] = 0;
            g_carParameters.Radars[i_Sensor].Mounting.pos_xyz_in_m[COORD_Y] = 0;
            g_carParameters.Radars[i_Sensor].Mounting.pos_xyz_in_m[COORD_Z] = 0;
        }
    }
    else
    {
        g_carParameters.drivenDistance = Vehicle.Cfg.Distance;
        g_carParameters.massTotal = Vehicle.Cfg.MassTotal;
        g_carParameters.gearBoxKind = Vehicle.Cfg.GBKind;
        g_carParameters.nbrOfBGears = Vehicle.Cfg.nBGears;
        g_carParameters.nbrOfFGears = Vehicle.Cfg.nFGears;
        g_carParameters.nbrOfWheels = Vehicle.Cfg.nWheels;
        g_carParameters.overhangFront = Vehicle.Cfg.OverhangFront;
        g_carParameters.overhangRear = Vehicle.Cfg.OverhangRear;
        g_carParameters.trackWidth = Vehicle.Cfg.TrackWidth;
        g_carParameters.velocityMax = Vehicle.Cfg.Velocity_Max;
        g_carParameters.wheelBase = Vehicle.Cfg.WheelBase;
        //g_carParameters.wheelRadius = Vehicle.Cfg.WhlRadius;

        for(i_Whl=0;i_Whl<MAX_NBR_OF_WHEELS;i_Whl++)
        {
            g_carParameters.Wheel[i_Whl].radiusBelt = Vehicle.Cfg.Tire[i_Whl].Radius_Belt;
            g_carParameters.Wheel[i_Whl].radiusRim = Vehicle.Cfg.Tire[i_Whl].Radius_Rim;
            g_carParameters.Wheel[i_Whl].width = Vehicle.Cfg.Tire[i_Whl].Width_Outer;
        }

        nSensors = ObjectSensorCount;
        nRadars = 0;

        if(nSensors > 0)
        {
            for(i_Sensor=0;i_Sensor<nSensors;i_Sensor++)
            {   
                RbObjectSensor = ObjectSensor_GetByIndex(i_Sensor);

                if(IsFVideo(RbObjectSensor->bs.Name))
                {
                    g_carParameters.FVideo.isActive = 1;
                    //strcpy(g_carParameters.FVideo.sName, RbObjectSensor->bs.Name);
                    // g_carParameters.FVideo.Mounting.ori_xyz_in_rad[COORD_X] = RbObjectSensor->rot_zyx[COORD_X];
                    // g_carParameters.FVideo.Mounting.ori_xyz_in_rad[COORD_Y] = RbObjectSensor->rot_zyx[COORD_Y];
                    g_carParameters.FVideo.Mounting.ori_xyz_in_rad[COORD_Z] = RbObjectSensor->rot_zyx[COORD_Z];
                    g_carParameters.FVideo.Mounting.pos_xyz_in_m[COORD_X] = RbObjectSensor->bs.Pos_B[COORD_X];
                    g_carParameters.FVideo.Mounting.pos_xyz_in_m[COORD_Y] = RbObjectSensor->bs.Pos_B[COORD_Y];
                    g_carParameters.FVideo.Mounting.pos_xyz_in_m[COORD_Z] = RbObjectSensor->bs.Pos_B[COORD_Z];
                }
                else
                {
                    radarIdx = GetRadarIdx(RbObjectSensor->bs.Name);

                    if(radarIdx != -1)
                    {
                        g_carParameters.Radars[radarIdx].isActive = 1;
                        //strcpy(g_carParameters.Radars[radarIdx].sName, RbObjectSensor->bs.Name);
                        // g_carParameters.Radars[radarIdx].Mounting.ori_xyz_in_rad[COORD_X] = RbObjectSensor->rot_zyx[COORD_X];
                        // g_carParameters.Radars[radarIdx].Mounting.ori_xyz_in_rad[COORD_Y] = RbObjectSensor->rot_zyx[COORD_Y];
                        g_carParameters.Radars[radarIdx].Mounting.ori_xyz_in_rad[COORD_Z] = RbObjectSensor->rot_zyx[COORD_Z];
                        g_carParameters.Radars[radarIdx].Mounting.pos_xyz_in_m[COORD_X] = RbObjectSensor->bs.Pos_B[COORD_X];
                        g_carParameters.Radars[radarIdx].Mounting.pos_xyz_in_m[COORD_Y] = RbObjectSensor->bs.Pos_B[COORD_Y];
                        g_carParameters.Radars[radarIdx].Mounting.pos_xyz_in_m[COORD_Z] = RbObjectSensor->bs.Pos_B[COORD_Z];

                        nRadars++;
                    }
                }
            }

            g_carParameters.nbrOfRadars = nRadars;
        }
    }

    return 0;
}