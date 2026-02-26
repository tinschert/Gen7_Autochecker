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
#define NOMINMAX

#include "../Includes/cdll.h"
#include "../Includes/VIA.h"
#include "../Includes/VIA_CDLL.h"
#include "RoadObj.hpp"

#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <map>

#if defined(_WIN64) || defined(__linux__)
#define X64
#endif

//#include "radarSensormodel.h"

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

    RoadObj::SensorHandler sensor_handler;

private:
    VIACapl *mCapl;
};

CaplInstanceData::CaplInstanceData(VIACapl *capl)
    // This function will initialize the CAPL callback function
    // with the NLL Pointer
    : mCapl(capl),
      sensor_handler()
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

// ============================================================================
// Initialize dll
// ============================================================================

long CAPLEXPORT CAPLPASCAL appInitRoadObj(uint32 handle, int simulator, int data_transfer_protocol)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    switch (simulator)
    {
    case 1:
        instance->sensor_handler.i_simulator = RoadObj::Simulator::Classe;
        break;

    case 2:
        instance->sensor_handler.i_simulator = RoadObj::Simulator::CarMaker;
        break;
    
    default:
        break;
    }
    switch (data_transfer_protocol)
    {
    case 1:
        instance->sensor_handler.i_transfer_protocol = RoadObj::Data_Transfer_Protocol::CAN_Bus;
        break;

    case 2:
        instance->sensor_handler.i_transfer_protocol = RoadObj::Data_Transfer_Protocol::CAN_TP;
        break;

    case 3:
        instance->sensor_handler.i_transfer_protocol = RoadObj::Data_Transfer_Protocol::Ethernet;
        break;
    
    default:
        break;
    }

    return 0;
}
long CAPLEXPORT CAPLPASCAL appCalcAllSensorTargetData(uint32 handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }

    instance->sensor_handler.calculate_all_sensor_target_data();

    return 0;
}
long CAPLEXPORT CAPLPASCAL appInputEgoValues(uint32 handle, double velocity_x, double velocity_y)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }

    instance->sensor_handler.set_ego_values(velocity_x,velocity_y);

    return 0;
}

// ============================================================================
// Input Radar Data
// ============================================================================
long CAPLEXPORT CAPLPASCAL appInputRadarDefinitionsRadarFC(uint32 handle, int loc_model,int loc_distribution_model,int loc_sim_active,int max_nr_loc,double loc_separation_angle,int radar_generation)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FC.set_radar_values(loc_model,loc_distribution_model,loc_sim_active,max_nr_loc,loc_separation_angle,radar_generation);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputRadarDefinitionsRadarFL(uint32 handle, int loc_model,int loc_distribution_model,int loc_sim_active,int max_nr_loc,double loc_separation_angle,int radar_generation)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FL.set_radar_values(loc_model,loc_distribution_model,loc_sim_active,max_nr_loc,loc_separation_angle,radar_generation);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputRadarDefinitionsRadarFR(uint32 handle, int loc_model,int loc_distribution_model,int loc_sim_active,int max_nr_loc,double loc_separation_angle,int radar_generation)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FR.set_radar_values(loc_model,loc_distribution_model,loc_sim_active,max_nr_loc,loc_separation_angle,radar_generation);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputRadarDefinitionsRadarRL(uint32 handle, int loc_model,int loc_distribution_model,int loc_sim_active,int max_nr_loc,double loc_separation_angle,int radar_generation)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_RL.set_radar_values(loc_model,loc_distribution_model,loc_sim_active,max_nr_loc,loc_separation_angle,radar_generation);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputRadarDefinitionsRadarRR(uint32 handle, int loc_model,int loc_distribution_model,int loc_sim_active,int max_nr_loc,double loc_separation_angle,int radar_generation)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_RR.set_radar_values(loc_model,loc_distribution_model,loc_sim_active,max_nr_loc,loc_separation_angle,radar_generation);

    return 0;
}

// ============================================================================
// Input Sensor Data
// ============================================================================

long CAPLEXPORT CAPLPASCAL appInputSensorDefinitionsRadarFC(uint32 handle, double mount_dx,double mount_dy,double mount_dz,double mount_yaw,double fov_angle,
                                                    int validity_sending_active,int obj_sim_active,int obj_count)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FC.set_sensor_values(mount_dx,mount_dy,mount_dz,mount_yaw,fov_angle,validity_sending_active,obj_sim_active,obj_count);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputSensorDefinitionsRadarFL(uint32 handle, double mount_dx,double mount_dy,double mount_dz,double mount_yaw,double fov_angle,
                                                    int validity_sending_active,int obj_sim_active,int obj_count)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FL.set_sensor_values(mount_dx,mount_dy,mount_dz,mount_yaw,fov_angle,validity_sending_active,obj_sim_active,obj_count);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputSensorDefinitionsRadarFR(uint32 handle, double mount_dx,double mount_dy,double mount_dz,double mount_yaw,double fov_angle,
                                                    int validity_sending_active,int obj_sim_active,int obj_count)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FR.set_sensor_values(mount_dx,mount_dy,mount_dz,mount_yaw,fov_angle,validity_sending_active,obj_sim_active,obj_count);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputSensorDefinitionsRadarRL(uint32 handle, double mount_dx,double mount_dy,double mount_dz,double mount_yaw,double fov_angle,
                                                    int validity_sending_active,int obj_sim_active,int obj_count)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_RL.set_sensor_values(mount_dx,mount_dy,mount_dz,mount_yaw,fov_angle,validity_sending_active,obj_sim_active,obj_count);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputSensorDefinitionsRadarRR(uint32 handle, double mount_dx,double mount_dy,double mount_dz,double mount_yaw,double fov_angle,
                                                    int validity_sending_active,int obj_sim_active,int obj_count)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_RR.set_sensor_values(mount_dx,mount_dy,mount_dz,mount_yaw,fov_angle,validity_sending_active,obj_sim_active,obj_count);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputSensorDefinitionsVideoFC(uint32 handle, double mount_dx,double mount_dy,double mount_dz,double mount_yaw,double fov_angle,
                                                    int validity_sending_active,int obj_sim_active,int obj_count)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Video_FC.set_sensor_values(mount_dx,mount_dy,mount_dz,mount_yaw,fov_angle,validity_sending_active,obj_sim_active,obj_count);

    return 0;
}

// ============================================================================
// Input Object Data
// ============================================================================

long CAPLEXPORT CAPLPASCAL appInputObjectDataRadarFC(uint32 handle, int obj_id,int sim_on,int sensor_mode,double dx,double dy,double vx,double vy,double ax,double ay,
                                                    double yaw_angle,double width,double length, double height, int type, double rcs, double snr, double rssi)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FC.set_object_values(obj_id,sim_on,sensor_mode,dx,dy,vx,vy,ax,ay,yaw_angle,width,length,height,type,rcs,snr,rssi);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputObjectDataRadarFL(uint32 handle, int obj_id,int sim_on,int sensor_mode,double dx,double dy,double vx,double vy,double ax,double ay,
                                                    double yaw_angle,double width,double length, double height, int type, double rcs, double snr, double rssi)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FL.set_object_values(obj_id,sim_on,sensor_mode,dx,dy,vx,vy,ax,ay,yaw_angle,width,length,height,type,rcs,snr,rssi);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputObjectDataRadarFR(uint32 handle, int obj_id,int sim_on,int sensor_mode,double dx,double dy,double vx,double vy,double ax,double ay,
                                                    double yaw_angle,double width,double length, double height, int type, double rcs, double snr, double rssi)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FR.set_object_values(obj_id,sim_on,sensor_mode,dx,dy,vx,vy,ax,ay,yaw_angle,width,length,height,type,rcs,snr,rssi);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputObjectDataRadarRL(uint32 handle, int obj_id,int sim_on,int sensor_mode,double dx,double dy,double vx,double vy,double ax,double ay,
                                                    double yaw_angle,double width,double length, double height, int type, double rcs, double snr, double rssi)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_RL.set_object_values(obj_id,sim_on,sensor_mode,dx,dy,vx,vy,ax,ay,yaw_angle,width,length,height,type,rcs,snr,rssi);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputObjectDataRadarRR(uint32 handle, int obj_id,int sim_on,int sensor_mode,double dx,double dy,double vx,double vy,double ax,double ay,
                                                    double yaw_angle,double width,double length, double height, int type, double rcs, double snr, double rssi)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_RR.set_object_values(obj_id,sim_on,sensor_mode,dx,dy,vx,vy,ax,ay,yaw_angle,width,length,height,type,rcs,snr,rssi);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputObjectDataVideoFC(uint32 handle, int obj_id,int sim_on,int sensor_mode,double dx,double dy,double vx,double vy,double ax,double ay,
                                                    double yaw_angle,double width,double length, double height, int type, double rcs, double snr, double rssi)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Video_FC.set_object_values(obj_id,sim_on,sensor_mode,dx,dy,vx,vy,ax,ay,yaw_angle,width,length,height,type,rcs,snr,rssi);

    return 0;
}

// ============================================================================
// Input Location Data
// ============================================================================

