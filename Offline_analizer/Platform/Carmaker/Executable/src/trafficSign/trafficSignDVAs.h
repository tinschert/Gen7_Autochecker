/*
 * FILE:            trafficSignDVAs.h
 * SW-COMPONENT:    trafficSignDVAs
 * DESCRIPTION:     Header file for the trafficSignDVAs component
 * COPYRIGHT:       © 2023 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */


#ifndef TRAFFIC_SIGN_DVAS_H_
#define TRAFFIC_SIGN_DVAS_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "DataDict.h"
#include "Vehicle/Sensor_Tsign.h"
#include "common/commonDefinitions.h"


constexpr unsigned int MAX_NUMBER_OF_TRAFFIC_SIGN_SENSORS = 1;
constexpr unsigned int MAX_NUMBER_OF_TRAFFIC_SIGNS = 5;

int RB_TrafficSign_IsActive(int sensor);
int RB_TrafficSign_DeclQuants();

#ifdef __cplusplus
}
#endif

#endif /* TRAFFIC_SIGN_DVAS_H_ */