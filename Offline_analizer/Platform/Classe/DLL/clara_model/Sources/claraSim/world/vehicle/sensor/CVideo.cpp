/*******************************************************************************
@author Robert Erhart, ett2si (19.08.2008)
@copyright (c) Robert Bosch GmbH 2008-2024. All rights reserved.
*******************************************************************************/

#include "CVideo.h"


////*********************************
//// CVideo
////*********************************
CVideo::CVideo():
    // m_viewSegment_a( 0 ),
    m_obstacle_a( 0 ),
    m_videoLine_a( 0 ),
    m_roadNetwork_p( nullptr ),
    m_egoLaneID( 0 ),
    m_xWorldLeftEdgeObstacle( 0 ),
    m_yWorldLeftEdgeObstacle( 0 ),
    m_zWorldLeftEdgeObstacle( 0 ),
    m_xWorldRightEdgeObstacle( 0 ),
    m_yWorldRightEdgeObstacle( 0 ),
    m_zWorldRightEdgeObstacle( 0 )
{
    /* Initialization messages */
    p_anglesFieldOfViewSegments.setInit( ::sim::to_radians( {+20, +15, +10, -10, -15, -20} ) ) ;
    p_maxRangesFieldOfViewSegments.setInit( CFloatVector( {60., 80., 100., 80., 60.} ) );
    p_minRangesFieldOfViewSegments.setInit( CFloatVector( 0.1, 5 ) );

    addMessageParameter( p_sensorBlind, false, CVideoDoc::p_sensorBlind );
    addMessageParameter( p_maxNumberOfRelevantLines, 8, CVideoDoc::p_maxNumberOfRelevantLines );

    addMessageOutput( o_xVideoLeftEdgeObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CVideoDoc::o_xVideoLeftEdgeObstacle );
    addMessageOutput( o_yVideoLeftEdgeObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CVideoDoc::o_yVideoLeftEdgeObstacle );
    addMessageOutput( o_zVideoLeftEdgeObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CVideoDoc::o_zVideoLeftEdgeObstacle );
    addMessageOutput( o_xVideoRightEdgeObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CVideoDoc::o_xVideoRightEdgeObstacle );
    addMessageOutput( o_yVideoRightEdgeObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CVideoDoc::o_yVideoRightEdgeObstacle );
    addMessageOutput( o_zVideoRightEdgeObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CVideoDoc::o_zVideoRightEdgeObstacle );
    addMessageOutput( o_alphaVideoLeftBorderObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CVideoDoc::o_alphaVideoLeftBorderObstacle );
    addMessageOutput( o_alphaVideoRightBorderObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CVideoDoc::o_alphaVideoRightBorderObstacle );
    addMessageOutput( o_alphaVideoLeftBorderObstacleRightCourseLine, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CVideoDoc::o_alphaVideoLeftBorderObstacleRightCourseLine );
    addMessageOutput( o_alphaVideoRightBorderObstacleLeftCourseLine, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CVideoDoc::o_alphaVideoRightBorderObstacleLeftCourseLine );

    addMessageOutput( o_typeLine, CIntVector( CInt( 0 ), p_maxNumberOfRelevantLines ), CVideoDoc::o_typeLine );
    addMessageOutput( o_arcLength, CFloatVector( 0.0, p_maxNumberOfRelevantLines ), CVideoDoc::o_arcLength );
    addMessageOutput( o_indexLine, CIntVector( CInt( 0 ), p_maxNumberOfRelevantLines ), CVideoDoc::o_indexLine );
    addMessageOutput( o_xVideoLineStart, CFloatVector( 0.0, p_maxNumberOfRelevantLines ), CVideoDoc::o_xVideoLineStart );
    addMessageOutput( o_yVideoLineStart, CFloatVector( 0.0, p_maxNumberOfRelevantLines ), CVideoDoc::o_yVideoLineStart );
    addMessageOutput( o_zVideoLineStart, CFloatVector( 0.0, p_maxNumberOfRelevantLines ), CVideoDoc::o_zVideoLineStart );
    addMessageOutput( o_gammaVideoLineStart, CFloatVector( 0.0, p_maxNumberOfRelevantLines ), CVideoDoc::o_gammaVideoLineStart );
    addMessageOutput( o_xVideoLineEnd, CFloatVector( 0.0, p_maxNumberOfRelevantLines ), CVideoDoc::o_xVideoLineEnd );
    addMessageOutput( o_yVideoLineEnd, CFloatVector( 0.0, p_maxNumberOfRelevantLines ), CVideoDoc::o_yVideoLineEnd );
    addMessageOutput( o_zVideoLineEnd, CFloatVector( 0.0, p_maxNumberOfRelevantLines ), CVideoDoc::o_zVideoLineEnd );
    addMessageOutput( o_curvatureLineStart, CFloatVector( 0.0, p_maxNumberOfRelevantLines ), CVideoDoc::o_curvatureLineStart );
    addMessageOutput( o_curvatureDerivativeLineStart, CFloatVector( 0.0, p_maxNumberOfRelevantLines ), CVideoDoc::o_curvatureDerivativeLineStart );

    addMessageInput( i_lateralOffsetCourseObstacleDynamic );
    addMessageInput( i_trackWidthBackObstacleDynamic );

    addMessageInput( i_lengthOfCourseRoad );
    addMessageInput( i_numberOfLanesRoad );
    addMessageInput( i_numberOfLanesLeftRoad );
    addMessageInput( i_numberOfLanesRightRoad );
    addMessageInput( i_indexOfLeftmostLaneRoad );
    addMessageInput( i_indexOfRightmostLaneRoad );
    addMessageInput( i_currentRoadIndex, -1 );
    addMessageInput( i_currentLaneID, -1 );
    addMessageInput( i_searchIDLane, 0LL );
}

