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

#if defined(_WIN64) || defined(__linux__)
#define X64
#endif

#include "../../Includes/cdll.h"
#include "../../Includes/VIA.h"
#include "../../Includes/VIA_CDLL.h"

#include "claraSim/framework/numericLib.h"
#include "claraSim/framework/CFloatVector.h"
#include "claraSim/framework/CMessage.h"
#include "claraSim/world/vehicle/sensor/CRadar.h"
#include "clara_MathLibrary.hpp"

#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <chrono>
#include <map>

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

    double sim_time_old_;
    // these members are linked ot the radar sensor model and stimulated later with the input data from cloe side
    CMessageInput<CFloatVectorXYZ> xyzWorld_;
    CMessageInput<CFloatVectorXYZ> velocityXYZWorld_;
    CMessageInput<CFloatVectorXYZ> accelerationXYZVehicleEgo_;
    CMessageInput<CFloatVectorXYZ> angleRollPitchYawEgo_;
    CMessageInput<CFloat> yawRateEgo_;
    //TODO (matthias): define number of dynamic and static objects, currently set to 0
    CObstacles obstacles_r_{40, 0U};
    CMessageInput<CBool> staticSimulation_;

    // radar model
    CRadar radar_model_;

    // math functions
    MathLibrary::TargetCalculation calculation_class;
    MathLibrary::CoordinateSystem contour_cs;

    //data handling
    int CoeffFlipRadar;
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
      sim_time_old_(),
      xyzWorld_(),
      velocityXYZWorld_(),
      accelerationXYZVehicleEgo_(),
      angleRollPitchYawEgo_(),
      yawRateEgo_(),
      obstacles_r_{40, 0U},
      staticSimulation_(),
      radar_model_(),
      calculation_class(),
      contour_cs()
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
long CAPLEXPORT CAPLPASCAL appInitClaraModel(uint32 handle, double sensor_mount_from_cog_dx, double sensor_mount_from_cog_dy, double sensor_mount_from_cog_dz, 
                                            double sensor_mount_yaw_angle, double loc_angle_separation, int loc_max_nr_per_obj)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    // Initialize the Clara model by giving Clara references to where the data will be written in later cycles
    instance->radar_model_.init(instance->xyzWorld_,
                instance->velocityXYZWorld_,
                instance->accelerationXYZVehicleEgo_,
                instance->angleRollPitchYawEgo_,
                instance->yawRateEgo_,
                instance->obstacles_r_,
                instance->staticSimulation_);
    
    // TODO(matthias): check if more parameters need to be set, currently a lot of default values are taken
    instance->radar_model_.p_sensorConfiguration.set(1);  // -1 means connector up

    // Set the mounting yaw angle of the sensor
    CFloatVectorXYZ rpy{0.0F, 0.0F, sensor_mount_yaw_angle};
    instance->radar_model_.p_angleRollPitchYawVehicleMounting.set(rpy);

    // Set the mounting position of the sensor
    CFloatVectorXYZ mount_from_cog_clara{sensor_mount_from_cog_dx, sensor_mount_from_cog_dy, sensor_mount_from_cog_dz};
    instance->radar_model_.p_xyzVehicleMountingPos.set(mount_from_cog_clara);

    // Set parameters to steer the number of generated locations
    instance->radar_model_.p_angleSeparationSensor.set(loc_angle_separation / 180.0F * M_PI);  // 7 degree is the default value provided by CLARA
    instance->radar_model_.p_maxNumberOfReflectionsPerObstacles.set(loc_max_nr_per_obj);

    // Set some further parameters of the radar, values come from Cloe integration of the Clara model
    instance->radar_model_.p_anglesFieldOfViewSegments.set(
        sim::to_radians({-90.0F, -45.0F, -10.0F, 10.0F, 45.0F, 90.0F}));
    instance->radar_model_.p_maxRangesFieldOfViewSegments.set({510.0F, 510.0F, 510.0F, 510.0F, 510.0F});
    instance->radar_model_.p_closeRange.set(0.0F); // 30.0F - 30 m is the default value provided by CLARA

    return 0;
}

