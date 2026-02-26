/*******************************************************************************
 $Source: CObstacleDynamic.cpp $
 $Date: 2017/06/28 11:24:42CEST $
 $Revision: 8.10 $

 @author Robert Erhart, ett2si (05.03.2007)
 @copyright (c) Robert Bosch GmbH 2007-2024. All rights reserved.
 *******************************************************************************/

#include "CObstacleDynamic.h"
#include "CObstacles.h"  //get enum type

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CObstacleDynamic::CObstacleDynamic() :
    CModule<NumberOfStates, NumberOfIntegrationSteps>(),
    m_roadNetwork_p( nullptr ),
    m_xLocalContour( 0.0, 4 ),
    m_yLocalContour( 0.0, 4 ),
    m_zLocalContour( 0.0, 4 ),
    m_targetLateralOffset( 0.0 ),
    m_initialLateralOffset( 0.0 ),
    m_lane_K1( 0 )
{
    /* Initialization messages */
    addMessageParameter( p_targetVelocity, 0.0, CObstacleDynamicDoc::p_targetVelocity );
    addMessageParameter( p_xCourseVelocity, INFINITY, CObstacleDynamicDoc::p_xCourseVelocity );
    addMessageParameter( p_targetLateralOffset, 0.0, CObstacleDynamicDoc::p_targetLateralOffset );
    addMessageParameter( p_lateralVelocity, 1.0, CObstacleDynamicDoc::p_lateralVelocity );
    addMessageParameter( p_lateralMovementType, 0, CObstacleDynamicDoc::p_lateralMovementType ); // standard behaviour: linear movement
    addMessageParameter( p_alignWithVelocity, false, CObstacleDynamicDoc::p_alignWithVelocity );
    addMessageParameter( p_acceleration, 0.0, CObstacleDynamicDoc::p_acceleration );
    p_type.setHistComSampleRateInit( 50 ); // reduce vector size for history vector
    addMessageParameter( p_type, EObstacleTyp::INVISIBLE, CObstacleDynamicDoc::p_type );
    addMessageParameter( p_depth, 5, CObstacleDynamicDoc::p_depth );
    addMessageParameter( p_height, 1.5, CObstacleDynamicDoc::p_height );
    addMessageParameter( p_width, 2, CObstacleDynamicDoc::p_width );
    addMessageParameter( p_offsetPos, 0, CObstacleDynamicDoc::p_offsetPos );
    addMessageParameter( p_coursePosition, INFINITY, CObstacleDynamicDoc::p_coursePosition );
    addMessageParameter( p_lateralOffset, INFINITY, CObstacleDynamicDoc::p_lateralOffset );
    addMessageParameter( p_road, 0LL, CObstacleDynamicDoc::p_road );
    addMessageParameter( p_lane, 0LL, CObstacleDynamicDoc::p_lane );
    addMessageParameter( p_visibility, 1.0, CObstacleDynamicDoc::p_visibility );

    addMessageInput( i_staticSimulation, false );

    addMessageOutput( o_coursePosition, 0.0, CObstacleDynamicDoc::o_coursePosition );
    addMessageOutput( o_vxCourse, 0.0, CObstacleDynamicDoc::o_vxCourse );
    addMessageOutput( o_vyCourse, 0.0, CObstacleDynamicDoc::o_vyCourse );
    addMessageOutput( o_lateralOffset, 0.0, CObstacleDynamicDoc::o_lateralOffset );
    addMessageOutput( o_acceleration, 0.0, CObstacleDynamicDoc::o_acceleration );

    o_x.setHistComSampleRateInit( 50 ); // reduce vector size for history vector
    addMessageOutput( o_x, 0.0 );       // (use o_xyzWorld; only needed for report visualisation)
    o_y.setHistComSampleRateInit( 50 ); // reduce vector size for history vector
    addMessageOutput( o_y, 0.0 );       // (use o_xyzWorld; only needed for report visualisation)
    o_z.setHistComSampleRateInit( 50 ); // reduce vector size for history vector
    addMessageOutput( o_z, 0.0 );       // (use o_xyzWorld; only needed for report visualisation)

    // o_xyz.setHistComSampleRateInit( 50 ); // reduce vector size for history vector
    addMessageOutput( o_xyzWorld, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CObstacleDynamicDoc::o_xyzWorld );
    m_xLocalContour = { -p_depth / 2, -p_depth / 2, +p_depth / 2, +p_depth / 2 };
    m_yLocalContour = { +p_width / 2, -p_width / 2, -p_width / 2, +p_width / 2 };
    m_zLocalContour = { +p_height / 2, +p_height / 2, +p_height / 2, +p_height / 2 };
    addMessageOutput( o_xWorldContour, m_xLocalContour, CObstacleDynamicDoc::o_xWorldContour );                             //world coordinates
    addMessageOutput( o_yWorldContour, m_yLocalContour, CObstacleDynamicDoc::o_yWorldContour );                             //world coordinates
    addMessageOutput( o_zWorldContour, m_zLocalContour, CObstacleDynamicDoc::o_zWorldContour );                             //world coordinates
    addMessageOutput( o_vWorld, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CObstacleDynamicDoc::o_vWorld );
    addMessageOutput( o_yawAngle, 0.0, CObstacleDynamicDoc::o_yawAngle );
    addMessageOutput( o_rollAngle, 0.0, CObstacleDynamicDoc::o_rollAngle );
    addMessageOutput( o_pitchAngle, 0.0, CObstacleDynamicDoc::o_pitchAngle );
    addMessageOutput( o_trackWidthBack, 0.0, CObstacleDynamicDoc::o_trackWidthBack );
    addMessageOutput( o_trackWidthFront, 0.0, CObstacleDynamicDoc::o_trackWidthFront );
}