CVideo::~CVideo()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CVideo::init( IMessage<CFloatVectorXYZ>& f_xyzWorld,
                   IMessage<CFloatVectorXYZ>& f_velocityXYZWorld,
                   IMessage<CFloatVectorXYZ>& f_accelerationXYZVehicleEgo,
                   IMessage<CFloatVectorXYZ>& f_angleRollPitchYawEgo,
                   IMessage<CFloat>& f_yawRateEgo,
                   CObstacles& f_obstacles_r,
                   IMessage<CBool>& f_staticSimulation,
                   IMessage<CInt>&   f_currentRoadIndex,
                   IMessage<CInt>&   f_currentLaneIndex,
                   IMessage<CInt>& f_searchIndexLane,
                   CRoadNetwork& f_roadNetwork_r )
{
    /* Call parent's init for standard input messages */
    CSensor::init( f_xyzWorld,
                   f_velocityXYZWorld,
                   f_accelerationXYZVehicleEgo,
                   f_angleRollPitchYawEgo,
                   f_yawRateEgo,
                   f_obstacles_r,
                   f_staticSimulation );

    /*
     * link input messages: mainly done inside CSensor, rest comes below
     */
    i_currentRoadIndex.link( f_currentRoadIndex );
    i_currentLaneID.link( f_currentLaneIndex );
    i_searchIDLane.link( f_searchIndexLane );

    i_trackWidthBackObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::o_trackWidthBack );
    i_lateralOffsetCourseObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::o_lateralOffset );

    m_roadNetwork_p = &f_roadNetwork_r;
    i_lengthOfCourseRoad.link( f_roadNetwork_r.roads, &CRoad::o_lengthOfCourse );
    i_numberOfLanesReferencePoints.link( f_roadNetwork_r.roads, &CRoad::o_numberOfLanesReferencePoints );
    i_numberOfLanesRoad.link( f_roadNetwork_r.roads, &CRoad::o_numberOfLanes );
    i_numberOfLanesLeftRoad.link( f_roadNetwork_r.roads, &CRoad::o_numberOfLanesLeft );
    i_numberOfLanesRightRoad.link( f_roadNetwork_r.roads, &CRoad::o_numberOfLanesRight );
    i_indexOfLeftmostLaneRoad.link( f_roadNetwork_r.roads, &CRoad::o_indexOfLeftmostLane );
    i_indexOfRightmostLaneRoad.link( f_roadNetwork_r.roads, &CRoad::o_indexOfRightmostLane );

    /* Initialization messages */
    initializationMessages();

    /* Re-Initialization of dependend messages */
    /* needs to stay here, not in CSensor!? */

    // messages defined in CSensor
    o_xViewSegment.init( CFloatVector( CFloat( 0.0 ), 3 * p_maxRangesFieldOfViewSegments.size() ) );
    o_yViewSegment.init( CFloatVector( CFloat( 0.0 ), 3 * p_maxRangesFieldOfViewSegments.size() ) );
    o_zViewSegment.init( CFloatVector( CFloat( 0.0 ), 3 * p_maxRangesFieldOfViewSegments.size() ) );

    o_indexObstacle.init( CIntVector( CInt( 0 ), p_maxNumberOfRelevantObstacles ) );
    o_typeObstacle.init( CIntVector( CInt( 0 ), p_maxNumberOfRelevantObstacles ) );
    o_referenceSurfaceObstacle.init( CIntVector( CInt( 0 ), p_maxNumberOfRelevantObstacles ) );
    o_visibilityObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_xSensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_ySensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_zSensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_alphaSensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_yawAngleSensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_heightSensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_widthSensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_depthSensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_vXSensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_vYSensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_vZSensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_aXVehicleObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_aYVehicleObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_aZVehicleObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_distanceSensorObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    // messages defined in CVideo
    o_xVideoLeftEdgeObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_yVideoLeftEdgeObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_zVideoLeftEdgeObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_xVideoRightEdgeObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_yVideoRightEdgeObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_zVideoRightEdgeObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_alphaVideoLeftBorderObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_alphaVideoRightBorderObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_alphaVideoLeftBorderObstacleRightCourseLine.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_alphaVideoRightBorderObstacleLeftCourseLine.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );

    /*
     * Output messages: sensor info
     */
    o_xyzWorldSensor.init( p_xyzVehicleMountingPos + i_xyzWorldVehicle );
    o_rotationWorld.init( i_angleRollPitchYawVehicle + p_angleRollPitchYawVehicleMounting );

    //one virtual obstacle with visibility -1 at the end, avoiding segmentation fault for finding next relevant obstacle ~Z380
    m_obstacleDynamicVisibility.resize( i_xyzWorldObstacleDynamic.size() + 1, -1.0 );
    m_obstacleDynamicVisibilityIndexList.resize( i_xyzWorldObstacleDynamic.size() + 1, 0LL );
    for( uint32_t index = 0; index < m_obstacleDynamicVisibilityIndexList.size(); index++ )
    {
        m_obstacleDynamicVisibilityIndexList[index] = index;
    }
    m_obstacleStaticVisibility.resize( i_xyzWorldObstacleStatic.size() + 1, -1.0 );
    m_obstacleStaticVisibilityIndexList.resize( i_xyzWorldObstacleStatic.size() + 1, 0LL );
    for( uint32_t index = 0; index < m_obstacleStaticVisibilityIndexList.size(); index++ )
    {
        m_obstacleStaticVisibilityIndexList[index] = index;
    }

    m_obstacle_a.resize( p_maxNumberOfRelevantObstacles );
    m_viewSegment_a.resize( p_maxRangesFieldOfViewSegments.size() );
    m_videoLine_a.resize( p_maxNumberOfRelevantLines );

    o_typeLine.init( CIntVector( CInt( 0 ), p_maxNumberOfRelevantLines ) );
    o_arcLength.init( CFloatVector( 0.0, p_maxNumberOfRelevantLines ) );
    o_indexLine.init( CIntVector( CInt( 0 ), p_maxNumberOfRelevantLines ) );
    o_xVideoLineStart.init( CFloatVector( 0.0, p_maxNumberOfRelevantLines ) );
    o_yVideoLineStart.init( CFloatVector( 0.0, p_maxNumberOfRelevantLines ) );
    o_zVideoLineStart.init( CFloatVector( 0.0, p_maxNumberOfRelevantLines ) );
    o_gammaVideoLineStart.init( CFloatVector( 0.0, p_maxNumberOfRelevantLines ) );
    o_xVideoLineEnd.init( CFloatVector( 0.0, p_maxNumberOfRelevantLines ) );
    o_yVideoLineEnd.init( CFloatVector( 0.0, p_maxNumberOfRelevantLines ) );
    o_zVideoLineEnd.init( CFloatVector( 0.0, p_maxNumberOfRelevantLines ) );
    o_curvatureLineStart.init( CFloatVector( 0.0, p_maxNumberOfRelevantLines ) );
    o_curvatureDerivativeLineStart.init( CFloatVector( 0.0, p_maxNumberOfRelevantLines ) );
}