long CAPLEXPORT CAPLPASCAL appUpdateEgoClara(uint32 handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    // Clara expects world coordinates, so also the ego position has to be given
    // For the first PoC we set the Ego to be standstill at (0/0)
    // Here we are referring to the link pointer of our intern members. Unfortunately, there does not seem to be a simpler option.
    // These members were linked in the radar_model_.init() as references to the radar model.
    // The link pointer receives the communication pointer of the respective wrapper class.
    // later in the call of the radar_model_.process() method clara will write the communication pointer value to the work value
    IMessageValue<CFloatVectorXYZ>* xyzWorld_comm = instance->xyzWorld_.getLinkPointer();
    IMessageValue<CFloatVectorXYZ>* velocityXYZWorld_comm = instance->velocityXYZWorld_.getLinkPointer();
    IMessageValue<CFloatVectorXYZ>* accelerationXYZVehicleEgo_comm =
        instance->accelerationXYZVehicleEgo_.getLinkPointer();
    IMessageValue<CFloatVectorXYZ>* angleRollPitchYawEgo_comm =
        instance->angleRollPitchYawEgo_.getLinkPointer();
    IMessageValue<CFloat>* yawRateEgo_comm = instance->yawRateEgo_.getLinkPointer();

    // now from the link pointer we get a reference to the value itself so that we can write to it and stimulate it
    CFloatVectorXYZ& xyzWorld_ref = xyzWorld_comm->getValue();
    CFloatVectorXYZ& velocityXYZWorld_ref = velocityXYZWorld_comm->getValue();
    CFloatVectorXYZ& accelerationXYZVehicleEgo_ref = accelerationXYZVehicleEgo_comm->getValue();
    CFloatVectorXYZ& angleRollPitchYawEgo_ref = angleRollPitchYawEgo_comm->getValue();
    CFloat& yawRateEgo_ref = yawRateEgo_comm->getValue();

    // provide the ego distance in world frame
    xyzWorld_ref.X(0.0);
    xyzWorld_ref.Y(0.0);
    xyzWorld_ref.Z(0.0);
  
    // provide the ego velocity in world frame
    velocityXYZWorld_ref.X(0.0);
    velocityXYZWorld_ref.Y(0.0);
    velocityXYZWorld_ref.Z(0.0);

    // provide the ego acceleration in ego coordinate frame
    accelerationXYZVehicleEgo_ref.X(0.0);
    accelerationXYZVehicleEgo_ref.Y(0.0);
    accelerationXYZVehicleEgo_ref.Z(0.0);

    // provide the ego yaw pitch and roll in world frame
    angleRollPitchYawEgo_ref.X(0.0);
    angleRollPitchYawEgo_ref.Y(0.0);
    angleRollPitchYawEgo_ref.Z(0.0);

    // provide the ego yaw rate in world frame
    yawRateEgo_ref = 0.0;

    return 0;
}