CObstacleDynamic::~CObstacleDynamic()
{
}

/*------------------*/
/* public methods  */
/*------------------*/
void CObstacleDynamic::init( CRoadNetwork& f_roadNetwork_r,
                             IMessage<CBool>& f_staticSimulation )
{
    /* define course for obstacle */
    m_roadNetwork_p = &f_roadNetwork_r;

    /* link input messages */
    i_staticSimulation.link( f_staticSimulation );

    /* Initialization messages */
    initializationMessages();

    m_xLocalContour = { -p_depth / 2, -p_depth / 2, +p_depth / 2, +p_depth / 2 };
    m_yLocalContour = { +p_width / 2, -p_width / 2, -p_width / 2, +p_width / 2 };
    m_zLocalContour = { +p_height / 2, +p_height / 2, +p_height / 2, +p_height / 2 };

    SCoursePositionInfo l_positionInfo = m_roadNetwork_p->roads[p_road].lanes[p_lane].getCoursePositionInfo( o_coursePosition, o_lateralOffset );
    o_x.init( l_positionInfo.x );
    o_y.init( l_positionInfo.y );
    o_z.init( l_positionInfo.z );
    o_xyzWorld.init( {l_positionInfo.x, l_positionInfo.y, l_positionInfo.z} );
    o_yawAngle.init( l_positionInfo.gammaAngle );
    o_rollAngle.init( -l_positionInfo.crossfallAngleLocal );
    o_pitchAngle.init( -l_positionInfo.slopeAngleLocal );

    //contour Points of obstacle
    for( auto index = 0 ; index < 4; index++ )
    {
        ::sim::coordinateRotation( o_rollAngle, o_pitchAngle, o_yawAngle,
                            m_xLocalContour[index], m_yLocalContour[index], m_zLocalContour[index],
                            o_xWorldContour[index], o_yWorldContour[index], o_zWorldContour[index] );
        o_xWorldContour[index] += o_xyzWorld[0];
        o_yWorldContour[index] += o_xyzWorld[1];
        o_zWorldContour[index] += o_xyzWorld[2];
    }

    /* Re-Initialization depended messages */
    o_trackWidthBack.init( m_roadNetwork_p->roads[p_road].lanes[p_lane].getTrackWidth( o_coursePosition ) );
    o_trackWidthFront.init( m_roadNetwork_p->roads[p_road].lanes[p_lane].getTrackWidth( o_coursePosition + p_depth ) );

    /* init state variables */
    state[COURSE_POSITION] = o_coursePosition;
    state[COURSE_VELOCITY] = o_vxCourse;
    state[LATERAL_OFFSET] = o_lateralOffset;
    m_initialLateralOffset = state[LATERAL_OFFSET];
    m_lane_K1 = p_lane;
    m_road_K1 = p_road;

    ddtState = 0.0;
}

