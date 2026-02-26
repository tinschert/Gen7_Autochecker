

/*
 * FILE:            fillInertialSensors.h
 * SW-COMPONENT:    fillInertialSensors
 * DESCRIPTION:     Header file for the fillInertialSensors component
 * COPYRIGHT:       © 2024 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#ifndef COMMON_DEFINITIONS_H_
#define COMMON_DEFINITIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

typedef enum {
    COORD_X = 0,
    COORD_Y,
    COORD_Z
} eCoordinates;

typedef enum {
    WHL_FL,
    WHL_FR,
    WHL_RL,
    WHL_RR
} eWheels;

typedef enum {
    INT_ST_OFF = 0,
    INT_ST_ON = 1
} eInterfaceStatus;

#ifdef __cplusplus
}
#endif

#endif /* COMMON_DEFINITIONS_H_ */