long CAPLEXPORT CAPLPASCAL appUpdateTgtClara(uint32 handle, int target_id, int target_type, double target_dx, double target_dy, double target_dz, double target_vx, double target_vy, double target_vz,
                                            double target_acceleration, double target_yaw_angle, double target_length, double target_width, double target_height)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    // Clara expects target data to be from ego cog to tgt cog
    // Here we are referring to the link pointer of our intern members. Unfortunately, there does not seem to be a simpler option.
    // These members were linked in the radar_model_.init() as references to the radar model.
    // The link pointer receives the communication pointer of the respective wrapper class.
    // later in the call of the radar_model_.process() method clara will write the communication pointer value to the work value
    IMessageValue<CFloatVectorXYZ>* dyn_xyzWorld =
        instance->obstacles_r_.ObstacleDynamic.at(target_id).o_xyzWorld.getLinkPointer();
    IMessageValue<CFloatVectorXYZ>* dyn_vWorld =
        instance->obstacles_r_.ObstacleDynamic.at(target_id).o_vWorld.getLinkPointer();
    IMessageValue<CFloat>* dyn_acc_object_frame =
        instance->obstacles_r_.ObstacleDynamic.at(target_id).o_acceleration.getLinkPointer();
    IMessageValue<CFloat>* dyn_yawAngleWorld =
        instance->obstacles_r_.ObstacleDynamic.at(target_id).o_yawAngle.getLinkPointer();

    IMessageValue<CFloat>* dyn_pVisibility =
        instance->obstacles_r_.ObstacleDynamic.at(target_id).p_visibility.getLinkPointer();
    IMessageValue<CInt>* dyn_pType = 
        instance->obstacles_r_.ObstacleDynamic.at(target_id).p_type.getLinkPointer();
    IMessageValue<CFloat>* dyn_depth =
        instance->obstacles_r_.ObstacleDynamic.at(target_id).p_depth.getLinkPointer();
    IMessageValue<CFloat>* dyn_height =
        instance->obstacles_r_.ObstacleDynamic.at(target_id).p_height.getLinkPointer();
    IMessageValue<CFloat>* dyn_width =
        instance->obstacles_r_.ObstacleDynamic.at(target_id).p_width.getLinkPointer();

    IMessageValue<CFloatVector>* dyn_xWorldContour =
        instance->obstacles_r_.ObstacleDynamic.at(target_id).o_xWorldContour.getLinkPointer();
    IMessageValue<CFloatVector>* dyn_yWorldContour =
        instance->obstacles_r_.ObstacleDynamic.at(target_id).o_yWorldContour.getLinkPointer();
    IMessageValue<CFloatVector>* dyn_zWorldContour =
        instance->obstacles_r_.ObstacleDynamic.at(target_id).o_zWorldContour.getLinkPointer();

    // now from the link pointer we get a reference to the value itself so that we can write to it and stimulate it
    CFloatVectorXYZ& dyn_xyzWorld_ref = dyn_xyzWorld->getValue();
    CFloatVectorXYZ& dyn_vWorld_ref = dyn_vWorld->getValue();
    CFloat& dyn_acc_object_frame_ref = dyn_acc_object_frame->getValue();
    CFloat& dyn_yawAngleWorld_ref = dyn_yawAngleWorld->getValue();

    CFloat& dyn_pVisibility_ref = dyn_pVisibility->getValue();
    CInt& dyn_pType_ref = dyn_pType->getValue();
    CFloat& dyn_depth_ref = dyn_depth->getValue();
    CFloat& dyn_height_ref = dyn_height->getValue();
    CFloat& dyn_width_ref = dyn_width->getValue();
    CFloatVector& dyn_xWorldContour_ref = dyn_xWorldContour->getValue();
    CFloatVector& dyn_yWorldContour_ref = dyn_yWorldContour->getValue();
    CFloatVector& dyn_zWorldContour_ref = dyn_zWorldContour->getValue();

    // provide the target distance in world frame
    dyn_xyzWorld_ref.X(target_dx);
    dyn_xyzWorld_ref.Y(target_dy);
    dyn_xyzWorld_ref.Z(target_dz);
  
    // provide the target velocity in world frame
    dyn_vWorld_ref.X(target_vx);
    dyn_vWorld_ref.Y(target_vy);
    dyn_vWorld_ref.Z(target_vz);

    // provide the target acceleration in target coordinate frame
    dyn_acc_object_frame_ref = target_acceleration;

    // provide the target yaw pitch and roll in world frame
    dyn_yawAngleWorld_ref = target_yaw_angle;

    // set the visibility, type, depth, height and width of the object.
    dyn_pVisibility_ref = 1.0;  // existence probability always set to 100%
    dyn_pType_ref = instance->calculation_class.map_type(target_type);
    dyn_depth_ref = target_length;
    dyn_height_ref = target_width;
    dyn_width_ref = target_height;

    // provide contour (edges) points P1 to P4
    // @verbatim
    //       LF           RF
    //         ____________
    //        |\          .\
    //   P4-->| \         .<--P3
    //        |. \ . . . ..  \
    //        \   \           \
    //   depth \   \___________\
    //          \  |   o       | height
    //        P1-->|           |<--P2
    //            \|___________|
    //                 width
    //            LR           RR
    instance->calculation_class.calculate_contour(target_height,target_width,target_length,target_dx,target_dy,target_yaw_angle);
    instance->contour_cs = instance->calculation_class.get_CS();

    /// provide contour points to clara
    dyn_xWorldContour_ref[0] = instance->contour_cs.dx_rear_left;
    dyn_xWorldContour_ref[1] = instance->contour_cs.dx_rear_right;
    dyn_xWorldContour_ref[2] = instance->contour_cs.dx_front_right;
    dyn_xWorldContour_ref[3] = instance->contour_cs.dx_front_left;

    dyn_yWorldContour_ref[0] = instance->contour_cs.dy_rear_left;
    dyn_yWorldContour_ref[1] = instance->contour_cs.dy_rear_right;
    dyn_yWorldContour_ref[2] = instance->contour_cs.dy_front_right;
    dyn_yWorldContour_ref[3] = instance->contour_cs.dy_front_left;

    dyn_zWorldContour_ref[0] = target_height/2;
    dyn_zWorldContour_ref[1] = target_height/2;
    dyn_zWorldContour_ref[2] = target_height/2;
    dyn_zWorldContour_ref[3] = target_height/2;

    return 0;
}

