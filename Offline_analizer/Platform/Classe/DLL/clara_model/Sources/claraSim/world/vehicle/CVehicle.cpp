/*******************************************************************************
@author Robert Erhart, ett2si (22.12.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
*******************************************************************************/

#include "CVehicle.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CVehicle::CVehicle( CInt numberOfRadars, CInt numberOfVideos, CInt numberOfLidars ) : CModule<NumberOfStates>(),
    radars( numberOfRadars ),
    videos( numberOfVideos ),
    lidars( numberOfLidars ),
    m_roadNetwork_p( nullptr ),
    m_positionInfo_s {0.0, 0.0, 0.0, 0.0, 0.0, /*{0., 0., 0.},*/ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0},
    m_positionInfo_as( 0 ),
    m_gammaRelativeCourse( 0 )
{
    addMessageOutput( o_numberOfRadars, numberOfRadars, CVehicleDoc::o_numberOfRadars );
    addMessageOutput( o_numberOfVideos, numberOfVideos, CVehicleDoc::o_numberOfVideos );
    addMessageOutput( o_numberOfLidars, numberOfLidars, CVehicleDoc::o_numberOfLidars );
    /* Initialization messages */
    addMessageParameter( p_lateralOffset, 0.0, CVehicleDoc::p_lateralOffset );
    addMessageParameter( p_targetLateralOffset, 0.0, CVehicleDoc::p_targetLateralOffset );
    addMessageParameter( p_lateralVelocity, 0.0, CVehicleDoc::p_lateralVelocity );
    addMessageParameter( p_road, 0LL, CVehicleDoc::p_road );
    addMessageParameter( p_lane, 0LL, CVehicleDoc::p_lane );

    addMessageOutput( o_x, 0.0 ); // (use o_xyzWorld; only needed for report visualization)
    addMessageOutput( o_y, 0.0 ); // (use o_xyzWorld; only needed for report visualization)
    addMessageOutput( o_z, 0.0 ); // (use o_xyzWorld; only needed for report visualization)
    addMessageOutput( o_xyzWorld, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CVehicleDoc::o_xyzWorld );
    addMessageOutput( o_latitude, 0.0 );
    addMessageOutput( o_longitude, 0.0 );
    addMessageOutput( o_s, 0.0, CVehicleDoc::o_s );

    // not changeabel by scene => no setMessage description
    addMessageOutput( o_angleRollPitchYawSurface, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );

    addMessageOutput( o_angleRollPitchYawChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CVehicleDoc::o_angleRollPitchYawChassis );
    addMessageOutput( o_gammaRelativeCourse, 0.0, CVehicleDoc::o_gammaRelativeCourse );
    addMessageOutput( o_beta, 0.0, CVehicleDoc::o_beta );
    addMessageOutput( o_velocity, 0.0, CVehicleDoc::o_velocity );
    addMessageOutput( o_vChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CVehicleDoc::o_vChassis );
    addMessageOutput( o_vWorld, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CVehicleDoc::o_vWorld );
    addMessageOutput( o_yawRate, 0.0, CVehicleDoc::o_yawRate );
    addMessageOutput( o_road, p_road, CVehicleDoc::o_road );
    addMessageOutput( o_lane, p_lane, CVehicleDoc::o_lane );
    addMessageOutput( o_lateralOffset, ::std::numeric_limits<CFloat>::max(), CVehicleDoc::o_lateralOffset );
    addMessageOutput( o_sCourse, 0.0, CVehicleDoc::o_sCourse );
    addMessageOutput( o_searchIndexLane, 0LL, CVehicleDoc::o_searchIndexLane );
    addMessageOutput( o_distanceToCourse, 0.0, CVehicleDoc::o_distanceToCourse );

    addMessageInput( i_staticSimulation, false );
    addMessageInput( i_FxyzArticulation, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );

    // input via internal modules
    addMessageInput( i_velocity, 0.0 );
    addMessageInput( i_vChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_beta, 0.0 );
    addMessageInput( i_yawRate, 0.0 );
    addMessageInput( i_angleRollPitchYawSuspension, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_h, 0.0 );
}

