/*----------------------------------------------------------------------------
|
| File Name: capldll.cpp
|
|            Example of a capl DLL implementation module and using CAPLLbacks.
|-----------------------------------------------------------------------------
|               A U T H O R   I D E N T I T Y
|-----------------------------------------------------------------------------
|   Author             Initials
|   ------             --------
|   Thomas  Riegraf    Ri              Vector Informatik GmbH
|   Hans    Quecke     Qu              Vector Informatik GmbH
|   Stefan  Albus      As              Vector Informatik GmbH
|-----------------------------------------------------------------------------
|               R E V I S I O N   H I S T O R Y
|-----------------------------------------------------------------------------
| Date         Ver  Author  Description
| ----------   ---  ------  --------------------------------------------------
| 2003-10-07   1.0  As      Created
| 2007-03-26   1.1  Ej      Export of the DLL function table as variable
|                           Use of CAPL_DLL_INFO3
|                           Support of long name CAPL function calls
| 2020-01-23   1.2  As      Support for GCC and Clang compiler on Linux
|                           Support for MINGW-64 compiler on Windows
|-----------------------------------------------------------------------------
|               C O P Y R I G H T
|-----------------------------------------------------------------------------
| Copyright (c) 1994 - 2003 by Vector Informatik GmbH.  All rights reserved.
 ----------------------------------------------------------------------------*/

#define USECDLL_FEATURE
#define _BUILDNODELAYERDLL

#include "../Includes/cdll.h"
#include "../Includes/VIA.h"
#include "../Includes/VIA_CDLL.h"

#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <map>
#include <iostream>
#include <fstream>

#if defined(_WIN64) || defined(__linux__)
#define X64
#endif

#include "radarSensormodel.h"

class CaplInstanceData;
typedef std::map<uint32_t, CaplInstanceData *> VCaplMap;
typedef std::map<uint32_t, VIACapl *> VServiceMap;

// ============================================================================
// global variables
// ============================================================================

static uint32_t data = 0;
static char dlldata[100];

char gModuleName[_MAX_FNAME]; // filename of this DLL
HINSTANCE gModuleHandle;      // windows instance handle of this DLL

VCaplMap gCaplMap;
VServiceMap gServiceMap;

// ============================================================================
// CaplInstanceData
//
// Data local for a single CAPL Block.
//
// A CAPL-DLL can be used by more than one CAPL-Block, so every piece of
// information thats like a global variable in CAPL, must now be wrapped into
// an instance of an object.
// ============================================================================
class CaplInstanceData
{
public:
    CaplInstanceData(VIACapl *capl);

    void GetCallbackFunctions();
    void ReleaseCallbackFunctions();

    RBStarModel::Radar_sensormodel sensormodel_;
    std::vector<RBStarModel::SimulationObjectState> star_model_object_list_;
    RBStarModel::MODEL_LOCATION_LIST_ST locations_;
    std::string path_to_database_;

    int max_nr_of_loc = 10;

    //Ford Specific
    byte byteArray_loc_FC[12500];
    byte byteArray_loc_FL[12500];
    byte byteArray_loc_FR[12500];
    byte byteArray_loc_RL[12500];
    byte byteArray_loc_RR[12500];
    int total_nr_of_loc_FC;
    int total_nr_of_loc_FL;
    int total_nr_of_loc_FR;
    int total_nr_of_loc_RL;
    int total_nr_of_loc_RR;
    
    
private:
    VIACapl *mCapl;
};

CaplInstanceData::CaplInstanceData(VIACapl *capl)
    // This function will initialize the CAPL callback function
    // with the NLL Pointer
    : mCapl(capl),
      sensormodel_(),
      star_model_object_list_(),
      locations_(),
      path_to_database_("")
{
}

void CaplInstanceData::GetCallbackFunctions()
{
}

void CaplInstanceData::ReleaseCallbackFunctions()
{
}

CaplInstanceData *GetCaplInstanceData(uint32_t handle)
{
    VCaplMap::iterator lSearchResult(gCaplMap.find(handle));
    if (gCaplMap.end() == lSearchResult)
    {
        return nullptr;
    }
    else
    {
        return lSearchResult->second;
    }
}

// ============================================================================
// FORD ONLY
// Including of the Byte Array parsing strategy
// Needs to be included after the definition of the Caapl Instance Data definition
// ============================================================================

