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

#include "../../Includes/cdll.h"
#include "../../Includes/VIA.h"
#include "../../Includes/VIA_CDLL.h"


#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <map>

#if defined(_WIN64) || defined(__linux__)
#define X64
#endif

//#include "radarSensormodel.h"
#include "Target_Calc.h"
// #include "MathLibrary.hpp"

// using namespace MathLibrary;

class CaplInstanceData;
typedef std::map<uint32_t, CaplInstanceData*> VCaplMap;
typedef std::map<uint32_t, VIACapl*> VServiceMap;

// ============================================================================
// global variables
// ============================================================================

static uint32_t data = 0;
static char dlldata[100];

char        gModuleName[_MAX_FNAME];  // filename of this DLL
HINSTANCE   gModuleHandle;            // windows instance handle of this DLL

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
    CaplInstanceData(VIACapl* capl);

    void GetCallbackFunctions();
    void ReleaseCallbackFunctions();

    // Definition of the class function.
    // This class function will call the CAPL callback functions
    uint32_t ShowValue(uint32_t x);
    uint32_t ShowDates(int16_t x, uint32_t y, int16_t z);
    void DllInfo(const char* x);
    void ArrayValues(uint32_t flags, uint32_t numberOfDatabytes, uint8_t databytes[], uint8_t controlcode);
    void DllVersion(const char* y);

    // RBStarModel::Radar_sensormodel sensormodel_;
    // std::vector<RBStarModel::SimulationObjectState> star_model_object_list_;
    // RBStarModel::MODEL_LOCATION_LIST_ST locations_;
    // std::string path_to_database{ "" };

    // could also be only added in a derived class
    // pointer to the callback in capl
    // VIACaplFunction*  mGetDataFromCanoe;
    // // pointer to the callback in capl
    // VIACaplFunction*  mSetDataToCanoe;
    //MidTarget_CoordinateSystem Target_mid;
    //CoordinateSystem TargetPosition;
    CoordinateSystem RCA_CS;
    CoordinateSystem Sensor_CS;
    CoordinateSystem CoG_CS;


private:
    // Pointer of the CAPL callback functions
    VIACaplFunction* mShowValue;
    VIACaplFunction* mShowDates;
    VIACaplFunction* mDllInfo;
    VIACaplFunction* mArrayValues;
    VIACaplFunction* mDllVersion;

    VIACapl* mCapl;
};

CaplInstanceData::CaplInstanceData(VIACapl* capl)
// This function will initialize the CAPL callback function
// with the NLL Pointer
    : mCapl(capl),
    mShowValue(nullptr),
    mShowDates(nullptr),
    mDllInfo(nullptr),
    mArrayValues(nullptr),
    mDllVersion(nullptr)
    //  mGetDataFromCanoe(NULL),
    //  mSetDataToCanoe(NULL),
    // sensormodel_(),
    // star_model_object_list_()
{

}

static bool sCheckParams(VIACaplFunction* f, char rtype, const char* ptype)
{
    char type;
    int32_t pcount;
    VIAResult rc;

    // check return type
    rc = f->ResultType(&type);
    if (rc != kVIA_OK || type != rtype)
    {
        return false;
    }

    // check number of parameters
    rc = f->ParamCount(&pcount);
    if (rc != kVIA_OK || strlen(ptype) != pcount)
    {
        return false;
    }

    // check type of parameters
    for (int32_t i = 0; i < pcount; ++i)
    {
        rc = f->ParamType(&type, i);
        if (rc != kVIA_OK || type != ptype[i])
        {
            return false;
        }
    }

    return true;
}

static VIACaplFunction* sGetCaplFunc(VIACapl* capl, const char* fname, char rtype, const char* ptype)
{
    VIACaplFunction* f;

    // get capl function object
    VIAResult rc = capl->GetCaplFunction(&f, fname);
    if (rc != kVIA_OK || f == nullptr)
    {
        return nullptr;
}

    // check signature of function
    if (sCheckParams(f, rtype, ptype))
    {
        return f;
    }
    else
    {
        capl->ReleaseCaplFunction(f);
        return nullptr;
    }
}

void CaplInstanceData::GetCallbackFunctions()
{
    // Get a CAPL function handle. The handle stays valid until end of
    // measurement or a call of ReleaseCaplFunction.
    mShowValue = sGetCaplFunc(mCapl, "CALLBACK_ShowValue", 'D', "D");
    mShowDates = sGetCaplFunc(mCapl, "CALLBACK_ShowDates", 'D', "IDI");
    mDllInfo = sGetCaplFunc(mCapl, "CALLBACK_DllInfo", 'V', "C");
    mArrayValues = sGetCaplFunc(mCapl, "CALLBACK_ArrayValues", 'V', "DBB");
    mDllVersion = sGetCaplFunc(mCapl, "CALLBACK_DllVersion", 'V', "C");
}

