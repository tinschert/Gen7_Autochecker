/*******************************************************************************
author Robert Erhart, ett2si (22.12.2004 - 00:00:00)
author Andreas Brunner, bnr2lr (04.07.2019)
author (c) Copyright Robert Bosch GmbH 2019-2024.  All rights reserved.
*******************************************************************************/

#include "CWorldTruck.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CWorldTruck::CWorldTruck( CInt NumberOfDynamicObstacles, CInt NumberOfStaticObstacles,
                          CInt NumberOfRoads, CInt NumberOfLanes,
                          CInt NumberOfRadars, CInt NumberOfVideos, CInt NumberOfLidars ):
    vehicle( NumberOfRadars, NumberOfVideos, NumberOfLidars ),
    trailer( 0, 0, 0 ),
    articulation(),
    roadNetwork( NumberOfRoads, NumberOfLanes ),
    Obstacles( NumberOfDynamicObstacles, NumberOfStaticObstacles )
{
    addMessageParameter( p_detach, false );
    addMessageOutput( o_zeroVector, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );

    init();
}

CWorldTruck::~CWorldTruck()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CWorldTruck::init()
{
    /* Connect input with internal variables */
    CInt l_initCounter = o_initCounter.get(); //preserve old value

    /* Initialization messages */
    initializationMessages();

    /* Initialization internal variables */

    /* init objects AND defines communication between objects */
    roadNetwork.init();

    Obstacles.init( roadNetwork, p_staticSimulation );

    vehicle.init( roadNetwork, Obstacles, articulation.o_FxyzFirstVehicle, p_staticSimulation );

    /* Set init values (position, velocity) for trailer consistently with truck values */
    trailer.o_s.setInit( vehicle.o_s.get() - trailer.chassis.p_xyzArticulation.X() - std::abs( vehicle.chassis.p_xyzArticulation.X() ) );
    trailer.chassis.dynamic.o_vChassis.init( vehicle.chassis.o_vChassis.get() );

    trailer.init( roadNetwork, Obstacles, articulation.o_FxyzSecondVehicle, p_staticSimulation );



    articulation.init( vehicle.o_angleRollPitchYawChassis,
                       trailer.o_angleRollPitchYawChassis,
                       vehicle.o_xyzWorld,
                       trailer.o_xyzWorld,
                       vehicle.chassis.p_xyzArticulation,
                       trailer.chassis.p_xyzArticulation,
                       p_detach );

    o_initCounter = l_initCounter + 1;
}

void CWorldTruck::processVehicle( CFloat f_dT, CFloat f_time )
{
    process( f_dT, f_time ); //calc his own process
    articulation.process( f_dT, f_time );
    vehicle.process( f_dT, f_time );
    trailer.process( f_dT, f_time );
}
void CWorldTruck::processEnvironment( CFloat f_dT, CFloat f_time )
{
    Obstacles.process( f_dT, f_time );
}

void CWorldTruck::processRadarSensors( CFloat f_dT, CFloat f_time )
{
    for( auto index = 0U; index < vehicle.radars.size(); index++ )
    {
        vehicle.radars[index].process( f_dT, f_time );
    }
}

void CWorldTruck::processVideoSensors( CFloat f_dT, CFloat f_time )
{
    for( auto index = 0U; index < vehicle.videos.size(); index++ )
    {
        vehicle.videos[index].process( f_dT, f_time );
    }
}

void CWorldTruck::processLidarSensors( CFloat f_dT, CFloat f_time )
{
    for( auto index = 0U; index < vehicle.lidars.size(); index++ )
    {
        vehicle.lidars[index].process( f_dT, f_time );
    }
}

/*------------------*/
/* private methods */
/*------------------*/
void CWorldTruck::calc( CFloat f_dT, CFloat f_time )
{
    //CWorldTruck.process(dT) called by processVehicle
    //don't call this elsewhere
}
