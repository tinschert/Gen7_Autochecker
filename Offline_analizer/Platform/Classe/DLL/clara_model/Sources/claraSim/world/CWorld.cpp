/*******************************************************************************
author Robert Erhart, ett2si (22.12.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004-2024. All rights reserved.
*******************************************************************************/

#include "CWorld.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CWorld::CWorld( CInt NumberOfDynamicObstacles, CInt NumberOfStaticObstacles,
                CInt NumberOfRoads, CInt NumberOfLanes,
                CInt NumberOfRadars, CInt NumberOfVideos, CInt NumberOfLidars ):
    vehicle( NumberOfRadars, NumberOfVideos, NumberOfLidars ),
    roadNetwork( NumberOfRoads, NumberOfLanes ),
    Obstacles( NumberOfDynamicObstacles, NumberOfStaticObstacles )
{
    addMessageParameter( p_staticSimulation, false, CWorldDoc::p_staticSimulation );
    addMessageOutput( o_initCounter, 0, CWorldDoc::o_initCounter );
    addMessageOutput( o_zeroVector, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );

    init();
}

CWorld::~CWorld()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CWorld::init()
{
    /* Connect input with internal variables */
    CInt l_initCounter = o_initCounter.get(); //preserve old value

    /* Initialization messages */
    initializationMessages();

    /* Initialization internal variables */

    /* init objects AND defines communication between objects */
    roadNetwork.init();

    Obstacles.init( roadNetwork, p_staticSimulation );

    vehicle.init( roadNetwork, Obstacles, o_zeroVector, p_staticSimulation );

    o_initCounter = l_initCounter + 1;
}

void CWorld::processVehicle( CFloat f_dT, CFloat f_time )
{
    process( f_dT, f_time ); //calc his own process
    vehicle.process( f_dT, f_time );
}

void CWorld::processEnvironment( CFloat f_dT, CFloat f_time )
{
    Obstacles.process( f_dT, f_time );
}

void CWorld::processRadarSensors( CFloat f_dT, CFloat f_time )
{
    for( auto index = 0U; index < vehicle.radars.size(); index++ )
    {
        vehicle.radars[index].process( f_dT, f_time );
    }
}

void CWorld::processVideoSensors( CFloat f_dT, CFloat f_time )
{
    for( auto index = 0U; index < vehicle.videos.size(); index++ )
    {
        vehicle.videos[index].process( f_dT, f_time );
    }
}

void CWorld::processLidarSensors( CFloat f_dT, CFloat f_time )
{
    for( auto index = 0U; index < vehicle.lidars.size(); index++ )
    {
        vehicle.lidars[index].process( f_dT, f_time );
    }
}

/*------------------*/
/* private methods */
/*------------------*/
void CWorld::calc( CFloat f_dT, CFloat f_time )
{
    //CWorld.process(dT) called by processVehicle
    //don't call this elsewhere
}