/*------------------*/
/* private methods */
/*------------------*/
void CVideo::calc( CFloat f_dT, CFloat f_time )
{
    // Call parent's calc for sensor coordinates, orientation, view segment output, and velocity from rotation.
    CSensor::calc( f_dT, f_time );

    // simulate Video measurement program
    if( p_sensorConfiguration != 0 and getExternTrigger() )
    {
        //***************************************************************************//
        //                                obstacles
        //***************************************************************************//
        //get relevant object indices with priolist for dynamic and static objects
        for( size_t l_idxObstacle = 0; l_idxObstacle < i_xyzWorldObstacleStatic.size() ; l_idxObstacle++ )
        {
            if( i_typeObstacleStatic[l_idxObstacle] != 0 and i_visibilityObstacleStatic[l_idxObstacle] > 0 )
            {
                CFloat l_visibility = 0;
                for( auto& it :  m_viewSegment_a )
                {
                    l_visibility =
                        ::sim::max( l_visibility,
                                    it.checkInRange( i_xWorldContourObstacleStatic[l_idxObstacle], i_yWorldContourObstacleStatic[l_idxObstacle], i_zWorldContourObstacleStatic[l_idxObstacle] )
                                  );
                }
                m_obstacleStaticVisibility[l_idxObstacle] = l_visibility;
            }
            else
            {
                m_obstacleStaticVisibility[l_idxObstacle] = 0.0;
            }
        }
        heapSortWithComparsionCriterion( m_obstacleStaticVisibilityIndexList, m_obstacleStaticVisibility );

        for( size_t l_idxObstacle = 0; l_idxObstacle < i_xyzWorldObstacleDynamic.size() ; l_idxObstacle++ )
        {
            if( i_typeObstacleDynamic[l_idxObstacle] != 0 and i_visibilityObstacleDynamic[l_idxObstacle] > 0 )
            {
                CFloat l_visibility = 0;
                for( auto& it :  m_viewSegment_a )
                {
                    l_visibility = 
                        ::sim::max( l_visibility,
                                    it.checkInRange( i_xWorldContourObstacleDynamic[l_idxObstacle], i_yWorldContourObstacleDynamic[l_idxObstacle], i_zWorldContourObstacleDynamic[l_idxObstacle] )
                                  );
                }
                m_obstacleDynamicVisibility[l_idxObstacle] = l_visibility;
            }
            else
            {

                m_obstacleDynamicVisibility[l_idxObstacle] = 0.0;
            }
        }
        heapSortWithComparsionCriterion( m_obstacleDynamicVisibilityIndexList, m_obstacleDynamicVisibility );

        // generate relevant obstacle array and calculate the relevant side of the obstacle
        CInt l_indexDynamic = 0;
        CInt l_indexStatic = 0;
        CFloat l_visibilityDynamic = m_obstacleDynamicVisibility[m_obstacleDynamicVisibilityIndexList[l_indexDynamic]];
        CFloat l_visibilityStatic = m_obstacleStaticVisibility[m_obstacleStaticVisibilityIndexList[l_indexStatic]];
        for( CInt index = 0; index < p_maxNumberOfRelevantObstacles; index++ )
        {
            if( l_visibilityStatic > 0 and l_visibilityStatic > l_visibilityDynamic )
            {
                CInt t_indexVisibility = m_obstacleStaticVisibilityIndexList[l_indexStatic];
                m_obstacle_a[index].init( -t_indexVisibility - 1,
                                          o_xyzWorldSensor,
                                          m_velocityXYZWorldSensor,
                                          ( CFloatVector )i_aWorldVehicle,
                                          i_angleRollPitchYawVehicle,
                                          p_angleRollPitchYawVehicleMounting,
                                          i_xyzWorldObstacleStatic[t_indexVisibility],
                                          CFloatVector( 0., 3 ), // velocity
                                          0, // acceleration (obstacle x direction)
                                          i_yawAngleObstacleStatic[t_indexVisibility], i_typeObstacleStatic[t_indexVisibility],
                                          CFloatVector( { i_depthObstacleStatic[t_indexVisibility], i_heightObstacleStatic[t_indexVisibility], i_widthObstacleStatic[t_indexVisibility] } ),
                                          ( p_sensorBlind == false ? i_visibilityObstacleStatic[t_indexVisibility] : 0.0 ),
                                          i_xWorldContourObstacleStatic[t_indexVisibility], i_yWorldContourObstacleStatic[t_indexVisibility], i_zWorldContourObstacleStatic[t_indexVisibility]
                                        );

                m_obstacle_a[index].calcProperties();

                l_indexStatic++;
                l_visibilityStatic = m_obstacleStaticVisibility[m_obstacleStaticVisibilityIndexList[l_indexStatic]];
            }
            else if( l_visibilityDynamic > 0 )
            {
                CInt t_indexVisibility = m_obstacleDynamicVisibilityIndexList[l_indexDynamic];
                m_obstacle_a[index].init( t_indexVisibility + 1,
                                          o_xyzWorldSensor,
                                          m_velocityXYZWorldSensor,
                                          ( CFloatVector )i_aWorldVehicle,
                                          i_angleRollPitchYawVehicle,
                                          p_angleRollPitchYawVehicleMounting,
                                          i_xyzWorldObstacleDynamic[t_indexVisibility],
                                          i_vWorldObstacleDynamic[t_indexVisibility],
                                          i_aObstacleDynamic[t_indexVisibility],
                                          i_yawAngleObstacleDynamic[t_indexVisibility], i_typeObstacleDynamic[t_indexVisibility],
                                          CFloatVector( { i_depthObstacleDynamic[t_indexVisibility], i_heightObstacleDynamic[t_indexVisibility], i_widthObstacleDynamic[t_indexVisibility] } ),
                                          ( p_sensorBlind == false ? i_visibilityObstacleDynamic[t_indexVisibility] : 0.0 ),
                                          i_xWorldContourObstacleDynamic[t_indexVisibility], i_yWorldContourObstacleDynamic[t_indexVisibility], i_zWorldContourObstacleDynamic[t_indexVisibility]
                                        );

                m_obstacle_a[index].calcProperties();

                l_indexDynamic++;
                l_visibilityDynamic = m_obstacleDynamicVisibility[m_obstacleDynamicVisibilityIndexList[l_indexDynamic]];
            }
            else
            {
                m_obstacle_a[index].init();
            }
        }

        for( auto l_index = 0U; l_index < m_obstacle_a.size() ; l_index++ )
        {
            if(
                m_obstacle_a[l_index].updateObstacleMessages(
                    o_indexObstacle[l_index],
                    o_typeObstacle[l_index],
                    o_referenceSurfaceObstacle[l_index],
                    o_visibilityObstacle[l_index],
                    o_xSensorObstacle[l_index], o_ySensorObstacle[l_index], o_zSensorObstacle[l_index],
                    o_alphaSensorObstacle[l_index],
                    o_yawAngleSensorObstacle[l_index],
                    o_heightSensorObstacle[l_index], o_widthSensorObstacle[l_index], o_depthSensorObstacle[l_index],
                    o_vXSensorObstacle[l_index], o_vYSensorObstacle[l_index], o_vZSensorObstacle[l_index],
                    o_aXVehicleObstacle[l_index], o_aYVehicleObstacle[l_index], o_aZVehicleObstacle[l_index],
                    o_distanceSensorObstacle[l_index],
                    p_referenceSurfaceObstacleFixed,
                    m_xWorldLeftEdgeObstacle, m_yWorldLeftEdgeObstacle, m_zWorldLeftEdgeObstacle,
                    m_xWorldRightEdgeObstacle, m_yWorldRightEdgeObstacle, m_zWorldRightEdgeObstacle,
                    o_xVideoLeftEdgeObstacle[l_index], o_yVideoLeftEdgeObstacle[l_index], o_zVideoLeftEdgeObstacle[l_index],
                    o_xVideoRightEdgeObstacle[l_index], o_yVideoRightEdgeObstacle[l_index], o_zVideoRightEdgeObstacle[l_index],
                    o_alphaVideoLeftBorderObstacle[l_index], o_alphaVideoRightBorderObstacle[l_index] ) and
                i_currentRoadIndex >= 0 and i_currentLaneID >= 0 )
            {
                // Presave searchIndex variable i_searchIDLane. To avoid change by findRightBoundaryPositionInfo
                CInt t_searchIndexLane = i_searchIDLane;
                SPositionInfo l_leftEdgeObstacleRightLane = m_roadNetwork_p->roads[i_currentRoadIndex].lanes[i_currentLaneID].findRightBoundaryPositionInfo( m_xWorldLeftEdgeObstacle, m_yWorldLeftEdgeObstacle, t_searchIndexLane );
                //coordinate transformation world -> Video coordinates
                l_leftEdgeObstacleRightLane.x = l_leftEdgeObstacleRightLane.x - o_xyzWorldSensor[0];
                l_leftEdgeObstacleRightLane.y = l_leftEdgeObstacleRightLane.y - o_xyzWorldSensor[1];
                l_leftEdgeObstacleRightLane.z = l_leftEdgeObstacleRightLane.z - o_xyzWorldSensor[2];
                ::sim::coordinateRotationInv( o_rotationWorld[0], o_rotationWorld[1], o_rotationWorld[2],
                                       l_leftEdgeObstacleRightLane.x, l_leftEdgeObstacleRightLane.y, l_leftEdgeObstacleRightLane.z,
                                       l_leftEdgeObstacleRightLane.x, l_leftEdgeObstacleRightLane.y, l_leftEdgeObstacleRightLane.z );
                o_alphaVideoLeftBorderObstacleRightCourseLine[l_index] = ::sim::atan2( l_leftEdgeObstacleRightLane.y, l_leftEdgeObstacleRightLane.x ) - o_alphaVideoLeftBorderObstacle[l_index];
                //o_alphaVideoRightBorderObstacleLeftCourseLine
                SPositionInfo l_rightEdgeObstacleLeftLane = m_roadNetwork_p->roads[i_currentRoadIndex].lanes[i_currentLaneID].findLeftBoundaryPositionInfo( m_xWorldRightEdgeObstacle, m_yWorldRightEdgeObstacle, t_searchIndexLane );
                //coordinate transformation world -> Video coordinates
                l_rightEdgeObstacleLeftLane.x = l_rightEdgeObstacleLeftLane.x - o_xyzWorldSensor[0];
                l_rightEdgeObstacleLeftLane.y = l_rightEdgeObstacleLeftLane.y - o_xyzWorldSensor[1];
                l_rightEdgeObstacleLeftLane.z = l_rightEdgeObstacleLeftLane.z - o_xyzWorldSensor[2];
                ::sim::coordinateRotationInv( o_rotationWorld[0], o_rotationWorld[1], o_rotationWorld[2],
                                       l_rightEdgeObstacleLeftLane.x, l_rightEdgeObstacleLeftLane.y, l_rightEdgeObstacleLeftLane.z,
                                       l_rightEdgeObstacleLeftLane.x, l_rightEdgeObstacleLeftLane.y, l_rightEdgeObstacleLeftLane.z );
                o_alphaVideoRightBorderObstacleLeftCourseLine[l_index] = ::sim::atan2( l_rightEdgeObstacleLeftLane.y, l_rightEdgeObstacleLeftLane.x ) - o_alphaVideoRightBorderObstacle[l_index];
            }
            else
            {
                o_alphaVideoLeftBorderObstacleRightCourseLine[l_index] = 0;
                o_alphaVideoRightBorderObstacleLeftCourseLine[l_index] = 0;
            }
        }

        //***************************************************************************//
        //                                video lines
        //***************************************************************************//

        //*****     Helper functions    *****//

        //! Helper lambda function for lane index iteration in fashion: 0 -> +1 -> -1 -> +2 -> -2 ...
        auto iterateLaneIndex = []( int& lane )
        {
            if( lane == 0 )     lane++;
            else if( lane > 0 ) lane = -lane;  // e.g. +1 -> -1
            else               lane = -lane + 1; // e.g. -1 -> +2
        };

        //! Helper lambda function to check if a connection exists within the FOV.
        auto connectionInFOV = [&]( CRoad & road_r, CInt laneIndex )
        {
            if( road_r.lanes[laneIndex].p_connections[0] >= 0 ) // connection defined
            {
                SCoursePositionInfo l_connectionPos = road_r.lanes[laneIndex].getCoursePositionInfo( road_r.lanes[laneIndex].p_connections[2], 0 );
                CFloat l_connectionInFOV = 0.;
                for( auto& it :  m_viewSegment_a )
                {
                    l_connectionInFOV += it.checkInRange( l_connectionPos.x, l_connectionPos.y, l_connectionPos.z );
                }
                return ( l_connectionInFOV > 0 );
            }
            else return false;
        };

        //! Helper lambda function for line numbering: case handling of left/right side line and lane side relative to ego
        auto getLineNumber = []( CInt & lineCounterLeft, CInt & lineCounterRight, CInt relativeLaneID, CInt lineSide )
        {
            // Which side does the line belong to?
            CInt side;
            if( relativeLaneID == 0 )    side = ( lineSide == CLane::left ? 1 : -1 ); // on ego lane: decide via 'lineSide'
            else                        side = ::sim::sig( relativeLaneID );                    // on other lanes: decide by lane ID sign (left: positive, right: negative)

            // Update counter of this side and return ID value
            if( side > 0 )
            {
                lineCounterLeft++;
                return lineCounterLeft;
            }
            else
            {
                lineCounterRight++;
                return -1 * lineCounterRight;
            }
        };

        auto l_videoLine_it = m_videoLine_a.begin();

        if( i_currentRoadIndex >= 0 ) // check for valid road and lane (not off-road)
        {
            CRoad& l_road_r = m_roadNetwork_p->roads[i_currentRoadIndex];

            // Get lane index "m_egoLaneID" in SIGNED notation (positive: to the left, negative: to the right of reference lane zero, see CRoad.h).
            m_egoLaneID = i_currentLaneID;
            CFloat l_sStart, l_sEnd;            // line arc length start and end values
            CInt l_laneID;
            ::std::vector<CInt> l_sides_a;      // sides array {CLane::left & right}
            bool l_checkForFork = false;        // line might become visible in case of a fork -> check for fork
            CInt l_laneIDForForkCheck = 0;
            CInt l_lineCounterLeft = 0;         // line ID counters for left and right hand side
            CInt l_lineCounterRight = 0;
            enum BoundaryIndicator { CURRENT, NEXTLANE, COMBINED };
            BoundaryIndicator l_whichBoundary = CURRENT;

            // Iterate relative lane index (l_iLane) in an alternating fashion 0 -> +1 -> -1 -> +2 -> -2 ... through adjacent lanes.
            // These indices follow the typical convention (see CRoad.h). Example:
            //
            // lane layout with e = ego position = lane C
            //
            //    A  B  C  D  E  F
            //  |  |  |  |  |  |  |
            //  |  |  |  |  |  |  |
            //  |  |  |e |  |  |  |
            //  |  |  |  |  |  |  |
            //
            //   2  1  0  -1 -2 -3   value of l_iLane (relative lane ID)
            //   3  2  1   0 -1 -2   value of l_laneID (absolute lane ID, assuming lane D is defined to be the reference lane)

            // If the resulting lane exists, iterate through both boundary sides of the lane.
            //   - For the ego lane (l_iLane == 0), compute lines on both sides.
            //   - For positive index lanes (l_iLane > 0), compute left lines only.
            //   - For negative index lanes, compute right lines only.
            //   - In addition, perform a case handling for connected roads:
            //       o  TODO: description of case handling


            // Iterate relative lane ID (l_iLane)
            for( int l_iLane = 0;           // start with ego lane
                 ( ::sim::abs( l_iLane ) < i_numberOfLanesRoad[i_currentRoadIndex] ) and ( l_videoLine_it != m_videoLine_a.end() );
                 iterateLaneIndex( l_iLane ) // propagate iterator
               )
            {
                // Retreive absolute laneID
                l_laneID    = m_egoLaneID + l_iLane;

                // If lane is not part of the road: skip initialization of videoLine element.
                if( not l_road_r.isValidLaneID( l_laneID ) )
                {
                    continue;
                }

                // Toggle side iteration order for correct ordering of lines
                if( l_iLane > 0 ) l_sides_a = {CLane::right, CLane::left};  // lanes to the left: start with right side
                else l_sides_a = {CLane::left, CLane::right};               // ego lane and lanes to the right: start with left side

                for( auto& l_side : l_sides_a )
                {
                    l_checkForFork = false;

                    if( ( l_iLane > 0 ) and ( l_side == CLane::right ) )
                    {
                        l_laneIDForForkCheck = l_laneID - 1;
                        if( l_road_r.isValidLaneID( l_laneIDForForkCheck ) ) l_checkForFork = true; // l_laneID-1 is a valid lane
                    }

                    if( ( l_iLane < 0 ) and ( l_side == CLane::left ) )
                    {
                        l_laneIDForForkCheck = l_laneID + 1;
                        if( l_road_r.isValidLaneID( l_laneIDForForkCheck ) ) l_checkForFork = true; // l_laneID+1 is a valid lane
                    }

                    auto& l_LaneBoundary_r = l_road_r.lanes[l_laneID].BoundaryLine[l_side];
                    CLine l_combinedBoundary;
                    CBool l_laneLineInFieldOfView = findIntersectionVideoLineAndFieldOfView( l_LaneBoundary_r, l_sStart, l_sEnd );

                    // Lines with "checkForFork" flag need to be considered only if this fork is actually in
                    // sight & the neighbouring lane is connected to a *different* road than the current lane.
                    // We need to perform these checks and skip the iteration (l_side) otherwise using 'continue'.
                    if( l_checkForFork )
                    {
                        // no connection on this lane inside FOV -> no fork
                        if( not connectionInFOV( l_road_r, l_laneID ) )
                        {
                            continue;
                        } // END no connection in FOV

                        // connection in sight on this lane -> check connection on neighbouring lane
                        else
                        {
                            // no connection defined on neighbour lane.
                            if( not connectionInFOV( l_road_r, l_laneIDForForkCheck ) )
                            {
                                continue;
                            }
                            // both lanes connected to the same road -> no fork
                            else if( l_road_r.lanes[l_laneID].p_connections[0] == l_road_r.lanes[l_laneIDForForkCheck].p_connections[0] )
                            {
                                continue;
                            }
                            // a relevant fork was found inside the FOV
                            else
                            {
                                l_whichBoundary = NEXTLANE;
                            } // END combined boundary used for forking lines
                        } // END connection exists inside FOV
                    } // END potential forking line

                    else // regular line (no need to check for fork)
                    {
                        if( connectionInFOV( l_road_r, l_laneID ) )
                        {
                            l_whichBoundary = COMBINED;
                        } // END non-forking connection

                        else // standard, non-connected lane
                        {
                            l_whichBoundary = CURRENT;
                        } // END non-connected (standard) lane
                    } // END case handling: no fork check needed (l_checkForFork == false)



                    switch( l_whichBoundary )
                    {
                        case( COMBINED ):
                        {
                            CInt l_connectedRoadIndex   = ( int ) l_road_r.lanes[l_laneID].p_connections[0];
                            CInt l_connectedLaneIndex   = ( int ) l_road_r.lanes[l_laneID].p_connections[1];
                            CLine l_secondLaneBoundary = m_roadNetwork_p->roads[l_connectedRoadIndex].lanes[l_connectedLaneIndex].BoundaryLine[l_side];

                            l_combinedBoundary.init( l_LaneBoundary_r, l_secondLaneBoundary ); // create new, combined boundary line
                            l_laneLineInFieldOfView = findIntersectionVideoLineAndFieldOfView( l_combinedBoundary, l_sStart, l_sEnd, l_combinedBoundary.getNumberOfLineReferencePoints(), i_searchIDLane );
                            break;
                        }
                        case( NEXTLANE ):
                        {
                            CInt l_connectedRoadIndex   = ( int ) l_road_r.lanes[l_laneID].p_connections[0];
                            CInt l_connectedLaneIndex   = ( int ) l_road_r.lanes[l_laneID].p_connections[1];

                            l_combinedBoundary = m_roadNetwork_p->roads[l_connectedRoadIndex].lanes[l_connectedLaneIndex].BoundaryLine[l_side];
                            l_laneLineInFieldOfView = findIntersectionVideoLineAndFieldOfView( l_combinedBoundary, l_sStart, l_sEnd, l_combinedBoundary.getNumberOfLineReferencePoints(), 1 ); // start index = 0 will lead to error, minimum value == 1
                            break;
                        }
                        case( CURRENT ):
                            // already calculated above
                            break;
                        default:
                            break;
                    }

                    // fill the current video line
                    if( l_laneLineInFieldOfView )
                    {
                        ( *l_videoLine_it ).init( getLineNumber( l_lineCounterLeft, l_lineCounterRight, l_iLane, l_side ),
                                                  o_rotationWorld[0], o_rotationWorld[1], o_rotationWorld[2],
                                                  o_xyzWorldSensor[0], o_xyzWorldSensor[1], o_xyzWorldSensor[2],
                                                  ( l_whichBoundary == CURRENT ) ? l_LaneBoundary_r : l_combinedBoundary,
                                                  l_sStart, l_sEnd );
                        l_videoLine_it = ::std::next( l_videoLine_it );
                    }

                } // END l_side loop
            } // END l_iLane loop


            // Empty initialization of unused m_videoLine_a elements
        }
        while( l_videoLine_it != m_videoLine_a.end() )
        {
            ( *l_videoLine_it ).init();
            l_videoLine_it = ::std::next( l_videoLine_it );
        }

        // Update the video lines' output messages
        for( uint32_t l_indexOutput = 0; l_indexOutput < m_videoLine_a.size(); l_indexOutput++ )
        {
            m_videoLine_a[l_indexOutput].updateVideoLineMessages(
                o_indexLine[l_indexOutput],
                o_typeLine[l_indexOutput],
                o_arcLength[l_indexOutput],
                o_xVideoLineStart[l_indexOutput],
                o_yVideoLineStart[l_indexOutput],
                o_zVideoLineStart[l_indexOutput],
                o_gammaVideoLineStart[l_indexOutput],
                o_xVideoLineEnd[l_indexOutput],
                o_yVideoLineEnd[l_indexOutput],
                o_zVideoLineEnd[l_indexOutput],
                o_curvatureLineStart[l_indexOutput],
                o_curvatureDerivativeLineStart[l_indexOutput]
            );
        }
    }
}