long CAPLEXPORT CAPLPASCAL appCalcClara(uint32 handle)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance == NULL)
    {
        return -1;
    }
    // Get ego data set values needed by radar model
    // Here we are referring to the link pointer of our intern members. Unfortunately, there does not seem to be a simpler option.
    // These members were linked in the radar_model_.init() as references to the radar model.
    // The link pointer receives the communication pointer of the respective wrapper class.
    // later in the call of the radar_model_.process() method clara will write the communication pointer value to the work value

    /// the sim time delta
    const auto sim_time_now = std::chrono::system_clock::now().time_since_epoch();
    const auto sim_time_now_seconds = 
        static_cast<double>(std::chrono::duration_cast< std::chrono::nanoseconds >(sim_time_now).count());
    const auto sim_time_delta = sim_time_now_seconds - instance->sim_time_old_;
    instance->sim_time_old_ = sim_time_now_seconds;

    // at least one object detected, set
    // copies values from com pointer to work value inside "i_ signals" from CRadar and CSensor
    // we need to set this extern trigger, otherwise the clara does not calculate any locations
    instance->radar_model_.setExternTrigger();

    // the process method copies the communication values to the work values for input signals,
    // and copies the work values to communication values for the out signals
    instance->radar_model_.process(sim_time_delta, sim_time_now_seconds);

    return 0;
}
// ============================================================================
// Getters - Location calculations
// ============================================================================
int CAPLEXPORT CAPLPASCAL appGetNextValidLoc(uint32_t handle, int previous_loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    
    if (instance != NULL)
    {
        int numlocs = (int) instance->radar_model_.o_xRadarLocation.get().size();
        int buffer = 0;

        // We expect on CANoe side that the initial request has the ID -1
        // In this case we switch the buffer to 0 to fulfill idx != previous_loc_nr later on
        if(previous_loc_nr == -1)
        {
            buffer = 0;
        }
        else
        {
            buffer = previous_loc_nr;
        }

        // loop through locations to find NEXT valid location
        for (int idx = buffer; idx < numlocs; idx++) {
            // do not consider a location if visibility is set to very small value and only take next id
            if (instance->radar_model_.o_visibilityLocation.get()[idx] > 0.001 && idx != previous_loc_nr) {
                return idx;
            }
        }
        return -1;
    }
    return -10;
}
double CAPLEXPORT CAPLPASCAL appGetRadialDistance(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    double radial_distance = 0;
    if (instance != NULL)
    {
        radial_distance = std::sqrt(std::pow(instance->radar_model_.o_xRadarLocation.get()[loc_nr], 2) +
                                         std::pow(instance->radar_model_.o_yRadarLocation.get()[loc_nr], 2) +
                                         std::pow(instance->radar_model_.o_zRadarLocation.get()[loc_nr], 2));
        return radial_distance;
    }
    return -3.141F;
}
double CAPLEXPORT CAPLPASCAL appGetAzimuthAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    double azimuth_angle = 0;
    if (instance != NULL)
    {
        azimuth_angle = instance->radar_model_.o_alphaRadarLocation.get()[loc_nr];
        return azimuth_angle;
    }
    return -3.142F;
}
double CAPLEXPORT CAPLPASCAL appGetElevationAngle(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    double elevation_angle = 0;
    if (instance != NULL)
    {
        elevation_angle = instance->radar_model_.o_elevationAngleLocation.get()[loc_nr];
        return elevation_angle;
    }
    return -3.143F;
}
double CAPLEXPORT CAPLPASCAL appGetRadialVelocity(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    double radial_velocity = 0;
    if (instance != NULL)
    {
        radial_velocity = instance->radar_model_.o_vRadialRadarLocation.get()[loc_nr];
        return radial_velocity;
    }
    return -3.144F;
}
double CAPLEXPORT CAPLPASCAL appGetRCS(uint32_t handle, int loc_nr)
{
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    double rcs = 0;
    if (instance != NULL)
    {
        rcs = instance->radar_model_.o_rcsCenterLocation.get()[loc_nr];
        return rcs;
    }
    return -3.144F;
}

