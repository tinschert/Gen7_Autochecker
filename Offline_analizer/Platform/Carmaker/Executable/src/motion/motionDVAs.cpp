/*
 * FILE:            motionDVAs.cpp
 * SW-COMPONENT:    motionDVAs
 * DESCRIPTION:     Source file for the motionDVAs component
 * COPYRIGHT:       © 2024 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#include <string>
#include "motionDVAs.h"
#include "common/commonDefinitions.h"

RbInertialSensors g_inertialSensors;
RbRoadAttributes g_road;

int RB_Motion_DeclQuants()
{
    int i_Sensor;
    double delta_in_m{0.0};

    struct {
        std::string isActive;
        std::string delta_pos_xyz[3];
    } str_SuspSensors[MAX_NBR_OF_SUSPENSION_SENSORS];

    struct {
        std::string steepness_pitch;
        std::string steepness_roll;
    } str_RoadAttr;
    
    std::string base_name = "RB.Motion.";

    str_RoadAttr.steepness_roll = base_name + "roadSteepness_roll";
    str_RoadAttr.steepness_pitch = base_name + "roadSteepness_pitch";

    DDefDouble(NULL, str_RoadAttr.steepness_roll.c_str(), "rad", &g_road.steepness_roll_in_rad,  DVA_None);
    DDefDouble(NULL, str_RoadAttr.steepness_pitch.c_str(), "rad", &g_road.steepness_pitch_in_rad,  DVA_None);

    // Suspension travel (inertial sensor)

    for(i_Sensor=0;i_Sensor<MAX_NBR_OF_SUSPENSION_SENSORS;i_Sensor++)
    {
        // str_SuspSensors[i_Sensor].isActive
        str_SuspSensors[i_Sensor].delta_pos_xyz[COORD_Z] = base_name + "Inertial." + gStrSuspSensors[i_Sensor] + ".delta_z";

        //DDefInt(NULL, str_SuspSensors.[i_Sensor].isActive.c_str(), "", &g_inertialSensors.Susp_Sensors[i_Sensor].isActive,  DVA_None);
        DDefDouble(NULL, str_SuspSensors[i_Sensor].delta_pos_xyz[COORD_Z].c_str(), "m", &g_inertialSensors.Susp_Sensors[i_Sensor].delta_pos_xyz_in_m[COORD_Z],  DVA_None);
    }

    return 0;
}