bool CVideo::findIntersectionVideoLineAndFieldOfView( CLine& f_laneBoundary_r, CFloat& f_sStart, CFloat& f_sEnd )
{
    return findIntersectionVideoLineAndFieldOfView( f_laneBoundary_r, f_sStart, f_sEnd, i_numberOfLanesReferencePoints[i_currentRoadIndex], i_searchIDLane );
}


bool CVideo::findIntersectionVideoLineAndFieldOfView( CLine& f_laneBoundary_r, CFloat& f_sStart, CFloat& f_sEnd, CInt f_noOfReferencePoints, CInt f_startIndex )
{
    // TODO: Idea for the algo below & refactoring
    // - start search at "i_searchIDLane" (=ego spline index)
    // - search for forward (plus) and backward (minus) indices that are in view segment range
    // - stop search if
    //      two "endpoints" were found
    //      OR search position deviates by +- 200 m from ego 's' position
    //      OR lane end reached (0 or numberOfLanesReferencePoints)


    //search method for video lines reference points
    //car position at r
    // 1)
    // -4 -3 -2 -1  0  1  2  3
    //  o  x  x  x  r  x  x  o

    // 2)
    // -3 -2 -1  0  1  2  3  4  5  6  7
    //  o  o  o  r  o  o  x  x  x  x  o

    // 3)
    // -4 -3 -2 -1  0  1  2
    //  o  x  x  0  r  o  o
    //

    //intersection between index and index +1; in l_lineEndPoints index is saved
    CInt l_numberOfLanesReferencePoints = f_noOfReferencePoints;
    CFloat l_sReferencePosition = ( *f_laneBoundary_r.getSLineVector() )[f_startIndex];
    CInt l_searchIndexPlus = f_startIndex + 1;
    CInt l_searchIndexMinus = f_startIndex - 1;
    CFloat l_sPositionIndexPlus = ( *f_laneBoundary_r.getSLineVector() )[l_searchIndexPlus];
    CFloat l_sPositionIndexMinus = ( *f_laneBoundary_r.getSLineVector() )[l_searchIndexMinus];
    ::std::vector<CInt> l_lineEndPoints( 2, -1 );
    uint16_t l_indexLineEndPoints = 0;
    CFloat l_visibilityK1IndexPlus = 0.0;
    CFloat l_visibilityK1IndexMinus = 0.0;
    for( auto& it :  m_viewSegment_a )
    {
        l_visibilityK1IndexPlus += it.checkInRange( ( *f_laneBoundary_r.getXLineVector() )[f_startIndex], ( *f_laneBoundary_r.getYLineVector() )[f_startIndex], ( *f_laneBoundary_r.getZLineVector() )[f_startIndex] );
    }
    l_visibilityK1IndexMinus = l_visibilityK1IndexPlus;
    while( ( l_searchIndexPlus < l_numberOfLanesReferencePoints or l_searchIndexMinus >= 0 )
           and
           l_indexLineEndPoints < 2
           and
           ( ( l_sPositionIndexPlus - l_sReferencePosition ) < 200 or ( l_sReferencePosition - l_sPositionIndexMinus ) < 200 ) ) //ToDo dynamic search range limitation
    {
        if( l_searchIndexPlus < l_numberOfLanesReferencePoints )
        {
            CFloat l_visibility = 0;
            for( auto& it :  m_viewSegment_a )
            {
                l_visibility += it.checkInRange( ( *f_laneBoundary_r.getXLineVector() )[l_searchIndexPlus], ( *f_laneBoundary_r.getYLineVector() )[l_searchIndexPlus], ( *f_laneBoundary_r.getZLineVector() )[l_searchIndexPlus] );
            }
            if( ( l_visibility > 0 ) != ( l_visibilityK1IndexPlus > 0 ) )
            {
                l_lineEndPoints[l_indexLineEndPoints] = l_searchIndexPlus - 1;
                if( l_visibility == 0 )
                {
                    //l_lineEndPoints[l_indexLineEndPoints]--;
                    l_searchIndexPlus = l_numberOfLanesReferencePoints;
                }
                else
                {
                    //the searchIndexMinus path is not relevant any more
                    l_searchIndexMinus = -1;
                    l_searchIndexPlus++;
                }
                //::std::cout << "l_lineEndPoints1: " << l_indexLineEndPoints << " " << l_lineEndPoints[l_indexLineEndPoints] << ::std::endl;
                l_indexLineEndPoints++;
            }
            else
            {
                l_searchIndexPlus++;
            }
            if( l_searchIndexPlus == l_numberOfLanesReferencePoints )
            {
                if( l_visibility > 0 )
                {
                    l_lineEndPoints[l_indexLineEndPoints] = l_searchIndexPlus - 1;
                    l_indexLineEndPoints++;
                }
            }
            else
            {
                l_sPositionIndexPlus = ( *f_laneBoundary_r.getSLineVector() )[l_searchIndexPlus];
            }
            l_visibilityK1IndexPlus = l_visibility;
        }
        if( l_searchIndexMinus >= 0 )
        {
            CFloat l_visibility = 0;
            for( auto& it :  m_viewSegment_a )
            {
                l_visibility += it.checkInRange( ( *f_laneBoundary_r.getXLineVector() )[l_searchIndexMinus], ( *f_laneBoundary_r.getYLineVector() )[l_searchIndexMinus], ( *f_laneBoundary_r.getZLineVector() )[l_searchIndexMinus] );
            }
            if( ( l_visibility > 0 ) != ( l_visibilityK1IndexMinus > 0 ) )
            {
                l_lineEndPoints[l_indexLineEndPoints] = l_searchIndexMinus;
                if( l_visibility == 0 )
                {
                    //l_lineEndPoints[l_indexLineEndPoints]++;
                    l_searchIndexMinus = -1;
                }
                else
                {
                    //the searchIndexPlus path is not relevant any more
                    l_searchIndexPlus = l_numberOfLanesReferencePoints;
                    l_searchIndexMinus--;
                }
                l_indexLineEndPoints++;
            }
            else
            {
                l_searchIndexMinus--;
            }
            if( l_searchIndexMinus < 0 )
            {
                if( l_visibility > 0 )
                {
                    l_lineEndPoints[l_indexLineEndPoints] = 0;//l_searchIndexMinus + 1;
                    l_indexLineEndPoints++;
                }
            }
            else
            {
                l_sPositionIndexMinus = ( *f_laneBoundary_r.getSLineVector() )[l_searchIndexMinus];
            }
            l_visibilityK1IndexMinus = l_visibility;
        }
    }
    //calculate intersection for index segments
    //simplification: one straight line between two neighbouring indices
    //findIntersectionWithLine() direkt an der Stelle einbauen ToDO
    if( l_indexLineEndPoints == 2 )
    {
        CFloat l_x1, l_y1, l_x2, l_y2, l_s2, l_sAdd;
        CInt l_startIndex = l_lineEndPoints[0];
        f_sStart = ( *f_laneBoundary_r.getSLineVector() )[l_startIndex];
        //l_s1 = ( *f_laneBoundary_r.getSLineVector() )[l_startIndex];
        l_x1 = ( *f_laneBoundary_r.getXLineVector() )[l_startIndex];
        l_y1 = ( *f_laneBoundary_r.getYLineVector() )[l_startIndex];
        l_s2 = ( *f_laneBoundary_r.getSLineVector() )[l_startIndex + 1];
        l_x2 = ( *f_laneBoundary_r.getXLineVector() )[l_startIndex + 1];
        l_y2 = ( *f_laneBoundary_r.getYLineVector() )[l_startIndex + 1];
        if( m_viewSegment_a[0].findIntersectionWithLine( 1, l_x1, l_y1, l_x2, l_y2, l_sAdd ) )
        {
            f_sStart += l_sAdd * ( l_s2 - f_sStart );
        }
        else if( m_viewSegment_a.rbegin()->findIntersectionWithLine( -1, l_x1, l_y1, l_x2, l_y2, l_sAdd ) )
        {
            f_sStart += l_sAdd * ( l_s2 - f_sStart );
        }
        CInt l_endIndex = l_lineEndPoints[1];
        f_sEnd = ( *f_laneBoundary_r.getSLineVector() )[l_endIndex];
        // l_endIndex + 1 is valid, else use endIndex directly
        if( l_endIndex < l_numberOfLanesReferencePoints - 1 )
        {
            //l_s1 = ( *f_laneBoundary_r.getSLineVector() )[l_endIndex];
            l_x1 = ( *f_laneBoundary_r.getXLineVector() )[l_endIndex];
            l_y1 = ( *f_laneBoundary_r.getYLineVector() )[l_endIndex];
            l_s2 = ( *f_laneBoundary_r.getSLineVector() )[l_endIndex + 1];
            l_x2 = ( *f_laneBoundary_r.getXLineVector() )[l_endIndex + 1];
            l_y2 = ( *f_laneBoundary_r.getYLineVector() )[l_endIndex + 1];
            if( m_viewSegment_a[0].findIntersectionWithLine( 1, l_x1, l_y1, l_x2, l_y2, l_sAdd ) )
            {
                f_sEnd += l_sAdd * ( l_s2 - f_sEnd );
            }
            else if( m_viewSegment_a.rbegin()->findIntersectionWithLine( -1, l_x1, l_y1, l_x2, l_y2, l_sAdd ) )
            {
                f_sEnd += l_sAdd * ( l_s2 - f_sEnd );
            }
            else
            {
                for( auto& it :  m_viewSegment_a )
                {
                    if( it.findIntersectionWithLine( 0, l_x1, l_y1, l_x2, l_y2, l_sAdd ) )
                    {
                        f_sEnd += l_sAdd * ( l_s2 - f_sEnd );
                        break;
                    }
                }
            }
        }
        return true;
    }
    return false;
}