#include "../Includes/DataHandling.h"

// ============================================================================
// CaplInstanceData
//
// Data local for a single CAPL Block.
//
// A CAPL-DLL can be used by more than one CAPL-Block, so every piece of
// information thats like a global variable in CAPL, must now be wrapped into
// an instance of an object.
// ============================================================================

void CAPLEXPORT CAPLPASCAL appInit(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (nullptr == instance)
    {
        VServiceMap::iterator lSearchService(gServiceMap.find(handle));
        if (gServiceMap.end() != lSearchService)
        {
            VIACapl *service = lSearchService->second;
            try
            {
                instance = new CaplInstanceData(service);
            }
            catch (std::bad_alloc &)
            {
                return; // proceed without change
            }
            instance->GetCallbackFunctions();
            gCaplMap[handle] = instance;
        }
    }
}

void CAPLEXPORT CAPLPASCAL appEnd(uint32_t handle)
{
    CaplInstanceData *inst = GetCaplInstanceData(handle);
    if (inst == nullptr)
    {
        return;
    }
    inst->ReleaseCallbackFunctions();

    delete inst;
    inst = nullptr;
    gCaplMap.erase(handle);
}

// ============================================================================
// VIARegisterCDLL
// ============================================================================
VIACLIENT(void)
VIARegisterCDLL(VIACapl *service)
{
    uint32_t handle;
    VIAResult result;

    if (service == nullptr)
    {
        return;
    }

    result = service->GetCaplHandle(&handle);
    if (result != kVIA_OK)
    {
        return;
    }

    // appInit (internal) resp. "DllInit" (CAPL code) has to follow
    gServiceMap[handle] = service;
}

void ClearAll()
{
    // destroy objects created by this DLL
    // may result from forgotten DllEnd calls
    VCaplMap::iterator lIter = gCaplMap.begin();
    const int32_t cNumberOfEntries = (int32_t)gCaplMap.size();
    int32_t i = 0;
    while (lIter != gCaplMap.end() && i < cNumberOfEntries)
    {
        appEnd((*lIter).first);
        lIter = gCaplMap.begin(); // first element should have vanished
        i++;                      // assure that no more erase trials take place than the original size of the map
    }

    // just for clarity (would be done automatically)
    gCaplMap.clear();
    gServiceMap.clear();
}

long CAPLEXPORT CAPLPASCAL appSetDatabasePath(uint32_t handle, char dataBlock[])
{
    CaplInstanceData *inst = GetCaplInstanceData(handle);
    if (inst == NULL)
    {
        return -1;
    }
    std::string database_path{dataBlock};
    inst->path_to_database_ = database_path;
    if(!std::ifstream(inst->path_to_database_)) return 2;
    return 0;
}

