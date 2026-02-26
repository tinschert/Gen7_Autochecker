/*
 * FILE:            carParametersDVAs.h
 * SW-COMPONENT:    carParametersDVAs
 * DESCRIPTION:     Header file for the carParametersDVAs component
 * COPYRIGHT:       © 2024 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */


#ifndef CAR_PARAMETERS_DVAS_H_
#define CAR_PARAMETERS_DVAS_H_

extern "C" {
    #include "DataDict.h"
}

#include <array>
#include <string>

static const int MAX_NBR_OF_RADARS = 5;
static const int MAX_NBR_OF_WHEELS = 4;
typedef enum {
    R_FC = 0,
    R_FL,
    R_FR,
    R_RL,
    R_RR
} eRadarType;

static const char gStrRadars[MAX_NBR_OF_RADARS][3] = {"FC","FL","FR","RL","RR"};
static const char gStrFVideo[3] = "FV";
static const char gStrWheelPos[MAX_NBR_OF_WHEELS][3] = {"FL","FR","RL","RR"};

struct RbCarParameters
{ 
    // dimensions
    double  wheelBase{0.0};
    double  trackWidth{0.0};
    double  overhangFront{0.0};
    double  overhangRear{0.0};
    // mass
    double	massTotal{0.0};
    // wheel
    int		nbrOfWheels{0};
    double	wheelRadius{0.0};
    struct {
        double	radiusBelt{0.0};
        double	radiusRim{0.0};
        double	width{0.0};
    } Wheel[MAX_NBR_OF_WHEELS];
    // gear
    int     gearBoxKind{0};
    int		nbrOfFGears{0};
    int		nbrOfBGears{0};
    // motion
    double	velocityMax{0.0};
    double	drivenDistance{0.0};

    int nbrOfRadars{0};
    struct {
        int isActive{0};
        char sName[32];
        struct {
            double pos_xyz_in_m[3];
            double ori_xyz_in_rad[3];
        } Mounting;
    } Radars[MAX_NBR_OF_RADARS];

    struct {
        int isActive{0};
        char sName[32];
        struct {
            double pos_xyz_in_m[3];
            double ori_xyz_in_rad[3];
        } Mounting;
    } FVideo;
};

int RB_Car_Param_DeclQuants();

#endif /* CAR_PARAMETERS_DVAS_H_ */