////*********************************
//// CObstacleVideo
////*********************************
CObstacleVideo::CObstacleVideo()
{}

CObstacleVideo::~CObstacleVideo()
{}

CBool CObstacleVideo::updateObstacleMessages(
    // generic messages
    CInt& f_indexObstacle_r, CInt& f_typeObstacle_r, CInt& f_referenceSurfaceObstacle_r, CFloat& f_visibilityObstacle_r,
    CFloat& f_xSensorObstacle_r, CFloat& f_ySensorObstacle_r, CFloat& f_zSensorObstacle_r,
    CFloat& f_azimuthSensorObstacle_r, CFloat& f_yawAngleSensorObstacle_r,
    CFloat& f_heightSensorObstacle_r, CFloat& f_widthSensorObstacle_r, CFloat& f_lengthSensorObstacle_r,
    CFloat& f_vXSensorObstacle_r, CFloat& f_vYSensorObstacle_r, CFloat& f_vZSensorObstacle_r,
    CFloat& f_aXVehicleObstacle_r, CFloat& f_aYVehicleObstacle_r, CFloat& f_aZVehicleObstacle_r,
    CFloat& f_distanceSensorObstacle_r,
    CInt f_referenceSurfaceObstacleFixed,
    // CVideo specific messages
    CFloat& f_xWorldLeftEdgeObstacle_r, CFloat& f_yWorldLeftEdgeObstacle_r, CFloat& f_zWorldLeftEdgeObstacle_r,
    CFloat& f_xWorldRightEdgeObstacle_r, CFloat& f_yWorldRightEdgeObstacle_r, CFloat& f_zWorldRightEdgeObstacle_r,
    CFloat& f_xSensorLeftEdgeObstacle_r, CFloat& f_ySensorLeftEdgeObstacle_r, CFloat& f_zSensorLeftEdgeObstacle_r,
    CFloat& f_xSensorRightEdgeObstacle_r, CFloat& f_ySensorRightEdgeObstacle_r, CFloat& f_zSensorRightEdgeObstacle_r,
    CFloat& f_azimuthSensorLeftBorderObstacle_r,
    CFloat& f_azimuthSensorRightBorderObstacle_r
)
{
    // first, call parent's updateObstacleMessages() for generic messages
    CBool l_visible = false;
    l_visible = CObstacleSensor::updateObstacleMessages(
                    f_indexObstacle_r, f_typeObstacle_r, f_referenceSurfaceObstacle_r, f_visibilityObstacle_r,
                    f_xSensorObstacle_r, f_ySensorObstacle_r, f_zSensorObstacle_r,
                    f_azimuthSensorObstacle_r, f_yawAngleSensorObstacle_r,
                    f_heightSensorObstacle_r, f_widthSensorObstacle_r, f_lengthSensorObstacle_r,
                    f_vXSensorObstacle_r, f_vYSensorObstacle_r, f_vZSensorObstacle_r,
                    f_aXVehicleObstacle_r, f_aYVehicleObstacle_r, f_aZVehicleObstacle_r,
                    f_distanceSensorObstacle_r,
                    f_referenceSurfaceObstacleFixed
                );
    // then, update CVideo specific object output messages
    // std::cout << "l_visible: " << l_visible ;
    if( l_visible )
    {
        f_xWorldLeftEdgeObstacle_r = ( *m_xWorldContourPoint_p )[m_indexRelevantSide];
        f_yWorldLeftEdgeObstacle_r = ( *m_yWorldContourPoint_p )[m_indexRelevantSide];
        f_zWorldLeftEdgeObstacle_r = ( *m_zWorldContourPoint_p )[m_indexRelevantSide];
        f_xWorldRightEdgeObstacle_r = ( *m_xWorldContourPoint_p )[m_indexRelevantSideNext];
        f_yWorldRightEdgeObstacle_r = ( *m_yWorldContourPoint_p )[m_indexRelevantSideNext];
        f_zWorldRightEdgeObstacle_r = ( *m_zWorldContourPoint_p )[m_indexRelevantSideNext];
        f_xSensorLeftEdgeObstacle_r = m_xSensorContourPoint[m_indexRelevantSide];
        // std::cout << "  xSensorLeftEdge: " << f_xSensorLeftEdgeObstacle_r << std::endl;
        f_ySensorLeftEdgeObstacle_r = m_ySensorContourPoint[m_indexRelevantSide];
        f_zSensorLeftEdgeObstacle_r = m_zSensorContourPoint[m_indexRelevantSide];
        f_xSensorRightEdgeObstacle_r = m_xSensorContourPoint[m_indexRelevantSideNext];
        f_ySensorRightEdgeObstacle_r = m_ySensorContourPoint[m_indexRelevantSideNext];
        f_zSensorRightEdgeObstacle_r = m_zSensorContourPoint[m_indexRelevantSideNext];

        f_azimuthSensorLeftBorderObstacle_r = m_azimuthSensorContourPoint[m_indexRelevantSide]; // ::sim::atan2( m_ySensorContourPoint[m_indexRelevantSide], m_xSensorContourPoint[m_indexRelevantSide] );
        f_azimuthSensorRightBorderObstacle_r = m_azimuthSensorContourPoint[m_indexRelevantSideNext]; //::sim::atan2( m_ySensorContourPoint[m_indexRelevantSideNext], m_xSensorContourPoint[m_indexRelevantSideNext] );
    }
    else
    {
        //std::cout << std::endl;
        f_xWorldLeftEdgeObstacle_r = 0;
        f_yWorldLeftEdgeObstacle_r = 0;
        f_zWorldLeftEdgeObstacle_r = 0;
        f_xWorldRightEdgeObstacle_r = 0;
        f_yWorldRightEdgeObstacle_r = 0;
        f_zWorldRightEdgeObstacle_r = 0;
        f_xSensorLeftEdgeObstacle_r = 0;
        f_ySensorLeftEdgeObstacle_r = 0;
        f_zSensorLeftEdgeObstacle_r = 0;
        f_xSensorRightEdgeObstacle_r = 0;
        f_ySensorRightEdgeObstacle_r = 0;
        f_zSensorRightEdgeObstacle_r = 0;
        f_azimuthSensorLeftBorderObstacle_r = 0;
        f_azimuthSensorRightBorderObstacle_r = 0;
    }

    return l_visible;
}