void CaplInstanceData::ReleaseCallbackFunctions()
{
    // Release all the requested Callback functions
    mCapl->ReleaseCaplFunction(mShowValue);
    mShowValue = nullptr;
    mCapl->ReleaseCaplFunction(mShowDates);
    mShowDates = nullptr;
    mCapl->ReleaseCaplFunction(mDllInfo);
    mDllInfo = nullptr;
    mCapl->ReleaseCaplFunction(mArrayValues);
    mArrayValues = nullptr;
    mCapl->ReleaseCaplFunction(mDllVersion);
    mDllVersion = nullptr;
}

void CaplInstanceData::DllVersion(const char* y)
{
    // Prepare the parameters for the call stack of CAPL.
    // Arrays uses a 8 byte (64 bit DLL: 12 byte) on the stack, 4 Bytes for the number of element,
    // and 4 bytes (64 bit DLL: 8 byte) for the pointer to the array
    int32_t sizeX = (int32_t)strlen(y) + 1;

#if defined(X64)
    uint8_t params[16];            // parameters for call stack, 16 Bytes total (8 bytes per parameter, reverse order of parameters)
    memcpy(params + 8, &sizeX, 4); // array size    of first parameter, 4 Bytes
    memcpy(params + 0, &y, 8);     // array pointer of first parameter, 8 Bytes
#else
    uint8_t params[8];                         // parameters for call stack, 8 Bytes total
    memcpy(params + 0, &sizeX, 4);             // array size    of first parameter, 4 Bytes
    memcpy(params + 4, &y, 4);                 // array pointer of first parameter, 4 Bytes
#endif

    if (mDllVersion != nullptr)
    {
        uint32_t result; // dummy variable
        VIAResult rc = mDllVersion->Call(&result, params);
    }
}

uint32_t CaplInstanceData::ShowValue(uint32_t x)
{
#if defined(X64)
    uint8_t params[8];         // parameters for call stack, 8 Bytes total
    memcpy(params + 0, &x, 8); // first parameter, 8 Bytes
#else
    void* params = &x;                         // parameters for call stack
#endif

    uint32_t result;

    if (mShowValue != nullptr)
    {
        VIAResult rc = mShowValue->Call(&result, params);
        if (rc == kVIA_OK)
        {
            return result;
        }
}
    return -1;
}

uint32_t CaplInstanceData::ShowDates(int16_t x, uint32_t y, int16_t z)
{
    // Prepare the parameters for the call stack of CAPL. The stack grows
    // from top to down, so the first parameter in the parameter list is the last
    // one in memory. CAPL uses also a 32 bit alignment for the parameters.

#if defined(X64)
    uint8_t params[24];         // parameters for call stack, 24 Bytes total (8 bytes per parameter, reverse order of parameters)
    memcpy(params + 16, &z, 2); // third  parameter, offset 16, 2 Bytes
    memcpy(params + 8, &y, 4);  // second parameter, offset 8,  4 Bytes
    memcpy(params + 0, &x, 2);  // first  parameter, offset 0,  2 Bytes
#else
    uint8_t params[12];                        // parameters for call stack, 12 Bytes total
    memcpy(params + 0, &z, 2);                 // third  parameter, offset 0, 2 Bytes
    memcpy(params + 4, &y, 4);                 // second parameter, offset 4, 4 Bytes
    memcpy(params + 8, &x, 2);                 // first  parameter, offset 8, 2 Bytes
#endif

    uint32_t result;

    if (mShowDates != nullptr)
    {
        VIAResult rc = mShowDates->Call(&result, params);
        if (rc == kVIA_OK)
        {
            return rc; // call successful
        }
}

    return -1; // call failed
}