CVehicle::~CVehicle()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CVehicle::init( CRoadNetwork& f_roadNetwork_r,
                     CObstacles& f_obstacles_r,
                     IMessage<CFloatVectorXYZ>& f_FxyzArticulation,
                     IMessage<CBool>& f_staticSimulation )
{
    /* set course for vehicle CLARA */
    m_roadNetwork_p = &f_roadNetwork_r;

    /* link input messages */
    i_FxyzArticulation.link( f_FxyzArticulation );
    i_staticSimulation.link( f_staticSimulation );

    // input via internal modules
    i_velocity.link( chassis.o_velocity );
    i_vChassis.link( chassis.o_vChassis );
    i_beta.link( chassis.o_beta );
    i_yawRate.link( chassis.o_yawRate );
    i_angleRollPitchYawSuspension.link( chassis.dynamic.o_angleRollPitchYawSuspension );
    i_h.link( chassis.p_h );

    /* Initialization messages */
    initializationMessages();

    /* Re-Initialization depended messages */
    SCoursePositionInfo l_positionInfo = m_roadNetwork_p->roads[p_road].lanes[p_lane].getCoursePositionInfo( o_s, p_lateralOffset );
    o_xyzWorld.init( CFloatVectorXYZ( l_positionInfo.x, l_positionInfo.y, i_h + l_positionInfo.z ) );
    o_x.init( o_xyzWorld.X() );
    o_y.init( o_xyzWorld.Y() );
    o_z.init( o_xyzWorld.Z() );

    /* slope / roll angle */
    m_gammaRelativeCourse = 0;
    o_gammaRelativeCourse = m_gammaRelativeCourse;
    CFloat l_rollAngle     = - m_positionInfo_s.crossfallAngleLocal * ::sim::cos( m_gammaRelativeCourse )
                             - m_positionInfo_s.slopeAngleLocal * ::sim::sin( m_gammaRelativeCourse );
    CFloat l_pitchAngle    = + m_positionInfo_s.crossfallAngleLocal * ::sim::sin( m_gammaRelativeCourse )
                             - m_positionInfo_s.slopeAngleLocal * ::sim::cos( m_gammaRelativeCourse );


    o_angleRollPitchYawSurface.init( CFloatVectorXYZ( l_rollAngle,
                                                      l_pitchAngle,
                                                      l_positionInfo.gammaAngle ) );

    o_angleRollPitchYawChassis.init( o_angleRollPitchYawSurface );

    // state init
    state[X] = o_xyzWorld.X();
    state[Y] = o_xyzWorld.Y();
    state[Z] = o_xyzWorld.Z();
    state[GAMMA] = o_angleRollPitchYawChassis.Z();
    state[S] = o_s;

    /* init variables */
    m_positionInfo_s.s = 0.0;
    m_positionInfo_s.lateralOffset = 0.0;
    m_positionInfo_s.x = 0.0;
    m_positionInfo_s.y = 0.0;
    m_positionInfo_s.z = 0.0;
    m_positionInfo_s.dx = 0.0;
    m_positionInfo_s.dy = 0.0;
    m_positionInfo_s.dz = 0.0;
    m_positionInfo_s.gammaAngle = 0.0;
    m_positionInfo_s.crossfallAngleLocal = 0.0;
    m_positionInfo_s.slopeAngleLocal = 0.0;
    m_positionInfo_s.trackwidth = 0.0;
    m_positionInfo_s.indexLast = 1;
    m_positionInfo_as = ::std::vector<::std::vector<SCoursePositionInfo> > ( m_roadNetwork_p->o_NumberOfRoads.get(), ::std::vector<SCoursePositionInfo>( m_roadNetwork_p->o_NumberOfLanes.get(), SCoursePositionInfo {0.0, 0.0, 0.0, 0.0, 0.0, /*{0.0, 0.0, 0.0},*/ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0} ) );

    /* defines communication between objects */
    dashboard.init( driver.o_accelerator,
                    driver.o_brakepedal,
                    driver.o_angleSteeringWheel,
                    steeringSystem.o_angleSteeringWheel,
                    driveTrain.motor.o_nEngine,
                    chassis.o_vChassis );
    // o_velocity is the velocity vector's absolute value and only gives complete information with o_beta. In the dashboard, we want the longitudinal velocity.

    //input values of dashboard must be initialized before other CModules

    driver.init( chassis.o_velocity,
                 chassis.o_vChassis,
                 chassis.p_m,
                 chassis.wheelLeftRear.p_rWheel,
                 driveTrain.motor.o_Mmax,
                 o_xyzWorld,
                 o_angleRollPitchYawChassis,
                 o_sCourse,
                 p_road,
                 p_lane,
                 p_lateralOffset,
                 p_targetLateralOffset,
                 p_lateralVelocity,
                 *m_roadNetwork_p,
                 i_staticSimulation,
                 dashboard.o_angleSteeringWheel,
                 dashboard.p_angleSteeringWheelAuto,
                 dashboard.p_acceleratorAuto,
                 dashboard.p_brakepedalAuto );

    steeringSystem.init( dashboard.o_angleSteeringWheelTarget,
                         chassis.o_velocity,
                         chassis.wheelLeftFront.o_FLateral,
                         chassis.wheelLeftFront.o_RvFLateral,
                         chassis.wheelRightFront.o_FLateral,
                         chassis.wheelRightFront.o_RvFLateral );

    driveTrain.init( dashboard.o_accelerator,
                     chassis.o_nWheelRightFront,
                     chassis.o_nWheelLeftFront,
                     chassis.o_nWheelRightRear,
                     chassis.o_nWheelLeftRear,
                     dashboard.p_clutch,
                     dashboard.p_gearStick,
                     dashboard.o_brakepedal,
                     dashboard.p_parkingBrake,
                     chassis.staticCar.o_FChassis,
                     chassis.staticCar.o_FvRChassis,
                     chassis.p_m,
                     chassis.wheelLeftFront.p_rWheel,
                     chassis.wheelRightFront.p_rWheel,
                     chassis.wheelLeftRear.p_rWheel,
                     chassis.wheelRightRear.p_rWheel,
                     o_angleRollPitchYawSurface );

    chassis.init( steeringSystem.o_angleWheelFront,
                  driveTrain.o_MWheelLeftFront,
                  driveTrain.o_RnMWheelLeftFront,
                  driveTrain.o_MWheelRightFront,
                  driveTrain.o_RnMWheelRightFront,
                  driveTrain.o_MWheelLeftRear,
                  driveTrain.o_RnMWheelLeftRear,
                  driveTrain.o_MWheelRightRear,
                  driveTrain.o_RnMWheelRightRear,
                  o_angleRollPitchYawSurface,
                  i_FxyzArticulation,
                  i_staticSimulation );

    for( unsigned int index = 0; index < radars.size(); index++ )
    {
        radars[index].init( o_xyzWorld,
                            o_vWorld,
                            chassis.dynamic.o_aChassis,
                            o_angleRollPitchYawChassis,
                            chassis.o_yawRate,
                            f_obstacles_r,
                            i_staticSimulation );
    }

    for( unsigned int index = 0; index < videos.size(); index++ )
    {
        videos[index].init( o_xyzWorld,
                            o_vWorld,
                            chassis.dynamic.o_aChassis,
                            o_angleRollPitchYawChassis,
                            chassis.o_yawRate,
                            f_obstacles_r,
                            i_staticSimulation,
                            o_road,
                            o_lane,
                            o_searchIndexLane,
                            f_roadNetwork_r );
    }

    for( unsigned int index = 0; index < lidars.size(); index++ )
    {
        lidars[index].init( o_xyzWorld,
                            o_vWorld,
                            chassis.dynamic.o_aChassis,
                            o_angleRollPitchYawChassis,
                            chassis.o_yawRate,
                            f_obstacles_r,
                            i_staticSimulation );
    }
}