long CAPLEXPORT CAPLPASCAL appInputLocationDataRadarFC(uint32 handle, int loc_id,double radial_distance, double radial_velocity, double elevation, double azimuth, 
                                                        double radar_cross_section, double rssi, double snr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FC.set_radar_loc_values(loc_id,radial_distance,radial_velocity,elevation,azimuth,radar_cross_section,rssi,snr);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputLocationDataRadarFL(uint32 handle, int loc_id,double radial_distance, double radial_velocity, double elevation, double azimuth, 
                                                        double radar_cross_section, double rssi, double snr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FL.set_radar_loc_values(loc_id,radial_distance,radial_velocity,elevation,azimuth,radar_cross_section,rssi,snr);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputLocationDataRadarFR(uint32 handle, int loc_id,double radial_distance, double radial_velocity, double elevation, double azimuth, 
                                                        double radar_cross_section, double rssi, double snr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_FR.set_radar_loc_values(loc_id,radial_distance,radial_velocity,elevation,azimuth,radar_cross_section,rssi,snr);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputLocationDataRadarRL(uint32 handle, int loc_id,double radial_distance, double radial_velocity, double elevation, double azimuth, 
                                                        double radar_cross_section, double rssi, double snr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_RL.set_radar_loc_values(loc_id,radial_distance,radial_velocity,elevation,azimuth,radar_cross_section,rssi,snr);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appInputLocationDataRadarRR(uint32 handle, int loc_id,double radial_distance, double radial_velocity, double elevation, double azimuth, 
                                                        double radar_cross_section, double rssi, double snr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    
    instance->sensor_handler.Radar_RR.set_radar_loc_values(loc_id,radial_distance,radial_velocity,elevation,azimuth,radar_cross_section,rssi,snr);

    return 0;
}

// ============================================================================
// Getters - RoadObj wide
// ============================================================================
long CAPLEXPORT CAPLPASCAL appGetTimeToCalculate(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.calculation_duration;
    }
    return 0;
}

// ============================================================================
// Getters - Valid Object Flags
// ============================================================================
long CAPLEXPORT CAPLPASCAL appGetValidityFlagRadarFC(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.get_in_obj_validity_flag(obj_id);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetValidityFlagRadarFL(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.get_in_obj_validity_flag(obj_id);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetValidityFlagRadarFR(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.get_in_obj_validity_flag(obj_id);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetValidityFlagRadarRL(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.get_in_obj_validity_flag(obj_id);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetValidityFlagRadarRR(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.get_in_obj_validity_flag(obj_id);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetValidityFlagVideoFC(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.get_in_obj_validity_flag(obj_id);
    }
    return 0;
}

// ============================================================================
// Getters - Empty Object Flags
// ============================================================================
long CAPLEXPORT CAPLPASCAL appGetEmptyFlagRadarFC(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.get_in_obj_empty_flag(obj_id);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetEmptyFlagRadarFL(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.get_in_obj_empty_flag(obj_id);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetEmptyFlagRadarFR(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.get_in_obj_empty_flag(obj_id);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetEmptyFlagRadarRL(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.get_in_obj_empty_flag(obj_id);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetEmptyFlagRadarRR(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.get_in_obj_empty_flag(obj_id);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetEmptyFlagVideoFC(uint32_t handle, int obj_id)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_id < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.get_in_obj_empty_flag(obj_id);
    }
    return 0;
}

// ============================================================================
// Getters - Radar FC
// ============================================================================
long CAPLEXPORT CAPLPASCAL appGetRadarFCValidObjCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.Radar_FC.get_sensor_valid_obj_count();
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCValidLocCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.Radar_FC.get_radar_valid_loc_count();
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCLocRadialDistance(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FC.Loc[loc_nr].o_radial_distance;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCLocRadialVelocity(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FC.Loc[loc_nr].o_radial_velocity;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCLocAzimuthAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FC.Loc[loc_nr].o_azimuth;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCLocElevationAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FC.Loc[loc_nr].o_elevation;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCLocRCS(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FC.Loc[loc_nr].o_radar_cross_section;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCLocRSSI(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FC.Loc[loc_nr].o_rssi;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCLocSNR(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FC.Loc[loc_nr].o_snr;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCObjDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_distance_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCObjDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_distance_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCObjVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_velocity_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCObjVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_velocity_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCObjAccelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_acceleration_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCObjAccelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_acceleration_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCObjYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_yaw_angle;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCObjRefPnt(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_reference_point;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCObjProbMoving(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_ra5_prob_moving;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCObjProbStationary(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_ra5_prob_stationary;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCObjProbNonObst(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_ra5_prob_non_obst;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCObjProbTruck(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_ra5_prob_truck;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCObjProbCar(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_ra5_prob_car;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCObjProb2Wheeler(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_ra5_prob_2wheeler;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCObjProbPedestrian(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_ra5_prob_pedestrian;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCObjRa6RCS(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_ra6_radar_cross_section;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCObjRa6ObjType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_ra6_obj_type;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCObjRa6MovingStatus(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.Obj[obj_nr].o_ra6_moving_status;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCInputObjectDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.get_in_obj_distance_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCInputObjectDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.get_in_obj_distance_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCInputObjectVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.get_in_obj_velocity_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCInputObjectVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.get_in_obj_velocity_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCInputObjectYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.get_in_obj_yaw_angle(obj_nr);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCInputObjectType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.get_in_obj_type(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCInputObjectWidth(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.get_in_obj_width(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCInputObjectLength(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.get_in_obj_length(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFCInputObjectHeight(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FC.get_in_obj_height(obj_nr);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFCByteArray(uint32_t handle, uint8_t byteArray[])
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        if(instance->sensor_handler.Radar_FC.get_radar_loc_sim() == 0)
        {   // RA6 SGU interface
            memcpy(byteArray+132,instance->sensor_handler.Radar_FC.byte_array_obj+132,3072); //Gen6 SGU can TP, 132bytes header, 48 objs of 64bytes
        }
        else if(instance->sensor_handler.i_transfer_protocol == RoadObj::Data_Transfer_Protocol::CAN_TP)
            memcpy(byteArray+128,instance->sensor_handler.Radar_FC.byte_array_loc+128,12000); //Gen6 can TP, 128bytes header, 500 locs of 24bytes
        else if (instance->sensor_handler.i_transfer_protocol == RoadObj::Data_Transfer_Protocol::Ethernet)
        {
            if (instance->sensor_handler.Radar_FC.get_radar_generation()==1)
                memcpy(byteArray+72,instance->sensor_handler.Radar_FC.byte_array_loc+72,71808); //Conti, 72bytes header, 1056 locs of 68bytes
            else
                memcpy(byteArray+128,instance->sensor_handler.Radar_FC.byte_array_loc+128,24000); //Gen6 ethernet, 128bytes header, 1000 locs of 24bytes
        }
        else
            return -1;
        return 0;
    }
    return -1;
}
long CAPLEXPORT CAPLPASCAL appResetByteArrayRadarFC(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        memset(instance->sensor_handler.Radar_FC.byte_array_loc,0, sizeof(instance->sensor_handler.Radar_FC.byte_array_loc));
        memset(instance->sensor_handler.Radar_FC.byte_array_obj,0, sizeof(instance->sensor_handler.Radar_FC.byte_array_obj));
        return 0;
    }
    return -1;
}

// ============================================================================
// Getters - Radar FL
// ============================================================================
long CAPLEXPORT CAPLPASCAL appGetRadarFLValidObjCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.Radar_FL.get_sensor_valid_obj_count();
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLValidLocCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.Radar_FL.get_radar_valid_loc_count();
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLLocRadialDistance(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FL.Loc[loc_nr].o_radial_distance;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLLocRadialVelocity(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FL.Loc[loc_nr].o_radial_velocity;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLLocAzimuthAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FL.Loc[loc_nr].o_azimuth;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLLocElevationAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FL.Loc[loc_nr].o_elevation;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLLocRCS(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FL.Loc[loc_nr].o_radar_cross_section;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLLocRSSI(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FL.Loc[loc_nr].o_rssi;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLLocSNR(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FL.Loc[loc_nr].o_snr;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLObjDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_distance_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLObjDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_distance_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLObjVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_velocity_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLObjVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_velocity_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLObjAccelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_acceleration_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLObjAccelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_acceleration_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLObjYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_yaw_angle;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLObjRefPnt(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_reference_point;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLObjProbMoving(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_ra5_prob_moving;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLObjProbStationary(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_ra5_prob_stationary;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLObjProbNonObst(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_ra5_prob_non_obst;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLObjProbTruck(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_ra5_prob_truck;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLObjProbCar(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_ra5_prob_car;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLObjProb2Wheeler(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_ra5_prob_2wheeler;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLObjProbPedestrian(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_ra5_prob_pedestrian;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLObjRa6RCS(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_ra6_radar_cross_section;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLObjRa6ObjType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_ra6_obj_type;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLObjRa6MovingStatus(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.Obj[obj_nr].o_ra6_moving_status;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLInputObjectDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.get_in_obj_distance_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLInputObjectDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.get_in_obj_distance_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLInputObjectVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.get_in_obj_velocity_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLInputObjectVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.get_in_obj_velocity_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLInputObjectYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.get_in_obj_yaw_angle(obj_nr);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLInputObjectType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.get_in_obj_type(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLInputObjectWidth(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.get_in_obj_width(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLInputObjectLength(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.get_in_obj_length(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFLInputObjectHeight(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FL.get_in_obj_height(obj_nr);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFLByteArray(uint32_t handle, uint8_t byteArray[])
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        if(instance->sensor_handler.Radar_FL.get_radar_loc_sim() == 0)
        {   // RA6 SGU interface
            memcpy(byteArray+132,instance->sensor_handler.Radar_FL.byte_array_obj+132,3072); //Gen6 SGU can TP, 132bytes header, 48 objs of 64bytes
        }
        else if(instance->sensor_handler.i_transfer_protocol == RoadObj::Data_Transfer_Protocol::CAN_TP)
            memcpy(byteArray+128,instance->sensor_handler.Radar_FL.byte_array_loc+128,12000); //Gen6 can TP, 128bytes header, 500 locs of 24bytes
        else if (instance->sensor_handler.i_transfer_protocol == RoadObj::Data_Transfer_Protocol::Ethernet)
        {
            if (instance->sensor_handler.Radar_FL.get_radar_generation()==1)
                memcpy(byteArray+88,instance->sensor_handler.Radar_FL.byte_array_loc+88,71808); //Conti, 84bytes header +4bytes some ip length field, 1056 locs of 68bytes
            else
                memcpy(byteArray+128,instance->sensor_handler.Radar_FL.byte_array_loc+128,24000); //Gen6 ethernet, 128bytes header, 1000 locs of 24bytes
        }
        else
            return -1;
        return 0;
    }
    return -1;
}
long CAPLEXPORT CAPLPASCAL appResetByteArrayRadarFL(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        memset(instance->sensor_handler.Radar_FL.byte_array_loc,0, sizeof(instance->sensor_handler.Radar_FL.byte_array_loc));
        memset(instance->sensor_handler.Radar_FL.byte_array_obj,0, sizeof(instance->sensor_handler.Radar_FL.byte_array_obj));
        return 0;
    }
    return -1;
}

// ============================================================================
// Getters - Radar FR
// ============================================================================
long CAPLEXPORT CAPLPASCAL appGetRadarFRValidObjCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.Radar_FR.get_sensor_valid_obj_count();
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRValidLocCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.Radar_FR.get_radar_valid_loc_count();
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRLocRadialDistance(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FR.Loc[loc_nr].o_radial_distance;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRLocRadialVelocity(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FR.Loc[loc_nr].o_radial_velocity;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRLocAzimuthAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FR.Loc[loc_nr].o_azimuth;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRLocElevationAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FR.Loc[loc_nr].o_elevation;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRLocRCS(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FR.Loc[loc_nr].o_radar_cross_section;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRLocRSSI(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FR.Loc[loc_nr].o_rssi;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRLocSNR(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_FR.Loc[loc_nr].o_snr;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRObjDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_distance_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRObjDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_distance_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRObjVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_velocity_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRObjVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_velocity_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRObjAccelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_acceleration_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRObjAccelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_acceleration_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRObjYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_yaw_angle;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRObjRefPnt(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_reference_point;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRObjProbMoving(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_ra5_prob_moving;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRObjProbStationary(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_ra5_prob_stationary;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRObjProbNonObst(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_ra5_prob_non_obst;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRObjProbTruck(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_ra5_prob_truck;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRObjProbCar(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_ra5_prob_car;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRObjProb2Wheeler(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_ra5_prob_2wheeler;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRObjProbPedestrian(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_ra5_prob_pedestrian;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRObjRa6RCS(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_ra6_radar_cross_section;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRObjRa6ObjType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_ra6_obj_type;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRObjRa6MovingStatus(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.Obj[obj_nr].o_ra6_moving_status;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRInputObjectDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.get_in_obj_distance_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRInputObjectDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.get_in_obj_distance_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRInputObjectVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.get_in_obj_velocity_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRInputObjectVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.get_in_obj_velocity_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRInputObjectYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.get_in_obj_yaw_angle(obj_nr);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRInputObjectType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.get_in_obj_type(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRInputObjectWidth(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.get_in_obj_width(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRInputObjectLength(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.get_in_obj_length(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarFRInputObjectHeight(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_FR.get_in_obj_height(obj_nr);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarFRByteArray(uint32_t handle, uint8_t byteArray[])
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        if(instance->sensor_handler.Radar_FR.get_radar_loc_sim() == 0)
        {   // RA6 SGU interface
            memcpy(byteArray+132,instance->sensor_handler.Radar_FR.byte_array_obj+132,3072); //Gen6 SGU can TP, 132bytes header, 48 objs of 64bytes
        }
        else if(instance->sensor_handler.i_transfer_protocol == RoadObj::Data_Transfer_Protocol::CAN_TP)
            memcpy(byteArray+128,instance->sensor_handler.Radar_FR.byte_array_loc+128,12000); //Gen6 can TP, 128bytes header, 500 locs of 24bytes
        else if (instance->sensor_handler.i_transfer_protocol == RoadObj::Data_Transfer_Protocol::Ethernet)
        {
            if (instance->sensor_handler.Radar_FR.get_radar_generation()==1)
                memcpy(byteArray+88,instance->sensor_handler.Radar_FR.byte_array_loc+88,71808); //Conti, 84bytes header + 4 bytes some ip length field, 1056 locs of 68bytes
            else
                memcpy(byteArray+128,instance->sensor_handler.Radar_FR.byte_array_loc+128,24000); //Gen6 ethernet, 128bytes header, 1000 locs of 24bytes
        }
        else
            return -1;
        return 0;
    }
    return -1;
}
long CAPLEXPORT CAPLPASCAL appResetByteArrayRadarFR(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        memset(instance->sensor_handler.Radar_FR.byte_array_loc,0, sizeof(instance->sensor_handler.Radar_FR.byte_array_loc));
        memset(instance->sensor_handler.Radar_FR.byte_array_obj,0, sizeof(instance->sensor_handler.Radar_FR.byte_array_obj));
        return 0;
    }
    return -1;
}

// ============================================================================
// Getters - Radar RL
// ============================================================================
long CAPLEXPORT CAPLPASCAL appGetRadarRLValidObjCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.Radar_RL.get_sensor_valid_obj_count();
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLValidLocCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.Radar_RL.get_radar_valid_loc_count();
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLLocRadialDistance(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RL.Loc[loc_nr].o_radial_distance;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLLocRadialVelocity(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RL.Loc[loc_nr].o_radial_velocity;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLLocAzimuthAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RL.Loc[loc_nr].o_azimuth;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLLocElevationAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RL.Loc[loc_nr].o_elevation;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLLocRCS(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RL.Loc[loc_nr].o_radar_cross_section;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLLocRSSI(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RL.Loc[loc_nr].o_rssi;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLLocSNR(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RL.Loc[loc_nr].o_snr;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLObjDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_distance_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLObjDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_distance_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLObjVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_velocity_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLObjVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_velocity_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLObjAccelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_acceleration_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLObjAccelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_acceleration_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLObjYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_yaw_angle;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLObjRefPnt(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_reference_point;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLObjProbMoving(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_ra5_prob_moving;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLObjProbStationary(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_ra5_prob_stationary;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLObjProbNonObst(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_ra5_prob_non_obst;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLObjProbTruck(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_ra5_prob_truck;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLObjProbCar(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_ra5_prob_car;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLObjProb2Wheeler(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_ra5_prob_2wheeler;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLObjProbPedestrian(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_ra5_prob_pedestrian;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLObjRa6RCS(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_ra6_radar_cross_section;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLObjRa6ObjType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_ra6_obj_type;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLObjRa6MovingStatus(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.Obj[obj_nr].o_ra6_moving_status;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLInputObjectDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.get_in_obj_distance_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLInputObjectDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.get_in_obj_distance_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLInputObjectVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.get_in_obj_velocity_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLInputObjectVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.get_in_obj_velocity_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLInputObjectYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.get_in_obj_yaw_angle(obj_nr);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLInputObjectType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.get_in_obj_type(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLInputObjectWidth(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.get_in_obj_width(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLInputObjectLength(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.get_in_obj_length(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRLInputObjectHeight(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RL.get_in_obj_height(obj_nr);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRLByteArray(uint32_t handle, uint8_t byteArray[])
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        if(instance->sensor_handler.Radar_RL.get_radar_loc_sim() == 0)
        {   // RA6 SGU interface
            memcpy(byteArray+132,instance->sensor_handler.Radar_RL.byte_array_obj+132,3072); //Gen6 SGU can TP, 132bytes header, 48 objs of 64bytes
        }
        else if(instance->sensor_handler.i_transfer_protocol == RoadObj::Data_Transfer_Protocol::CAN_TP)
            memcpy(byteArray+128,instance->sensor_handler.Radar_RL.byte_array_loc+128,12000); //Gen6 can TP, 128bytes header, 500 locs of 24bytes
        else if (instance->sensor_handler.i_transfer_protocol == RoadObj::Data_Transfer_Protocol::Ethernet)
        {
            if (instance->sensor_handler.Radar_RL.get_radar_generation()==1)
                memcpy(byteArray+88,instance->sensor_handler.Radar_RL.byte_array_loc+88,71808); //Conti, 84bytes header + 4 bytes some ip length field, 1056 locs of 68bytes
            else
                memcpy(byteArray+128,instance->sensor_handler.Radar_RL.byte_array_loc+128,24000); //Gen6 ethernet, 128bytes header, 1000 locs of 24bytes
        }
        else
            return -1;
        return 0;
    }
    return -1;
}
long CAPLEXPORT CAPLPASCAL appResetByteArrayRadarRL(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        memset(instance->sensor_handler.Radar_RL.byte_array_loc,0, sizeof(instance->sensor_handler.Radar_RL.byte_array_loc));
        memset(instance->sensor_handler.Radar_RL.byte_array_obj,0, sizeof(instance->sensor_handler.Radar_RL.byte_array_obj));
        return 0;
    }
    return -1;
}

// ============================================================================
// Getters - Radar RR
// ============================================================================
long CAPLEXPORT CAPLPASCAL appGetRadarRRValidObjCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.Radar_RR.get_sensor_valid_obj_count();
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRValidLocCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.Radar_RR.get_radar_valid_loc_count();
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRLocRadialDistance(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RR.Loc[loc_nr].o_radial_distance;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRLocRadialVelocity(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RR.Loc[loc_nr].o_radial_velocity;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRLocAzimuthAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RR.Loc[loc_nr].o_azimuth;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRLocElevationAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RR.Loc[loc_nr].o_elevation;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRLocRCS(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RR.Loc[loc_nr].o_radar_cross_section;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRLocRSSI(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RR.Loc[loc_nr].o_rssi;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRLocSNR(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && loc_nr < maximum_location_quantity)
    {
        return instance->sensor_handler.Radar_RR.Loc[loc_nr].o_snr;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRObjDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_distance_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRObjDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_distance_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRObjVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_velocity_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRObjVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_velocity_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRObjAccelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_acceleration_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRObjAccelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_acceleration_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRObjYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_yaw_angle;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRObjRefPnt(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_reference_point;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRObjProbMoving(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_ra5_prob_moving;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRObjProbStationary(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_ra5_prob_stationary;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRObjProbNonObst(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_ra5_prob_non_obst;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRObjProbTruck(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_ra5_prob_truck;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRObjProbCar(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_ra5_prob_car;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRObjProb2Wheeler(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_ra5_prob_2wheeler;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRObjProbPedestrian(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_ra5_prob_pedestrian;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRObjRa6RCS(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_ra6_radar_cross_section;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRObjRa6ObjType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_ra6_obj_type;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRObjRa6MovingStatus(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.Obj[obj_nr].o_ra6_moving_status;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRInputObjectDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.get_in_obj_distance_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRInputObjectDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.get_in_obj_distance_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRInputObjectVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.get_in_obj_velocity_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRInputObjectVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.get_in_obj_velocity_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRInputObjectYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.get_in_obj_yaw_angle(obj_nr);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRInputObjectType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.get_in_obj_type(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRInputObjectWidth(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.get_in_obj_width(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRInputObjectLength(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.get_in_obj_length(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetRadarRRInputObjectHeight(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Radar_RR.get_in_obj_height(obj_nr);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetRadarRRByteArray(uint32_t handle, uint8_t byteArray[])
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        if(instance->sensor_handler.Radar_RR.get_radar_loc_sim() == 0)
        {   // RA6 SGU interface
            memcpy(byteArray+132,instance->sensor_handler.Radar_RR.byte_array_obj+132,3072); //Gen6 SGU can TP, 132bytes header, 48 objs of 64bytes
        }
        else if(instance->sensor_handler.i_transfer_protocol == RoadObj::Data_Transfer_Protocol::CAN_TP)
            memcpy(byteArray+128,instance->sensor_handler.Radar_RR.byte_array_loc+128,12000); //Gen6 can TP, 128bytes header, 500 locs of 24bytes
        else if (instance->sensor_handler.i_transfer_protocol == RoadObj::Data_Transfer_Protocol::Ethernet)
        {
            if (instance->sensor_handler.Radar_RR.get_radar_generation()==1)
                memcpy(byteArray+88,instance->sensor_handler.Radar_RR.byte_array_loc+88,71808); //Conti, 84bytes header + 4 bytes length field, 1056 locs of 68bytes
            else
                memcpy(byteArray+128,instance->sensor_handler.Radar_RR.byte_array_loc+128,24000); //Gen6 ethernet, 128bytes header, 1000 locs of 24bytes
        }
        else
            return -1;
        return 0;
    }
    return -1;
}
long CAPLEXPORT CAPLPASCAL appResetByteArrayRadarRR(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        memset(instance->sensor_handler.Radar_RR.byte_array_loc,0, sizeof(instance->sensor_handler.Radar_RR.byte_array_loc));
        memset(instance->sensor_handler.Radar_RR.byte_array_obj,0, sizeof(instance->sensor_handler.Radar_RR.byte_array_obj));
        return 0;
    }
    return -1;
}

// ============================================================================
// Getters - Video FC
// ============================================================================
long CAPLEXPORT CAPLPASCAL appGetVideoFCValidObjCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_handler.Video_FC.get_sensor_valid_obj_count();
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_distance_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_distance_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_velocity_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_velocity_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjAccelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_acceleration_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjAccelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_acceleration_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_yaw_angle;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjVisibleView(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_visible_view;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjClassifiedView(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_classified_view;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjPhiTop(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_phi_top;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjPhiMid(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_phi_mid;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjPhiBottom(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_phi_bottom;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjPhiLeft(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_phi_left;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjPhiRight(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_phi_right;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjNormVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_norm_velocity_x;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjNormVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_norm_velocity_y;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCObjNormAccelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_norm_acceleration_x;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjProbMoveLong(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_movement_prob_long;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjProbMoveLat(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_movement_prob_lat;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjMovementObserved(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_movement_observed;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjBrakeLight(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_brake_light;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjTurnLight(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_turn_light;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjOncoming(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_oncoming;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjTargetACCType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_target_acc_type;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjReliability(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_reliability;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjMeasSource(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_meas_source;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_type;
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCObjHeadOrientation(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.Obj[obj_nr].o_head_orientation;
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCInputObjectDistX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.get_in_obj_distance_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCInputObjectDistY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.get_in_obj_distance_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCInputObjectVelX(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.get_in_obj_velocity_x(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCInputObjectVelY(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.get_in_obj_velocity_y(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCInputObjectYawAngle(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.get_in_obj_yaw_angle(obj_nr);
    }
    return 0;
}
long CAPLEXPORT CAPLPASCAL appGetVideoFCInputObjectType(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.get_in_obj_type(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCInputObjectWidth(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.get_in_obj_width(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCInputObjectLength(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.get_in_obj_length(obj_nr);
    }
    return 0;
}
double CAPLEXPORT CAPLPASCAL appGetVideoFCInputObjectHeight(uint32_t handle, int obj_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL && obj_nr < maximum_object_quantity)
    {
        return instance->sensor_handler.Video_FC.get_in_obj_height(obj_nr);
    }
    return 0;
}

// ============================================================================
// Offline Analyzer
// Function definitions for the ByteArray handling
// Function names have to start with oa for python environment to identify them correct
// ============================================================================
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6LGU_Radial_Distance(uint8_t byteArray[], int loc_index)
{
    DataHandler byte_array_generator;

    return byte_array_generator.Read_ByteArray_Location_Distance(byteArray,loc_index);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6LGU_Radial_Velocity(uint8_t byteArray[], int loc_index)
{
    DataHandler byte_array_generator;

    return byte_array_generator.Read_ByteArray_Location_Velocity(byteArray,loc_index);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6LGU_Azimuth(uint8_t byteArray[], int loc_index)
{
    DataHandler byte_array_generator;

    return byte_array_generator.Read_ByteArray_Location_Azimuth(byteArray,loc_index);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6LGU_RCS(uint8_t byteArray[], int loc_index)
{
    DataHandler byte_array_generator;

    return byte_array_generator.Read_ByteArray_Location_RCS(byteArray,loc_index);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6LGU_Mounting_Position_X(uint8_t byteArray[])
{
    DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_Mounting_Position_X(byteArray);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6LGU_Mounting_Position_Y(uint8_t byteArray[])
{
    DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_Mounting_Position_Y(byteArray);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6LGU_Mounting_Position_Z(uint8_t byteArray[])
{
    DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_Mounting_Position_Z(byteArray);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6LGU_Mounting_Position_Yaw(uint8_t byteArray[])
{
    DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_Mounting_Position_Yaw(byteArray);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6LGU_Num_Valid_Loc(uint8_t byteArray[])
{
    DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_Num_Valid_Loc(byteArray);
}

double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_Distance_X(uint8_t byteArray[], int obj_index)
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_Distance_X(byteArray,obj_index);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_Distance_Y(uint8_t byteArray[], int obj_index)
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_Distance_Y(byteArray,obj_index);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_Velocity_X(uint8_t byteArray[], int obj_index)
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_Velocity_X(byteArray,obj_index);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_Velocity_Y(uint8_t byteArray[], int obj_index)
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_Velocity_Y(byteArray,obj_index);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_Yaw_Angle(uint8_t byteArray[], int obj_index)
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_Yaw_Angle(byteArray,obj_index);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_RCS(uint8_t byteArray[], int obj_index)
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_RCS(byteArray,obj_index);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_Reference_Point(uint8_t byteArray[], int obj_index)
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_Reference_Point(byteArray,obj_index);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_Mounting_Position_X(uint8_t byteArray[])
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_Mounting_Position_X(byteArray);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_Mounting_Position_Y(uint8_t byteArray[])
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_Mounting_Position_Y(byteArray);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_Mounting_Position_Z(uint8_t byteArray[])
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_Mounting_Position_Z(byteArray);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_Mounting_Position_Yaw(uint8_t byteArray[])
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_Mounting_Position_Yaw(byteArray);
}
double CAPLEXPORT CAPLPASCAL oa_Read_ByteArray_RA6SGU_Num_Valid_Obj(uint8_t byteArray[])
{
    RA6SGU_DataHandler byte_array_generator;
    
    return byte_array_generator.Read_ByteArray_RA6SGU_Num_Valid_Obj(byteArray);
}

// ============================================================================
// CAPL_DLL_INFO_LIST : list of exported functions
//   The first field is predefined and mustn't be changed!
//   The list has to end with a {0,0} entry!
// New struct supporting function names with up to 50 characters
// ============================================================================
CAPL_DLL_INFO4 table[] = {
    {CDLL_VERSION_NAME, (CAPL_FARCALL)CDLL_VERSION, "", "", CAPL_DLL_CDECL, 0xabcd, CDLL_EXPORT},
    {"dllInitRoadObjDll", (CAPL_FARCALL)appInit, "CAPL_DLL", "This function will initialize all callback functions in the CAPLDLL", 'V', 1, "D", "", {"handle"}},
    {"dllEndRoadObjDll", (CAPL_FARCALL)appEnd, "CAPL_DLL", "This function will release the CAPL function handle in the CAPLDLL", 'V', 1, "D", "", {"handle"}},
    {"dllInitRoadObj", (CAPL_FARCALL)appInitRoadObj, "CAPL_DLL", "Initialize basic values of the RoadObj dll", 'V', 3, "DLL", "", {"handle", "simulator", "data_transfer_protocol"}},

    {"dllInputEgoValues", (CAPL_FARCALL)appInputEgoValues, "CAPL_DLL", "This function puts the given data into the definition struct of the ego vehicle", 'L', 3, "DFF", "", {"handle", "velocity_x", "velocity_y"}},
    {"dllCalcAllSensorTargetData", (CAPL_FARCALL)appCalcAllSensorTargetData, "CAPL_DLL", "This function triggers the calculation of the target data for all objects on all sensors", 'L', 1, "D", "", {"handle"}},

    {"dllInputRadarDefinitionsRadarFC", (CAPL_FARCALL)appInputRadarDefinitionsRadarFC, "CAPL_DLL", "This function puts the given data into the definition struct of the radar", 'L', 7, "DLLLLFL", "", {"handle", "loc_model", "loc_distribution_model", "loc_sim_active", "max_nr_loc", "loc_separation_angle", "radar_generation"}},
    {"dllInputRadarDefinitionsRadarFL", (CAPL_FARCALL)appInputRadarDefinitionsRadarFL, "CAPL_DLL", "This function puts the given data into the definition struct of the radar", 'L', 7, "DLLLLFL", "", {"handle", "loc_model", "loc_distribution_model", "loc_sim_active", "max_nr_loc", "loc_separation_angle", "radar_generation"}},
    {"dllInputRadarDefinitionsRadarFR", (CAPL_FARCALL)appInputRadarDefinitionsRadarFR, "CAPL_DLL", "This function puts the given data into the definition struct of the radar", 'L', 7, "DLLLLFL", "", {"handle", "loc_model", "loc_distribution_model", "loc_sim_active", "max_nr_loc", "loc_separation_angle", "radar_generation"}},
    {"dllInputRadarDefinitionsRadarRL", (CAPL_FARCALL)appInputRadarDefinitionsRadarRL, "CAPL_DLL", "This function puts the given data into the definition struct of the radar", 'L', 7, "DLLLLFL", "", {"handle", "loc_model", "loc_distribution_model", "loc_sim_active", "max_nr_loc", "loc_separation_angle", "radar_generation"}},
    {"dllInputRadarDefinitionsRadarRR", (CAPL_FARCALL)appInputRadarDefinitionsRadarRR, "CAPL_DLL", "This function puts the given data into the definition struct of the radar", 'L', 7, "DLLLLFL", "", {"handle", "loc_model", "loc_distribution_model", "loc_sim_active", "max_nr_loc", "loc_separation_angle", "radar_generation"}},
    
    {"dllInputSensorDefinitionsRadarFC", (CAPL_FARCALL)appInputSensorDefinitionsRadarFC, "CAPL_DLL", "This function puts the given data into the definition struct of the sensor", 'L', 9, "DFFFFFLLL", "", {"handle", "mount_dx", "mount_dy", "mount_dz", "mount_yaw", "fov_angle", "validity_sending_active", "obj_sim_active", "loc_sim_active", "loc_model", "obj_count"}},
    {"dllInputSensorDefinitionsRadarFL", (CAPL_FARCALL)appInputSensorDefinitionsRadarFL, "CAPL_DLL", "This function puts the given data into the definition struct of the sensor", 'L', 9, "DFFFFFLLL", "", {"handle", "mount_dx", "mount_dy", "mount_dz", "mount_yaw", "fov_angle", "validity_sending_active", "obj_sim_active", "loc_sim_active", "loc_model", "obj_count"}},
    {"dllInputSensorDefinitionsRadarFR", (CAPL_FARCALL)appInputSensorDefinitionsRadarFR, "CAPL_DLL", "This function puts the given data into the definition struct of the sensor", 'L', 9, "DFFFFFLLL", "", {"handle", "mount_dx", "mount_dy", "mount_dz", "mount_yaw", "fov_angle", "validity_sending_active", "obj_sim_active", "loc_sim_active", "loc_model", "obj_count"}},
    {"dllInputSensorDefinitionsRadarRL", (CAPL_FARCALL)appInputSensorDefinitionsRadarRL, "CAPL_DLL", "This function puts the given data into the definition struct of the sensor", 'L', 9, "DFFFFFLLL", "", {"handle", "mount_dx", "mount_dy", "mount_dz", "mount_yaw", "fov_angle", "validity_sending_active", "obj_sim_active", "loc_sim_active", "loc_model", "obj_count"}},
    {"dllInputSensorDefinitionsRadarRR", (CAPL_FARCALL)appInputSensorDefinitionsRadarRR, "CAPL_DLL", "This function puts the given data into the definition struct of the sensor", 'L', 9, "DFFFFFLLL", "", {"handle", "mount_dx", "mount_dy", "mount_dz", "mount_yaw", "fov_angle", "validity_sending_active", "obj_sim_active", "loc_sim_active", "loc_model", "obj_count"}},
    {"dllInputSensorDefinitionsVideoFC", (CAPL_FARCALL)appInputSensorDefinitionsVideoFC, "CAPL_DLL", "This function puts the given data into the definition struct of the sensor", 'L', 9, "DFFFFFLLL", "", {"handle", "mount_dx", "mount_dy", "mount_dz", "mount_yaw", "fov_angle", "validity_sending_active", "obj_sim_active", "loc_sim_active", "loc_model", "obj_count"}},

    {"dllInputObjectDataRadarFC", (CAPL_FARCALL)appInputObjectDataRadarFC, "CAPL_DLL", "This function puts the given data into the object struct of the sensor", 'L', 18, "DLLLFFFFFFFFFFLFFF", "", {"handle", "obj_id", "sim_on", "sensor_mode", "dx", "dy", "vx", "vy", "ax", "ay", "yaw_angle", "width", "length" ,"height", "type", "rcs", "snr", "rssi"}},
    {"dllInputObjectDataRadarFL", (CAPL_FARCALL)appInputObjectDataRadarFL, "CAPL_DLL", "This function puts the given data into the object struct of the sensor", 'L', 18, "DLLLFFFFFFFFFFLFFF", "", {"handle", "obj_id", "sim_on", "sensor_mode", "dx", "dy", "vx", "vy", "ax", "ay", "yaw_angle", "width", "length" ,"height", "type", "rcs", "snr", "rssi"}},
    {"dllInputObjectDataRadarFR", (CAPL_FARCALL)appInputObjectDataRadarFR, "CAPL_DLL", "This function puts the given data into the object struct of the sensor", 'L', 18, "DLLLFFFFFFFFFFLFFF", "", {"handle", "obj_id", "sim_on", "sensor_mode", "dx", "dy", "vx", "vy", "ax", "ay", "yaw_angle", "width", "length" ,"height", "type", "rcs", "snr", "rssi"}},
    {"dllInputObjectDataRadarRL", (CAPL_FARCALL)appInputObjectDataRadarRL, "CAPL_DLL", "This function puts the given data into the object struct of the sensor", 'L', 18, "DLLLFFFFFFFFFFLFFF", "", {"handle", "obj_id", "sim_on", "sensor_mode", "dx", "dy", "vx", "vy", "ax", "ay", "yaw_angle", "width", "length" ,"height", "type", "rcs", "snr", "rssi"}},
    {"dllInputObjectDataRadarRR", (CAPL_FARCALL)appInputObjectDataRadarRR, "CAPL_DLL", "This function puts the given data into the object struct of the sensor", 'L', 18, "DLLLFFFFFFFFFFLFFF", "", {"handle", "obj_id", "sim_on", "sensor_mode", "dx", "dy", "vx", "vy", "ax", "ay", "yaw_angle", "width", "length" ,"height", "type", "rcs", "snr", "rssi"}},
    {"dllInputObjectDataVideoFC", (CAPL_FARCALL)appInputObjectDataVideoFC, "CAPL_DLL", "This function puts the given data into the object struct of the sensor", 'L', 18, "DLLLFFFFFFFFFFLFFF", "", {"handle", "obj_id", "sim_on", "sensor_mode", "dx", "dy", "vx", "vy", "ax", "ay", "yaw_angle", "width", "length" ,"height", "type", "rcs", "snr", "rssi"}},

    {"dllInputLocationDataRadarFC", (CAPL_FARCALL)appInputLocationDataRadarFC, "CAPL_DLL", "This function puts the given data into the location struct of the sensor", 'L', 9, "DLFFFFFFF", "", {"handle", "loc_id", "radial_distance", "radial_velocity", "elevation", "azimuth", "radar_cross_section", "rssi", "snr"}},
    {"dllInputLocationDataRadarFL", (CAPL_FARCALL)appInputLocationDataRadarFL, "CAPL_DLL", "This function puts the given data into the location struct of the sensor", 'L', 9, "DLFFFFFFF", "", {"handle", "loc_id", "radial_distance", "radial_velocity", "elevation", "azimuth", "radar_cross_section", "rssi", "snr"}},
    {"dllInputLocationDataRadarFR", (CAPL_FARCALL)appInputLocationDataRadarFR, "CAPL_DLL", "This function puts the given data into the location struct of the sensor", 'L', 9, "DLFFFFFFF", "", {"handle", "loc_id", "radial_distance", "radial_velocity", "elevation", "azimuth", "radar_cross_section", "rssi", "snr"}},
    {"dllInputLocationDataRadarRL", (CAPL_FARCALL)appInputLocationDataRadarRL, "CAPL_DLL", "This function puts the given data into the location struct of the sensor", 'L', 9, "DLFFFFFFF", "", {"handle", "loc_id", "radial_distance", "radial_velocity", "elevation", "azimuth", "radar_cross_section", "rssi", "snr"}},
    {"dllInputLocationDataRadarRR", (CAPL_FARCALL)appInputLocationDataRadarRR, "CAPL_DLL", "This function puts the given data into the location struct of the sensor", 'L', 9, "DLFFFFFFF", "", {"handle", "loc_id", "radial_distance", "radial_velocity", "elevation", "azimuth", "radar_cross_section", "rssi", "snr"}},

    {"dllGetTimeToCalculate", (CAPL_FARCALL)appGetTimeToCalculate, "CAPL_DLL", "This function gives back the time to calculate all object and location data for all sensors in microseconds", 'L', 1, "D", "", {"handle"}},

    {"dllGetValidityFlagVideoFC", (CAPL_FARCALL)appGetValidityFlagVideoFC, "CAPL_DLL", "This function gives back the validity flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},
    {"dllGetValidityFlagRadarFC", (CAPL_FARCALL)appGetValidityFlagRadarFC, "CAPL_DLL", "This function gives back the validity flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},
    {"dllGetValidityFlagRadarFL", (CAPL_FARCALL)appGetValidityFlagRadarFL, "CAPL_DLL", "This function gives back the validity flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},
    {"dllGetValidityFlagRadarFR", (CAPL_FARCALL)appGetValidityFlagRadarFR, "CAPL_DLL", "This function gives back the validity flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},
    {"dllGetValidityFlagRadarRL", (CAPL_FARCALL)appGetValidityFlagRadarRL, "CAPL_DLL", "This function gives back the validity flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},
    {"dllGetValidityFlagRadarRR", (CAPL_FARCALL)appGetValidityFlagRadarRR, "CAPL_DLL", "This function gives back the validity flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},

    {"dllGetEmptyFlagRadarFC", (CAPL_FARCALL)appGetEmptyFlagRadarFC, "CAPL_DLL", "This function gives back the empty flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},
    {"dllGetEmptyFlagRadarFL", (CAPL_FARCALL)appGetEmptyFlagRadarFL, "CAPL_DLL", "This function gives back the empty flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},
    {"dllGetEmptyFlagRadarFR", (CAPL_FARCALL)appGetEmptyFlagRadarFR, "CAPL_DLL", "This function gives back the empty flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},
    {"dllGetEmptyFlagRadarRL", (CAPL_FARCALL)appGetEmptyFlagRadarRL, "CAPL_DLL", "This function gives back the empty flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},
    {"dllGetEmptyFlagRadarRR", (CAPL_FARCALL)appGetEmptyFlagRadarRR, "CAPL_DLL", "This function gives back the empty flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},
    {"dllGetEmptyFlagVideoFC", (CAPL_FARCALL)appGetEmptyFlagVideoFC, "CAPL_DLL", "This function gives back the empty flag of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_id"}},

    {"dllGetRadarFCValidObjCount", (CAPL_FARCALL)appGetRadarFCValidObjCount, "CAPL_DLL", "This function gives back the number of calculated valid objects", 'L', 1, "D", "", {"handle"}},
    {"dllGetRadarFCValidLocCount", (CAPL_FARCALL)appGetRadarFCValidLocCount, "CAPL_DLL", "This function gives back the number of calculated valid locations", 'L', 1, "D", "", {"handle"}},
    {"dllGetRadarFCLocRadialDistance", (CAPL_FARCALL)appGetRadarFCLocRadialDistance, "CAPL_DLL", "This function gives back the radial distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFCLocRadialVelocity", (CAPL_FARCALL)appGetRadarFCLocRadialVelocity, "CAPL_DLL", "This function gives back the radial velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFCLocAzimuthAngle", (CAPL_FARCALL)appGetRadarFCLocAzimuthAngle, "CAPL_DLL", "This function gives back the azimuth angle of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFCLocElevationAngle", (CAPL_FARCALL)appGetRadarFCLocElevationAngle, "CAPL_DLL", "This function gives back the elevation angle of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFCLocRCS", (CAPL_FARCALL)appGetRadarFCLocRCS, "CAPL_DLL", "This function gives back the RCS value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFCLocRSSI", (CAPL_FARCALL)appGetRadarFCLocRSSI, "CAPL_DLL", "This function gives back the RSSI value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFCLocSNR", (CAPL_FARCALL)appGetRadarFCLocSNR, "CAPL_DLL", "This function gives back the Signal to Noise Ratio value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFCObjDistX", (CAPL_FARCALL)appGetRadarFCObjDistX, "CAPL_DLL", "This function gives back the longitudinal distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjDistY", (CAPL_FARCALL)appGetRadarFCObjDistY, "CAPL_DLL", "This function gives back the lateral distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjVelX", (CAPL_FARCALL)appGetRadarFCObjVelX, "CAPL_DLL", "This function gives back the longitudinal velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjVelY", (CAPL_FARCALL)appGetRadarFCObjVelY, "CAPL_DLL", "This function gives back the lateral velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjAccelX", (CAPL_FARCALL)appGetRadarFCObjAccelX, "CAPL_DLL", "This function gives back the longitudinal velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjAccelY", (CAPL_FARCALL)appGetRadarFCObjAccelY, "CAPL_DLL", "This function gives back the lateral velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjYawAngle", (CAPL_FARCALL)appGetRadarFCObjYawAngle, "CAPL_DLL", "This function gives back the yaw angle of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjRefPnt", (CAPL_FARCALL)appGetRadarFCObjRefPnt, "CAPL_DLL", "This function gives back the reference point of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjProbMoving", (CAPL_FARCALL)appGetRadarFCObjProbMoving, "CAPL_DLL", "This function gives back the probability the target to be moving of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjProbStationary", (CAPL_FARCALL)appGetRadarFCObjProbStationary, "CAPL_DLL", "This function gives back the probability the target to be stationary of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjProbNonObst", (CAPL_FARCALL)appGetRadarFCObjProbNonObst, "CAPL_DLL", "This function gives back the probability the target to be a non obstacle of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjProbTruck", (CAPL_FARCALL)appGetRadarFCObjProbTruck, "CAPL_DLL", "This function gives back the probability the target to be a truck of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjProbCar", (CAPL_FARCALL)appGetRadarFCObjProbCar, "CAPL_DLL", "This function gives back the probability the target to be a car of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjProb2Wheeler", (CAPL_FARCALL)appGetRadarFCObjProb2Wheeler, "CAPL_DLL", "This function gives back the probability the target to be a 2wheeler of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjProbPedestrian", (CAPL_FARCALL)appGetRadarFCObjProbPedestrian, "CAPL_DLL", "This function gives back the probability the target to be a pedestrian of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjRa6RCS", (CAPL_FARCALL)appGetRadarFCObjRa6RCS, "CAPL_DLL", "This function gives back the radar cross section of the target with the given ID according to the radar gen6", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjRa6ObjType", (CAPL_FARCALL)appGetRadarFCObjRa6ObjType, "CAPL_DLL", "This function gives back the object type of the target with the given ID according to the radar gen6", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCObjRa6MovingStatus", (CAPL_FARCALL)appGetRadarFCObjRa6MovingStatus, "CAPL_DLL", "This function gives back the moving status of the target with the given ID according to the radar gen6", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCInputObjectDistX", (CAPL_FARCALL)appGetRadarFCInputObjectDistX, "CAPL_DLL", "This function gives back the longitudinal distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCInputObjectDistY", (CAPL_FARCALL)appGetRadarFCInputObjectDistY, "CAPL_DLL", "This function gives back the lateral distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCInputObjectVelX", (CAPL_FARCALL)appGetRadarFCInputObjectVelX, "CAPL_DLL", "This function gives back the longitudinal velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCInputObjectVelY", (CAPL_FARCALL)appGetRadarFCInputObjectVelY, "CAPL_DLL", "This function gives back the lateral velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCInputObjectYawAngle", (CAPL_FARCALL)appGetRadarFCInputObjectYawAngle, "CAPL_DLL", "This function gives back the yaw angle input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCInputObjectType", (CAPL_FARCALL)appGetRadarFCInputObjectType, "CAPL_DLL", "This function gives back the type input data of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCInputObjectWidth", (CAPL_FARCALL)appGetRadarFCInputObjectWidth, "CAPL_DLL", "This function gives back the width input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCInputObjectLength", (CAPL_FARCALL)appGetRadarFCInputObjectLength, "CAPL_DLL", "This function gives back the length input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCInputObjectHeight", (CAPL_FARCALL)appGetRadarFCInputObjectHeight, "CAPL_DLL", "This function gives back the height input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFCByteArray", (CAPL_FARCALL)appGetRadarFCByteArray, "CAPL_DLL", "This function gives back the CAN TP byte array created using all the calculated locations", 'L', 2, "DB", "\000\001", {"handle", "byte_array"}},
    {"dllResetByteArrayRadarFC", (CAPL_FARCALL)appResetByteArrayRadarFC, "CAPL_DLL", "This function resets the byte array of the specific sensor", 'L', 1, "D", "", {"handle"}},

    {"dllGetRadarFLValidObjCount", (CAPL_FARCALL)appGetRadarFLValidObjCount, "CAPL_DLL", "This function gives back the number of calculated valid objects", 'L', 1, "D", "", {"handle"}},
    {"dllGetRadarFLValidLocCount", (CAPL_FARCALL)appGetRadarFLValidLocCount, "CAPL_DLL", "This function gives back the number of calculated valid locations", 'L', 1, "D", "", {"handle"}},
    {"dllGetRadarFLLocRadialDistance", (CAPL_FARCALL)appGetRadarFLLocRadialDistance, "CAPL_DLL", "This function gives back the radial distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFLLocRadialVelocity", (CAPL_FARCALL)appGetRadarFLLocRadialVelocity, "CAPL_DLL", "This function gives back the radial velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFLLocAzimuthAngle", (CAPL_FARCALL)appGetRadarFLLocAzimuthAngle, "CAPL_DLL", "This function gives back the azimuth angle of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFLLocElevationAngle", (CAPL_FARCALL)appGetRadarFLLocElevationAngle, "CAPL_DLL", "This function gives back the elevation angle of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFLLocRCS", (CAPL_FARCALL)appGetRadarFLLocRCS, "CAPL_DLL", "This function gives back the RCS value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFLLocRSSI", (CAPL_FARCALL)appGetRadarFLLocRSSI, "CAPL_DLL", "This function gives back the RSSI value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFLLocSNR", (CAPL_FARCALL)appGetRadarFLLocSNR, "CAPL_DLL", "This function gives back the Signal to Noise Ratio value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFLObjDistX", (CAPL_FARCALL)appGetRadarFLObjDistX, "CAPL_DLL", "This function gives back the longitudinal distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjDistY", (CAPL_FARCALL)appGetRadarFLObjDistY, "CAPL_DLL", "This function gives back the lateral distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjVelX", (CAPL_FARCALL)appGetRadarFLObjVelX, "CAPL_DLL", "This function gives back the longitudinal velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjVelY", (CAPL_FARCALL)appGetRadarFLObjVelY, "CAPL_DLL", "This function gives back the lateral velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjAccelX", (CAPL_FARCALL)appGetRadarFLObjAccelX, "CAPL_DLL", "This function gives back the longitudinal velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjAccelY", (CAPL_FARCALL)appGetRadarFLObjAccelY, "CAPL_DLL", "This function gives back the lateral velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjYawAngle", (CAPL_FARCALL)appGetRadarFLObjYawAngle, "CAPL_DLL", "This function gives back the yaw angle of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjRefPnt", (CAPL_FARCALL)appGetRadarFLObjRefPnt, "CAPL_DLL", "This function gives back the reference point of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjProbMoving", (CAPL_FARCALL)appGetRadarFLObjProbMoving, "CAPL_DLL", "This function gives back the probability the target to be moving of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjProbStationary", (CAPL_FARCALL)appGetRadarFLObjProbStationary, "CAPL_DLL", "This function gives back the probability the target to be stationary of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjProbNonObst", (CAPL_FARCALL)appGetRadarFLObjProbNonObst, "CAPL_DLL", "This function gives back the probability the target to be a non obstacle of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjProbTruck", (CAPL_FARCALL)appGetRadarFLObjProbTruck, "CAPL_DLL", "This function gives back the probability the target to be a truck of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjProbCar", (CAPL_FARCALL)appGetRadarFLObjProbCar, "CAPL_DLL", "This function gives back the probability the target to be a car of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjProb2Wheeler", (CAPL_FARCALL)appGetRadarFLObjProb2Wheeler, "CAPL_DLL", "This function gives back the probability the target to be a 2wheeler of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjProbPedestrian", (CAPL_FARCALL)appGetRadarFLObjProbPedestrian, "CAPL_DLL", "This function gives back the probability the target to be a pedestrian of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjRa6RCS", (CAPL_FARCALL)appGetRadarFLObjRa6RCS, "CAPL_DLL", "This function gives back the radar cross section of the target with the given ID according to the radar gen6", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjRa6ObjType", (CAPL_FARCALL)appGetRadarFLObjRa6ObjType, "CAPL_DLL", "This function gives back the object type of the target with the given ID according to the radar gen6", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLObjRa6MovingStatus", (CAPL_FARCALL)appGetRadarFLObjRa6MovingStatus, "CAPL_DLL", "This function gives back the moving status of the target with the given ID according to the radar gen6", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLInputObjectDistX", (CAPL_FARCALL)appGetRadarFLInputObjectDistX, "CAPL_DLL", "This function gives back the longitudinal distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLInputObjectDistY", (CAPL_FARCALL)appGetRadarFLInputObjectDistY, "CAPL_DLL", "This function gives back the lateral distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLInputObjectVelX", (CAPL_FARCALL)appGetRadarFLInputObjectVelX, "CAPL_DLL", "This function gives back the longitudinal velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLInputObjectVelY", (CAPL_FARCALL)appGetRadarFLInputObjectVelY, "CAPL_DLL", "This function gives back the lateral velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLInputObjectYawAngle", (CAPL_FARCALL)appGetRadarFLInputObjectYawAngle, "CAPL_DLL", "This function gives back the yaw angle input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLInputObjectType", (CAPL_FARCALL)appGetRadarFLInputObjectType, "CAPL_DLL", "This function gives back the type input data of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLInputObjectWidth", (CAPL_FARCALL)appGetRadarFLInputObjectWidth, "CAPL_DLL", "This function gives back the width input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLInputObjectLength", (CAPL_FARCALL)appGetRadarFLInputObjectLength, "CAPL_DLL", "This function gives back the length input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLInputObjectHeight", (CAPL_FARCALL)appGetRadarFLInputObjectHeight, "CAPL_DLL", "This function gives back the height input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFLByteArray", (CAPL_FARCALL)appGetRadarFLByteArray, "CAPL_DLL", "This function gives back the CAN TP byte array created using all the calculated locations", 'L', 2, "DB", "\000\001", {"handle", "byte_array"}},
    {"dllResetByteArrayRadarFL", (CAPL_FARCALL)appResetByteArrayRadarFL, "CAPL_DLL", "This function resets the byte array of the specific sensor", 'L', 1, "D", "", {"handle"}},
    
    {"dllGetRadarFRValidObjCount", (CAPL_FARCALL)appGetRadarFRValidObjCount, "CAPL_DLL", "This function gives back the number of calculated valid objects", 'L', 1, "D", "", {"handle"}},
    {"dllGetRadarFRValidLocCount", (CAPL_FARCALL)appGetRadarFRValidLocCount, "CAPL_DLL", "This function gives back the number of calculated valid locations", 'L', 1, "D", "", {"handle"}},
    {"dllGetRadarFRLocRadialDistance", (CAPL_FARCALL)appGetRadarFRLocRadialDistance, "CAPL_DLL", "This function gives back the radial distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFRLocRadialVelocity", (CAPL_FARCALL)appGetRadarFRLocRadialVelocity, "CAPL_DLL", "This function gives back the radial velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFRLocAzimuthAngle", (CAPL_FARCALL)appGetRadarFRLocAzimuthAngle, "CAPL_DLL", "This function gives back the azimuth angle of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFRLocElevationAngle", (CAPL_FARCALL)appGetRadarFRLocElevationAngle, "CAPL_DLL", "This function gives back the elevation angle of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFRLocRCS", (CAPL_FARCALL)appGetRadarFRLocRCS, "CAPL_DLL", "This function gives back the RCS value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFRLocRSSI", (CAPL_FARCALL)appGetRadarFRLocRSSI, "CAPL_DLL", "This function gives back the RSSI value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFRLocSNR", (CAPL_FARCALL)appGetRadarFRLocSNR, "CAPL_DLL", "This function gives back the Signal to Noise Ratio value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarFRObjDistX", (CAPL_FARCALL)appGetRadarFRObjDistX, "CAPL_DLL", "This function gives back the longitudinal distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjDistY", (CAPL_FARCALL)appGetRadarFRObjDistY, "CAPL_DLL", "This function gives back the lateral distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjVelX", (CAPL_FARCALL)appGetRadarFRObjVelX, "CAPL_DLL", "This function gives back the longitudinal velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjVelY", (CAPL_FARCALL)appGetRadarFRObjVelY, "CAPL_DLL", "This function gives back the lateral velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjAccelX", (CAPL_FARCALL)appGetRadarFRObjAccelX, "CAPL_DLL", "This function gives back the longitudinal velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjAccelY", (CAPL_FARCALL)appGetRadarFRObjAccelY, "CAPL_DLL", "This function gives back the lateral velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjYawAngle", (CAPL_FARCALL)appGetRadarFRObjYawAngle, "CAPL_DLL", "This function gives back the yaw angle of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjRefPnt", (CAPL_FARCALL)appGetRadarFRObjRefPnt, "CAPL_DLL", "This function gives back the reference point of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjProbMoving", (CAPL_FARCALL)appGetRadarFRObjProbMoving, "CAPL_DLL", "This function gives back the probability the target to be moving of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjProbStationary", (CAPL_FARCALL)appGetRadarFRObjProbStationary, "CAPL_DLL", "This function gives back the probability the target to be stationary of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjProbNonObst", (CAPL_FARCALL)appGetRadarFRObjProbNonObst, "CAPL_DLL", "This function gives back the probability the target to be a non obstacle of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjProbTruck", (CAPL_FARCALL)appGetRadarFRObjProbTruck, "CAPL_DLL", "This function gives back the probability the target to be a truck of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjProbCar", (CAPL_FARCALL)appGetRadarFRObjProbCar, "CAPL_DLL", "This function gives back the probability the target to be a car of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjProb2Wheeler", (CAPL_FARCALL)appGetRadarFRObjProb2Wheeler, "CAPL_DLL", "This function gives back the probability the target to be a 2wheeler of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjProbPedestrian", (CAPL_FARCALL)appGetRadarFRObjProbPedestrian, "CAPL_DLL", "This function gives back the probability the target to be a pedestrian of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjRa6RCS", (CAPL_FARCALL)appGetRadarFRObjRa6RCS, "CAPL_DLL", "This function gives back the radar cross section of the target with the given ID according to the radar gen6", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjRa6ObjType", (CAPL_FARCALL)appGetRadarFRObjRa6ObjType, "CAPL_DLL", "This function gives back the object type of the target with the given ID according to the radar gen6", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRObjRa6MovingStatus", (CAPL_FARCALL)appGetRadarFRObjRa6MovingStatus, "CAPL_DLL", "This function gives back the moving status of the target with the given ID according to the radar gen6", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRInputObjectDistX", (CAPL_FARCALL)appGetRadarFRInputObjectDistX, "CAPL_DLL", "This function gives back the longitudinal distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRInputObjectDistY", (CAPL_FARCALL)appGetRadarFRInputObjectDistY, "CAPL_DLL", "This function gives back the lateral distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRInputObjectVelX", (CAPL_FARCALL)appGetRadarFRInputObjectVelX, "CAPL_DLL", "This function gives back the longitudinal velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRInputObjectVelY", (CAPL_FARCALL)appGetRadarFRInputObjectVelY, "CAPL_DLL", "This function gives back the lateral velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRInputObjectYawAngle", (CAPL_FARCALL)appGetRadarFRInputObjectYawAngle, "CAPL_DLL", "This function gives back the yaw angle input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRInputObjectType", (CAPL_FARCALL)appGetRadarFRInputObjectType, "CAPL_DLL", "This function gives back the type input data of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRInputObjectWidth", (CAPL_FARCALL)appGetRadarFRInputObjectWidth, "CAPL_DLL", "This function gives back the width input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRInputObjectLength", (CAPL_FARCALL)appGetRadarFRInputObjectLength, "CAPL_DLL", "This function gives back the length input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRInputObjectHeight", (CAPL_FARCALL)appGetRadarFRInputObjectHeight, "CAPL_DLL", "This function gives back the height input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarFRByteArray", (CAPL_FARCALL)appGetRadarFRByteArray, "CAPL_DLL", "This function gives back the CAN TP byte array created using all the calculated locations", 'L', 2, "DB", "\000\001", {"handle", "byte_array"}},
    {"dllResetByteArrayRadarFR", (CAPL_FARCALL)appResetByteArrayRadarFR, "CAPL_DLL", "This function resets the byte array of the specific sensor", 'L', 1, "D", "", {"handle"}},
    
    {"dllGetRadarRLValidObjCount", (CAPL_FARCALL)appGetRadarRLValidObjCount, "CAPL_DLL", "This function gives back the number of calculated valid objects", 'L', 1, "D", "", {"handle"}},
    {"dllGetRadarRLValidLocCount", (CAPL_FARCALL)appGetRadarRLValidLocCount, "CAPL_DLL", "This function gives back the number of calculated valid locations", 'L', 1, "D", "", {"handle"}},
    {"dllGetRadarRLLocRadialDistance", (CAPL_FARCALL)appGetRadarRLLocRadialDistance, "CAPL_DLL", "This function gives back the radial distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRLLocRadialVelocity", (CAPL_FARCALL)appGetRadarRLLocRadialVelocity, "CAPL_DLL", "This function gives back the radial velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRLLocAzimuthAngle", (CAPL_FARCALL)appGetRadarRLLocAzimuthAngle, "CAPL_DLL", "This function gives back the azimuth angle of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRLLocElevationAngle", (CAPL_FARCALL)appGetRadarRLLocElevationAngle, "CAPL_DLL", "This function gives back the elevation angle of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRLLocRCS", (CAPL_FARCALL)appGetRadarRLLocRCS, "CAPL_DLL", "This function gives back the RCS value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRLLocRSSI", (CAPL_FARCALL)appGetRadarRLLocRSSI, "CAPL_DLL", "This function gives back the RSSI value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRLLocSNR", (CAPL_FARCALL)appGetRadarRLLocSNR, "CAPL_DLL", "This function gives back the Signal to Noise Ratio value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRLObjDistX", (CAPL_FARCALL)appGetRadarRLObjDistX, "CAPL_DLL", "This function gives back the longitudinal distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjDistY", (CAPL_FARCALL)appGetRadarRLObjDistY, "CAPL_DLL", "This function gives back the lateral distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjVelX", (CAPL_FARCALL)appGetRadarRLObjVelX, "CAPL_DLL", "This function gives back the longitudinal velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjVelY", (CAPL_FARCALL)appGetRadarRLObjVelY, "CAPL_DLL", "This function gives back the lateral velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjAccelX", (CAPL_FARCALL)appGetRadarRLObjAccelX, "CAPL_DLL", "This function gives back the longitudinal velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjAccelY", (CAPL_FARCALL)appGetRadarRLObjAccelY, "CAPL_DLL", "This function gives back the lateral velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjYawAngle", (CAPL_FARCALL)appGetRadarRLObjYawAngle, "CAPL_DLL", "This function gives back the yaw angle of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjRefPnt", (CAPL_FARCALL)appGetRadarRLObjRefPnt, "CAPL_DLL", "This function gives back the reference point of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjProbMoving", (CAPL_FARCALL)appGetRadarRLObjProbMoving, "CAPL_DLL", "This function gives back the probability the target to be moving of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjProbStationary", (CAPL_FARCALL)appGetRadarRLObjProbStationary, "CAPL_DLL", "This function gives back the probability the target to be stationary of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjProbNonObst", (CAPL_FARCALL)appGetRadarRLObjProbNonObst, "CAPL_DLL", "This function gives back the probability the target to be a non obstacle of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjProbTruck", (CAPL_FARCALL)appGetRadarRLObjProbTruck, "CAPL_DLL", "This function gives back the probability the target to be a truck of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjProbCar", (CAPL_FARCALL)appGetRadarRLObjProbCar, "CAPL_DLL", "This function gives back the probability the target to be a car of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjProb2Wheeler", (CAPL_FARCALL)appGetRadarRLObjProb2Wheeler, "CAPL_DLL", "This function gives back the probability the target to be a 2wheeler of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjProbPedestrian", (CAPL_FARCALL)appGetRadarRLObjProbPedestrian, "CAPL_DLL", "This function gives back the probability the target to be a pedestrian of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjRa6RCS", (CAPL_FARCALL)appGetRadarRLObjRa6RCS, "CAPL_DLL", "This function gives back the radar cross section of the target with the given ID according to the radar gen6", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjRa6ObjType", (CAPL_FARCALL)appGetRadarRLObjRa6ObjType, "CAPL_DLL", "This function gives back the object type of the target with the given ID according to the radar gen6", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLObjRa6MovingStatus", (CAPL_FARCALL)appGetRadarRLObjRa6MovingStatus, "CAPL_DLL", "This function gives back the moving status of the target with the given ID according to the radar gen6", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLInputObjectDistX", (CAPL_FARCALL)appGetRadarRLInputObjectDistX, "CAPL_DLL", "This function gives back the longitudinal distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLInputObjectDistY", (CAPL_FARCALL)appGetRadarRLInputObjectDistY, "CAPL_DLL", "This function gives back the lateral distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLInputObjectVelX", (CAPL_FARCALL)appGetRadarRLInputObjectVelX, "CAPL_DLL", "This function gives back the longitudinal velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLInputObjectVelY", (CAPL_FARCALL)appGetRadarRLInputObjectVelY, "CAPL_DLL", "This function gives back the lateral velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLInputObjectYawAngle", (CAPL_FARCALL)appGetRadarRLInputObjectYawAngle, "CAPL_DLL", "This function gives back the yaw angle input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLInputObjectType", (CAPL_FARCALL)appGetRadarRLInputObjectType, "CAPL_DLL", "This function gives back the type input data of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLInputObjectWidth", (CAPL_FARCALL)appGetRadarRLInputObjectWidth, "CAPL_DLL", "This function gives back the width input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLInputObjectLength", (CAPL_FARCALL)appGetRadarRLInputObjectLength, "CAPL_DLL", "This function gives back the length input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLInputObjectHeight", (CAPL_FARCALL)appGetRadarRLInputObjectHeight, "CAPL_DLL", "This function gives back the height input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRLByteArray", (CAPL_FARCALL)appGetRadarRLByteArray, "CAPL_DLL", "This function gives back the CAN TP byte array created using all the calculated locations", 'L', 2, "DB", "\000\001", {"handle", "byte_array"}},
    {"dllResetByteArrayRadarRL", (CAPL_FARCALL)appResetByteArrayRadarRL, "CAPL_DLL", "This function resets the byte array of the specific sensor", 'L', 1, "D", "", {"handle"}},
    
    {"dllGetRadarRRValidObjCount", (CAPL_FARCALL)appGetRadarRRValidObjCount, "CAPL_DLL", "This function gives back the number of calculated valid objects", 'L', 1, "D", "", {"handle"}},
    {"dllGetRadarRRValidLocCount", (CAPL_FARCALL)appGetRadarRRValidLocCount, "CAPL_DLL", "This function gives back the number of calculated valid locations", 'L', 1, "D", "", {"handle"}},
    {"dllGetRadarRRLocRadialDistance", (CAPL_FARCALL)appGetRadarRRLocRadialDistance, "CAPL_DLL", "This function gives back the radial distance of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRRLocRadialVelocity", (CAPL_FARCALL)appGetRadarRRLocRadialVelocity, "CAPL_DLL", "This function gives back the radial velocity of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRRLocAzimuthAngle", (CAPL_FARCALL)appGetRadarRRLocAzimuthAngle, "CAPL_DLL", "This function gives back the azimuth angle of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRRLocElevationAngle", (CAPL_FARCALL)appGetRadarRRLocElevationAngle, "CAPL_DLL", "This function gives back the elevation angle of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRRLocRCS", (CAPL_FARCALL)appGetRadarRRLocRCS, "CAPL_DLL", "This function gives back the RCS value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRRLocRSSI", (CAPL_FARCALL)appGetRadarRRLocRSSI, "CAPL_DLL", "This function gives back the RSSI value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRRLocSNR", (CAPL_FARCALL)appGetRadarRRLocSNR, "CAPL_DLL", "This function gives back the Signal to Noise Ratio value of the location with the given ID", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetRadarRRObjDistX", (CAPL_FARCALL)appGetRadarRRObjDistX, "CAPL_DLL", "This function gives back the longitudinal distance of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjDistY", (CAPL_FARCALL)appGetRadarRRObjDistY, "CAPL_DLL", "This function gives back the lateral distance of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjVelX", (CAPL_FARCALL)appGetRadarRRObjVelX, "CAPL_DLL", "This function gives back the longitudinal velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjVelY", (CAPL_FARCALL)appGetRadarRRObjVelY, "CAPL_DLL", "This function gives back the lateral velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjAccelX", (CAPL_FARCALL)appGetRadarRRObjAccelX, "CAPL_DLL", "This function gives back the longitudinal velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjAccelY", (CAPL_FARCALL)appGetRadarRRObjAccelY, "CAPL_DLL", "This function gives back the lateral velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjYawAngle", (CAPL_FARCALL)appGetRadarRRObjYawAngle, "CAPL_DLL", "This function gives back the yaw angle of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjRefPnt", (CAPL_FARCALL)appGetRadarRRObjRefPnt, "CAPL_DLL", "This function gives back the reference point of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjProbMoving", (CAPL_FARCALL)appGetRadarRRObjProbMoving, "CAPL_DLL", "This function gives back the probability the target to be moving of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjProbStationary", (CAPL_FARCALL)appGetRadarRRObjProbStationary, "CAPL_DLL", "This function gives back the probability the target to be stationary of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjProbNonObst", (CAPL_FARCALL)appGetRadarRRObjProbNonObst, "CAPL_DLL", "This function gives back the probability the target to be a non obstacle of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjProbTruck", (CAPL_FARCALL)appGetRadarRRObjProbTruck, "CAPL_DLL", "This function gives back the probability the target to be a truck of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjProbCar", (CAPL_FARCALL)appGetRadarRRObjProbCar, "CAPL_DLL", "This function gives back the probability the target to be a car of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjProb2Wheeler", (CAPL_FARCALL)appGetRadarRRObjProb2Wheeler, "CAPL_DLL", "This function gives back the probability the target to be a 2wheeler of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjProbPedestrian", (CAPL_FARCALL)appGetRadarRRObjProbPedestrian, "CAPL_DLL", "This function gives back the probability the target to be a pedestrian of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjRa6RCS", (CAPL_FARCALL)appGetRadarRRObjRa6RCS, "CAPL_DLL", "This function gives back the radar cross section of the target with the given ID according to the radar gen6", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjRa6ObjType", (CAPL_FARCALL)appGetRadarRRObjRa6ObjType, "CAPL_DLL", "This function gives back the object type of the target with the given ID according to the radar gen6", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRObjRa6MovingStatus", (CAPL_FARCALL)appGetRadarRRObjRa6MovingStatus, "CAPL_DLL", "This function gives back the moving status of the target with the given ID according to the radar gen6", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRInputObjectDistX", (CAPL_FARCALL)appGetRadarRRInputObjectDistX, "CAPL_DLL", "This function gives back the longitudinal distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRInputObjectDistY", (CAPL_FARCALL)appGetRadarRRInputObjectDistY, "CAPL_DLL", "This function gives back the lateral distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRInputObjectVelX", (CAPL_FARCALL)appGetRadarRRInputObjectVelX, "CAPL_DLL", "This function gives back the longitudinal velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRInputObjectVelY", (CAPL_FARCALL)appGetRadarRRInputObjectVelY, "CAPL_DLL", "This function gives back the lateral velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRInputObjectYawAngle", (CAPL_FARCALL)appGetRadarRRInputObjectYawAngle, "CAPL_DLL", "This function gives back the yaw angle input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRInputObjectType", (CAPL_FARCALL)appGetRadarRRInputObjectType, "CAPL_DLL", "This function gives back the type input data of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRInputObjectWidth", (CAPL_FARCALL)appGetRadarRRInputObjectWidth, "CAPL_DLL", "This function gives back the width input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRInputObjectLength", (CAPL_FARCALL)appGetRadarRRInputObjectLength, "CAPL_DLL", "This function gives back the length input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRInputObjectHeight", (CAPL_FARCALL)appGetRadarRRInputObjectHeight, "CAPL_DLL", "This function gives back the height input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetRadarRRByteArray", (CAPL_FARCALL)appGetRadarRRByteArray, "CAPL_DLL", "This function gives back the CAN TP byte array created using all the calculated locations", 'L', 2, "DB", "\000\001", {"handle", "byte_array"}},
    {"dllResetByteArrayRadarRR", (CAPL_FARCALL)appResetByteArrayRadarRR, "CAPL_DLL", "This function resets the byte array of the specific sensor", 'L', 1, "D", "", {"handle"}},

    {"dllGetVideoFCValidObjCount", (CAPL_FARCALL)appGetVideoFCValidObjCount, "CAPL_DLL", "This function gives back the number of calculated valid objects", 'L', 1, "D", "", {"handle"}},
    {"dllGetVideoFCObjDistX", (CAPL_FARCALL)appGetVideoFCObjDistX, "CAPL_DLL", "This function gives back the longitudinal distance of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjDistY", (CAPL_FARCALL)appGetVideoFCObjDistY, "CAPL_DLL", "This function gives back the lateral distance of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjVelX", (CAPL_FARCALL)appGetVideoFCObjVelX, "CAPL_DLL", "This function gives back the longitudinal velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjVelY", (CAPL_FARCALL)appGetVideoFCObjVelY, "CAPL_DLL", "This function gives back the lateral velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjAccelX", (CAPL_FARCALL)appGetVideoFCObjAccelX, "CAPL_DLL", "This function gives back the longitudinal acceleration of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjAccelY", (CAPL_FARCALL)appGetVideoFCObjAccelY, "CAPL_DLL", "This function gives back the lateral acceleration of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjYawAngle", (CAPL_FARCALL)appGetVideoFCObjYawAngle, "CAPL_DLL", "This function gives back the yaw angle of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjVisibleView", (CAPL_FARCALL)appGetVideoFCObjVisibleView, "CAPL_DLL", "This function gives back the visible view on the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjClassifiedView", (CAPL_FARCALL)appGetVideoFCObjClassifiedView, "CAPL_DLL", "This function gives back the classified view on the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjPhiTop", (CAPL_FARCALL)appGetVideoFCObjPhiTop, "CAPL_DLL", "This function gives back the phi top edge of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjPhiMid", (CAPL_FARCALL)appGetVideoFCObjPhiMid, "CAPL_DLL", "This function gives back the phi mid edge of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjPhiBottom", (CAPL_FARCALL)appGetVideoFCObjPhiBottom, "CAPL_DLL", "This function gives back the phi bottom edge of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjPhiLeft", (CAPL_FARCALL)appGetVideoFCObjPhiLeft, "CAPL_DLL", "This function gives back the phi left edge of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjPhiRight", (CAPL_FARCALL)appGetVideoFCObjPhiRight, "CAPL_DLL", "This function gives back the phi right edge of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjNormVelX", (CAPL_FARCALL)appGetVideoFCObjNormVelX, "CAPL_DLL", "This function gives back the longitudinal normalized velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjNormVelY", (CAPL_FARCALL)appGetVideoFCObjNormVelY, "CAPL_DLL", "This function gives back the lateral normalized velocity of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjNormAccelX", (CAPL_FARCALL)appGetVideoFCObjNormAccelX, "CAPL_DLL", "This function gives back the longitudinal normalized acceleration of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjProbMoveLong", (CAPL_FARCALL)appGetVideoFCObjProbMoveLong, "CAPL_DLL", "This function gives back the longitudinal moving probability of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjProbMoveLat", (CAPL_FARCALL)appGetVideoFCObjProbMoveLat, "CAPL_DLL", "This function gives back the lateral moving probability of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjMovementObserved", (CAPL_FARCALL)appGetVideoFCObjMovementObserved, "CAPL_DLL", "This function gives back if movement was observed of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjBrakeLight", (CAPL_FARCALL)appGetVideoFCObjBrakeLight, "CAPL_DLL", "This function gives back the brake light of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjTurnLight", (CAPL_FARCALL)appGetVideoFCObjTurnLight, "CAPL_DLL", "This function gives back the turn light of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjOncoming", (CAPL_FARCALL)appGetVideoFCObjOncoming, "CAPL_DLL", "This function gives back the flag if the object with the given ID is oncoming", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjTargetACCType", (CAPL_FARCALL)appGetVideoFCObjTargetACCType, "CAPL_DLL", "This function gives back the ACC type of the target of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjReliability", (CAPL_FARCALL)appGetVideoFCObjReliability, "CAPL_DLL", "This function gives back the reliability of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjMeasSource", (CAPL_FARCALL)appGetVideoFCObjMeasSource, "CAPL_DLL", "This function gives back the meas source of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjType", (CAPL_FARCALL)appGetVideoFCObjType, "CAPL_DLL", "This function gives back the video specific type of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCObjHeadOrientation", (CAPL_FARCALL)appGetVideoFCObjHeadOrientation, "CAPL_DLL", "This function gives back the video specific head orientation of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCInputObjectDistX", (CAPL_FARCALL)appGetVideoFCInputObjectDistX, "CAPL_DLL", "This function gives back the longitudinal distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCInputObjectDistY", (CAPL_FARCALL)appGetVideoFCInputObjectDistY, "CAPL_DLL", "This function gives back the lateral distance input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCInputObjectVelX", (CAPL_FARCALL)appGetVideoFCInputObjectVelX, "CAPL_DLL", "This function gives back the longitudinal velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCInputObjectVelY", (CAPL_FARCALL)appGetVideoFCInputObjectVelY, "CAPL_DLL", "This function gives back the lateral velocity input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCInputObjectYawAngle", (CAPL_FARCALL)appGetVideoFCInputObjectYawAngle, "CAPL_DLL", "This function gives back the yaw angle input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCInputObjectType", (CAPL_FARCALL)appGetVideoFCInputObjectType, "CAPL_DLL", "This function gives back the type input data of the object with the given ID", 'L', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCInputObjectWidth", (CAPL_FARCALL)appGetVideoFCInputObjectWidth, "CAPL_DLL", "This function gives back the width input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCInputObjectLength", (CAPL_FARCALL)appGetVideoFCInputObjectLength, "CAPL_DLL", "This function gives back the length input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {"dllGetVideoFCInputObjectHeight", (CAPL_FARCALL)appGetVideoFCInputObjectHeight, "CAPL_DLL", "This function gives back the height input data of the object with the given ID", 'F', 2, "DL", "", {"handle", "obj_nr"}},
    {0, 0}};
CAPLEXPORT CAPL_DLL_INFO4 *caplDllTable4 = table;