void CaplInstanceData::DllInfo(const char* x)
{
    // Prepare the parameters for the call stack of CAPL.
    // Arrays uses a 8 byte (64 bit DLL: 12 byte) on the stack, 4 Bytes for the number of element,
    // and 4 bytes (64 bit DLL: 8 byte) for the pointer to the array
    int32_t sizeX = (int32)strlen(x) + 1;

#if defined(X64)
    uint8_t params[16];            // parameters for call stack, 16 Bytes total (8 bytes per parameter, reverse order of parameters)
    memcpy(params + 8, &sizeX, 4); // array size    of first parameter, 4 Bytes
    memcpy(params + 0, &x, 8);     // array pointer of first parameter, 8 Bytes
#else
    uint8_t params[8];                         // parameters for call stack, 8 Bytes total
    memcpy(params + 0, &sizeX, 4);             // array size    of first parameter, 4 Bytes
    memcpy(params + 4, &x, 4);                 // array pointer of first parameter, 4 Bytes
#endif

    if (mDllInfo != nullptr)
    {
        uint32_t result; // dummy variable
        VIAResult rc = mDllInfo->Call(&result, params);
    }
}

void CaplInstanceData::ArrayValues(uint32_t flags, uint32_t numberOfDatabytes, uint8_t databytes[], uint8_t controlcode)
{
    // Prepare the parameters for the call stack of CAPL. The stack grows
    // from top to down, so the first parameter in the parameter list is the last
    // one in memory. CAPL uses also a 32 bit alignment for the parameters.
    // Arrays uses a 8 byte (64 bit DLL: 12 byte) on the stack, 4 Bytes for the number of element,
    // and 4 bytes (64 bit DLL: 8 byte) for the pointer to the array

#if defined(X64)
    uint8_t params[32];                         // parameters for call stack, 32 Bytes total (8 bytes per parameter, reverse order of parameters)
    memcpy(params + 24, &controlcode, 1);       // third parameter,                  offset 24, 1 Bytes
    memcpy(params + 16, &numberOfDatabytes, 4); // second parameter (array size),    offset 16, 4 Bytes
    memcpy(params + 8, &databytes, 8);          // second parameter (array pointer), offset  8, 8 Bytes
    memcpy(params + 0, &flags, 4);              // first  parameter,                 offset  0, 4 Bytes
#else
    uint8_t params[16];                        // parameters for call stack, 16 Bytes total
    memcpy(params + 0, &controlcode, 1);       // third parameter,                  offset  0, 1 Bytes
    memcpy(params + 4, &numberOfDatabytes, 4); // second parameter (array size),    offset  4, 4 Bytes
    memcpy(params + 8, &databytes, 4);         // second parameter (array pointer), offset  8, 4 Bytes
    memcpy(params + 12, &flags, 4);            // first  parameter,                 offset 12, 4 Bytes
#endif

    if (mArrayValues != nullptr)
    {
        uint32_t result; // dummy variable
        VIAResult rc = mArrayValues->Call(&result, params);
    }
}