long CAPLEXPORT CAPLPASCAL appSetInputValues(uint32_t handle, int32_t id, double x, double y, double z, double vx, double vy, double ax, double ay, double heading, double length, double width, double height, int32_t object_type)
{
    CaplInstanceData *inst = GetCaplInstanceData(handle);
    if (inst == NULL)
    {
        return -1;
    }

    RBStarModel::SimulationObjectState star_model_object{};

    /// object dx and dy are cartesian and relative to ego vehicle! dx positive
    /// -> right ; dy positive -> front/forward
    star_model_object.id = id;
    star_model_object.x = static_cast<vfc::float32_t>(-y);
    star_model_object.y = static_cast<vfc::float32_t>(x);
    star_model_object.z = static_cast<vfc::float32_t>(z);
    star_model_object.vx = static_cast<vfc::float32_t>(-vy);
    star_model_object.vy = static_cast<vfc::float32_t>(vx);
    star_model_object.ax = static_cast<vfc::float32_t>(ax);
    star_model_object.ay = static_cast<vfc::float32_t>(ay);
    star_model_object.heading = static_cast<vfc::float32_t>(heading);
    star_model_object.length = static_cast<vfc::float32_t>(length);
    star_model_object.width = static_cast<vfc::float32_t>(width);
    star_model_object.height = static_cast<vfc::float32_t>(height);

    switch (object_type)
    {
    case 0: // 0 means non obstacle on HIL
        star_model_object.objectType = RBStarModel::SensormodelObjectType::Undefined;
        break;
    case 1: // 1 means unknown on HIL
        star_model_object.objectType = RBStarModel::SensormodelObjectType::Undefined;
        break;
    case 2: // 2 means roadside barrier in HIL, there is no equivalent in star model for this
        star_model_object.objectType = RBStarModel::SensormodelObjectType::ConstructionElement;
        break;
    case 3: // 3 means two wheeler on HIL (according to star model docu, Motorbike is mapped to Bicycle, so they are the same)
        star_model_object.objectType = RBStarModel::SensormodelObjectType::Motorbike;
        break;
    case 4: // 4 means pedestrian
        star_model_object.objectType = RBStarModel::SensormodelObjectType::Pedestrian;
        break;
    case 5: // 5 means truck
        star_model_object.objectType = RBStarModel::SensormodelObjectType::Truck;
        break;
    case 6: // 6 means car
        star_model_object.objectType = RBStarModel::SensormodelObjectType::Car;
        break;
    default:
        throw std::runtime_error("Unexpected value for object_type");
        return -2;
        break;
    }

    inst->star_model_object_list_.push_back(star_model_object);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appGetNumLocs(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->locations_.NumLocs;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetDistance(uint32_t handle, uint32_t index)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        if (index < instance->locations_.NumLocs)
        {
            return instance->locations_.Item[index].getRadialDistance();
        }
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetAzimuthAngle(uint32_t handle, uint32_t index)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        if (index < instance->locations_.NumLocs)
        {
            return instance->locations_.Item[index].getAzimuthAngle();
        }
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetElevationAngle(uint32_t handle, uint32_t index)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        if (index < instance->locations_.NumLocs)
        {
            return instance->locations_.Item[index].getElevationAngle();
        }
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetRelativeRadialVelocity(uint32_t handle, uint32_t index)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        if (index < instance->locations_.NumLocs)
        {
            // Note: The StarModel uses negative values in case the object moves relative towards the ego,
            // hence we multiply with -1 to comply with the official definition. (e.g. in OSI).
            // Note: The constant offset of 3.92 is added manually here as it was seen in many tests (including unit tests).
            return -1 * instance->locations_.Item[index].getRelativeRadialVelocity() - 3.92;
        }
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetRcs(uint32_t handle, uint32_t index)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        if (index < instance->locations_.NumLocs)
        {
            return instance->locations_.Item[index].getRcs();
        }
    }
    return 0.0F;
}

long CAPLEXPORT CAPLPASCAL appInitStarModel(uint32 handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        instance->sensormodel_.shallPerformDynamicObjectFiltering(false);
        instance->sensormodel_.shallPerformStationaryObjectFiltering(false);
        instance->sensormodel_.shallPerformRadialDistanceObjectFiltering(false);
        // path to database, disable locations, loadDatabaseInSeparateThread
        if(!std::ifstream(instance->path_to_database_)) return 2;
        instance->sensormodel_.init(instance->path_to_database_, false, false);
        return 0;
    }
    return -1;
}

long CAPLEXPORT CAPLPASCAL appRunStarModel(uint32 handle, uint32 timestamp)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        if (!instance->sensormodel_.databaseIsLoaded())
        {
            return -1;
        }

        instance->sensormodel_.addObjectList(instance->star_model_object_list_);

        instance->sensormodel_.setSensorAlignment(0.0F, 0.0F, 0.0F, 0.0F, 0.0F);
        instance->sensormodel_.setVehicleDynamics(0.0F, 0.0F);
        // set maximumAzimuthAngle to large value, i.e 90 degree to each side (which is 1.5708 rad)
        vfc::float32_t maximumAzimuthAngle{1.5708F};
        vfc::float32_t minimumLongitudinalDistance{0.0}; // default by star model is 0.3
        vfc::float32_t maximumLongitudinalDistance{500.0F}; // default by star model is 280
        vfc::float32_t maximumLateralDistance{500.0F};

        // arguments are float32_t maximumAzimuthAngleRad, float32_t minimumLongitudinalDistance, float32_t maximumLongitudinalDistance, float32_t maximumLateralDistance
        instance->sensormodel_.setAbsoluteLimits(maximumAzimuthAngle,
                                                 minimumLongitudinalDistance,
                                                 maximumLongitudinalDistance,
                                                 maximumLateralDistance);
        bool is_valid_calculation = instance->sensormodel_.calculate(timestamp);

        if (is_valid_calculation)
        {
            instance->locations_ = instance->sensormodel_.getLocations();
            // clear object list in order to be able to fill again
            instance->star_model_object_list_.clear();
            return 0;
        }

        // clear object list in order to be able to fill again
        instance->star_model_object_list_.clear();
        return -2;
    }
    return -3;
}