// ============================================================================
// FORD ONLY
// Definition fo the functions for the ByteArray Handling for CAN TP
// ============================================================================

//Currently hardcoded for 500 locations
long CAPLEXPORT CAPLPASCAL appClaraPushLocToByteArray(uint32_t handle, uint32_t flagFlip, uint32_t radar_id)
{
    int iteration_count = 0;
    int clara_loc_id = 0;
    CaplInstanceData *instance = GetCaplInstanceData(handle);
    if (instance != NULL)
    {
        // Need to flip azimuth and elevation of FL and RR in Ford
        if(flagFlip) instance->CoeffFlipRadar = -1;
        else instance->CoeffFlipRadar = 1;
        clara_loc_id= appGetNextValidLoc(handle, -1);
        // iterates through the location sgenerated for this object and add it to the byte array
        // for now limit hardcoded to 500 locations
        for(iteration_count=1;iteration_count<=500;iteration_count++)
        {
            // As only 1 single handle is generated out of the registerCAPLDLL function, differenciation must happen in dll
            // Or 5 dlls
            switch(radar_id)
            {
                case 1: // Front Center
                Write_ByteArray_RXX_Location(iteration_count,instance->byteArray_loc_FC, clara_loc_id, instance);
                instance->total_nr_of_loc_FC = instance->total_nr_of_loc_FC + 1;
                break;
                case 2: // Front Left
                Write_ByteArray_RXX_Location(iteration_count,instance->byteArray_loc_FL, clara_loc_id, instance);
                instance->total_nr_of_loc_FL = instance->total_nr_of_loc_FL + 1;
                break;
                case 3: // Front Right
                Write_ByteArray_RXX_Location(iteration_count,instance->byteArray_loc_FR, clara_loc_id, instance);
                instance->total_nr_of_loc_FR = instance->total_nr_of_loc_FR + 1;
                break;
                case 4: // Rear Left
                Write_ByteArray_RXX_Location(iteration_count,instance->byteArray_loc_RL, clara_loc_id, instance);
                instance->total_nr_of_loc_RL = instance->total_nr_of_loc_RL + 1;
                break;
                case 5: // Rear Right
                Write_ByteArray_RXX_Location(iteration_count,instance->byteArray_loc_RR, clara_loc_id, instance);
                instance->total_nr_of_loc_RR = instance->total_nr_of_loc_RR + 1;
                break;
            }

            clara_loc_id= appGetNextValidLoc(handle, clara_loc_id);
            //escape the for loop when there are no other locations
            if(!(clara_loc_id>=0)) break;
        }
        return 0;
    }
    return -1;
}

//Update the ByteArray on CAPL side by call by reference
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
        return 0;
    }
    return -1;
}

long CAPLEXPORT CAPLPASCAL appResetClaraModel(uint32_t handle, uint32_t radar_id)
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
        instance->CoeffFlipRadar = 1;
        return 0;
    }
    return -1;
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