/*------------------*/
/* private methods */
/*------------------*/
void CObstacleDynamic::changeLane( CInt f_newLaneID )
{
    // If the new lane index == current lane index: do nothing, return directly
    if( f_newLaneID == m_lane_K1 ) return;

    //! Helper function for Euclidean distance calculation. Returns distance squared (!) for improved speed.
    auto calcDistance = []( SCoursePositionInfo pos, SCoursePositionInfo ref )
    {
        return ::sim::pow( pos.x - ref.x, 2 ) + ::sim::pow( pos.y - ref.y, 2 ) + ::sim::pow( pos.z - ref.z, 2 );
    };

    // Current obstacle position
    SCoursePositionInfo l_currentPosInfo = m_roadNetwork_p->roads[p_road].lanes[m_lane_K1].getCoursePositionInfo( state[COURSE_POSITION], state[LATERAL_OFFSET] );

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //
    // Find new lane position parameter ("s") by minimizing distance between original lane point and new lane point.
    //
    // For this, we use the Golden Ratio minimization algorithm, which is a simple, robust minimization method for unimodal functions.
    // Typically, it converges in < 50 us and ~ 20 iterations.
    //
    // Since the distance
    //      dist(s)
    // is not strictly unimodal, i.e. there might be several local minima (*).
    // The algorithm implemented here converges correctly under two assumptions:
    //      1) The new lane minimal distance "s" is within +-100 meters of the original lane "s_ref" (this is true for typical tracks in CLARA)
    //      2) Unimodality on the given interval (+-100 m), which translates to tracks that are not excessively curvy, spiralling, etc.
    //
    // The procedure is as follows:
    //      A) Define an interval for the new "s": [sA, sB]
    //      B) If the interval width is below a threshold, we declare convergence.
    //      C) Else, narrow the interval to [sA2, sB2] using the Golden Ratio formula
    //      D) Evaluate distance at sA2 and sB2, update sA, sB accordingly, and reiterate
    //
    //
    // (*) An example for local minima is a spiralling or winding track. When the track approaches the origin, distance to origin has a local minimum.
    //       origin -->  ____o______
    //                              \    <--
    //                               |   <-- curve
    //     <-- track dir. ___x______/    <--
    //
    //     o = reference position
    //     x = local distance minimum to "o"
    //     global minimum at position = o (zero distance)
    //
    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // A)
    // Define local variables for interval handling
    CFloat l_sA = ::sim::max( 0.L, state[COURSE_POSITION] - 100.0 ); // start at (s-100) meters; avoid sub-zero values
    CFloat l_sB = ::sim::min( state[COURSE_POSITION] + 100., m_roadNetwork_p->roads[p_road].lanes[f_newLaneID].CourseLine.getLengthOfLine() ); // end at (s+100) meters; avoid values beyond course length
    CFloat l_sA2, l_sB2;
    CFloat l_distB = 0.;
    CFloat l_distA2, l_distB2;
    const CFloat GoldenRatio = 0.618;

    SCoursePositionInfo l_posInfoB;
    SCoursePositionInfo l_posInfoA2, l_posInfoB2;

    for( int i = 0; i < 100; i++ )
    {
        // B)
        // Abort iteration if five centimeter precision are reached
        if( ::sim::abs( l_sA - l_sB ) < 0.05 )
        {
            l_posInfoB = m_roadNetwork_p->roads[p_road].lanes[f_newLaneID].getCoursePositionInfo( l_sB, 0.0 );
            l_distB = calcDistance( l_posInfoB, l_currentPosInfo );
            break;
        }

        // C)
        // Narrow down the interval.
        l_sA2 = l_sA + ( 1 - GoldenRatio ) * ( l_sB - l_sA );
        l_sB2 = l_sA + GoldenRatio * ( l_sB - l_sA );

        // D)
        // Retrieve positions at sA2, sB2, evaluate distances to current position...
        l_posInfoA2 = m_roadNetwork_p->roads[p_road].lanes[f_newLaneID].getCoursePositionInfo( l_sA2, 0.0 );
        l_posInfoB2 = m_roadNetwork_p->roads[p_road].lanes[f_newLaneID].getCoursePositionInfo( l_sB2, 0.0 );
        l_distA2 = calcDistance( l_posInfoA2, l_currentPosInfo );
        l_distB2 = calcDistance( l_posInfoB2, l_currentPosInfo );

        // ... and update interval edge that is associated with non-minimal value.
        if( l_distA2 < l_distB2 )
        {
            l_sB = l_sB2;
        }
        else
        {
            l_sA = l_sA2;
        }
    }

    // Use "sB" parameter to initiate lane change. "sB" is ahead of "sA" and therefore better suited for forward moving obstacles.

    // Set state variables to initiate lane change.
    state[COURSE_POSITION] = l_sB;
    // m_lane_K1 = p_lane;

    // REMARK: lateral velocity and lateral movement type need to be set separately (e.g. from test script)
    //      p_lateralVelocity.set(3.);
    //      p_lateralMovementType.set(0);
    // If no direct jump is required: sustain current position by setting lateral offset w.r.t new lane.
    // Set target offset = 0 to start lateral approach to new lane center
    if( p_lateralMovementType != 2 )
    {
        // Since l_distB holds distance SQUARED, calc sqrt first.
        l_distB = std::pow( l_distB, 0.5 );
        // Decide on correct sign of lateral offset numerically:
        //   + l_distB (if this creates an appropriate position with close distance < 0.3 meters)
        //   - l_distB (otherwise)
        CFloat l_distSign = ( calcDistance( m_roadNetwork_p->roads[p_road].lanes[f_newLaneID].getCoursePositionInfo( l_sB, l_distB ), l_currentPosInfo ) < 0.3 ) ? 1. : -1.;
        p_lateralOffset = l_distSign * l_distB;
        p_targetLateralOffset.set( 0.0 );
    }
}


