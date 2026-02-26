/*
 * FILE:            motionDVAs.h
 * SW-COMPONENT:    motionDVAs
 * DESCRIPTION:     Header file for the motionDVAs component
 * COPYRIGHT:       © 2024 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */


#ifndef MOTION_DVAS_H_
#define MOTION_DVAS_H_

extern "C" {
    #include "DataDict.h"
}

#include <array>
#include <string>

static const int MAX_NBR_OF_SUSPENSION_SENSORS = 4;
typedef enum {
    SUSP_FL = 0,
    SUSP_FR,
    SUSP_RL,
    SUSP_RR
} eInSensorType;

static const char gStrSuspSensors[MAX_NBR_OF_SUSPENSION_SENSORS][8] = {"Susp_FL","Susp_FR","Susp_RL","Susp_RR"};

struct RbRoadAttributes
{ 
    double steepness_roll_in_rad;
    double steepness_pitch_in_rad;
};

struct RbInertialSensors
{ 
    struct {
        int isActive{0};
        char sName[32];
        double mount_pos_xyz_in_m[3]; // Fr1
        double actl_pos_xyz_in_m[3]; // Fr0
        double delta_pos_xyz_in_m[3]; // Fr1
    } Susp_Sensors[MAX_NBR_OF_SUSPENSION_SENSORS];
};

int RB_Motion_DeclQuants();

#endif /* MOTION_DVAS_H_ */