// ============================================================================
// CAPL_DLL_INFO_LIST : list of exported functions
//   The first field is predefined and mustn't be changed!
//   The list has to end with a {0,0} entry!
// New struct supporting function names with up to 50 characters
// ============================================================================
CAPL_DLL_INFO4 table[] = {
    {CDLL_VERSION_NAME, (CAPL_FARCALL)CDLL_VERSION, "", "", CAPL_DLL_CDECL, 0xabcd, CDLL_EXPORT},
    {"dllInitClaraDll", (CAPL_FARCALL)appInit, "CAPL_DLL", "This function will initialize all callback functions in the CAPLDLL", 'V', 1, "D", "", {"handle"}},
    {"dllEndClaraDll", (CAPL_FARCALL)appEnd, "CAPL_DLL", "This function will release the CAPL function handle in the CAPLDLL", 'V', 1, "D", "", {"handle"}},
    {"dllClaraInitModel", (CAPL_FARCALL)appInitClaraModel, "CAPL_DLL", "This function initializes basic parameters of the Clara Model", 'L', 7, "DFFFFFL", "", {"handle", "sensor_mount_from_cog_dx", "sensor_mount_from_cog_dy", "sensor_mount_from_cog_dz", "sensor_mount_yaw_angle", "loc_angle_separation", "loc_max_nr_per_obj"}},
    {"dllClaraUpdateEgo", (CAPL_FARCALL)appUpdateEgoClara, "CAPL_DLL", "This function updates the data of the ego vehicle in reference to the world coordinate system", 'L', 1, "D", "", {"handle"}},
    {"dllClaraUpdateTgt", (CAPL_FARCALL)appUpdateTgtClara, "CAPL_DLL", "This function updates the data of the target vehicle in reference to the world coordinate system", 'L', 14, "DLLFFFFFFFFFFF", "", {"handle", "target_id", "target_type", "target_dx", "target_dy", "target_dz", "target_vx", "target_vy", "target_vz", "target_acceleration", "target_yaw_angle", "target_length", "target_width", "target_height"}},
    {"dllClaraCalc", (CAPL_FARCALL)appCalcClara, "CAPL_DLL", "This function triggers the calculation via Clara with the previously given data", 'L', 1, "D", "", {"handle"}},
    {"dllClaraGetTotalNrLoc", (CAPL_FARCALL)appGetTotalNrLoc, "CAPL_DLL", "This function gets the total nr of locations", 'L', 2, "DD", "", {"handle", "radarId"}},
    {"dllClaraPushLocToByteArray", (CAPL_FARCALL)appClaraPushLocToByteArray, "CAPL_DLL", "This parse the locations generated in the byte array", 'L', 3, "DDD", "", {"handle", "flagFlipSensor", "radarId"}},
    {"dllClaraGetByteArray", (CAPL_FARCALL)appGetByteArray, "CAPL_DLL", "This function sets the byte array", 'L', 3, "LBD", "\000\001", {"handle", "byteArray", "radarId"}},
    {"dllResetClaraModel", (CAPL_FARCALL)appResetClaraModel, "CAPL_DLL", "This function reset the Clara model", 'L', 2, "DD", "", {"handle", "radarId"}},
    {"dllClaraGetNextValidLoc", (CAPL_FARCALL)appGetNextValidLoc, "CAPL_DLL", "This function gives back the ID of the next valid location. -1 in case no more valid locations.", 'L', 2, "DL", "", {"handle", "previous_loc_nr"}},
    {"dllClaraGetRadialDistance", (CAPL_FARCALL)appGetRadialDistance, "CAPL_DLL", "This function gives back the radial distance of the location with the loc_nr given.", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllClaraGetRadialVelocity", (CAPL_FARCALL)appGetRadialVelocity, "CAPL_DLL", "This function gives back the radial velocity of the location with the loc_nr given.", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllClaraGetAzimuthAngle", (CAPL_FARCALL)appGetAzimuthAngle, "CAPL_DLL", "This function gives back the azimuth angle (horizontal) of the location with the loc_nr given.", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllClaraGetElevationAngle", (CAPL_FARCALL)appGetElevationAngle, "CAPL_DLL", "This function gives back the elevation angle (vertical) of the location with the loc_nr given.", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {"dllClaraGetRCS", (CAPL_FARCALL)appGetRCS, "CAPL_DLL", "This function gives back the RCS of the location with the loc_nr given.", 'F', 2, "DL", "", {"handle", "loc_nr"}},
    {0, 0}};
CAPLEXPORT CAPL_DLL_INFO4 *caplDllTable4 = table;