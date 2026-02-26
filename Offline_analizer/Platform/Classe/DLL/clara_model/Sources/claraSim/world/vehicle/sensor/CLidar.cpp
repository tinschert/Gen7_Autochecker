/*******************************************************************************
@author Robert Erhart, ett2si (06.07.2016)
@copyright (c) Robert Bosch GmbH 2016-2024. All rights reserved.
*******************************************************************************/

#include "CLidar.h"


////*********************************
//// CLidar
////*********************************
CLidar::CLidar():
    // m_viewSegment_a( 0 ),
    m_obstacle_a( 0 )
{
    m_numberOfVerticesDynamic = 0;
    m_numberOfObstaclesDynamic = 0;
    m_numberOfObstaclesStatic = 0;
    m_numberOfVerticesStatic = 0;
    m_numberOfVertices = 0;
    p_maxNumberOfRelevantObstacles = 0;

    /* Initialization messages */
    p_anglesFieldOfViewSegments.setInit( ::sim::to_radians( {70, -70} ) ) ;
    p_maxRangesFieldOfViewSegments.setInit( CFloatVector( {200} ) );
    p_minRangesFieldOfViewSegments.setInit( CFloatVector( {1} ) );

    addMessageParameter( p_maxNumberOfVerticesPerObstacles, 20, CLidarDoc::p_maxNumberOfVerticesPerObstacles );
    addMessageParameter( p_angleSeparationSensor, 0.8 / 180 * M_PI, CLidarDoc::p_angleSeparationSensor );

    addMessageOutput( o_xWorldVertex, CFloatVector( 0.0, m_numberOfVertices ), CLidarDoc::o_xWorldVertex );
    addMessageOutput( o_yWorldVertex, CFloatVector( 0.0, m_numberOfVertices ), CLidarDoc::o_yWorldVertex );
    addMessageOutput( o_zWorldVertex, CFloatVector( 0.0, m_numberOfVertices ), CLidarDoc::o_zWorldVertex );

    addMessageOutput( o_xLidarVertex, CFloatVector( 0.0, m_numberOfVertices ), CLidarDoc::o_xLidarVertex );
    addMessageOutput( o_yLidarVertex, CFloatVector( 0.0, m_numberOfVertices ), CLidarDoc::o_yLidarVertex );
    addMessageOutput( o_zLidarVertex, CFloatVector( 0.0, m_numberOfVertices ), CLidarDoc::o_zLidarVertex );
    addMessageOutput( o_alphaLidarVertex, CFloatVector( 0.0, m_numberOfVertices ), CLidarDoc::o_alphaLidarVertex );
    addMessageOutput( o_dLidarVertex, CFloatVector( 0.0, m_numberOfVertices ), CLidarDoc::o_dLidarVertex );
    addMessageOutput( o_dvRadialVertex, CFloatVector( 0.0, m_numberOfVertices ), CLidarDoc::o_dvRadialVertex );
    addMessageOutput( o_dvLateralVertex, CFloatVector( 0.0, m_numberOfVertices ), CLidarDoc::o_dvLateralVertex );
    addMessageOutput( o_typeVertex, CIntVector( CInt(0), m_numberOfVertices ), CLidarDoc::o_typeVertex );
    addMessageOutput( o_visibilityVertex, CFloatVector( 0.0, m_numberOfVertices ), CLidarDoc::o_visibilityVertex );
    addMessageOutput( o_prioIndexVertex, CIntVector( CInt( 0 ), m_numberOfVertices ), CLidarDoc::o_prioIndexVertex );

    addMessageOutput( o_xWorldObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CLidarDoc::o_xWorldObstacle );
    addMessageOutput( o_yWorldObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CLidarDoc::o_yWorldObstacle );
    addMessageOutput( o_zWorldObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CLidarDoc::o_zWorldObstacle );

    addMessageOutput( o_dvLateralLidarObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CLidarDoc::o_dvLateralLidarObstacle );
    addMessageOutput( o_dvRadialLidarObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CLidarDoc::o_dvRadialLidarObstacle );
    addMessageOutput( o_prioIndexObstacle, CIntVector( CInt( 0 ), p_maxNumberOfRelevantObstacles ), CLidarDoc::o_prioIndexObstacle );
}

