#ifndef CVEHICLE_H
#define CVEHICLE_H

/*!
********************************************************************************
@class CVehicle
@ingroup vehicle
@brief Calculate vehicle position in absolute (world) Cartesian coordinate system

@author Robert Erhart, ett2si (22.12.2004 - 00:00:00)
@author Andreas Brunner, bnr2lr (28.05.2019)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
********************************************************************************
@remark
- car definition
@verbatim
           leftFront    rightFront
               0-----------0
                     ^ x
                     |
                     |
             y <-----. Center of Gravity (h = height over the street)
                     |
                     |
               0-----------0
           leftRear     rightRear
@endverbatim

- structure
@dot
 digraph vehicle
 {
     node [shape=box; fontsize=12;];
     edge [fontsize=10;];
     vehicle -> chassis;
     vehicle -> dashboard;
     vehicle -> driver;
     vehicle -> driveTrain;
     vehicle -> sensor;
     vehicle -> steeringSystem;
 }
@enddot

********************************************************************************
@param[in] i_staticSimulation    [bool]  switch between static or dynamic enviroment simulation. Verhicle states would be updated, but the scene didn't change.
@param[in] i_FxyzArticulation    [N]     articulation x,y,z force vector (input from coupled vehicle, in current vehicle's coordinate system)
********************************************************************************
@param[out] o_numberOfRadars     [-]     number of radar sensors
@param[out] o_numberOfVideos     [-]     number of video sensors
@param[out] o_numberOfLidars     [-]     number of lidar sensors
@param[out] o_x                  [m]     x position of vehicle in world coordinate-system (center of gravity of ego) (use o_xyzWorld; only needed for report visualisation)
@param[out] o_y                  [m]     y position of vehicle in world coordinate-system (center of gravity of ego) (use o_xyzWorld; only needed for report visualisation)
@param[out] o_z                  [m]     z position of vehicle in world coordinate-system (center of gravity of ego) (use o_xyzWorld; only needed for report visualisation)
@param[out] o_xyzWorld           [m]     (x,y,z) position vector of vehicle in world coordinate-system (center of gravity of ego)
@param[out] o_latitude           [deg]   ego latitude in decimal degrees, positive values = north of Equator
@param[out] o_longitude          [deg]   ego longitude in decimal degrees, positive values = east of Prime Meridian
@param[out] o_s                  [m]     driving distance of vehicle
@param[out] o_angleRollPitchYawSurface  [rad]  driving surface angle vector; world <-> driving Surface
@param[out] o_angleRollPitchYawChassis  [rad]  vehicle's (roll, pitch, yaw) angle vector; world <-> chassis
@param[out] o_gammaRelativeCourse [rad]   angle relative to course
@param[out] o_velocity           [m/s]   velocity of vehicle
@param[out] o_beta               [rad]   sideslip angle
@param[out] o_vChassis           [m/s]   velocity vector car coordinate-system
@param[out] o_vWorld             [m/s]   vehicle velocity vector (x,y,z) in world coordinate-system
@param[out] o_yawRate            [rad/s] yaw rate of vehicle
@param[out] o_road               [int]   current road index of the ego; negative value indicates off-road position.
@param[out] o_lane               [int]   current lane ID of the ego. Zero = reference lane, positive = lanes to the left, negative = lanes to the right.
@param[out] o_lateralOffset      [m]     current lateral offset from center line of road 'o_road', lane 'o_lane'
@param[out] o_sCourse            [m]     course position on the target road and lane (see p_lane and p_road)
@param[out] o_searchIndexLane    []      nearest lane
@param[out] o_distanceToCourse   [m]     distance to course relative to nearest lane o_searchIndexLane
********************************************************************************
@param[in,out] p_lateralOffset       [m]     lateral offset from course (used by CDriver and for init)
@param[in,out] p_targetLateralOffset [m]     target lateral offset from course (used by CDriver)
@param[in,out] p_lateralVelocity     [m/s]   lateral velocity (used by CDriver)
@param[in,out] p_road                []      >=0; target road index of the ego (used by CDriver and for init)
@param[in,out] p_lane                []      target lane ID of the ego on road 'p_road' (used by CDriver and for init)
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CVehicleDoc
{
    const auto o_numberOfRadars = "number of radar sensors";
    const auto o_numberOfVideos = "number of video sensors";
    const auto o_numberOfLidars = "number of lidar sensors";
    const auto o_xyzWorld       = "[m] (x,y,z) position vector of vehicle in world coordinate-system (center of gravity of ego)";
    const auto o_latitude       = "[deg] ego latitude in decimal degrees, positive values = north of Equator";
    const auto o_longitude      = "[deg] ego longitude in decimal degrees, positive values = east of Prime Meridian";
    const auto o_s              = "[m] driving distance of vehicle";
    const auto o_angleRollPitchYawChassis = "[rad] vehicle's (roll, pitch, yaw) angle vector; world <-> chassis";
    const auto o_angleRollPitchYawSurface = "[rad] driving surface angle vector; world <-> driving Surface";
    const auto o_gammaRelativeCourse = "[rad] angle relative to course";
    const auto o_beta           = "[rad] sideslip angle";
    const auto o_velocity       = "[m/s] velocity of vehicle";
    const auto o_vChassis       = "[m/s] velocity vector car coordinate-system";
    const auto o_vWorld         = "[m/s] vehicle velocity vector (x,y,z) in world coordinate-system";
    const auto o_yawRate        = "[rad/s] yaw rate of vehicle";

    const auto o_angleSteeringWheel = "[rad] steering wheel angle";
    const auto o_road           =     "current road index of the ego; negative value indicates off-road position.";
    const auto o_lane           =     "current lane ID of the ego. Zero = reference lane, positive = lanes to the left, negative = lanes to the right.";
    const auto o_lateralOffset  =     "[m] lateral offset from center line of road 'o_road', lane 'o_lane'";
    const auto o_sCourse        =     "[m] course position on the target road and lane (see p_lane and p_road)";
    const auto o_searchIndexLane =    "[] nearest lane";
    const auto o_distanceToCourse =   "[m] distance to course relative to nearest lane o_searchIndexLane";

    const auto p_lateralOffset          = "[m] lateral offset from course (used by driver and for init)";
    const auto p_targetLateralOffset    = "[m] target lateral offset from course (used by driver)";
    const auto p_lateralVelocity        = "[m/s] lateral velocity (used by CDriver)";
    const auto p_road                   = "target road index of the ego (used by CDriver and for init)";
    const auto p_lane                   = "target lane ID of the ego on road 'p_road' (used by CDriver and for init)";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/world/roadNetwork/CRoadNetwork.h>
#include <claraSim/world/obstacle/CObstacles.h>
#include <claraSim/world/vehicle/driver/CDriver.h>
#include <claraSim/world/vehicle/dashboard/CDashboard.h>
#include <claraSim/world/vehicle/sensor/CRadar.h>
#include <claraSim/world/vehicle/sensor/CVideo.h>
#include <claraSim/world/vehicle/sensor/CLidar.h>
#include "chassis/CChassisCar.h"
#include <claraSim/world/vehicle/driveTrain/CDriveTrain.h>
#include <claraSim/world/vehicle/steeringSystem/CSteeringSystem.h>
#include <vector>

class CVehicle : public CModule<5>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CVehicle( CInt numberOfRadars, CInt numberOfVideos, CInt numberOfLidars );
    virtual ~CVehicle();
private:
    CVehicle( const CVehicle& obj ) = delete;


    //*******************************
    //classes
    //*******************************
public:
    CDriver driver;
    CDashboard dashboard;
    CModuleVector<CRadar> radars;
    CModuleVector<CVideo> videos;
    CModuleVector<CLidar> lidars;
    CDriveTrain driveTrain;
    CChassisCar chassis;
    CSteeringSystem steeringSystem;
    CRoadNetwork* m_roadNetwork_p;
private:


    //*******************************
    //messages
    //*******************************
public:
    CMessageOutput<CInt> o_numberOfRadars;
    CMessageOutput<CInt> o_numberOfVideos;
    CMessageOutput<CInt> o_numberOfLidars;

    CMessageOutput<CFloat, 100000> o_x; // (use o_xyzWorld; only needed for report visualization)
    CMessageOutput<CFloat, 100000> o_y; // (use o_xyzWorld; only needed for report visualization)
    CMessageOutput<CFloat, 100000> o_z; // (use o_xyzWorld; only needed for report visualization)
    CMessageOutput<CFloatVectorXYZ> o_xyzWorld;
    CMessageOutput<CFloat> o_latitude;
    CMessageOutput<CFloat> o_longitude;
    CMessageOutput<CFloat> o_s;
    CMessageOutput<CFloatVectorXYZ> o_angleRollPitchYawSurface;
    CMessageOutput<CFloatVectorXYZ> o_angleRollPitchYawChassis;
    CMessageOutput<CFloat> o_gammaRelativeCourse;
    CMessageOutput<CFloat> o_beta;
    CMessageOutput<CFloat> o_velocity;
    CMessageOutput<CFloatVectorXYZ> o_vChassis;
    CMessageOutput<CFloatVectorXYZ> o_vWorld;
    CMessageOutput<CFloat> o_yawRate;
    CMessageOutput<CFloat> o_angleSteeringWheel;
    CMessageOutput<CInt>   o_road;
    CMessageOutput<CInt>   o_lane;
    CMessageOutput<CFloat> o_lateralOffset;
    CMessageOutput<CFloat> o_sCourse;
    CMessageOutput<CInt>   o_searchIndexLane;
    CMessageOutput<CFloat> o_distanceToCourse;

    CMessageParameter<CBool> p_detach; // helper dummy CMessageParameter for syntax compatibility

    CMessageParameter<CFloat> p_lateralOffset;
    CMessageParameter<CFloat> p_targetLateralOffset;
    CMessageParameter<CFloat> p_lateralVelocity;
    CMessageParameter<CInt> p_road;
    CMessageParameter<CInt> p_lane;
private:
    CMessageInput<CBool>  i_staticSimulation;
    CMessageInput<CFloatVectorXYZ> i_FxyzArticulation;

    // input via internal modules (documentation only here)
    CMessageInput<CFloat> i_velocity;
    CMessageInput<CFloat> i_beta;
    CMessageInput<CFloatVectorXYZ> i_vChassis;
    CMessageInput<CFloat> i_yawRate;
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYawSuspension; // [rad] (roll,pitch,yaw) angle vector of the chassis
    CMessageInput<CFloat> i_h;                                    // [m] centre-of-gravity height over street level

    //*******************************
    // methods
    //*******************************
public:
    void init( CRoadNetwork& f_roadNetwork_r,
               CObstacles& f_obstacles_r,
               IMessage<CFloatVectorXYZ>& f_FxyzArticulation,
               IMessage<CBool>& f_staticSimulation );
private:
    void calcPre( CFloat f_dT, CFloat f_time );
    CFloatVector& ddt( CFloatVector& state );

    /*! Handle connections to another road. Update road and lane assignment as well as
        GNSS output, roll/pitch/yaw angle output, ... */
    void calcPost( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
    char vehicle_type = 'c';  // car
private:
    enum { X, Y, Z, GAMMA, S, NumberOfStates };
    //unsigned int m_index;
    SCoursePositionInfo m_positionInfo_s;
    ::std::vector<::std::vector<SCoursePositionInfo> > m_positionInfo_as;
    CFloat m_gammaRelativeCourse;
};

#endif // CVEHICLE_H