// ============================================================================
// FORD ONLY
// Definition fo the functions for the ByteArray Handling for CAN TP
// ============================================================================
long CAPLEXPORT CAPLPASCAL appStarPushLocToByteArray(uint32 handle, uint32 flagFlip, uint32_t radar_id)
{
    int i;
    int iteration_count = 0;
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        switch(radar_id)
        {
            case 1:
            for(i=instance->total_nr_of_loc_FC; i < instance->total_nr_of_loc_FC+min(instance->max_nr_of_loc, (int)instance->locations_.NumLocs); i++)
            {
                //pre filter
                instance->locations_.Item[iteration_count].v = instance->locations_.Item[iteration_count].v + 3.92F;
                if(instance->locations_.Item[iteration_count].theta>180.0F) instance->locations_.Item[iteration_count].theta = instance->locations_.Item[iteration_count].theta-2*180.0f;
                if(flagFlip)
                {
                    instance->locations_.Item[iteration_count].theta = -instance->locations_.Item[iteration_count].theta;
                    instance->locations_.Item[iteration_count].phi = -instance->locations_.Item[iteration_count].phi;
                }
                //write byte array
                Write_ByteArray_RXX_Location(i, instance->byteArray_loc_FC, iteration_count, instance);
                iteration_count++;
            }
            instance->total_nr_of_loc_FC = instance->total_nr_of_loc_FC + min(instance->max_nr_of_loc, (int)instance->locations_.NumLocs);
            break;
            case 2:
            for(i=instance->total_nr_of_loc_FL; i < instance->total_nr_of_loc_FL+min(instance->max_nr_of_loc, (int)instance->locations_.NumLocs); i++)
            {
                //pre filter
                instance->locations_.Item[iteration_count].v = instance->locations_.Item[iteration_count].v + 3.92F;
                if(instance->locations_.Item[iteration_count].theta>180.0F) instance->locations_.Item[iteration_count].theta = instance->locations_.Item[iteration_count].theta-2*180.0f;
                if(flagFlip)
                {
                    instance->locations_.Item[iteration_count].theta = -instance->locations_.Item[iteration_count].theta;
                    instance->locations_.Item[iteration_count].phi = -instance->locations_.Item[iteration_count].phi;
                }
                //write byte array
                Write_ByteArray_RXX_Location(i, instance->byteArray_loc_FL, iteration_count, instance);
                iteration_count++;
            }
            instance->total_nr_of_loc_FL = instance->total_nr_of_loc_FL + min(instance->max_nr_of_loc, (int)instance->locations_.NumLocs);
            break;
            case 3:
            for(i=instance->total_nr_of_loc_FR; i < instance->total_nr_of_loc_FR+min(instance->max_nr_of_loc, (int)instance->locations_.NumLocs); i++)
            {
                //pre filter
                instance->locations_.Item[iteration_count].v = instance->locations_.Item[iteration_count].v + 3.92F;
                if(instance->locations_.Item[iteration_count].theta>180.0F) instance->locations_.Item[iteration_count].theta = instance->locations_.Item[iteration_count].theta-2*180.0f;
                if(flagFlip)
                {
                    instance->locations_.Item[iteration_count].theta = -instance->locations_.Item[iteration_count].theta;
                    instance->locations_.Item[iteration_count].phi = -instance->locations_.Item[iteration_count].phi;
                }
                //write byte array
                Write_ByteArray_RXX_Location(i, instance->byteArray_loc_FR, iteration_count, instance);
                iteration_count++;
            }
            instance->total_nr_of_loc_FR = instance->total_nr_of_loc_FR + min(instance->max_nr_of_loc, (int)instance->locations_.NumLocs);
            break;
            case 4:
            for(i=instance->total_nr_of_loc_RL; i < instance->total_nr_of_loc_RL+min(instance->max_nr_of_loc, (int)instance->locations_.NumLocs); i++)
            {
                //pre filter
                instance->locations_.Item[iteration_count].v = instance->locations_.Item[iteration_count].v + 3.92F;
                if(instance->locations_.Item[iteration_count].theta>180.0F) instance->locations_.Item[iteration_count].theta = instance->locations_.Item[iteration_count].theta-2*180.0f;
                if(flagFlip)
                {
                    instance->locations_.Item[iteration_count].theta = -instance->locations_.Item[iteration_count].theta;
                    instance->locations_.Item[iteration_count].phi = -instance->locations_.Item[iteration_count].phi;
                }
                //write byte array
                Write_ByteArray_RXX_Location(i, instance->byteArray_loc_RL, iteration_count, instance);
                iteration_count++;
            }
            instance->total_nr_of_loc_RL = instance->total_nr_of_loc_RL + min(instance->max_nr_of_loc, (int)instance->locations_.NumLocs);
            break;
            case 5:
            for(i=instance->total_nr_of_loc_RR; i < instance->total_nr_of_loc_RR+min(instance->max_nr_of_loc, (int)instance->locations_.NumLocs); i++)
            {
                //pre filter
                instance->locations_.Item[iteration_count].v = instance->locations_.Item[iteration_count].v + 3.92F;
                if(instance->locations_.Item[iteration_count].theta>180.0F) instance->locations_.Item[iteration_count].theta = instance->locations_.Item[iteration_count].theta-2*180.0f;
                if(flagFlip)
                {
                    instance->locations_.Item[iteration_count].theta = -instance->locations_.Item[iteration_count].theta;
                    instance->locations_.Item[iteration_count].phi = -instance->locations_.Item[iteration_count].phi;
                }
                //write byte array
                Write_ByteArray_RXX_Location(i, instance->byteArray_loc_RR, iteration_count, instance);
                iteration_count++;
            }
            instance->total_nr_of_loc_RR = instance->total_nr_of_loc_RR + min(instance->max_nr_of_loc, (int)instance->locations_.NumLocs);
            break;
        }

        return 0;
    }
    return -1;
}