void CObstacleDynamic::calcPre( CFloat f_dT, CFloat f_time )
{
    // Check for change in p_lane while p_road remains unchanged (pure lane change, NOT change to connecting road).
    // If change occured, initiate lane change procedure
    if( ( p_lane.get() != m_lane_K1 ) and ( p_road.get() == m_road_K1 ) )
    {
        changeLane( p_lane.get() );
    }
    m_lane_K1 = p_lane.get();
    m_road_K1 = p_road.get();
}


CFloatVector& CObstacleDynamic::ddt( CFloatVector& state )
{
    /**************************************************************************
     *                  Accelerate to target velocity
     *************************************************************************/
    if( p_xCourseVelocity == INFINITY )
        // Default case: "p_xCourseVelocity" has not been set or changed.
        //      Accelerate to "p_targetVelocity".
    {
        CFloat deltaVelocity = p_targetVelocity - state[COURSE_VELOCITY];
        CFloat dt = getDtIntegration();
        if( ::sim::abs( deltaVelocity ) >= ( dt * ::sim::abs( p_acceleration ) ) )
            /* Target velocity not reached in next step. Keep accelerating. */
        {
            ddtState[COURSE_VELOCITY] = ::sim::sign_of( deltaVelocity ) * ::sim::abs( p_acceleration );
        }
        else /*Dealing with numerical inaccuracies:
            Once the deviation from target is less than the step size, then consider the target to be reached*/
        {
            ddtState[COURSE_VELOCITY] = 0;
            state[COURSE_VELOCITY] = p_targetVelocity;
        }
    }
    else // "p_xCourseVelocity" has changed. Set this velocity and fall back to default case.
    {
        state[COURSE_VELOCITY] = p_xCourseVelocity;
        p_xCourseVelocity.set( INFINITY );
    }

    /* calc sCourse */
    if( p_coursePosition == INFINITY )
    {
        ddtState[COURSE_POSITION] = state[COURSE_VELOCITY];
    }
    else
    {
        state[COURSE_POSITION] = p_coursePosition;
        p_coursePosition.set( INFINITY );
    }

    /**************************************************************************
     *                  Longitudinal movement
     *************************************************************************/

    /* p_lateralOffset unchanged: keep approaching lateral position given by 'targetlateralOffset' */
    if( p_lateralOffset == INFINITY )
    {
        /* p_targetLateralOffset is unchanged: keep approaching lateral position given by 'targetLateralOffset' */
        if( p_targetLateralOffset == INFINITY )
        {
            CFloat deltaLateral = m_targetLateralOffset - state[LATERAL_OFFSET];
            CFloat dt = getDtIntegration();

            // check whether target is reached within next time step
            if( ::sim::abs( deltaLateral ) >=  ::sim::abs( p_lateralVelocity * dt ) )
            {
                /**************************
                * LINEAR lateral movement
                ***************************/
                if( p_lateralMovementType != 1 )
                {
                    /* move to target lateral value with lateral velocity */
                    ddtState[LATERAL_OFFSET] = ::sim::sign_of( deltaLateral ) * p_lateralVelocity;
                }

                /********************************
                 * SIGMOID-type lateral movement
                 ********************************/
                else
                {
                    CFloat normingDistance          = ::sim::abs( m_targetLateralOffset - m_initialLateralOffset );
                    if( normingDistance > 1e-3 ) // avoid division by zero
                    {
                        /* A Sigmoid trajectory is achieved by setting the instantaneous lateral velocity (v) as a function of relative lateral distance (x)
                        *       v = v_0 * (x - x^2)
                        *
                        * To avoid deadlock where v ~ 0 (x=0 and x=1), a minimum lateral velocity of 0.01 m/s is defined */
                        CFloat normalizedDeltaLateral = ::sim::abs( deltaLateral / normingDistance );
                        ddtState[LATERAL_OFFSET] = ::sim::sign_of( deltaLateral ) * ::sim::max( 0.01L, ::sim::abs( p_lateralVelocity * 4. * ( normalizedDeltaLateral - normalizedDeltaLateral * normalizedDeltaLateral ) ) );
                    }
                    else // less than 1 mm to move: consider targetOffset to be reached
                    {
                        m_initialLateralOffset = m_targetLateralOffset;
                    }
                }
            }
            // target reached within this timestep: set to target offset.
            else
            {
                ddtState[LATERAL_OFFSET] = 0;
                state[LATERAL_OFFSET] = m_targetLateralOffset;
                // m_initialLateralOffset = m_targetLateralOffset; // target reached: set initialOffset for a possible subsequent change in 'offset'
            }
        }

        /* p_targetLateralOffset was changed: update member variables */
        else
        {
            m_targetLateralOffset = p_targetLateralOffset;
            m_initialLateralOffset = state[LATERAL_OFFSET];
            p_targetLateralOffset.set( INFINITY );
        }
    }

    /* override lateral position: set "state[LATERAL_OFFSET]" directly */
    else
    {
        state[LATERAL_OFFSET] = p_lateralOffset;
        m_initialLateralOffset = p_lateralOffset;
        p_lateralOffset.set( INFINITY );
    }

    if( i_staticSimulation == true )
    {
        ddtState[COURSE_VELOCITY] = 0;
        ddtState[COURSE_POSITION] = 0;
        ddtState[LATERAL_OFFSET] = 0;
    }

    return ddtState;
}


