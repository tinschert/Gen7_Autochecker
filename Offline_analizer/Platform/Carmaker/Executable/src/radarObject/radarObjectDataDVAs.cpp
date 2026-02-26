/*
 * FILE:            radarObjectDataDVAs.cpp
 * SW-COMPONENT:    radarObjectDataDVAs
 * DESCRIPTION:     Source file for the radarObjectDataDVAs component
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
#include <string>
#include <array>
#include "radarObjectDataDVAs.h"

tRbRadarData g_radarData;

std::array<std::string, (Config::Radar::TOTAL_RADAR_COUNT*2)> g_radarSensorNames = {
    "FC",
    "FL",
    "FR",
    "RR",
    "RL",
    "FC_P",
    "FL_P",
    "FR_P",
    "RR_P",
    "RL_P"
};

std::array<std::string, (Config::Radar::TOTAL_RADAR_COUNT*2)> g_radarRCSSensorNames = {
    "FC_RCS",
    "FL_RCS",
    "FR_RCS",
    "RR_RCS",
    "RL_RCS",
    "FC_RCS_P",
    "FL_RCS_P",
    "FR_RCS_P",
    "RR_RCS_P",
    "RL_RCS_P"
};

extern int ObjectSensorCount;
extern int RadarCount;

int RB_RadarObj_IsActive(size_t sensor)
{
    return (
        (ObjectSensor_FindIndexForName(g_radarSensorNames[sensor].c_str()) != -1) &&
        (RadarSensor_FindIndexForName(g_radarRCSSensorNames[sensor].c_str()) != -1)
        ) ? (INT_ST_ON) : (INT_ST_OFF);
}

int RB_Radar_DeclQuants()
{
    std::string uaq_base_name = "RB.Radar.";   
	
	for(size_t radar_sensor_index = 0; radar_sensor_index < Config::Radar::TOTAL_RADAR_COUNT; radar_sensor_index++)
	{
#if defined(RB_INT_VARIANT_HANDLING_ON)
        if(RB_RadarObj_IsActive(radar_sensor_index) == INT_ST_ON)
#endif
        {
            std::string uaq_sensor_name = g_radarSensorNames[radar_sensor_index];

            std::string uaq_name_objectCount = uaq_base_name + uaq_sensor_name + ".object_count";
            DDefUInt(NULL, uaq_name_objectCount.c_str(), "", &g_radarData.radarSensorData[radar_sensor_index].object_count, DVA_IO_Out);
            
            std::string uaq_name_radar_type_req = uaq_base_name + uaq_sensor_name + ".radar_type_req";
            DDefUInt(NULL, uaq_name_radar_type_req.c_str(), "Driv/Park", &g_radarData.radar_type_req[radar_sensor_index], DVA_IO_Out);            

#if !defined (UDP_INTERFACE_ON)
            for(size_t object_index = 0; object_index < Config::Radar::MAX_RADAR_OBJECTS; object_index++)		
            {			
                std::string uaq_name_dxN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".dxN";
                std::string uaq_name_dyN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".dyN";
                std::string uaq_name_dzN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".dzN";
                std::string uaq_name_vxN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".vxN";
                std::string uaq_name_vyN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".vyN";
                std::string uaq_name_axN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".axN";
                std::string uaq_name_ayN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".ayN";
                std::string uaq_name_dLengthN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".dLengthN";
                std::string uaq_name_dWidthN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".dWidthN";
                std::string uaq_name_alpPiYawAngleN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".alpPiYawAngleN";
                std::string uaq_name_rcsN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".rcsN";
                std::string uaq_name_snrN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".snrN";
                std::string uaq_name_signalStrengthN = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".signalStrengthN";
                std::string uaq_name_classification = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".classification";
                std::string uaq_name_inLineOfSight = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".inLineOfSight";
                std::string uaq_name_objId = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".objId";
                std::string uaq_name_radarType = uaq_base_name + uaq_sensor_name + ".object" + std::to_string(object_index) + ".radarType";
                
                DDefDouble(NULL, uaq_name_dxN.c_str(), "m", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].dxN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_dyN.c_str(), "m", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].dyN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_dzN.c_str(), "m", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].dzN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_vxN.c_str(), "m/s", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].vxN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_vyN.c_str(), "m/s", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].vyN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_axN.c_str(), "m/s^2", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].axN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_ayN.c_str(), "m/s^2", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].ayN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_dLengthN.c_str(), "m", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].dLengthN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_dWidthN.c_str(), "m", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].dWidthN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_alpPiYawAngleN.c_str(), "rad", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].alpPiYawAngleN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_rcsN.c_str(), "dB", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].rcsN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_snrN.c_str(), "dB", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].snrN, DVA_IO_Out);
                DDefDouble(NULL, uaq_name_signalStrengthN.c_str(), "dB", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].signalStrengthN, DVA_IO_Out);
                DDefUChar(NULL, uaq_name_classification.c_str(), "", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].classification, DVA_IO_Out);       
                DDefInt(NULL, uaq_name_inLineOfSight.c_str(), "", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].inLineOfSight, DVA_IO_Out);             
                DDefInt(NULL, uaq_name_objId.c_str(), "", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].objId, DVA_IO_Out);            
                DDefInt(NULL, uaq_name_radarType.c_str(), "Driv/Park", &g_radarData.radarSensorData[radar_sensor_index].objects[object_index].radar_type, DVA_None);            
            }
#endif
        }
    }
	return 0;
}