long CAPLEXPORT CAPLPASCAL appGetByteArray(uint32_t handle, uint8_t byteArray[], uint32_t radar_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        switch(radar_id)
        {
            case 1:
            memcpy(byteArray,instance->byteArray_loc_FC,12500);
            break;
            case 2:
            memcpy(byteArray,instance->byteArray_loc_FL,12500);
            break;
            case 3:
            memcpy(byteArray,instance->byteArray_loc_FR,12500);
            break;
            case 4:
            memcpy(byteArray,instance->byteArray_loc_RL,12500);
            break;
            case 5:
            memcpy(byteArray,instance->byteArray_loc_RR,12500);
            break;
        }
        
        return 1;
    }
    return 0;
}

long CAPLEXPORT CAPLPASCAL appResetStarModel(uint32_t handle, uint32_t radar_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        switch(radar_id)
        {
            case 1:
            memset(instance->byteArray_loc_FC,0, sizeof(instance->byteArray_loc_FC));
            instance->total_nr_of_loc_FC = 0;
            break;
            case 2:
            memset(instance->byteArray_loc_FL,0, sizeof(instance->byteArray_loc_FL));
            instance->total_nr_of_loc_FL = 0;
            break;
            case 3:
            memset(instance->byteArray_loc_FR,0, sizeof(instance->byteArray_loc_FR));
            instance->total_nr_of_loc_FR = 0;
            break;
            case 4:
            memset(instance->byteArray_loc_RL,0, sizeof(instance->byteArray_loc_RL));
            instance->total_nr_of_loc_RL = 0;
            break;
            case 5:
            memset(instance->byteArray_loc_RR,0, sizeof(instance->byteArray_loc_RR));
            instance->total_nr_of_loc_RR = 0;
            break;
        }

        return 1;
    }
    return 0;
}

long CAPLEXPORT CAPLPASCAL appGetTotalNrLoc(uint32_t handle, uint32_t radar_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        switch(radar_id)
        {
            case 1:
            return instance->total_nr_of_loc_FC;
            case 2:
            return instance->total_nr_of_loc_FL;
            case 3:
            return instance->total_nr_of_loc_FR;
            case 4:
            return instance->total_nr_of_loc_RL;
            case 5:
            return instance->total_nr_of_loc_RR;
        }
        
    }
    return -1;
}

long CAPLEXPORT CAPLPASCAL appSetMaxNrLoc(uint32_t handle, uint32_t maxValue)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        instance->max_nr_of_loc = maxValue;
        return 0;
    }
    return -1;
}