//////*********************************
////// CLineVideo
//////*********************************
CLineVideo::CLineVideo():
    m_indexLine( 0 ),
    m_lineObject_p( nullptr ),
    m_typeLine( 0 ),
    m_arcLength( 0 ),
    m_xVideoLineStart( 0.0 ),
    m_yVideoLineStart( 0.0 ),
    m_zVideoLineStart( 0.0 ),
    m_gammaVideoLineStart( 0.0 ),
    m_xVideoLineEnd( 0.0 ),
    m_yVideoLineEnd( 0.0 ),
    m_zVideoLineEnd( 0.0 ),
    m_gammaVideoLineEnd( 0.0 ),
    m_xWorldLineStart( 0.0 ),
    m_yWorldLineStart( 0.0 ),
    m_zWorldLineStart( 0.0 ),
    m_dxWorldLineStart( 0.0 ),
    m_dyWorldLineStart( 0.0 ),
    m_dzWorldLineStart( 0.0 ),
    m_ddxWorldLineStart( 0.0 ),
    m_ddyWorldLineStart( 0.0 ),
    m_ddzWorldLineStart( 0.0 ),
    m_xWorldLineEnd( 0.0 ),
    m_yWorldLineEnd( 0.0 ),
    m_zWorldLineEnd( 0.0 ),
    m_dxWorldLineEnd( 0.0 ),
    m_dyWorldLineEnd( 0.0 ),
    m_dzWorldLineEnd( 0.0 ),
    m_ddxWorldLineEnd( 0.0 ),
    m_ddyWorldLineEnd( 0.0 ),
    m_ddzWorldLineEnd( 0.0 ),
    m_gammaWorldLineStart( 0.0 ),
    m_curvatureLineStart( 0.0 ),
    m_curvatureLineEnd( 0.0 ),
    m_curvatureDerivativeLineStart( 0.0 )
{

}

