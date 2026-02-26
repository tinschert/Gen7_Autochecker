/*
 * FILE:            fillVideoObjectData.cpp
 * SW-COMPONENT:    fillTVideoObjectData
 * DESCRIPTION:     Source file for the fillTVideoObjectData component
 * COPYRIGHT:       © 2023 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#include <Config.h>
#include "fillVideoObjectData.h"
#include "videoObjectDataDVAs.h"
#include <common/objectData.h>
#include <string>
#include <array>
#include "SimCore.h"

extern tSensorData g_videoData;

extern std::string g_sensor_name_to_find;

int fillVideoObjectData()
{   
    if(RB_Video_IsActive() == INT_ST_ON)
    {
        if (SimCore.State != SCState_Simulate)
        {
            g_videoData.object_count = 0;
            return 0;
        }

        int sensorId = ObjectSensor_FindIndexForName(g_sensor_name_to_find.c_str());

    int object_count = 0;
    for (int objNr = 0; objNr < ObjectSensor[sensorId].nObsvObjects && object_count < Config::Radar::MAX_RADAR_OBJECTS; objNr++)
    {
        // fill the data
        const tObjectSensorObj *sensorObject = ObjectSensor_GetObject(sensorId, objNr);

        if (sensorObject != NULL && sensorObject->dtct == 1)
        {
            const tTrafficObj *trafficObject = Traffic_GetByObjId(sensorObject->ObjId);

            if (trafficObject == NULL)
            {
                continue;
            }

            auto& videoObjectData = g_videoData.objects[object_count];

            videoObjectData.dxN = sensorObject->RefPnt.ds[0];
            videoObjectData.dyN = sensorObject->RefPnt.ds[1];
            videoObjectData.dzN = sensorObject->RefPnt.ds[2];

            videoObjectData.vxN = sensorObject->RefPnt.dv[0];
            videoObjectData.vyN = sensorObject->RefPnt.dv[1];

            // Carmaker does not provide acceleration for ref point (and near point), set values to zero
            videoObjectData.axN = 0.0;
            videoObjectData.ayN = 0.0;

            videoObjectData.dLengthN = sensorObject->l;
            videoObjectData.dWidthN = sensorObject->w;

            switch (trafficObject->Cfg.RCSClass)
            {
            case RCS_Unknown:
                videoObjectData.classification = 0;
                break;
            case RCS_Pedestrian:
                videoObjectData.classification = 1;
                break;
            case RCS_Bicycle:
                videoObjectData.classification = 2;
                break;
            case RCS_Motorcycle:
                videoObjectData.classification = 3;
                break;
            case RCS_Car:
                videoObjectData.classification = 4;
                break;
            case RCS_Truck:
                videoObjectData.classification = 5;
                break;
            default:
                videoObjectData.classification = 0;
                break;
            }

            if(trafficObject->Cfg.MotionKind == MotionKind_SemiTrailer)
            {
                videoObjectData.classification = 6;
            }

            videoObjectData.alpPiYawAngleN = sensorObject->RefPnt.r_zyx[2];

            videoObjectData.objId = sensorObject->ObjId;

            object_count++;
        }
    }

    g_videoData.object_count = object_count;
    }

    return 0;
}