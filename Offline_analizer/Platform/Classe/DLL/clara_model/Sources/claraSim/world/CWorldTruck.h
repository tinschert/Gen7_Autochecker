#ifndef CWorldTruck_H
#define CWorldTruck_H
/*!
********************************************************************************
@class CWorldTruck
@ingroup world
@brief model class of the whole CLARA simulation model (truck)

@author Robert Erhart, ett2si (22.12.2004 - 00:00:00)
@author Andreas Brunner, bnr2lr (04.07.2019)
@copyright (c) Robert Bosch GmbH 2019-2024. All rights reserved.
********************************************************************************
@remark
If you include CWorldTruck, CWorld is extended to a truck/trailer vehicle.

********************************************************************************
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CWorldTruckDoc
{
    const auto o_initCounter = "counter of init() calls";
    const auto p_staticSimulation = "switch between static and dynamic mode";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/world/vehicle/CVehicle.h>
#include <claraSim/world/vehicle/chassis/CArticulation.h>
#include <claraSim/world/obstacle/CObstacles.h>
#include <claraSim/world/roadNetwork/CRoadNetwork.h>


class CWorldTruck : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CWorldTruck( CInt NumberOfDynamicObstacles = 10, CInt NumberOfStaticObstacles = 10,
                 CInt NumberOfRoads = 1, CInt NumberOfLanes = 4,
                 CInt NumberOfRadars = 2, CInt NumberOfVideos = 1, CInt NumberOfLidars = 0 );
    virtual ~CWorldTruck();


    //*******************************
    // methods
    //*******************************
public:
    void init();
    void processVehicle( CFloat f_dT, CFloat f_time );
    void processEnvironment( CFloat f_dT, CFloat f_time );
    void processRadarSensors( CFloat f_dT, CFloat f_time );
    void processVideoSensors( CFloat f_dT, CFloat f_time );
    void processLidarSensors( CFloat f_dT, CFloat f_time );
private:
    void calc( CFloat f_dT, CFloat f_time ); // Redefine calc() here. Private methods of parent are not passed on to child.

    //*******************************
    //classes
    //*******************************
public:
    CVehicle vehicle;
    CVehicle trailer;
    CArticulation articulation;
    CRoadNetwork roadNetwork;
    CObstacles Obstacles;

    //*******************************
    //messages
    //*******************************
public:
    CMessageParameter<CBool> p_staticSimulation;

    CMessageOutput<CInt> o_initCounter;
    CMessageParameter<CBool> p_detach;  // detach trailer?
    CMessageOutput<CFloatVectorXYZ> o_zeroVector; // helper dummy CMessageOutput for syntax compatibility


    //*******************************
    //variables
    //*******************************
public:
private:
};

#endif // CWorldTruck_H
