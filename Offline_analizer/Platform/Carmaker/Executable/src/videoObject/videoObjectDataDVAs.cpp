/*
 * FILE:            videoObjectDataDVAs.cpp
 * SW-COMPONENT:    videoObjectDataDVAs
 * DESCRIPTION:     Source file for the videoObjectDataDVAs component
 * COPYRIGHT:       © 2023 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#include <Config.h>
#include <common/objectData.h>
#include <array>
#include <string>
#include "videoObjectDataDVAs.h"

std::string g_sensor_name_to_find = "FV";

tSensorData g_videoData;

int RB_Video_IsActive()
{
    return (ObjectSensor_FindIndexForName(g_sensor_name_to_find.c_str()) != -1) ? (INT_ST_ON) : (INT_ST_OFF);
}

int RB_Video_DeclQuants()
{
#if defined(RB_INT_VARIANT_HANDLING_ON)
    if(RB_Video_IsActive() == INT_ST_ON)
#endif
    {
        std::string uaq_base_name = "RB.Video.FV";

        std::string uaq_name_objectCount = uaq_base_name + ".object_count";
        DDefUInt(NULL, uaq_name_objectCount.c_str(), "", &g_videoData.object_count, DVA_None);

        for (size_t object_index = 0; object_index < Config::Radar::MAX_RADAR_OBJECTS; object_index++)
        {
            std::string uaq_name_dxN = uaq_base_name + ".object" + std::to_string(object_index) + ".dxN";
            std::string uaq_name_dyN = uaq_base_name + ".object" + std::to_string(object_index) + ".dyN";
            std::string uaq_name_dzN = uaq_base_name + ".object" + std::to_string(object_index) + ".dzN";
            std::string uaq_name_vxN = uaq_base_name + ".object" + std::to_string(object_index) + ".vxN";
            std::string uaq_name_vyN = uaq_base_name + ".object" + std::to_string(object_index) + ".vyN";
            std::string uaq_name_axN = uaq_base_name + ".object" + std::to_string(object_index) + ".axN";
            std::string uaq_name_ayN = uaq_base_name + ".object" + std::to_string(object_index) + ".ayN";
            std::string uaq_name_dLengthN = uaq_base_name + ".object" + std::to_string(object_index) + ".dLengthN";
            std::string uaq_name_dWidthN = uaq_base_name + ".object" + std::to_string(object_index) + ".dWidthN";
            std::string uaq_name_alpPiYawAngleN = uaq_base_name + ".object" + std::to_string(object_index) + ".alpPiYawAngleN";
            std::string uaq_name_classification = uaq_base_name + ".object" + std::to_string(object_index) + ".classification";
            std::string uaq_name_objId = uaq_base_name + ".object" + std::to_string(object_index) + ".objId";

            DDefDouble(NULL, uaq_name_dxN.c_str(), "m", &g_videoData.objects[object_index].dxN, DVA_None);
            DDefDouble(NULL, uaq_name_dyN.c_str(), "m", &g_videoData.objects[object_index].dyN, DVA_None);
            DDefDouble(NULL, uaq_name_dzN.c_str(), "m", &g_videoData.objects[object_index].dzN, DVA_None);
            DDefDouble(NULL, uaq_name_vxN.c_str(), "m/s", &g_videoData.objects[object_index].vxN, DVA_None);
            DDefDouble(NULL, uaq_name_vyN.c_str(), "m/s", &g_videoData.objects[object_index].vyN, DVA_None);
            DDefDouble(NULL, uaq_name_axN.c_str(), "m/s^2", &g_videoData.objects[object_index].axN, DVA_None);
            DDefDouble(NULL, uaq_name_ayN.c_str(), "m/s^2", &g_videoData.objects[object_index].ayN, DVA_None);
            DDefDouble(NULL, uaq_name_dLengthN.c_str(), "m", &g_videoData.objects[object_index].dLengthN, DVA_None);
            DDefDouble(NULL, uaq_name_dWidthN.c_str(), "m", &g_videoData.objects[object_index].dWidthN, DVA_None);
            DDefDouble(NULL, uaq_name_alpPiYawAngleN.c_str(), "rad", &g_videoData.objects[object_index].alpPiYawAngleN, DVA_None);
            DDefUChar(NULL, uaq_name_classification.c_str(), "", &g_videoData.objects[object_index].classification, DVA_None);
            DDefInt(NULL, uaq_name_objId.c_str(), "", &g_videoData.objects[object_index].objId, DVA_None);
        }
    }

    return 0;
}