/*------------------*/
/* private methods */
/*------------------*/
void CVehicle::calcPre( CFloat f_dT, CFloat f_time )
{
    /* calculate vehicle components */
    dashboard.process( f_dT, f_time );
    driver.process( f_dT, f_time );
    steeringSystem.process( f_dT, f_time );
    driveTrain.process( f_dT, f_time );
    chassis.process( f_dT, f_time );

    o_velocity = i_velocity;
    o_vChassis = i_vChassis;
    o_yawRate  = i_yawRate;
    o_beta     = i_beta;

    /* Calculate vehicle position in environment:                               */
    /*   - Fill array of positionInfos relative to every [roadIndex][laneIndex] */
    /*   - Check if we are ON a lane, then update o_road and o_lane accordingly */

    // TODO:    Find a better way for choosing relevant road!
    //          Now, only distance is used, angle no longer considered

    m_gammaRelativeCourse = ::std::numeric_limits<CFloat>::max();

    //CFloat l_lateralOffsetK1 =  o_lateralOffset;
    CInt l_roadK1 = o_road;
    CInt l_laneK1 = o_lane;

    o_lateralOffset = ::std::numeric_limits<CFloat>::max();
    o_road = -1;
    o_lane = -1;
    CInt t_laneID;
    for( CInt t_indexRoad = 0; t_indexRoad < m_roadNetwork_p->o_NumberOfRoads.get(); t_indexRoad++ )
    {
        for( CInt t_indexLane = 0; t_indexLane < m_roadNetwork_p->roads[t_indexRoad].o_numberOfLanes.get(); t_indexLane++ )
        {
            if( m_roadNetwork_p->roads[t_indexRoad].isValidLaneArrayIndex( t_indexLane ) )
            {
                t_laneID = m_roadNetwork_p->roads[t_indexRoad].getLaneID( t_indexLane );
                m_positionInfo_as[t_indexRoad][t_indexLane] = m_roadNetwork_p->roads[t_indexRoad].lanes[t_laneID].findCoursePositionInfo( state[X], state[Y], m_positionInfo_as[t_indexRoad][t_indexLane].indexLast );
                // if we are on the current lane, i.e. lateralOffset < trackwidth/2:
                //      update o_road and o_lane, if lateral offset is smaller than found before
                if( ( m_positionInfo_as[t_indexRoad][t_indexLane].trackwidth / 2.0 ) >= ::sim::abs( m_positionInfo_as[t_indexRoad][t_indexLane].lateralOffset ) )
                {
                    if( ::sim::abs( m_positionInfo_as[t_indexRoad][t_indexLane].lateralOffset ) < ::sim::abs( o_lateralOffset ) )
                    {
                        o_road = t_indexRoad;
                        o_lane = t_laneID;
                        o_lateralOffset = m_positionInfo_as[t_indexRoad][t_indexLane].lateralOffset;
                    }
                }
            }
        }
    }

    if(o_road >= 0 and l_roadK1 >= 0)
    {
        if( m_positionInfo_as[l_roadK1][m_roadNetwork_p->roads[l_roadK1].getLaneArrayIndex(l_laneK1)].trackwidth / 3.0 >= ::sim::abs( m_positionInfo_as[l_roadK1][m_roadNetwork_p->roads[l_roadK1].getLaneArrayIndex(l_laneK1)].lateralOffset ) )
        {
            o_road = l_roadK1;
            o_lane = l_laneK1;
            o_lateralOffset = m_positionInfo_as[l_roadK1][m_roadNetwork_p->roads[l_roadK1].getLaneArrayIndex(l_laneK1)].lateralOffset;
        }
    }

    if( o_road == -1 )  // off road
    {
        m_positionInfo_s = m_positionInfo_as[p_road][m_roadNetwork_p->roads[p_road].getLaneArrayIndex( p_lane )];
    }
    else
    {
        m_positionInfo_s = m_positionInfo_as[o_road][m_roadNetwork_p->roads[o_road].getLaneArrayIndex( o_lane )];
    }

    o_searchIndexLane = m_positionInfo_s.indexLast;
    o_distanceToCourse = m_positionInfo_s.lateralOffset;

    /* slope / roll angle */
    m_gammaRelativeCourse = state[GAMMA] - m_positionInfo_s.gammaAngle;
    o_gammaRelativeCourse = m_gammaRelativeCourse;
    CFloat l_rollAngle     = - m_positionInfo_s.crossfallAngleLocal * cos( m_gammaRelativeCourse )
                             - m_positionInfo_s.slopeAngleLocal * sin( m_gammaRelativeCourse );
    CFloat l_pitchAngle    = + m_positionInfo_s.crossfallAngleLocal * sin( m_gammaRelativeCourse )
                             - m_positionInfo_s.slopeAngleLocal * cos( m_gammaRelativeCourse );
    o_angleRollPitchYawSurface.XYZ( l_rollAngle, l_pitchAngle, state[GAMMA] ); // relative to course
}

