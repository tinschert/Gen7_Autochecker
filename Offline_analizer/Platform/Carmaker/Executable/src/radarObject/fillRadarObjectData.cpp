#include <Config.h>
#include "fillRadarObjectData.h"
#include "radarObjectDataDVAs.h"
#include "common/objectData.h"

#include <string>
#include <array>
#include <map>

#include "Vehicle/Sensor_Object.h"
#include "Vehicle/Sensor_Radar.h"
#include "SimCore.h"

extern tRbRadarData g_radarData;
extern std::array<std::string, (Config::Radar::TOTAL_RADAR_COUNT*2)> g_radarSensorNames;
extern std::array<std::string, (Config::Radar::TOTAL_RADAR_COUNT*2)> g_radarRCSSensorNames;


/// @brief Create a map of radar objects from a CarMaker tRadarSensor instance
/// @param radarSensorID The ID of a CarMaker Radar Sensor instance to create the map from
/// @return A map containing carmaker object traffic ID keys mapped to carmaker tRadObject pointers.
///         Will return an empty map if the Radar Sensor is not found / valid
/// @note This method must return a constant map to prevent key lookups using [] notation from returning
///       empty / default values from the map if the key is not present within the map
///       see: https://en.cppreference.com/w/cpp/container/map/operator_at return values
const std::map<int, const tRadObject*> createRadarObjectMap(const int radarSensorID)
{
    std::map<int, const tRadObject*> radarObjectMap;

    if (radarSensorID == -1)
    {
        return radarObjectMap;
    }

    const tRadarSensor* radarSensor = RadarSensor_GetByIndex(radarSensorID);
    if (nullptr == radarSensor)
    {
        return radarObjectMap;
    }

    // Insert all radar objects into the map
    for (int i = 0; i < radarSensor->GlobalInf->nObj; i++)
    {
        const int objID = radarSensor->ObjList[i].ObjId;

        const int objTrafficID = Traffic_ObjId2TrfId(objID);
        if (objTrafficID == -1)
        {
            continue;
        }

        // radarSensor->RadObj is indexed via the TrafficID of an object
        const tRadObject* currRadObj = &radarSensor->RadObj[objTrafficID];
        if (nullptr == currRadObj)
        {
            continue;
        }

        if (currRadObj->dtct == true)
        {
            radarObjectMap.insert(std::pair<int, const tRadObject*>(objID, currRadObj));
        }
    }  

    return radarObjectMap;
}


/// @brief Gets a tRadObject from a radar object map or nullptr if the object at objectID does not exist
/// @param map A reference to a map containing traffic object IDs mapped to radarObjects
/// @param objectID The traffic object ID to get from the radar object map
/// @return A pointer to the tRadObject matching objectID or a nullptr if not object found
const tRadObject* getRadarObjectFromMap(const std::map<int, const tRadObject*>& map, int objectID)
{
    auto radarObjectMapResult = map.find(objectID);
    if (radarObjectMapResult != map.end())
    {
        return radarObjectMapResult->second;
    }
    return nullptr;
}


/// @brief Fill a tObject with data from a detected tObjectSensorObj from a CarMaker object sensor
/// @param rbObject A reference to a tObject to fill with object data
/// @param radarObject A point to a carmaker object to use for filling the tObject
void fillRBObjectFromObjectSensorData(tObject& rbObject, const tObjectSensorObj* sensorObject)
{
    if (nullptr == sensorObject)
    {
        return;
    }

    const tTrafficObj* trafficObject = Traffic_GetByObjId(sensorObject->ObjId);	
    if (nullptr == trafficObject)
    {
        return;
    }

    rbObject.dxN = sensorObject->RefPnt.ds[0];
    rbObject.dyN = sensorObject->RefPnt.ds[1];
    rbObject.dzN = sensorObject->RefPnt.ds[2];

    rbObject.vxN = sensorObject->RefPnt.dv[0];
    rbObject.vyN = sensorObject->RefPnt.dv[1];

    // Carmaker does not provide acceleration for ref point (and near point), set values to zero
    rbObject.axN = 0.0;
    rbObject.ayN = 0.0;

    rbObject.dLengthN = sensorObject->l;
    rbObject.dWidthN = sensorObject->w;
    
    rbObject.alpPiYawAngleN = sensorObject->RefPnt.r_zyx[2];

    
    switch (trafficObject->Cfg.RCSClass) 
    {
        case RCS_Unknown:
            rbObject.classification = 0;
            break;
        case RCS_Pedestrian:
            rbObject.classification = 1;
            break;
        case RCS_Bicycle:
            rbObject.classification = 2;
            break;
        case RCS_Motorcycle:
            rbObject.classification = 3;
            break;
        case RCS_Car:
            rbObject.classification = 4;
            break;
        case RCS_Truck:
            rbObject.classification = 5;
            break;
        default:
            rbObject.classification = 0;
            break;
    }

    if(trafficObject->Cfg.MotionKind == MotionKind_SemiTrailer)
    {
        rbObject.classification = 6;
    }
}


