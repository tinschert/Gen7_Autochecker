/*
 * FILE:            radarObjectDataDVAs.h
 * SW-COMPONENT:    radarObjectDataDVAs
 * DESCRIPTION:     Header file for the radarObjectDataDVAs component
 * COPYRIGHT:       © 2017 - 2024 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */


#ifndef RADAR_OBJECT_DATA_DVAS_H_
#define RADAR_OBJECT_DATA_DVAS_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "DataDict.h"
#include "Vehicle/Sensor_Object.h"
#include "Vehicle/Sensor_Radar.h"
#include "common/commonDefinitions.h"

int RB_RadarObj_IsActive(size_t sensor);
int RB_Radar_DeclQuants();

#ifdef __cplusplus
}
#endif

#endif /* OBJECT_DATA_DVAS_H_ */