/* ddt */
CFloatVector& CVehicle::ddt( CFloatVector& state )
{
    /* Start    "equation of state */
    if( i_staticSimulation == false )
    {
        ddtState[X]     = o_vChassis.X() * ::sim::cos( state[GAMMA] ) - o_vChassis.Y() * ::sim::sin( state[GAMMA] ); //only valid for small pitch and slope angle
        ddtState[Y]     = o_vChassis.X() * ::sim::sin( state[GAMMA] ) + o_vChassis.Y() * ::sim::cos( state[GAMMA] ); //only valid for small pitch and slope angle
        ddtState[Z]     = 0; // TODO: add Z dynamics
        ddtState[GAMMA] = o_yawRate; //only valid for small pitch and slope angle
        ddtState[S]     = o_velocity;
    }
    else
    {
        ddtState[X]     = 0;
        ddtState[Y]     = 0;
        ddtState[Z]     = 0;
        ddtState[GAMMA] = 0;
        ddtState[S]     = 0;
    }
    /* End      "equation of state */
    return ddtState;
}

void CVehicle::calcPost( CFloat f_dT, CFloat f_time )
{
    // Helper function for Euclidean distance calculation. Returns distance squared (!) for improved speed.
    auto calcDistance = []( SCoursePositionInfo pos, SCoursePositionInfo ref )
    {
        return ::sim::pow( pos.x - ref.x, 2 ) + ::sim::pow( pos.y - ref.y, 2 ) + ::sim::pow( pos.z - ref.z, 2 );
    };

    bool l_laneConnected = false;
    bool l_jumpDetected  = false;

    // Worker variables l_road, l_lane using output messages if valid, else parameter messages
    CInt l_road = ( o_road >= 0 ) ? o_road : p_road;
    CInt l_lane = ( o_road >= 0 ) ? o_lane : p_lane;
    CFloat l_lateralOffset = ( o_road >= 0 ) ? o_lateralOffset : p_lateralOffset;

    // TODO: check for negative velocity (go to preceding road)
    CFloatVector l_connectedLaneInfo = m_roadNetwork_p->roads[l_road].lanes[l_lane].p_connections.get();
    if( l_connectedLaneInfo.size() > 2 ) // at least one entry (tuple of three)
    {
        if( l_connectedLaneInfo[0] >= 0 )
        {
            l_laneConnected = ( o_sCourse > l_connectedLaneInfo[2] - o_velocity * f_dT );
        }
    }

    // Connection to a new lane.
    // -> Set new road and lane parameters.
    //    Update X,Y,Z and orientation (GAMMA) here only if a jump is required
    if( l_laneConnected )
    {
        p_road = static_cast<CInt>(l_connectedLaneInfo[0]);
        p_road.set(static_cast<CInt>(l_connectedLaneInfo[0]) );
        o_road = static_cast<CInt>(l_connectedLaneInfo[0]);

        p_lane = static_cast<CInt>(l_connectedLaneInfo[1]);
        p_lane.set(static_cast<CInt>(l_connectedLaneInfo[1]) );
        o_lane = static_cast<CInt>(l_connectedLaneInfo[1]);
        o_sCourse = 0; // will this lead to jumps?


        SCoursePositionInfo m_newLanePositionInfo_s = m_roadNetwork_p->roads[p_road].lanes[p_lane].getCoursePositionInfo( 0, l_lateralOffset );
        if( calcDistance( m_newLanePositionInfo_s, m_positionInfo_s ) > 1 ) // distance between current position and new lane bigger than 1 m ==> jump is required
        {
            l_jumpDetected = true;
        }
    }


    // No new connection, but road is coming to an end:
    // -> jump back to origin of *current* lane
    // CAUTION: use 'p_road' on both sides of the inequality for consinstency, don't mix with o_road!
    else if( m_positionInfo_as[p_road][p_lane].s > m_roadNetwork_p->roads[p_road].o_lengthOfCourse.get() - o_velocity * f_dT )
    {
        l_jumpDetected = true;
    }
    // If a jump has been detected:
    // Reset m_positionInfo_s to origin of new road/lane.
    if( l_jumpDetected )
    {
        SCoursePositionInfo m_positionInfo_s = m_roadNetwork_p->roads[p_road].lanes[p_lane].getCoursePositionInfo( 0, l_lateralOffset );
        state[X] = m_positionInfo_s.x;
        state[Y] = m_positionInfo_s.y;
        state[Z] = m_positionInfo_s.z;
        state[GAMMA] = m_positionInfo_s.gammaAngle;

        //set back search index for local minimum
        for( size_t t_indexRoad = 0; t_indexRoad < m_roadNetwork_p->roads.size(); t_indexRoad++ )
        {
            for( size_t t_indexLane = 0; t_indexLane < m_roadNetwork_p->roads[t_indexRoad].lanes.size(); t_indexLane++ )
            {
                m_positionInfo_as[t_indexRoad][t_indexLane].indexLast = 1;
            }
        }
    }

    o_xyzWorld.XYZ( state[X], state[Y], ( i_h + m_positionInfo_s.z - m_positionInfo_s.lateralOffset * atan( m_positionInfo_s.crossfallAngleLocal ) ) );
    o_x = o_xyzWorld.X();
    o_y = o_xyzWorld.Y();
    o_z = o_xyzWorld.Z();
    o_vWorld.XYZ( ddtState[X], ddtState[Y], ddtState[Z] );
    o_sCourse = m_positionInfo_as[p_road][m_roadNetwork_p->roads[p_road].getLaneArrayIndex( p_lane )].s; //always correspond to the target lane and road


    o_latitude = m_roadNetwork_p->getLatitude( o_x, o_y );
    o_longitude = m_roadNetwork_p->getLongitude( o_x, o_y );

    // @ToDo: addition of angles is not correct. This is only an approximation for small angles.
    o_angleRollPitchYawChassis.X( o_angleRollPitchYawSurface.X() + i_angleRollPitchYawSuspension.X() );
    o_angleRollPitchYawChassis.Y( o_angleRollPitchYawSurface.Y() + i_angleRollPitchYawSuspension.Y() );
    o_angleRollPitchYawChassis.Z( state[GAMMA] );
    o_s = state[S];

}