/// @brief Fill a tObject with data from a detected tRadObject from a CarMaker radar sensor
/// @param rbObject A reference to a tObject to fill with radar object data
/// @param radarObjectMap A map containing carmaker object traffic ID keys mapped to carmaker tRadObject pointers
/// @param objectID The objectID of the radar object to add
/// @note This method is supplemental to fillRBObjectFromObjectSensorData and in it's current state will not
///       fully define an object
void fillRBObjectFromRadarSensorData(
    tObject& rbObject, const std::map<int, const tRadObject*>& radarObjectMap, int objectID)
{
    const tRadObject* radarObject = getRadarObjectFromMap(radarObjectMap, objectID);

    if (radarObject == nullptr)
    {
        rbObject.inLineOfSight = 0;
        rbObject.rcsN = 0;
        rbObject.snrN = 0;
        rbObject.signalStrengthN = 0;
    } 
    else 
    {
        rbObject.inLineOfSight = 1;
        rbObject.rcsN = radarObject->OutQuants.RCS;
        rbObject.snrN = radarObject->OutQuants.SNR;
        rbObject.signalStrengthN = radarObject->OutQuants.SignalStrength;
    }
}


int fillRadarObjectData()
{
    unsigned int sensor_idx = 0;
    for(unsigned int i = 0; i < Config::Radar::TOTAL_RADAR_COUNT; i++)
	{
        sensor_idx = i;
        if(g_radarData.radar_type_req[i] == RT_PARKING) // 1 - Parking; otherwise Driving
        {
            sensor_idx += Config::Radar::TOTAL_RADAR_COUNT;
        }

        if(RB_RadarObj_IsActive(sensor_idx) == INT_ST_ON)
        {
            if(SimCore.State != SCState_Simulate)
            {
                g_radarData.radarSensorData[i].object_count = 0;
                continue;
            }
            
            // Get the Sensor IDs
            int sensorObjectId = ObjectSensor_FindIndexForName(g_radarSensorNames[sensor_idx].c_str());
            int sensorRadarID = RadarSensor_FindIndexForName(g_radarRCSSensorNames[sensor_idx].c_str());

            // Get a pointer to the ObjectSensor
            const tObjectSensor* objectSensorPtr = ObjectSensor_GetByIndex(sensorObjectId);
            if (nullptr == objectSensorPtr)
            {
                continue;
            }

            // Get the mounting positions of the radar [Relative to Body Frame - Fr1]
            tSensorData& localObjectSensorData = g_radarData.radarSensorData[i];
            localObjectSensorData.mountPosX = objectSensorPtr->bs.Pos_B[0];
            localObjectSensorData.mountPosY = objectSensorPtr->bs.Pos_B[1];
            localObjectSensorData.mountPosZ = objectSensorPtr->bs.Pos_B[2];

            // Note: radarObjectMap is a map containing a tRadObjects ID as a key and a constant point
            // to the tRadObject as its value. This map is updated each cycle to contain a mapping to all 
            // radar objects that were detected by the radar sensor (sensorRadar)
            const std::map<int, const tRadObject*> radarObjectMap = createRadarObjectMap(sensorRadarID);

            int object_count = 0;
            for(int objNr = 0; objNr < ObjectSensor[sensorObjectId].nObsvObjects && object_count < Config::Radar::MAX_RADAR_OBJECTS; objNr++)
            {

                // Read the data from the object sensor
                const tObjectSensorObj* sensorObject = ObjectSensor_GetObjectByObjId(sensorObjectId, ObjectSensor[sensorObjectId].ObsvObjects[objNr]);

                if (sensorObject != NULL && sensorObject->dtct == 1) 
                {
                    tObject& radarObjectData = g_radarData.radarSensorData[i].objects[object_count];

                    radarObjectData.objId = sensorObject->ObjId;
                    radarObjectData.radar_type = __max(RT_DRIVING, __min(RT_PARKING, g_radarData.radar_type_req[i]));

                    fillRBObjectFromObjectSensorData(radarObjectData, sensorObject);

                    // Add the radar object data to the tObject if the radar sensor exists
                    if (sensorRadarID != -1)
                    {
                        fillRBObjectFromRadarSensorData(radarObjectData, radarObjectMap, sensorObject->ObjId);
                    }
                    
                    object_count++;
                }
            }

            // Reset all unused object indexes to default state
            for (int objNr = object_count; objNr < Config::Radar::MAX_RADAR_OBJECTS; objNr++)
            {
                g_radarData.radarSensorData[i].objects[objNr] = tObject();
                g_radarData.radarSensorData[i].objects[objNr].radar_type = __max(RT_DRIVING, __min(RT_PARKING, g_radarData.radar_type_req[i]));
            }

            g_radarData.radarSensorData[i].object_count = object_count;
        }
    }

    return 0;
}