// ============================================================================
// CAPL_DLL_INFO_LIST : list of exported functions
//   The first field is predefined and mustn't be changed!
//   The list has to end with a {0,0} entry!
// New struct supporting function names with up to 50 characters
// ============================================================================
CAPL_DLL_INFO4 table[] = {
    {CDLL_VERSION_NAME, (CAPL_FARCALL)CDLL_VERSION, "", "", CAPL_DLL_CDECL, 0xabcd, CDLL_EXPORT},
    {"dllInit", (CAPL_FARCALL)appInit, "CAPL_DLL", "This function will initialize all callback functions in the CAPLDLL", 'V', 1, "D", "", {"handle"}},
    {"dllEnd", (CAPL_FARCALL)appEnd, "CAPL_DLL", "This function will release the CAPL function handle in the CAPLDLL", 'V', 1, "D", "", {"handle"}},
    {"dllInitStarModel", (CAPL_FARCALL)appInitStarModel, "CAPL_DLL", "This function initializes the star model", 'L', 1, "D", "", {"handle"}},
    {"dllRunStarModel", (CAPL_FARCALL)appRunStarModel, "CAPL_DLL", "This function runs the star model", 'L', 2, "DD", "", {"handle", "timestamp"}},
    {"dllSetInputValues", (CAPL_FARCALL)appSetInputValues, "CAPL_DLL", "This function sets the input objects for the star model", 'L', 14, "DLFFFFFFFFFFFL", "", {"handle", "id", "x", "y", "z", "vx", "vy", "ax", "ay", "heading", "length", "width", "height", "object_type"}},
    {"dllGetNumLocs", (CAPL_FARCALL)appGetNumLocs, "CAPL_DLL", "This function gets the number of locations", 'L', 1, "L", "", {"handle"}},
    {"dllGetDistance", (CAPL_FARCALL)appGetDistance, "CAPL_DLL", "This function gets the distance of a location", 'F', 2, "LL", "", {"handle", "index"}},
    {"dllGetAzimuthAngle", (CAPL_FARCALL)appGetAzimuthAngle, "CAPL_DLL", "This function gets the azimuth angle of a location", 'F', 2, "LL", "", {"handle", "index"}},
    {"dllGetElevationAngle", (CAPL_FARCALL)appGetElevationAngle, "CAPL_DLL", "This function gets the elevation angle of a location", 'F', 2, "LL", "", {"handle", "index"}},
    {"dllGetRelativeRadialVelocity", (CAPL_FARCALL)appGetRelativeRadialVelocity, "CAPL_DLL", "This function gets the radial velocity of a location", 'F', 2, "LL", "", {"handle", "index"}},
    {"dllGetRcs", (CAPL_FARCALL)appGetRcs, "CAPL_DLL", "This function gets Rcs value of the location", 'F', 2, "LL", "", {"handle", "index"}},
    {"dllSetMaxNrLoc", (CAPL_FARCALL)appSetMaxNrLoc, "CAPL_DLL", "This function set the max number of locations per obj", 'L', 2, "LL", "", {"handle", "maxValue"}},
    {"dllSetDatabasePath", (CAPL_FARCALL)appSetDatabasePath, "CAPL_DLL", "This function sets database path", 'L', 2, "LC", "\000\001", {"handle", "datablock"}},
    {"dllResetStarModel", (CAPL_FARCALL)appResetStarModel, "CAPL_DLL", "This function reset the star model", 'L', 2, "LD", "", {"handle", "radarId"}},
    {"dllStarGetByteArray", (CAPL_FARCALL)appGetByteArray, "CAPL_DLL", "This function sets the byte array", 'L', 3, "LBD", "\000\001\000", {"handle", "byteArray", "radarId"}},
    {"dllStarGetTotalNrLoc", (CAPL_FARCALL)appGetTotalNrLoc, "CAPL_DLL", "This function gets the total nr of locations", 'L', 2, "LD", "", {"handle", "radarId"}},
    {"dllStarPushLocToByteArray", (CAPL_FARCALL)appStarPushLocToByteArray, "CAPL_DLL", "This parse the locations generated in the byte array", 'L', 3, "DDD", "", {"handle", "flagFlipSensor", "RadarId"}},
    {0, 0}};
CAPLEXPORT CAPL_DLL_INFO4 *caplDllTable4 = table;