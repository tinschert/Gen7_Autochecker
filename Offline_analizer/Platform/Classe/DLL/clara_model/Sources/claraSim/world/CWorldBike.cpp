/*******************************************************************************
author Robert Erhart, ett2si (22.12.2004 - 00:00:00)
author Andreas Brunner, bnr2lr (04.07.2019)
author (c) Copyright Robert Bosch GmbH 2019-2024. All rights reserved.
*******************************************************************************/

#include "CWorldBike.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CWorldBike::CWorldBike( CInt NumberOfDynamicObstacles, CInt NumberOfStaticObstacles,
                        CInt NumberOfRoads, CInt NumberOfLanes,
                        CInt NumberOfRadars, CInt NumberOfVideos, CInt NumberOfLidars ):
    vehicle( NumberOfRadars, NumberOfVideos, NumberOfLidars ),
    roadNetwork( NumberOfRoads, NumberOfLanes ),
    Obstacles( NumberOfDynamicObstacles, NumberOfStaticObstacles )
{
    addMessageParameter( p_staticSimulation, false, CWorldBikeDoc::p_staticSimulation );
    addMessageOutput( o_initCounter, 0, CWorldBikeDoc::o_initCounter );
    addMessageOutput( o_zeroVector, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );

    init();
}

CWorldBike::~CWorldBike()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CWorldBike::init()
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

void CWorldBike::processVehicle( CFloat f_dT, CFloat f_time )
{
    process( f_dT, f_time ); //calc his own process
    vehicle.process( f_dT, f_time );
}

void CWorldBike::processEnvironment( CFloat f_dT, CFloat f_time )
{
    Obstacles.process( f_dT, f_time );
}

void CWorldBike::processRadarSensors( CFloat f_dT, CFloat f_time )
{
    for( auto index = 0U; index < vehicle.radars.size(); index++ )
    {
        vehicle.radars[index].process( f_dT, f_time );
    }
}

void CWorldBike::processVideoSensors( CFloat f_dT, CFloat f_time )
{
    for( auto index = 0U; index < vehicle.videos.size(); index++ )
    {
        vehicle.videos[index].process( f_dT, f_time );
    }
}

void CWorldBike::processLidarSensors( CFloat f_dT, CFloat f_time )
{
    for( auto index = 0U; index < vehicle.lidars.size(); index++ )
    {
        vehicle.lidars[index].process( f_dT, f_time );
    }
}

/*------------------*/
/* private methods */
/*------------------*/
void CWorldBike::calc( CFloat f_dT, CFloat f_time )
{
    //CWorldBike.process(dT) called by processVehicle
    //don't call this elsewhere
}