CLidar::~CLidar()
{}

void CLidar::init( IMessage<CFloatVectorXYZ>& f_xyzWorld,
                   IMessage<CFloatVectorXYZ>& f_velocityXYZWorld,
                   IMessage<CFloatVectorXYZ>& f_accelerationXYZVehicleEgo,
                   IMessage<CFloatVectorXYZ>& f_angleRollPitchYawEgo,
                   IMessage<CFloat>& f_yawRateEgo,
                   CObstacles& f_obstacles_r,
                   IMessage<CBool>& f_staticSimulation )
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
     * link input messages: all done inside CSensor
     */

    /* Initialization messages */
    initializationMessages();


    /* get pointer to obstacle array */
    m_numberOfObstaclesDynamic = f_obstacles_r.ObstacleDynamic.size();
    m_numberOfObstaclesStatic = f_obstacles_r.ObstacleStatic.size();
    m_numberOfVertices = p_maxNumberOfRelevantObstacles * p_maxNumberOfVerticesPerObstacles;
    p_maxNumberOfRelevantObstacles = p_maxNumberOfRelevantObstacles;



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
    // messages specific to CLidar
    o_xWorldObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_yWorldObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_zWorldObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_dvLateralLidarObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );
    o_dvRadialLidarObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );

    /*
     * Output messages: objects
     */
    o_xWorldVertex.init( CFloatVector( 0.0, m_numberOfVertices ) );
    o_yWorldVertex.init( CFloatVector( 0.0, m_numberOfVertices ) );
    o_zWorldVertex.init( CFloatVector( 0.0, m_numberOfVertices ) );
    o_visibilityVertex.init( CFloatVector( 0.0, m_numberOfVertices ) );
    o_xLidarVertex.init( CFloatVector( 0.0, m_numberOfVertices ) );
    o_yLidarVertex.init( CFloatVector( 0.0, m_numberOfVertices ) );
    o_zLidarVertex.init( CFloatVector( 0.0, m_numberOfVertices ) );
    o_alphaLidarVertex.init( CFloatVector( 0.0, m_numberOfVertices ) );
    o_dLidarVertex.init( CFloatVector( 0.0, m_numberOfVertices ) );
    o_dvRadialVertex.init( CFloatVector( 0.0, m_numberOfVertices ) );
    o_dvLateralVertex.init( CFloatVector( 0.0, m_numberOfVertices ) );
    o_typeVertex.init( CIntVector( CInt( 0 ), m_numberOfVertices ) );
    o_prioIndexVertex.init( CIntVector( CInt( 0 ), m_numberOfVertices ) );
    for( size_t index = 0; index < m_numberOfVertices; index++ )
    {
        o_prioIndexVertex[index] = m_numberOfVertices - index - 1;
    }

    //o_elevationAngleObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );

    o_xyzWorldSensor.init( p_xyzVehicleMountingPos + i_xyzWorldVehicle );
    o_rotationWorld.init( i_angleRollPitchYawVehicle + p_angleRollPitchYawVehicleMounting );

    o_prioIndexObstacle.init( CIntVector( CInt( 0 ), p_maxNumberOfRelevantObstacles ) );
    for( long int index = 0; index < p_maxNumberOfRelevantObstacles; index++ )
    {
        o_prioIndexObstacle[index] = p_maxNumberOfRelevantObstacles - index - 1;
    }

    //one virtual obstacle with visibility -1 at the end, avoiding segmentation fault for finding next relevant obstacle ~Z380
    m_obstacleDynamicVisibility.resize( m_numberOfObstaclesDynamic + 1, -1.0 );
    m_obstacleDynamicVisibilityIndexList.resize( m_numberOfObstaclesDynamic + 1, 0LL );
    for( uint32_t index = 0; index < m_obstacleDynamicVisibilityIndexList.size(); index++ )
    {
        m_obstacleDynamicVisibilityIndexList[index] = index;
    }
    m_obstacleStaticVisibility.resize( m_numberOfObstaclesStatic + 1, -1.0 );
    m_obstacleStaticVisibilityIndexList.resize( m_numberOfObstaclesStatic + 1, 0LL );
    for( uint32_t index = 0; index < m_obstacleStaticVisibilityIndexList.size(); index++ )
    {
        m_obstacleStaticVisibilityIndexList[index] = index;
    }

    m_obstacle_a.resize( p_maxNumberOfRelevantObstacles );
    m_viewSegment_a.resize( p_maxRangesFieldOfViewSegments.size() );

    if( p_maxNumberOfVerticesPerObstacles < 1 )
    {
        p_maxNumberOfVerticesPerObstacles.init( 1 );
        ::std::cerr << "WARNING <CLidar::init>: p_maxNumberOfVerticesPerObstacles < 0; Set to 1!!!" << ::std::endl;
    }
}