void CObstacleDynamic::calcPost( CFloat f_dT, CFloat f_time )
{
    SCoursePositionInfo l_positionInfo;
    bool l_laneConnected = false;

    // TODO: check for negative velocity (go to preceding road)
    CFloatVector l_connectedLaneInfo = m_roadNetwork_p->roads[p_road].lanes[p_lane].p_connections.get();

    // As of now, the first defined connection is considered only.
    // If the connection's course position is to be exceeded within
    // the current step, update to new road & lane.
    if( l_connectedLaneInfo.size() > 2 ) // at least one complete connection entry (tuples of three)
    {
        if( l_connectedLaneInfo[0] >= 0 ) // positive road index: valid connection
        {
            l_laneConnected = ( state[COURSE_POSITION] > l_connectedLaneInfo[2] - state[COURSE_VELOCITY] * f_dT );
        }
    }

    if( l_laneConnected ) // connection has been reached
    {
        state[COURSE_POSITION] = 0;

        p_lane = static_cast<CInt>( l_connectedLaneInfo[1] );
        p_lane.set( static_cast<CInt>( l_connectedLaneInfo[1] ) );

        p_road = static_cast<CInt>( l_connectedLaneInfo[0] );
        p_road.set( static_cast<CInt>( l_connectedLaneInfo[0] ) );

        l_positionInfo = m_roadNetwork_p->roads[p_road].lanes[p_lane].getCoursePositionInfo( state[COURSE_POSITION], state[LATERAL_OFFSET] );
        o_x = l_positionInfo.x;
        o_y = l_positionInfo.y;
        o_z = l_positionInfo.z;
        o_xyzWorld.XYZ( l_positionInfo.x, l_positionInfo.y, l_positionInfo.z );
    }
    else // no connected road -> stay on lane_K1
    {
 
        l_positionInfo = m_roadNetwork_p->roads[p_road].lanes[m_lane_K1].getCoursePositionInfo( state[COURSE_POSITION], state[LATERAL_OFFSET] );
        
        if( l_positionInfo.s > m_roadNetwork_p->roads[p_road].o_lengthOfCourse.get() - state[COURSE_VELOCITY] * f_dT )
        // end of course reached
        {
            state[COURSE_POSITION] = 0;
        }

        o_x = l_positionInfo.x;
        o_y = l_positionInfo.y;
        o_z = l_positionInfo.z;
        o_xyzWorld.XYZ( l_positionInfo.x, l_positionInfo.y, l_positionInfo.z );
    }

    // rotate obstacle along its velocity
    o_yawAngle = p_alignWithVelocity ? l_positionInfo.gammaAngle + ::sim::atan2( o_vyCourse, o_vxCourse ) : l_positionInfo.gammaAngle;
    o_rollAngle = -l_positionInfo.crossfallAngleLocal;
    o_pitchAngle = -l_positionInfo.slopeAngleLocal;

    o_vxCourse = state[COURSE_VELOCITY]; // caution: NO LATERAL_OFFSET considered
    o_vyCourse = ddtState[LATERAL_OFFSET];
    o_acceleration = ddtState[COURSE_VELOCITY]; // caution: NO LATERAL_OFFSET considered
    o_lateralOffset = state[LATERAL_OFFSET];
    state[COURSE_POSITION] = state[COURSE_POSITION] + p_offsetPos;
    p_offsetPos.init( 0 ); //ToDo remove workaround to change course position dynamic //never use this workaround with vector
    o_coursePosition = state[COURSE_POSITION];

    // set track info at obstacle position
    if( l_laneConnected )
    {
        o_trackWidthBack = m_roadNetwork_p->roads[p_road].lanes[p_lane].getTrackWidth( o_coursePosition );
        o_trackWidthFront = m_roadNetwork_p->roads[p_road].lanes[p_lane].getTrackWidth( o_coursePosition + p_depth );
    }
    else
    {
        o_trackWidthBack = m_roadNetwork_p->roads[p_road].lanes[m_lane_K1].getTrackWidth( o_coursePosition );
        o_trackWidthFront = m_roadNetwork_p->roads[p_road].lanes[m_lane_K1].getTrackWidth( o_coursePosition + p_depth );
    }

    //Calculate velocity in world coordinates from course related velocities and angles (o_vxCourse, ...)
    if( i_staticSimulation == false )
    {
        CFloat l_vxWorld, l_vyWorld, l_vzWorld;
        // Note: in the following ::sim::coordinateRotation, we need to consider course angles to transform velocity from vCourse to vWorld.
        //       If 'alginWithVelocity' is not used, these angles are equivalent to roll/pitch/yawAngles.
        ::sim::coordinateRotation( -l_positionInfo.crossfallAngleLocal, -l_positionInfo.slopeAngleLocal, l_positionInfo.gammaAngle,
                            o_vxCourse,  o_vyCourse,   0,
                            l_vxWorld,   l_vyWorld,    l_vzWorld );
        o_vWorld.XYZ( l_vxWorld, l_vyWorld, l_vzWorld );
    }
    else
    {
        o_vWorld.XYZ( 0.0, 0.0, 0.0 );
    }


    //contour Points of obstacle
    m_xLocalContour[0] = -p_depth / 2;
    m_xLocalContour[1] = -p_depth / 2;
    m_xLocalContour[2] = +p_depth / 2;
    m_xLocalContour[3] = +p_depth / 2;
    m_yLocalContour[0] = +p_width / 2;
    m_yLocalContour[1] = -p_width / 2;
    m_yLocalContour[2] = -p_width / 2;
    m_yLocalContour[3] = +p_width / 2;
    m_zLocalContour[0] = +p_height / 2;
    m_zLocalContour[1] = +p_height / 2;
    m_zLocalContour[2] = +p_height / 2;
    m_zLocalContour[3] = +p_height / 2;
    for( auto index = 0 ; index < 4; index++ )
    {
        ::sim::coordinateRotation( o_rollAngle, o_pitchAngle, o_yawAngle,
                            m_xLocalContour[index], m_yLocalContour[index], m_zLocalContour[index],
                            o_xWorldContour[index], o_yWorldContour[index], o_zWorldContour[index] );
        o_xWorldContour[index] += o_xyzWorld[0];
        o_yWorldContour[index] += o_xyzWorld[1];
        o_zWorldContour[index] += o_xyzWorld[2];
    }
}


