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

#include "../../Includes/cdll.h"
#include "../../Includes/VIA.h"
#include "../../Includes/VIA_CDLL.h"
#include "MathLibrary.hpp"

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

    MathLibrary::TargetCalculation calculation_class;
    MathLibrary::CoordinateSystem rca_cs;
    MathLibrary::CoordinateSystem sensor_cs;
    MathLibrary::LocationContour locations;

    //data handling
    //int CoeffFlipRadar;
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
      calculation_class(),
      rca_cs(),
      sensor_cs(),
      locations()
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

#include "DataHandling.h"

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
// Object calculation
// ============================================================================

long CAPLEXPORT CAPLPASCAL appCalcObjectReferencePoint(uint32 handle, double height, double width, double length, double rca_dist_x, double rca_dist_y, 
                                            double rca_heading_angle, double sensor_dist_x, double sensor_dist_y, double sensor_heading_angle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }

    //calculate 
    instance->calculation_class.calculate_ref_point(height,width,length,rca_dist_x,rca_dist_y,rca_heading_angle,sensor_dist_x,sensor_dist_y,sensor_heading_angle);

    //save the calculated cs
    instance->rca_cs = instance->calculation_class.get_RCA();
    instance->sensor_cs = instance->calculation_class.get_Sensor_CS();

    return 0;
}

long CAPLEXPORT CAPLPASCAL appCalcACCS(uint32 handle, double vx, double vy, double ax, double ay)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }

    //save edges for ACCS calcs
    double edge_left_previous = instance->calculation_class.get_edge_left();
    double edge_right_previous = instance->calculation_class.get_edge_right();
    double edge_mid_previous = instance->calculation_class.get_edge_mid();

    //calculate 
    instance->calculation_class.calculate_ACCS(vx,vy,ax,ay,edge_left_previous,edge_right_previous,edge_mid_previous);

    return 0;
}

long CAPLEXPORT CAPLPASCAL appCalcLocations(uint32_t handle, int loc_nr, int loc_distribution, int obj_type, double height, double vx, double vy)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }

    //calculate 
    instance->calculation_class.calculate_Locations(loc_nr,loc_distribution,obj_type,height,vx,vy);
    
    instance->locations = instance->calculation_class.get_location_contour();

    return 0;
}

