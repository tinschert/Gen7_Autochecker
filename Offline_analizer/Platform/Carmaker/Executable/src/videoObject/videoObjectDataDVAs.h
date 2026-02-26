/*
 * FILE:            videoObjectDataDVAs.h
 * SW-COMPONENT:    videoObjectDataDVAs
 * DESCRIPTION:     Header file for the videoObjectDataDVAs component
 * COPYRIGHT:       © 2017 - 2024 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */


#ifndef VIDEO_OBJECT_DATA_DVAS_H_
#define VIDEO_OBJECT_DATA_DVAS_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "DataDict.h"
#include "Vehicle/Sensor_Object.h"
#include "common/commonDefinitions.h"

int RB_Video_IsActive();
int RB_Video_DeclQuants();

#ifdef __cplusplus
}
#endif

#endif /* VIDEO_OBJECT_DATA_DVAS_H_ */