CaplInstanceData* GetCaplInstanceData(uint32_t handle)
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
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (nullptr == instance)
    {
        VServiceMap::iterator lSearchService(gServiceMap.find(handle));
        if (gServiceMap.end() != lSearchService)
        {
            VIACapl* service = lSearchService->second;
            try
            {
                instance = new CaplInstanceData(service);
            }
            catch (std::bad_alloc&)
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
    CaplInstanceData* inst = GetCaplInstanceData(handle);
    if (inst == nullptr)
    {
        return;
    }
    inst->ReleaseCallbackFunctions();

    delete inst;
    inst = nullptr;
    gCaplMap.erase(handle);
}

int32_t CAPLEXPORT CAPLPASCAL appSetValue(uint32_t handle, int32_t x)
{
    CaplInstanceData* inst = GetCaplInstanceData(handle);
    if (inst == nullptr)
    {
        return -1;
    }

    return inst->ShowValue(x);
}

int32_t CAPLEXPORT CAPLPASCAL appReadData(uint32_t handle, int32_t a)
{
    CaplInstanceData* inst = GetCaplInstanceData(handle);
    if (inst == nullptr)
    {
        return -1;
    }

    int16_t x = (a >= 0) ? +1 : -1;
    uint32_t y = abs(a);
    int16_t z = (int16)(a & 0x0f000000) >> 24;

    inst->DllVersion("Version 1.1");

    inst->DllInfo("DLL: processing");

    uint8_t databytes[8] = { 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88 };

    inst->ArrayValues(0xaabbccdd, sizeof(databytes), databytes, 0x01);

    return inst->ShowDates(x, y, z);
}

// ============================================================================
// VIARegisterCDLL
// ============================================================================

VIACLIENT(void)
VIARegisterCDLL(VIACapl* service)
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


long CAPLEXPORT CAPLPASCAL calculate_coordinates_target(uint32_t handle, double length, double heading_angle, double dist_x, double dist_y, 
                                            double vel_x, double vel_y, double mount_pos_dx, double mount_pos_dy, double mount_pos_yaw, 
                                            int ego_current_ref_point, int target_current_ref_point)
    {
        /**
         * Shift the distances, velocities and heading_angle if needed via the current_ref_point
         * ego_current_ref_point == 0 -> RCA
         * ego_current_ref_point == 1 -> Sensor
         * The formula for the x component is: x * cos(+-yaw) - y * sin(+-yaw)
         * The formula for the y component is: x * sin(+-yaw) + y * cos(+-yaw)
         * The sign results from the fact that the coordinate system is rotated clockwise when the sign is positive
        */
        CaplInstanceData* inst = GetCaplInstanceData(handle);
        if (inst == NULL)
        {
            return -1;
        }
        //Shift the distances from Sensor position to the RCA and rotate them to fit the ego direction -> sign is the same as the mount_yaw
        //double dx_rca, dy_rca;
        if(ego_current_ref_point == 0)
        {   //ref_point == RCA
            inst->RCA_CS.dx = dist_x;
            inst->RCA_CS.dy = dist_y;
            //RCA values = inputs
            inst->RCA_CS.vx = vel_x;
            inst->RCA_CS.vy = vel_y;
            inst->RCA_CS.heading = heading_angle;
            //Sensor values have to be rotated to fit the sensor cs -> sign is the opposite of the mount_yaw

            inst->Sensor_CS.dx = (dist_x-mount_pos_dx)*cos(mount_pos_yaw)+(dist_y-mount_pos_dy)*sin(mount_pos_yaw);
            inst->Sensor_CS.dy = (dist_y-mount_pos_dy)*cos(mount_pos_yaw)-(dist_x-mount_pos_dx)*sin(mount_pos_yaw);

            inst->Sensor_CS.vx = vel_x * cos(-mount_pos_yaw) - vel_y * sin(-mount_pos_yaw);
            inst->Sensor_CS.vy = vel_x * sin(-mount_pos_yaw) + vel_y * cos(-mount_pos_yaw);
            inst->Sensor_CS.heading = heading_angle - mount_pos_yaw;
        }
        else if(ego_current_ref_point == 1)
        {   //ref_point == Sensor
            inst->RCA_CS.dx = dist_x * cos(mount_pos_yaw) - dist_y * sin(mount_pos_yaw) + mount_pos_dx;
            inst->RCA_CS.dy = dist_x * sin(mount_pos_yaw) + dist_y * cos(mount_pos_yaw) + mount_pos_dy;
            //Sensor values have to be rotated to fit the rca -> sign is the same as the mount_yaw
            inst->RCA_CS.vx = vel_x * cos(mount_pos_yaw) - vel_y * sin(mount_pos_yaw);
            inst->RCA_CS.vy = vel_x * sin(mount_pos_yaw) + vel_y * cos(mount_pos_yaw);
            inst->RCA_CS.heading = heading_angle + mount_pos_yaw;
            //Sensor values = inputs
            inst->Sensor_CS.dx = dist_x;
            inst->Sensor_CS.dy = dist_y;

            inst->Sensor_CS.vx = vel_x;
            inst->Sensor_CS.vy = vel_y;
            inst->Sensor_CS.heading = heading_angle;
        }

        // Center of Gravity on Ego side
        // Basically the same as RCA just moved longitudinal from mid of rear axle to the geometrical middle of the Ego vehicle
        inst->CoG_CS.dx = inst->RCA_CS.dx + 0.32 * length;  // Assumption: rear bumper to RCA is 0.18 * length
        inst->CoG_CS.dy = inst->RCA_CS.dy;
        //RCA values = inputs
        inst->CoG_CS.vx = inst->RCA_CS.vx;
        inst->CoG_CS.vy = inst->RCA_CS.vy;
        inst->CoG_CS.heading = inst->RCA_CS.heading;

        if(target_current_ref_point==0)
        {  //Target reference is Mid Rear Bumper
        //Calculate middle of Geometry
            inst->RCA_CS.dx = inst->RCA_CS.dx+(length/2.0f)*cos(inst->RCA_CS.heading);
            inst->RCA_CS.dy = inst->RCA_CS.dy+(length/2.0f)*sin(inst->RCA_CS.heading);

            inst->Sensor_CS.dx = inst->Sensor_CS.dx+(length/2.0f)*cos(inst->Sensor_CS.heading);
            inst->Sensor_CS.dy = inst->Sensor_CS.dy+(length/2.0f)*sin(inst->Sensor_CS.heading);
        }
        return 0;
    }
double CAPLEXPORT CAPLPASCAL appGetRCADx(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->RCA_CS.dx;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetRCADy(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->RCA_CS.dy;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetRCAVx(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->RCA_CS.vx;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetRCAVy(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->RCA_CS.vy;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetRCAHeading(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->RCA_CS.heading;
    }
    return -1;
}
double CAPLEXPORT CAPLPASCAL appGetCogDx(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->CoG_CS.dx;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetCogDy(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->CoG_CS.dy;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetCogVx(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->CoG_CS.vx;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetCogVy(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->CoG_CS.vy;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetCogHeading(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->CoG_CS.heading;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetSensorDx(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->Sensor_CS.dx;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetSensorDy(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->Sensor_CS.dy;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetSensorVx(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->Sensor_CS.vx;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetSensorVy(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->Sensor_CS.vy;
    }
    return -1;
}

double CAPLEXPORT CAPLPASCAL appGetSensorHeading(uint32_t handle)
{
    CaplInstanceData* instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        return instance->Sensor_CS.heading;
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

    {"dllRotationInit", (CAPL_FARCALL)appInit, "CAPL_DLL", "This function will initialize all callback functions in the CAPLDLL", 'V', 1, "D", "", {"handle"}},
    {"dllRotationEnd", (CAPL_FARCALL)appEnd, "CAPL_DLL", "This function will release the CAPL function handle in the CAPLDLL", 'V', 1, "D", "", {"handle"}},
    {"dllRotationSetValue", (CAPL_FARCALL)appSetValue, "CAPL_DLL", "This function will call a callback functions", 'L', 2, "DL", "", {"handle", "x"}},
    {"dllRotationReadData", (CAPL_FARCALL)appReadData, "CAPL_DLL", "This function will call a callback functions", 'L', 2, "DL", "", {"handle", "x"}},
    {"dllRotationCalcTarget", (CAPL_FARCALL)calculate_coordinates_target, "CAPL_DLL", "This function calculate the middle of the target coordintes in both RCA and Sensor coordinates", 'L', 12, "DFFFFFFFFFDD", "", {"handle", "length", "heading angle", "x", "y", "vx", "vy" , "mount_x", "mount_y", "mount_yaw","ego_current_ref_point 0: RCA 1: Sensor", "target_current_ref_point 0: Mid rear bumper 1:Mid Geometry"}},
    {"dllRotationGetRCADx", (CAPL_FARCALL)appGetRCADx, "CAPL_DLL", "Get the RCA dx", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetRCADy", (CAPL_FARCALL)appGetRCADy, "CAPL_DLL", "Get the RCA dy", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetRCAVx", (CAPL_FARCALL)appGetRCAVx, "CAPL_DLL", "Get the RCA vx", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetRCAVy", (CAPL_FARCALL)appGetRCAVy, "CAPL_DLL", "Get the RCA vy", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetRCAHeading", (CAPL_FARCALL)appGetRCAHeading, "CAPL_DLL", "Get the RCA heading", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetCogDx", (CAPL_FARCALL)appGetCogDx, "CAPL_DLL", "Get the CoG dx", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetCogDy", (CAPL_FARCALL)appGetCogDy, "CAPL_DLL", "Get the CoG dy", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetCogVx", (CAPL_FARCALL)appGetCogVx, "CAPL_DLL", "Get the CoG vx", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetCogVy", (CAPL_FARCALL)appGetCogVy, "CAPL_DLL", "Get the CoG vy", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetCogHeading", (CAPL_FARCALL)appGetCogHeading, "CAPL_DLL", "Get the CoG heading", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetSensorDx", (CAPL_FARCALL)appGetSensorDx, "CAPL_DLL", "Get the Sensor dx", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetSensorDy", (CAPL_FARCALL)appGetSensorDy, "CAPL_DLL", "Get the Sensor dy", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetSensorVx", (CAPL_FARCALL)appGetSensorVx, "CAPL_DLL", "Get the Sensor vx", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetSensorVy", (CAPL_FARCALL)appGetSensorVy, "CAPL_DLL", "Get the Sensor vy", 'F', 1, "L", "", {"handle"}},
    {"dllRotationGetSensorHeading", (CAPL_FARCALL)appGetSensorHeading, "CAPL_DLL", "Get the Sensor heading", 'F', 1, "L", "", {"handle"}},
    {0, 0} };
CAPLEXPORT CAPL_DLL_INFO4* caplDllTable4 = table;