CLineVideo::~CLineVideo()
{

}

void CLineVideo::init()
{
    m_typeLine = 0;
    m_indexLine = 0;
}

void CLineVideo::init( CInt f_indexLine,
                       CFloat f_rollAngle, CFloat f_pitchAngle, CFloat f_yawAngle,
                       CFloat f_x, CFloat f_y, CFloat f_z,
                       CLine& f_line_r,
                       CFloat f_sStart, CFloat f_sEnd )
{
    m_indexLine = f_indexLine;
    m_lineObject_p = &f_line_r;
    m_typeLine = f_line_r.getType( ( f_sEnd - f_sStart ) / 2 + f_sStart );
    m_arcLength = f_sEnd - f_sStart;
    f_line_r.getXYZ( f_sStart, m_xWorldLineStart, m_yWorldLineStart, m_zWorldLineStart, m_dxWorldLineStart, m_dyWorldLineStart, m_dzWorldLineStart, m_ddxWorldLineStart, m_ddyWorldLineStart, m_ddzWorldLineStart );
    f_line_r.getXYZ( f_sEnd, m_xWorldLineEnd, m_yWorldLineEnd, m_zWorldLineEnd, m_dxWorldLineEnd, m_dyWorldLineEnd, m_dzWorldLineEnd, m_ddxWorldLineEnd, m_ddyWorldLineEnd, m_ddzWorldLineEnd );

    // Calculate START position & angle of line (video coordinates)
    m_xVideoLineStart = m_xWorldLineStart - f_x;
    m_yVideoLineStart = m_yWorldLineStart - f_y;
    m_zVideoLineStart = m_zWorldLineStart - f_z;
    ::sim::coordinateRotationInv( f_rollAngle, f_pitchAngle, f_yawAngle,
                           m_xVideoLineStart, m_yVideoLineStart, m_zVideoLineStart,
                           m_xVideoLineStart, m_yVideoLineStart, m_zVideoLineStart );
    m_gammaWorldLineStart = ::sim::atan2( m_dyWorldLineStart, m_dxWorldLineStart );
    if( m_arcLength < 0 )
    {
        m_gammaWorldLineStart += M_PI;
    }
    m_gammaVideoLineStart = m_gammaWorldLineStart - f_yawAngle;

    // Calculate END position & curvature of line (video coordinates)
    m_xVideoLineEnd = m_xWorldLineEnd - f_x;
    m_yVideoLineEnd = m_yWorldLineEnd - f_y;
    m_zVideoLineEnd = m_zWorldLineEnd - f_z;
    ::sim::coordinateRotationInv( f_rollAngle, f_pitchAngle, f_yawAngle,
                           m_xVideoLineEnd, m_yVideoLineEnd, m_zVideoLineEnd,
                           m_xVideoLineEnd, m_yVideoLineEnd, m_zVideoLineEnd );

    // curvature for curve given parametrically
    // absolute curvature is independent from the world or video coordinate system
    // reference: http://www.mathepedia.de/kruemmung.aspx
    CInt l_sig = ::sim::sig( m_arcLength );
    m_curvatureLineStart = l_sig * ( m_dxWorldLineStart * m_ddyWorldLineStart - m_ddxWorldLineStart * m_dyWorldLineStart ) /::sim::pow( ::sim::pow( m_dxWorldLineStart, 2 ) + ::sim::pow( m_dyWorldLineStart, 2 ), 3.0L / 2.0L );
    m_curvatureLineEnd = l_sig * ( m_dxWorldLineEnd * m_ddyWorldLineEnd - m_ddxWorldLineEnd * m_dyWorldLineEnd ) /::sim::pow( ::sim::pow( m_dxWorldLineEnd, 2 ) + ::sim::pow( m_dyWorldLineEnd, 2 ), 3.0L / 2.0L );
    m_curvatureDerivativeLineStart = l_sig * ( m_curvatureLineEnd - m_curvatureLineStart ) / m_arcLength;
}