void CLidar::calc( CFloat f_dT, CFloat f_time )
{
    /* Call parent's calc for sensor coordinates, orientation, view segment output, and velocity from rotation. */
    CSensor::calc( f_dT, f_time );

    //simulate LIDAR measurement program
    if( ( p_sensorConfiguration != -1 or p_sensorConfiguration == 1 )
        and getExternTrigger() )
    {
        //get relevant object indices with priolist
        //for dynamic and static objects
        for( size_t l_idxObstacle = 0; l_idxObstacle < i_xyzWorldObstacleDynamic.size() ; l_idxObstacle++ )
        {
            if( i_typeObstacleStatic[l_idxObstacle] != 0 and i_visibilityObstacleStatic[l_idxObstacle] > 0 )
            {
                CFloat l_visibility = 0;
                for( auto& segment :  m_viewSegment_a )
                {
                    l_visibility = ::sim::max( l_visibility,
                                        segment.checkInRange( i_xWorldContourObstacleStatic[l_idxObstacle], i_yWorldContourObstacleStatic[l_idxObstacle], i_zWorldContourObstacleStatic[l_idxObstacle] )
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
                for( auto& segment :  m_viewSegment_a )
                {
                    l_visibility =
                        ::sim::max( l_visibility,
                                    segment.checkInRange( i_xWorldContourObstacleDynamic[l_idxObstacle], i_yWorldContourObstacleDynamic[l_idxObstacle], i_zWorldContourObstacleDynamic[l_idxObstacle] )
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

        // generate the relevant obstacle array and calculate the Vertices and object data
        CInt l_indexDynamic = 0;
        CInt l_indexStatic = 0;
        CFloat l_visibilityDynamic = m_obstacleDynamicVisibility[m_obstacleDynamicVisibilityIndexList[l_indexDynamic]];
        CFloat l_visibilityStatic = m_obstacleStaticVisibility[m_obstacleStaticVisibilityIndexList[l_indexStatic]];
        size_t l_indexVertex = 0;
        for( size_t index = 0; index < static_cast<size_t>(p_maxNumberOfRelevantObstacles); index++ )
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
                                          i_visibilityObstacleStatic[t_indexVisibility],
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
                                          i_visibilityObstacleDynamic[t_indexVisibility],
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
            l_indexVertex = m_obstacle_a[index].calcVertices( l_indexVertex, p_angleSeparationSensor, p_maxNumberOfVerticesPerObstacles,
                                                              o_xWorldVertex, o_yWorldVertex, o_zWorldVertex,
                                                              o_xLidarVertex, o_yLidarVertex, o_zLidarVertex, o_alphaLidarVertex,
                                                              o_dLidarVertex, o_dvRadialVertex, o_dvLateralVertex,
                                                              o_typeVertex, o_visibilityVertex );

            m_obstacle_a[index].updateObstacleMessages( o_indexObstacle[index], o_typeObstacle[index], o_referenceSurfaceObstacle[index], o_visibilityObstacle[index],
                                                        o_xSensorObstacle[index], o_ySensorObstacle[index], o_zSensorObstacle[index],
                                                        o_alphaSensorObstacle[index], o_yawAngleSensorObstacle[index],
                                                        o_heightSensorObstacle[index], o_widthSensorObstacle[index], o_depthSensorObstacle[index],
                                                        o_vXSensorObstacle[index], o_vYSensorObstacle[index], o_vZSensorObstacle[index],
                                                        o_aXVehicleObstacle[index], o_aYVehicleObstacle[index], o_aZVehicleObstacle[index],
                                                        o_distanceSensorObstacle[index],
                                                        p_referenceSurfaceObstacleFixed,
                                                        o_xWorldObstacle[index], o_yWorldObstacle[index], o_zWorldObstacle[index],
                                                        o_dvRadialLidarObstacle[index], o_dvLateralLidarObstacle[index] );
        }
        for( size_t index = l_indexVertex; index < m_numberOfVertices; index++ )
        {
            o_xWorldVertex[index] = 0;
            o_yWorldVertex[index] = 0;
            o_zWorldVertex[index] = 0;
            o_xLidarVertex[index] = 0;
            o_yLidarVertex[index] = 0;
            o_zLidarVertex[index] = 0;
            o_alphaLidarVertex[index] = 0;
            o_dLidarVertex[index] = 0;
            o_dvRadialVertex[index] = 0;
            o_dvLateralVertex[index] = 0;
            o_typeVertex[index] = 0;
            o_visibilityVertex[index] = 0;
        }

        // simulation over-the-air interface
        for( size_t index = 0; index < l_indexVertex; index++ )
        {
            //ToDo Verdeckung
            // object visibility?
            CFloat l_visibility = 0;
            for( auto& segment :  m_viewSegment_a )
            {
                l_visibility = segment.checkInRange( o_xWorldVertex[index], o_yWorldVertex[index], o_zWorldVertex[index] );
                if( l_visibility > 0 )
                {
                    break;
                }
            }
            if( l_visibility > 0 )
            {
                o_visibilityVertex[index] = o_visibilityVertex[index] / o_dLidarVertex[index];
            }
            else
            {
                o_visibilityVertex[index] = 0;
            }
        }
        // sort o_prioIndexObstacle array into descending order, use o_visibilityObstacle as comparison criterion
        heapSortWithComparsionCriterion( o_prioIndexVertex, o_visibilityVertex );
        heapSortWithComparsionCriterion( o_prioIndexObstacle, o_visibilityObstacle );
    }
}


////*********************************
//// CObstacleLidar
////*********************************
CObstacleLidar::CObstacleLidar()
{}

CObstacleLidar::~CObstacleLidar()
{}

CBool CObstacleLidar::updateObstacleMessages( CInt& f_indexObstacle_r, CInt& f_typeObstacle_r, CInt& f_referenceSurfaceObstacle_r, CFloat& f_visibilityObstacle_r,
                                              CFloat& f_xSensorObstacle_r, CFloat& f_ySensorObstacle_r, CFloat& f_zSensorObstacle_r,
                                              CFloat& f_azimuthSensorObstacle_r, CFloat& f_yawAngleSensorObstacle_r,
                                              CFloat& f_heightSensorObstacle_r, CFloat& f_widthSensorObstacle_r, CFloat& f_lengthSensorObstacle_r,
                                              CFloat& f_vXSensorObstacle_r, CFloat& f_vYSensorObstacle_r, CFloat& f_vZSensorObstacle_r,
                                              CFloat& f_aXVehicleObstacle_r, CFloat& f_aYVehicleObstacle_r, CFloat& f_aZVehicleObstacle_r,
                                              CFloat& f_distanceSensorObstacle_r,
                                              CInt f_referenceSurfaceObstacleFixed,
                                              CFloat& f_xWorldObstacle_r, CFloat& f_yWorldObstacle_r, CFloat& f_zWorldObstacle_r,
                                              CFloat& f_dvRadialLidar_r, CFloat& f_dvLateralLidar_r )
{
    // first, call parent's updateObstacleMessages() for generic messages,...
    CBool l_visible = false;
    l_visible = CObstacleSensor::updateObstacleMessages( f_indexObstacle_r, f_typeObstacle_r, f_referenceSurfaceObstacle_r, f_visibilityObstacle_r,
                                                         f_xSensorObstacle_r, f_ySensorObstacle_r, f_zSensorObstacle_r,
                                                         f_azimuthSensorObstacle_r, f_yawAngleSensorObstacle_r,
                                                         f_heightSensorObstacle_r, f_widthSensorObstacle_r, f_lengthSensorObstacle_r,
                                                         f_vXSensorObstacle_r, f_vYSensorObstacle_r, f_vZSensorObstacle_r,
                                                         f_aXVehicleObstacle_r, f_aYVehicleObstacle_r, f_aZVehicleObstacle_r,
                                                         f_distanceSensorObstacle_r,
                                                         f_referenceSurfaceObstacleFixed
                                                       );

    // ...then, update CLidar specific object outputs
    if( l_visible )
    {
        // TODO: WHY? "for current LIDAR sensors the width and depth is independent of reference surface"
        // -> overwrite here
        f_widthSensorObstacle_r = m_depthHeightWidthObstacle[2];
        f_lengthSensorObstacle_r = m_depthHeightWidthObstacle[0];

        f_xWorldObstacle_r = m_xyzWorldObstacle.X();
        f_yWorldObstacle_r = m_xyzWorldObstacle.Y();
        f_zWorldObstacle_r = m_xyzWorldObstacle.Z();

        // TODO: shouldn't we use "vx*WORLD*Obstacle - vxWorldSensor" to get dvXWorldObstacle?
        CFloat l_dvXWorldObstacle = m_vXYZSensorObstacle.X() - m_vXYZWorldSensor.X();
        CFloat l_dvYWorldObstacle = m_vXYZSensorObstacle.Y() - m_vXYZWorldSensor.Y();
        CFloat l_angle = m_yawAngle + f_azimuthSensorObstacle_r; //ToDo: yawAngle only valid for small pitch and roll angles
        f_dvRadialLidar_r  =  ::sim::cos( l_angle ) * l_dvXWorldObstacle + ::sim::sin( l_angle ) * l_dvYWorldObstacle;
        f_dvLateralLidar_r = -::sim::sin( l_angle ) * l_dvXWorldObstacle + ::sim::cos( l_angle ) * l_dvYWorldObstacle;
    }
    else
    {
        f_xWorldObstacle_r = 0;
        f_yWorldObstacle_r = 0;
        f_zWorldObstacle_r = 0;
        f_dvRadialLidar_r = 0;
        f_dvLateralLidar_r = 0;
    }
    return l_visible;
}


size_t CObstacleLidar::calcVertices( CInt f_startIndex, CFloat f_angleSeparation, CInt f_maxNoOfVerticesObstacle,
                                   CFloatVector& f_xWorldVertex, CFloatVector& f_yWorldVertex, CFloatVector& f_zWorldVertex,
                                   CFloatVector& f_xLidarVertex, CFloatVector& f_yLidarVertex, CFloatVector& f_zLidarVertex, CFloatVector& f_alphaLidarVertex,
                                   CFloatVector& f_dLidarVertex, CFloatVector& f_dvRadialVertex, CFloatVector& f_dvLateralVertex,
                                   CIntVector& f_typeVertex, CFloatVector& f_visibilityVertex )
{
    size_t l_indexVertex = f_startIndex;
    if( m_visibilityObstacle > 0 and m_typeObstacle != EObstacleTyp::INVISIBLE )
    {
        CFloat l_minDistance = ::sim::sin( f_angleSeparation ) * m_dSensorContourPoint[m_indexNearestPoint];//only a rough estimation
        CFloat l_contourLength = 0;
        for( CInt l_contourIndex : m_contourPoints_a )
        {
            l_contourLength += ::sim::sqrt( ::sim::pow( m_xWorldContourLine[l_contourIndex], 2 ) + ::sim::pow( m_yWorldContourLine[l_contourIndex], 2 ) + ::sim::pow( m_zWorldContourLine[l_contourIndex], 2 ) );
        }
        CInt l_maxNoOfVerticesPerMinDistance = static_cast<CInt>(::sim::max( l_contourLength / l_minDistance, 1.0L ));
        CFloat l_drContour = 2.0L / ::sim::min( l_maxNoOfVerticesPerMinDistance, f_maxNoOfVerticesObstacle );
        CFloat l_factor = ( m_rMainReference - m_rMin ) / l_drContour;
        CFloat l_rMinNew = m_rMainReference - ::sim::floor( l_factor ) * l_drContour;

        CInt l_contourIndex = 0;
        CFloat l_r =  l_rMinNew;
        while( l_r <= 1 )
        {
            CFloat t_r = l_r;
            if( t_r < 0 )
            {
                l_contourIndex = m_contourPoints_a[1];
                t_r = 1 + t_r;
            }
            else
            {
                l_contourIndex = m_contourPoints_a[0];
            }
            //P = A + r*AB
            //WORLD coordinates
            f_xWorldVertex[l_indexVertex] = ( *m_xWorldContourPoint_p )[l_contourIndex] + t_r * m_xWorldContourLine[l_contourIndex];
            f_yWorldVertex[l_indexVertex] = ( *m_yWorldContourPoint_p )[l_contourIndex] + t_r * m_yWorldContourLine[l_contourIndex];
            f_zWorldVertex[l_indexVertex] = ( *m_zWorldContourPoint_p )[l_contourIndex] + t_r * m_zWorldContourLine[l_contourIndex];
            //f_alphaWorldVertex[l_indexVertex] = ::sim::atan2( f_yWorldVertex[l_indexVertex], f_xWorldVertex[l_indexVertex] );
            //Lidar coordinates
            f_xLidarVertex[l_indexVertex] = m_xSensorContourPoint[l_contourIndex] + t_r * m_xSensorContourLine[l_contourIndex];
            f_yLidarVertex[l_indexVertex] = m_ySensorContourPoint[l_contourIndex] + t_r * m_ySensorContourLine[l_contourIndex];
            f_zLidarVertex[l_indexVertex] = m_zSensorContourPoint[l_contourIndex] + t_r * m_zSensorContourLine[l_contourIndex];
            f_alphaLidarVertex[l_indexVertex] = ::sim::atan2( f_yLidarVertex[l_indexVertex], f_xLidarVertex[l_indexVertex] );

            f_dLidarVertex[l_indexVertex] = ::sim::sqrt( ::sim::pow( f_xLidarVertex[l_indexVertex], 2 ) + ::sim::pow( f_yLidarVertex[l_indexVertex], 2 ) + ::sim::pow( f_zLidarVertex[l_indexVertex], 2 ) );

            CFloat l_dvXWorldObstacleVertex = m_vXYZWorldObstacle.X() - m_vXYZWorldSensor.X();  //ToDo: consider yawRate obstacle
            CFloat l_dvYWorldObstacleVertex = m_vXYZWorldObstacle.Y() - m_vXYZWorldSensor.Y();  //ToDo: consider yawRate obstacle
            //ToDo m_vz
            CFloat l_angle = m_yawAngle + f_alphaLidarVertex[l_indexVertex]; //ToDo: yawAngle only valid for small pitch and roll angles
            f_dvRadialVertex[l_indexVertex]  =  ::sim::cos( l_angle ) * l_dvXWorldObstacleVertex + ::sim::sin( l_angle ) * l_dvYWorldObstacleVertex;
            f_dvLateralVertex[l_indexVertex] = -::sim::sin( l_angle ) * l_dvXWorldObstacleVertex + ::sim::cos( l_angle ) * l_dvYWorldObstacleVertex;
            f_typeVertex[l_indexVertex] = m_typeObstacle;
            f_visibilityVertex[l_indexVertex] = m_visibilityObstacle;
            l_r += l_drContour;
            l_indexVertex++;
        }
    }
    return l_indexVertex;
}

