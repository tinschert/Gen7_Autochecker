/*
 * FILE:            carParametersDVAs.cpp
 * SW-COMPONENT:    carParametersDVAs
 * DESCRIPTION:     Source file for the carParametersDVAs component
 * COPYRIGHT:       © 2024 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#include <string>
#include "carParametersDVAs.h"
#include "common/commonDefinitions.h"
//#include "DataDict.h"

RbCarParameters g_carParameters;

int RB_Car_Param_DeclQuants()
{
    int i_Whl, i_Sensor;

    struct {
        std::string radiusBelt;
        std::string radiusRim;
        std::string width;
    } str_WheelInfo[MAX_NBR_OF_WHEELS];

    struct {
        std::string isActive;
        struct {
            std::string pos_xyz[3];
            std::string ori_xyz[3];
        } Mounting;
    } str_Radars[MAX_NBR_OF_RADARS];

    struct {
        std::string isActive;
        struct {
            std::string pos_xyz[3];
            std::string ori_xyz[3];
        } Mounting;
    } str_FVideo;
    
    std::string base_name = "RB.CarParam";

    // dimensions
    std::string wheelBase = base_name + ".wheelBase";
    std::string trackWidth = base_name + ".trackWidth";
    std::string overhangFront = base_name + ".overhangFront";
    std::string overhangRear = base_name + ".overhangRear";
    // mass
    std::string massTotal = base_name + ".massTotal";
    // wheel
    std::string nbrOfWheels = base_name + ".nbrOfWheels";
    //std::string wheelRadius = base_name + ".wheelRadius";
    // gear
    std::string gearBoxKind = base_name + ".gearBoxKind";
    std::string nbrOfFGears = base_name + ".nbrOfFGears";
    std::string nbrOfBGears = base_name + ".nbrOfBGears";
    // motion
    std::string velocityMax = base_name + ".velocityMax";
    std::string drivenDistance = base_name + ".drivenDistance";
    std::string nbrOfRadars = base_name + ".Radar.nbrOfRadars";

    DDefDouble(NULL, wheelBase.c_str(), "m", &g_carParameters.wheelBase,  DVA_None);
    DDefDouble(NULL, trackWidth.c_str(), "m", &g_carParameters.trackWidth,  DVA_None);
    DDefDouble(NULL, overhangFront.c_str(), "m", &g_carParameters.overhangFront,  DVA_None);
    DDefDouble(NULL, overhangRear.c_str(), "m", &g_carParameters.overhangRear,  DVA_None);
    DDefDouble(NULL, massTotal.c_str(), "kg", &g_carParameters.massTotal,  DVA_None);
    DDefInt(NULL, nbrOfWheels.c_str(), "-", &g_carParameters.nbrOfWheels,  DVA_None);
    //DDefDouble(NULL, wheelRadius.c_str(), "m", &g_carParameters.wheelRadius,  DVA_None);
    
    for(i_Whl=0;i_Whl<MAX_NBR_OF_WHEELS;i_Whl++)
    {
        str_WheelInfo[i_Whl].radiusBelt = base_name + ".Wheel" + gStrWheelPos[i_Whl] + ".radiusBelt";
        str_WheelInfo[i_Whl].radiusRim = base_name + ".Wheel" + gStrWheelPos[i_Whl] + ".radiusRim";
        str_WheelInfo[i_Whl].width = base_name + ".Wheel" + gStrWheelPos[i_Whl] + ".width";
        
        DDefDouble(NULL, str_WheelInfo[i_Whl].radiusBelt.c_str(), "m", &g_carParameters.Wheel[i_Whl].radiusBelt,  DVA_None);
        DDefDouble(NULL, str_WheelInfo[i_Whl].radiusRim.c_str(), "m", &g_carParameters.Wheel[i_Whl].radiusRim,  DVA_None);
        DDefDouble(NULL, str_WheelInfo[i_Whl].width.c_str(), "m", &g_carParameters.Wheel[i_Whl].width,  DVA_None);
    }
    
    DDefInt(NULL, gearBoxKind.c_str(), "-", &g_carParameters.gearBoxKind,  DVA_None);
    DDefInt(NULL, nbrOfFGears.c_str(), "-", &g_carParameters.nbrOfFGears,  DVA_None);
    DDefInt(NULL, nbrOfBGears.c_str(), "-", &g_carParameters.nbrOfBGears,  DVA_None);
    DDefDouble(NULL, velocityMax.c_str(), "m/s", &g_carParameters.velocityMax,  DVA_None);
    DDefDouble(NULL, drivenDistance.c_str(), "m", &g_carParameters.drivenDistance,  DVA_None);
    
    // Radar quantities

    DDefInt(NULL, nbrOfRadars.c_str(), "-", &g_carParameters.nbrOfRadars,  DVA_None);

    for(i_Sensor=0;i_Sensor<MAX_NBR_OF_RADARS;i_Sensor++)
    {
        // str_Radars[i_Sensor].isActive
        // str_Radars[i_Sensor].Mounting.ori_xyz[COORD_X] = base_name + ".Radar." + gStrRadars[i_Sensor] + ".oriRoll"; // x axis
        // str_Radars[i_Sensor].Mounting.ori_xyz[COORD_Y] = base_name + ".Radar." + gStrRadars[i_Sensor] + ".oriPitch"; // y axis
        str_Radars[i_Sensor].Mounting.ori_xyz[COORD_Z] = base_name + ".Radar." + gStrRadars[i_Sensor] + ".oriYaw"; // z axis
        str_Radars[i_Sensor].Mounting.pos_xyz[COORD_X] = base_name + ".Radar." + gStrRadars[i_Sensor] + ".d_x";
        str_Radars[i_Sensor].Mounting.pos_xyz[COORD_Y] = base_name + ".Radar." + gStrRadars[i_Sensor] + ".d_y";
        str_Radars[i_Sensor].Mounting.pos_xyz[COORD_Z] = base_name + ".Radar." + gStrRadars[i_Sensor] + ".d_z";

        //DDefInt(NULL, str_Radars[i_Sensor].isActive.c_str(), "", &g_carParameters.Radars[i_Sensor].isActive,  DVA_None);
        // DDefDouble(NULL, str_Radars[i_Sensor].Mounting.ori_xyz[COORD_X].c_str(), "rad", &g_carParameters.Radars[i_Sensor].Mounting.ori_xyz_in_rad[COORD_X],  DVA_None);
        // DDefDouble(NULL, str_Radars[i_Sensor].Mounting.ori_xyz[COORD_Y].c_str(), "rad", &g_carParameters.Radars[i_Sensor].Mounting.ori_xyz_in_rad[COORD_Y],  DVA_None);
        DDefDouble(NULL, str_Radars[i_Sensor].Mounting.ori_xyz[COORD_Z].c_str(), "rad", &g_carParameters.Radars[i_Sensor].Mounting.ori_xyz_in_rad[COORD_Z],  DVA_None);
        DDefDouble(NULL, str_Radars[i_Sensor].Mounting.pos_xyz[COORD_X].c_str(), "m", &g_carParameters.Radars[i_Sensor].Mounting.pos_xyz_in_m[COORD_X],  DVA_None);
        DDefDouble(NULL, str_Radars[i_Sensor].Mounting.pos_xyz[COORD_Y].c_str(), "m", &g_carParameters.Radars[i_Sensor].Mounting.pos_xyz_in_m[COORD_Y],  DVA_None);
        DDefDouble(NULL, str_Radars[i_Sensor].Mounting.pos_xyz[COORD_Z].c_str(), "m", &g_carParameters.Radars[i_Sensor].Mounting.pos_xyz_in_m[COORD_Z],  DVA_None);
    }

    // FVideo quantities

    //str_FVideo.isActive
    // str_FVideo.Mounting.ori_xyz[COORD_X] = base_name + ".Camera." + gStrFVideo + ".oriRoll";
    // str_FVideo.Mounting.ori_xyz[COORD_Y] = base_name + ".Camera." + gStrFVideo + ".oriPitch";
    str_FVideo.Mounting.ori_xyz[COORD_Z] = base_name + ".Camera." + gStrFVideo + ".oriYaw";
    str_FVideo.Mounting.pos_xyz[COORD_X] = base_name + ".Camera." + gStrFVideo + ".d_x";
    str_FVideo.Mounting.pos_xyz[COORD_Y] = base_name + ".Camera." + gStrFVideo + ".d_y";
    str_FVideo.Mounting.pos_xyz[COORD_Z] = base_name + ".Camera." + gStrFVideo + ".d_z";

    //DDefInt(NULL, str_FVideo.isActive.c_str(), "", &g_carParameters.FVideo.isActive,  DVA_None);
    // DDefDouble(NULL, str_FVideo.Mounting.ori_xyz[COORD_X].c_str(), "rad", &g_carParameters.FVideo.Mounting.ori_xyz_in_rad[COORD_X],  DVA_None);
    // DDefDouble(NULL, str_FVideo.Mounting.ori_xyz[COORD_Y].c_str(), "rad", &g_carParameters.FVideo.Mounting.ori_xyz_in_rad[COORD_Y],  DVA_None);
    DDefDouble(NULL, str_FVideo.Mounting.ori_xyz[COORD_Z].c_str(), "rad", &g_carParameters.FVideo.Mounting.ori_xyz_in_rad[COORD_Z],  DVA_None);
    DDefDouble(NULL, str_FVideo.Mounting.pos_xyz[COORD_X].c_str(), "m", &g_carParameters.FVideo.Mounting.pos_xyz_in_m[COORD_X],  DVA_None);
    DDefDouble(NULL, str_FVideo.Mounting.pos_xyz[COORD_Y].c_str(), "m", &g_carParameters.FVideo.Mounting.pos_xyz_in_m[COORD_Y],  DVA_None);
    DDefDouble(NULL, str_FVideo.Mounting.pos_xyz[COORD_Z].c_str(), "m", &g_carParameters.FVideo.Mounting.pos_xyz_in_m[COORD_Z],  DVA_None);

    return 0;
}
