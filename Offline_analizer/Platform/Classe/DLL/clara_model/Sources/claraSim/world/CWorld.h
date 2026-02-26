#ifndef CWorld_H
#define CWorld_H
/*!
********************************************************************************
@class CWorld
@ingroup world
@brief model class of the whole CLARA simulation model

@author Robert Erhart, ett2si (22.12.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
********************************************************************************
@remark
if you include CWorld, you can simple use the whole simulation model in your
environment
********************************************************************************
********************************************************************************
@param[out] o_initCounter           []     counter of init() calls
********************************************************************************
@param[in,out] p_staticSimulation   [bool] switch between static and dynamic mode
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CWorldDoc
{
    const auto o_initCounter = "counter of init() calls";
    const auto p_staticSimulation = "switch between static and dynamic mode";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/world/vehicle/CVehicle.h>
#include <claraSim/world/obstacle/CObstacles.h>
#include <claraSim/world/roadNetwork/CRoadNetwork.h>


class CWorld : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CWorld( CInt NumberOfDynamicObstacles = 10, CInt NumberOfStaticObstacles = 10,
            CInt NumberOfRoads = 1, CInt NumberOfLanes = 4,
            CInt NumberOfRadars = 2, CInt NumberOfVideos = 1, CInt NumberOfLidars = 0 );
    virtual ~CWorld();


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
    void calc( CFloat f_dT, CFloat f_time );


    //*******************************
    //classes
    //*******************************
public:
    CVehicle vehicle;
    CRoadNetwork roadNetwork;
    CObstacles Obstacles;


    //*******************************
    //messages
    //*******************************
public:
    CMessageParameter<CBool> p_staticSimulation;

    CMessageOutput<CInt> o_initCounter;
    CMessageOutput<CFloatVectorXYZ> o_zeroVector;  // helper dummy CMessageOutput for syntax compatibility


    //*******************************
    //variables
    //*******************************
public:
private:
};

#endif // CWorld_H