// ============================================================================
// Getters - RCA Coordinate System
// Naming Convention for Distance-Getters: appGet(Ego position)(Target position)(Value)
// ============================================================================
double CAPLEXPORT CAPLPASCAL appGetRCARefptDistX(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->rca_cs.dx_ref_point;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetRCARefptDistY(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->rca_cs.dy_ref_point;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetRCALeftDistX(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->rca_cs.dx_left;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetRCALeftDistY(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->rca_cs.dy_left;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetRCARightDistX(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->rca_cs.dx_right;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetRCARightDistY(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->rca_cs.dy_right;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetRCAFrontDistX(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->rca_cs.dx_front;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetRCAFrontDistY(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->rca_cs.dy_front;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetRCARearDistX(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->rca_cs.dx_rear;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetRCARearDistY(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->rca_cs.dy_rear;
    }
    return 0.0F;
}

// ============================================================================
// Getters - Sensor Coordinate System
// Naming Convention for Distance-Getters: appGet(Ego position)(Target position)(Value)
// ============================================================================
double CAPLEXPORT CAPLPASCAL appGetSensorRefpt(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return static_cast<int>(instance->calculation_class.get_reference_point());
    }
    return 0;
}

double CAPLEXPORT CAPLPASCAL appGetSensorRefptDistX(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_cs.dx_ref_point;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetSensorRefptDistY(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_cs.dy_ref_point;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetSensorLeftDistX(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_cs.dx_left;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetSensorLeftDistY(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_cs.dy_left;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetSensorRightDistX(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_cs.dx_right;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetSensorRightDistY(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_cs.dy_right;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetSensorFrontDistX(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_cs.dx_front;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetSensorFrontDistY(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_cs.dy_front;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetSensorRearDistX(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_cs.dx_rear;
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetSensorRearDistY(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->sensor_cs.dy_rear;
    }
    return 0.0F;
}

// ============================================================================
// Getters - Location calculations
// ============================================================================
double CAPLEXPORT CAPLPASCAL appGetLocRadDist(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.location_cloud[loc_nr].radial_distance;
    }
    return -3.141F;
}
double CAPLEXPORT CAPLPASCAL appGetLocRadVel(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.location_cloud[loc_nr].radial_velocity;
    }
    return -3.141F;
}

double CAPLEXPORT CAPLPASCAL appGetLocAzimuth(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.location_cloud[loc_nr].azimuth_angle;
    }
    return -3.141F;
}

double CAPLEXPORT CAPLPASCAL appGetLocElevation(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.location_cloud[loc_nr].elevation_angle;
    }
    return -3.141F;
}

double CAPLEXPORT CAPLPASCAL appGetLocRCS(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.location_cloud[loc_nr].radar_cross_section;
    }
    return -3.141F;
}

double CAPLEXPORT CAPLPASCAL appSetLocRCS(uint32_t handle, int loc_nr, double rcs)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        instance->calculation_class.location_cloud[loc_nr].radar_cross_section = rcs;
        return 1;
    }
    return -3.141F;
}

int CAPLEXPORT CAPLPASCAL appGetLocCount(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->locations.total_loc_count;
    }
    return -1;
}

// ============================================================================
// Getters - Aligned Camera Coordinate System (ACCS)
// Naming Convention for Distance-Getters: appGet(Ego position)(Target position)(Value)
// ============================================================================
int CAPLEXPORT CAPLPASCAL appGetACCSVisibleView(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return static_cast<int>(instance->calculation_class.get_visible_view());
    }
    return 0;
}

int CAPLEXPORT CAPLPASCAL appGetACCSClassifiedView(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return static_cast<int>(instance->calculation_class.get_reference_point());
    }
    return 0;
}

double CAPLEXPORT CAPLPASCAL appGetACCSEdgeLeft(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.get_edge_left();
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetACCSEdgeRight(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.get_edge_right();
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetACCSEdgeMid(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.get_edge_mid();
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetACCSEdgeTop(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.get_edge_top();
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetACCSEdgeBottom(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.get_edge_bottom();
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetACCSEdgeLeftNormVy(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.get_norm_vel_y_edge_left();
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetACCSEdgeRightNormVy(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.get_norm_vel_y_edge_left();
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetACCSNormVx(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.get_norm_vel_x();
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetACCSNormVy(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.get_norm_vel_y();
    }
    return 0.0F;
}

double CAPLEXPORT CAPLPASCAL appGetACCSNormAx(uint32_t handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->calculation_class.get_norm_accel_x();
    }
    return 0.0F;
}


// ============================================================================
// FORD ONLY
// Definition fo the functions for the ByteArray Handling for CAN TP
// ============================================================================
long CAPLEXPORT CAPLPASCAL app1ObjXLocPushLocToByteArray(uint32 handle, uint32 flagFlip, uint32_t radar_id)
{
    int i;
    int iteration_count = 0;
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        switch(radar_id)
        {
            case 1:
            for(i=instance->total_nr_of_loc_FC; i < instance->total_nr_of_loc_FC+instance->locations.total_loc_count; i++)
            {
                //pre filter
                if(flagFlip)
                {
                    instance->calculation_class.location_cloud[iteration_count].azimuth_angle = -instance->calculation_class.location_cloud[iteration_count].azimuth_angle;
                    instance->calculation_class.location_cloud[iteration_count].elevation_angle = -instance->calculation_class.location_cloud[iteration_count].elevation_angle;
                }
                //write byte array
                Write_ByteArray_RXX_Location(i, instance->byteArray_loc_FC, iteration_count, instance);
                iteration_count++;
            }
            instance->total_nr_of_loc_FC = instance->total_nr_of_loc_FC + instance->locations.total_loc_count;
            break;
            case 2:
            for(i=instance->total_nr_of_loc_FL; i < instance->total_nr_of_loc_FL+instance->locations.total_loc_count; i++)
            {
                //pre filter
                if(flagFlip)
                {
                    instance->calculation_class.location_cloud[iteration_count].azimuth_angle = -instance->calculation_class.location_cloud[iteration_count].azimuth_angle;
                    instance->calculation_class.location_cloud[iteration_count].elevation_angle = -instance->calculation_class.location_cloud[iteration_count].elevation_angle;
                }
                //write byte array
                Write_ByteArray_RXX_Location(i, instance->byteArray_loc_FL, iteration_count, instance);
                iteration_count++;
            }
            instance->total_nr_of_loc_FL = instance->total_nr_of_loc_FL + instance->locations.total_loc_count;
            break;
            case 3:
            for(i=instance->total_nr_of_loc_FR; i < instance->total_nr_of_loc_FR+instance->locations.total_loc_count; i++)
            {
                //pre filter
                if(flagFlip)
                {
                    instance->calculation_class.location_cloud[iteration_count].azimuth_angle = -instance->calculation_class.location_cloud[iteration_count].azimuth_angle;
                    instance->calculation_class.location_cloud[iteration_count].elevation_angle = -instance->calculation_class.location_cloud[iteration_count].elevation_angle;
                }
                //write byte array
                Write_ByteArray_RXX_Location(i, instance->byteArray_loc_FR, iteration_count, instance);
                iteration_count++;
            }
            instance->total_nr_of_loc_FR = instance->total_nr_of_loc_FR + instance->locations.total_loc_count;
            break;
            case 4:
            for(i=instance->total_nr_of_loc_RL; i < instance->total_nr_of_loc_RL+instance->locations.total_loc_count; i++)
            {
                //pre filter
                if(flagFlip)
                {
                    instance->calculation_class.location_cloud[iteration_count].azimuth_angle = -instance->calculation_class.location_cloud[iteration_count].azimuth_angle;
                    instance->calculation_class.location_cloud[iteration_count].elevation_angle = -instance->calculation_class.location_cloud[iteration_count].elevation_angle;
                }
                //write byte array
                Write_ByteArray_RXX_Location(i, instance->byteArray_loc_RL, iteration_count, instance);
                iteration_count++;
            }
            instance->total_nr_of_loc_RL = instance->total_nr_of_loc_RL + instance->locations.total_loc_count;
            break;
            case 5:
            for(i=instance->total_nr_of_loc_RR; i < instance->total_nr_of_loc_RR+instance->locations.total_loc_count; i++)
            {
                //pre filter
                if(flagFlip)
                {
                    instance->calculation_class.location_cloud[iteration_count].azimuth_angle = -instance->calculation_class.location_cloud[iteration_count].azimuth_angle;
                    instance->calculation_class.location_cloud[iteration_count].elevation_angle = -instance->calculation_class.location_cloud[iteration_count].elevation_angle;
                }
                //write byte array
                Write_ByteArray_RXX_Location(i, instance->byteArray_loc_RR, iteration_count, instance);
                iteration_count++;
            }
            instance->total_nr_of_loc_RR = instance->total_nr_of_loc_RR + instance->locations.total_loc_count;
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

long CAPLEXPORT CAPLPASCAL appReset1ObjXLocModel(uint32_t handle, uint32_t radar_id)
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

// ============================================================================
// CAPL_DLL_INFO_LIST : list of exported functions
//   The first field is predefined and mustn't be changed!
//   The list has to end with a {0,0} entry!
// New struct supporting function names with up to 50 characters
// ============================================================================
CAPL_DLL_INFO4 table[] = {
    {CDLL_VERSION_NAME, (CAPL_FARCALL)CDLL_VERSION, "", "", CAPL_DLL_CDECL, 0xabcd, CDLL_EXPORT},
    {"dllInitObjectCalc", (CAPL_FARCALL)appInit, "CAPL_DLL", "This function will initialize all callback functions in the CAPLDLL", 'V', 1, "D", "", {"handle"}},
    {"dllEndObjectCalc", (CAPL_FARCALL)appEnd, "CAPL_DLL", "This function will release the CAPL function handle in the CAPLDLL", 'V', 1, "D", "", {"handle"}},
    {"dllCalcObjectReferencePoint", (CAPL_FARCALL)appCalcObjectReferencePoint, "CAPL_DLL", "This function calculates a rectangle around the given middle of the geometry and further calculates the reference side of the object", 'L', 10, "DFFFFFFFFF", "", {"handle", "height", "width", "length", "rca_dist_x", "rca_dist_y", "rca_heading_angle", "sensor_dist_x", "sensor_dist_y", "sensor_heading_angle"}},
    {"dllCalcACCS", (CAPL_FARCALL)appCalcACCS, "CAPL_DLL", "This function calculates camera specific values", 'L', 5, "DFFFF", "", {"handle", "vx", "vy", "ax", "ay"}},
    {"dllCalcLocations", (CAPL_FARCALL)appCalcLocations, "CAPL_DLL", "This function calculates locations out of the previous calculated reference point", 'L', 7, "DLLLFFF", "", {"handle", "nr_max_loc", "location_distribution", "object_type", "height", "vx", "vy"}},
    
    {"dllGetRCARefptDistX", (CAPL_FARCALL)appGetRCARefptDistX, "CAPL_DLL", "This function gives back the distance in longitudinal direction from RCA to the calculated reference point", 'F', 1, "D", "", {"handle"}},
    {"dllGetRCARefptDistY", (CAPL_FARCALL)appGetRCARefptDistY, "CAPL_DLL", "This function gives back the distance in lateral direction from RCA to the calculated reference point", 'F', 1, "D", "", {"handle"}},
    {"dllGetRCALeftDistX", (CAPL_FARCALL)appGetRCALeftDistX, "CAPL_DLL", "This function gives back the distance in longitudinal direction from RCA to the calculated middle of the targets left side", 'F', 1, "D", "", {"handle"}},
    {"dllGetRCALeftDistY", (CAPL_FARCALL)appGetRCALeftDistY, "CAPL_DLL", "This function gives back the distance in lateral direction from RCA to the calculated middle of the targets left side", 'F', 1, "D", "", {"handle"}},
    {"dllGetRCARightDistX", (CAPL_FARCALL)appGetRCARightDistX, "CAPL_DLL", "This function gives back the distance in longitudinal direction from RCA to the calculated middle of the targets right side", 'F', 1, "D", "", {"handle"}},
    {"dllGetRCARightDistY", (CAPL_FARCALL)appGetRCARightDistY, "CAPL_DLL", "This function gives back the distance in lateral direction from RCA to the calculated middle of the targets right side", 'F', 1, "D", "", {"handle"}},
    {"dllGetRCAFrontDistX", (CAPL_FARCALL)appGetRCAFrontDistX, "CAPL_DLL", "This function gives back the distance in longitudinal direction from RCA to the calculated middle of the targets front side", 'F', 1, "D", "", {"handle"}},
    {"dllGetRCAFrontDistY", (CAPL_FARCALL)appGetRCAFrontDistY, "CAPL_DLL", "This function gives back the distance in lateral direction from RCA to the calculated middle of the targets front side", 'F', 1, "D", "", {"handle"}},
    {"dllGetRCARearDistX", (CAPL_FARCALL)appGetRCARearDistX, "CAPL_DLL", "This function gives back the distance in longitudinal direction from RCA to the calculated middle of the targets rear side", 'F', 1, "D", "", {"handle"}},
    {"dllGetRCARearDistY", (CAPL_FARCALL)appGetRCARearDistY, "CAPL_DLL", "This function gives back the distance in lateral direction from RCA to the calculated middle of the targets rear side", 'F', 1, "D", "", {"handle"}},
    
    {"dllGetSensorRefpt", (CAPL_FARCALL)appGetSensorRefpt, "CAPL_DLL", "This function gives back the reference point from the sensors perspective which is located in the middle of the side. 1=Front,2=Rear,3=Left,4=Right,", 'L', 1, "D", "", {"handle"}},
    {"dllGetSensorRefptDistX", (CAPL_FARCALL)appGetSensorRefptDistX, "CAPL_DLL", "This function gives back the distance in longitudinal direction from Sensor position to the calculated reference point", 'F', 1, "D", "", {"handle"}},
    {"dllGetSensorRefptDistY", (CAPL_FARCALL)appGetSensorRefptDistY, "CAPL_DLL", "This function gives back the distance in lateral direction from Sensor position to the calculated reference point", 'F', 1, "D", "", {"handle"}},
    {"dllGetSensorLeftDistX", (CAPL_FARCALL)appGetSensorLeftDistX, "CAPL_DLL", "This function gives back the distance in longitudinal direction from Sensor position to the calculated middle of the targets left side", 'F', 1, "D", "", {"handle"}},
    {"dllGetSensorLeftDistY", (CAPL_FARCALL)appGetSensorLeftDistY, "CAPL_DLL", "This function gives back the distance in lateral direction from Sensor position to the calculated middle of the targets left side", 'F', 1, "D", "", {"handle"}},
    {"dllGetSensorRightDistX", (CAPL_FARCALL)appGetSensorRightDistX, "CAPL_DLL", "This function gives back the distance in longitudinal direction from Sensor position to the calculated middle of the targets right side", 'F', 1, "D", "", {"handle"}},
    {"dllGetSensorRightDistY", (CAPL_FARCALL)appGetSensorRightDistY, "CAPL_DLL", "This function gives back the distance in lateral direction from Sensor position to the calculated middle of the targets right side", 'F', 1, "D", "", {"handle"}},
    {"dllGetSensorFrontDistX", (CAPL_FARCALL)appGetSensorFrontDistX, "CAPL_DLL", "This function gives back the distance in longitudinal direction from Sensor position to the calculated middle of the targets front side", 'F', 1, "D", "", {"handle"}},
    {"dllGetSensorFrontDistY", (CAPL_FARCALL)appGetSensorFrontDistY, "CAPL_DLL", "This function gives back the distance in lateral direction from Sensor position to the calculated middle of the targets front side", 'F', 1, "D", "", {"handle"}},
    {"dllGetSensorRearDistX", (CAPL_FARCALL)appGetSensorRearDistX, "CAPL_DLL", "This function gives back the distance in longitudinal direction from Sensor position to the calculated middle of the targets rear side", 'F', 1, "D", "", {"handle"}},
    {"dllGetSensorRearDistY", (CAPL_FARCALL)appGetSensorRearDistY, "CAPL_DLL", "This function gives back the distance in lateral direction from Sensor position to the calculated middle of the targets rear side", 'F', 1, "D", "", {"handle"}},
    
    {"dllGetLocRadDist", (CAPL_FARCALL)appGetLocRadDist, "CAPL_DLL", "This function gives back the radial distance of the location with the loc_nr given. Those distances are points on the visible side(s) of the target.", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetLocRadVel", (CAPL_FARCALL)appGetLocRadVel, "CAPL_DLL", "This function gives back the radial velocity of the location with the loc_nr given.", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetLocRCS", (CAPL_FARCALL)appGetLocRCS, "CAPL_DLL", "This function gives back the calculated RCS of the object.", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllSetLocRCS", (CAPL_FARCALL)appSetLocRCS, "CAPL_DLL", "This function sets the RCS value of the location with the given ID.", 'F', 3, "DLF", "", {"handle", "loc_nr", "rcs"}},
    {"dllGetLocAzimuth", (CAPL_FARCALL)appGetLocAzimuth, "CAPL_DLL", "This function gives back the calculated Azimuth angle of the location. In rad!", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetLocElevation", (CAPL_FARCALL)appGetLocElevation, "CAPL_DLL", "This function gives back the calculated Elevation angle of the location. In rad!", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllGetLocCount", (CAPL_FARCALL)appGetLocCount, "CAPL_DLL", "This function gives back the total amount of calculated locations.", 'L', 1, "D", "", {"handle"}},

    {"dllGetACCSVisibleView", (CAPL_FARCALL)appGetACCSVisibleView, "CAPL_DLL", "This function gives back the visible view from the cameras perspective on the target", 'L', 1, "D", "", {"handle"}},
    {"dllGetACCSClassifiedView", (CAPL_FARCALL)appGetACCSClassifiedView, "CAPL_DLL", "This function gives back the classified view from the cameras perspective on the target", 'L', 1, "D", "", {"handle"}},
    {"dllGetACCSEdgeLeft", (CAPL_FARCALL)appGetACCSEdgeLeft, "CAPL_DLL", "This function gives back the left edge of the side facing the ego", 'F', 1, "D", "", {"handle"}},
    {"dllGetACCSEdgeRight", (CAPL_FARCALL)appGetACCSEdgeRight, "CAPL_DLL", "This function gives back the right edge of the side facing the ego", 'F', 1, "D", "", {"handle"}},
    {"dllGetACCSEdgeMid", (CAPL_FARCALL)appGetACCSEdgeMid, "CAPL_DLL", "This function gives back the far edge if the camera is seeing an L shape", 'F', 1, "D", "", {"handle"}},
    {"dllGetACCSEdgeTop", (CAPL_FARCALL)appGetACCSEdgeTop, "CAPL_DLL", "This function gives back the top edge of the side facing the ego", 'F', 1, "D", "", {"handle"}},
    {"dllGetACCSEdgeBottom", (CAPL_FARCALL)appGetACCSEdgeBottom, "CAPL_DLL", "This function gives back the bottom edge of the side facing the ego", 'F', 1, "D", "", {"handle"}},
    {"dllGetACCSEdgeLeftNormVy", (CAPL_FARCALL)appGetACCSEdgeLeftNormVy, "CAPL_DLL", "This function gives back the normalized lateral velocity of the left edge of the side facing the ego", 'F', 1, "D", "", {"handle"}},
    {"dllGetACCSEdgeRightNormVy", (CAPL_FARCALL)appGetACCSEdgeRightNormVy, "CAPL_DLL", "This function gives back the normalized lateral velocity of the right edge of the side facing the ego", 'F', 1, "D", "", {"handle"}},
    {"dllGetACCSNormVx", (CAPL_FARCALL)appGetACCSNormVx, "CAPL_DLL", "This function gives back the normalized relative longitudinal velocity of the target", 'F', 1, "D", "", {"handle"}},
    {"dllGetACCSNormVy", (CAPL_FARCALL)appGetACCSNormVy, "CAPL_DLL", "This function gives back the normalized relative lateral velocity of the target", 'F', 1, "D", "", {"handle"}},
    {"dllGetACCSNormAx", (CAPL_FARCALL)appGetACCSNormAx, "CAPL_DLL", "This function gives back the normalized relative longitudinal acceleration of the target", 'F', 1, "D", "", {"handle"}},
    
    {"dll1ObjXLocPushLocToByteArray", (CAPL_FARCALL)app1ObjXLocPushLocToByteArray, "CAPL_DLL", "This parse the locations generated in the byte array", 'L', 3, "DDD", "", {"handle", "flagFlipSensor", "radarId"}},
    {"dll1ObjXLocGetByteArray", (CAPL_FARCALL)appGetByteArray, "CAPL_DLL", "This function sets the byte array", 'L', 3, "LBD", "\000\001", {"handle", "byteArray", "radarId"}},
    {"dllReset1ObjXLocModel", (CAPL_FARCALL)appReset1ObjXLocModel, "CAPL_DLL", "This function reset the 1ObjXLoc model", 'L', 2, "DD", "", {"handle", "radarId"}},
    
    {0, 0}};
CAPLEXPORT CAPL_DLL_INFO4 *caplDllTable4 = table;