void CLineVideo::init( CInt f_indexLine,
                       CFloat f_rollAngle, CFloat f_pitchAngle, CFloat f_yawAngle,
                       CFloat f_x, CFloat f_y, CFloat f_z,
                       CLine& f_firstLine_r,
                       CLine& f_secondLine_r,
                       CFloat f_sStart, CFloat f_sConnection, CFloat f_sEnd )
{
    m_indexLine = f_indexLine;
    // m_lineObject_p = &f_firstLine_r; // never used!
    m_typeLine = f_firstLine_r.getType( f_sStart ); // todo: type detection for two lines
    m_arcLength = f_sEnd + f_sConnection - f_sStart;
    f_firstLine_r.getXYZ( f_sStart, m_xWorldLineStart, m_yWorldLineStart, m_zWorldLineStart, m_dxWorldLineStart, m_dyWorldLineStart, m_dzWorldLineStart, m_ddxWorldLineStart, m_ddyWorldLineStart, m_ddzWorldLineStart );
    f_secondLine_r.getXYZ( f_sEnd, m_xWorldLineEnd, m_yWorldLineEnd, m_zWorldLineEnd, m_dxWorldLineEnd, m_dyWorldLineEnd, m_dzWorldLineEnd, m_ddxWorldLineEnd, m_ddyWorldLineEnd, m_ddzWorldLineEnd );

    // Calculate START position & angle of line (video coordinates)
    m_xVideoLineStart = m_xWorldLineStart - f_x;
    m_yVideoLineStart = m_yWorldLineStart - f_y;
    m_zVideoLineStart = m_zWorldLineStart - f_z;
    ::sim::coordinateRotationInv( f_rollAngle, f_pitchAngle, f_yawAngle,
                           m_xVideoLineStart, m_yVideoLineStart, m_zVideoLineStart,
                           m_xVideoLineStart, m_yVideoLineStart, m_zVideoLineStart );
    m_gammaWorldLineStart = ::sim::atan2( m_dyWorldLineStart, m_dxWorldLineStart );
    if( m_arcLength < 0 )
    {
        m_gammaWorldLineStart += M_PI;
    }
    m_gammaVideoLineStart = m_gammaWorldLineStart - f_yawAngle;

    // Calculate END position & curvature of line (video coordinates)
    m_xVideoLineEnd = m_xWorldLineEnd - f_x;
    m_yVideoLineEnd = m_yWorldLineEnd - f_y;
    m_zVideoLineEnd = m_zWorldLineEnd - f_z;
    ::sim::coordinateRotationInv( f_rollAngle, f_pitchAngle, f_yawAngle,
                           m_xVideoLineEnd, m_yVideoLineEnd, m_zVideoLineEnd,
                           m_xVideoLineEnd, m_yVideoLineEnd, m_zVideoLineEnd );

    // curvature for curve given parametrically
    // absolute curvature is independent from the world or video coordinate system
    // reference: http://www.mathepedia.de/kruemmung.aspx
    CInt l_sig = ::sim::sig( m_arcLength );
    m_curvatureLineStart = l_sig * ( m_dxWorldLineStart * m_ddyWorldLineStart - m_ddxWorldLineStart * m_dyWorldLineStart ) /::sim::pow( ::sim::pow( m_dxWorldLineStart, 2 ) + ::sim::pow( m_dyWorldLineStart, 2 ), 3.0L / 2.0L );
    m_curvatureLineEnd = l_sig * ( m_dxWorldLineEnd * m_ddyWorldLineEnd - m_ddxWorldLineEnd * m_dyWorldLineEnd ) /::sim::pow( ::sim::pow( m_dxWorldLineEnd, 2 ) + ::sim::pow( m_dyWorldLineEnd, 2 ), 3.0L / 2.0L );
    m_curvatureDerivativeLineStart = l_sig * ( m_curvatureLineEnd - m_curvatureLineStart ) / m_arcLength;
}

CInt CLineVideo::updateVideoLineMessages(
    CInt&    f_indexLine_r,
    CInt&    f_typeLine_r,
    CFloat&  f_arcLength,
    CFloat& f_xVideoLineStart,
    CFloat& f_yVideoLineStart,
    CFloat& f_zVideoLineStart,
    CFloat& f_gammaVideoLineStart,
    CFloat& f_xVideoLineEnd,
    CFloat& f_yVideoLineEnd,
    CFloat& f_zVideoLineEnd,
    CFloat& f_curvatureLineStart,
    CFloat& f_curvatureDerivativeLineStart
)
{
    f_indexLine_r = m_indexLine;
    f_typeLine_r = m_typeLine;
    f_arcLength = m_arcLength;
    f_xVideoLineStart = m_xVideoLineStart;
    f_yVideoLineStart = m_yVideoLineStart;
    f_zVideoLineStart = m_zVideoLineStart;
    f_gammaVideoLineStart = m_gammaVideoLineStart;
    f_xVideoLineEnd = m_xVideoLineEnd;
    f_yVideoLineEnd = m_yVideoLineEnd;
    f_zVideoLineEnd = m_zVideoLineEnd;
    f_curvatureLineStart = m_curvatureLineStart;
    f_curvatureDerivativeLineStart = m_curvatureDerivativeLineStart;
    return m_typeLine;
}

