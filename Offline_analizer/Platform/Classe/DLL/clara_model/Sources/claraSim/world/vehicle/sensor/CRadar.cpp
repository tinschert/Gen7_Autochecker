/*******************************************************************************
@author Andreas Brunner, bnr2lr
@author Robert Erhart, ett2si (08.07.2005 - 11:17:38; 19.03.2007; 31.05.2016)
@copyright (c) Robert Bosch GmbH 2005-2024. All rights reserved.
*******************************************************************************/

#include "CRadar.h"
#include <cassert>


////*********************************
//// CRadar
////*********************************
CRadar::CRadar():
    m_obstacle_a( 0 ),
    NormalRCS( 0.0, 1.0 )
{
    m_numberOfReflectionsDynamic = 0;
    m_numberOfLocations = 0;
    m_numberOfObstaclesDynamic = 0;
    m_numberOfObstaclesStatic = 0;
    m_numberOfReflectionsStatic = 0;
    m_numberOfReflectionsSum = 0;
    m_numberOfLocations = 0;
    m_counter = 0;

    /* Initialization messages */
    // approximate parameters for CR5CP radar
    p_anglesFieldOfViewSegments.setInit( ::sim::to_radians( {+55, +30, +6, -6, -30, -55} ) );
    p_maxRangesFieldOfViewSegments.setInit( {15., 70., 150., 70., 15.} );
    p_minRangesFieldOfViewSegments.setInit( CFloatVector( 0.1, 5 ) );

    addMessageParameter( p_xRadarVehicleOffset, 0.0, CRadarDoc::p_xRadarVehicleOffset );
    addMessageParameter( p_yRadarVehicleOffset, 0.0, CRadarDoc::p_yRadarVehicleOffset );
    addMessageParameter( p_vObstacleRadarOffset, 0.0, CRadarDoc::p_vObstacleRadarOffset );
    addMessageParameter( p_closeRange, 30.0, CRadarDoc::p_closeRange );
    addMessageParameter( p_meanPowerIndDuty, 5, CRadarDoc::p_meanPowerIndDuty );
    addMessageParameter( p_meanPowerIndCycle, 5, CRadarDoc::p_meanPowerIndCycle );
    addMessageParameter( p_maxNumberOfReflectionsPerObstacles, 6, CRadarDoc::p_maxNumberOfReflectionsPerObstacles );

    addMessageParameter( p_vehicleRcsBaseLocation, 20.0, CRadarDoc::p_vehicleRcsBaseLocation );
    addMessageParameter( p_vehicleRcsDistanceFactor, 0.0, CRadarDoc::p_vehicleRcsDistanceFactor );
    addMessageParameter( p_vehicleDeltaRcsUpLocation, -8.0, CRadarDoc::p_vehicleDeltaRcsUpLocation );

    addMessageParameter( p_pedRcsBaseLocation, -1.0, CRadarDoc::p_pedRcsBaseLocation );
    addMessageParameter( p_pedRcsDistanceFactor, 0.0, CRadarDoc::p_pedRcsDistanceFactor );
    addMessageParameter( p_pedDeltaRcsUpLocation, 0.0, CRadarDoc::p_pedDeltaRcsUpLocation );

    addMessageParameter( p_angleSeparationSensor, 7.0 / 180 * M_PI, CRadarDoc::p_angleSeparationSensor );
    addMessageParameter( p_probHasBeenObservedMoving, CFloatVector( 0.99, p_maxNumberOfRelevantObstacles ), CRadarDoc::p_probHasBeenObservedMoving );
    addMessageParameter( p_dirAngleVar, CFloatVector( 0.001, p_maxNumberOfRelevantObstacles ), CRadarDoc::p_dirAngleVar );
    addMessageParameter( p_xVar, CFloatVector( 0.001, p_maxNumberOfRelevantObstacles ), CRadarDoc::p_xVar );
    addMessageParameter( p_yVar, CFloatVector( 0.001, p_maxNumberOfRelevantObstacles ), CRadarDoc::p_yVar );
    addMessageParameter( p_spdXVar, CFloatVector( 0.001, p_maxNumberOfRelevantObstacles ), CRadarDoc::p_spdXVar );
    addMessageParameter( p_spdYVar, CFloatVector( 0.001, p_maxNumberOfRelevantObstacles ), CRadarDoc::p_spdYVar );

    addMessageOutput( o_xWorldReflection, CFloatVector( 0.0, m_numberOfReflectionsSum ), CRadarDoc::o_xWorldReflection );
    addMessageOutput( o_yWorldReflection, CFloatVector( 0.0, m_numberOfReflectionsSum ), CRadarDoc::o_yWorldReflection );
    addMessageOutput( o_zWorldReflection, CFloatVector( 0.0, m_numberOfReflectionsSum ), CRadarDoc::o_zWorldReflection );
    addMessageOutput( o_visibilityReflection, CFloatVector( 0.0, m_numberOfReflectionsSum ), CRadarDoc::o_visibilityReflection );

    addMessageOutput( o_xRadarLocation, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_xRadarLocation );
    addMessageOutput( o_yRadarLocation, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_yRadarLocation );
    addMessageOutput( o_zRadarLocation, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_zRadarLocation );
    addMessageOutput( o_alphaRadarLocation, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_alphaRadarLocation );
    addMessageOutput( o_distanceLocation, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_distanceLocation );
    addMessageOutput( o_visibilityLocation, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_visibilityLocation );

    addMessageOutput( o_vLateralRadarLocation, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_vLateralRadarLocation );
    addMessageOutput( o_vRadialRadarLocation, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_vRadialRadarLocation );
    addMessageOutput( o_rcsCenterLocation, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_rcsCenterLocation );
    addMessageOutput( o_rcsUpLocation, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_rcsUpLocation );
    addMessageOutput( o_elevationAngleLocation, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_elevationAngleLocation );
    addMessageOutput( o_prioIndexLocation, CIntVector( CInt( 0 ), m_numberOfLocations ), CRadarDoc::o_prioIndexLocation );
    addMessageOutput( o_meanPowerInd, CIntVector( CInt( 0 ), m_numberOfLocations ), CRadarDoc::o_meanPowerInd );
    addMessageOutput( o_elevationInd, CIntVector( CInt( 0 ), m_numberOfLocations ), CRadarDoc::o_elevationInd );
    addMessageOutput( o_multipathInd, CIntVector( CInt( 0 ), m_numberOfLocations ), CRadarDoc::o_multipathInd );
    addMessageOutput( o_detectionInd, CIntVector( CInt( 0 ), m_numberOfLocations ), CRadarDoc::o_detectionInd );
    addMessageOutput( o_microDopplerPwr, CFloatVector( 0.0, m_numberOfLocations ), CRadarDoc::o_microDopplerPwr );
    //objects
    addMessageOutput( o_yawAngleEgoObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CRadarDoc::o_yawAngleEgoObstacle );

}

CRadar::~CRadar()
{}

/***********************************************************************
 * CRadar takes ego position, velocity, and rotation as input messages.
 *
 * Additionally, obstacle information is given via the 'f_obstacles_r'
 * CObstacles object. It contains vectors of static and dynamic obstacles.
 * Obstacle properties are extracted from these CObstacles and bound to
 * CRadar's input messages.
 *
 ***********************************************************************/


void CRadar::init( IMessage<CFloatVectorXYZ>& f_xyzWorld,
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
    m_numberOfReflectionsSum = p_maxNumberOfRelevantObstacles * p_maxNumberOfReflectionsPerObstacles;
    m_numberOfLocations = ( m_numberOfReflectionsSum ) * 2; //double reflections

    m_xRadarReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new
    m_yRadarReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new
    m_zRadarReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new
    m_alphaRadarReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new
    m_dRadarReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new
    m_typReflection.resize( m_numberOfReflectionsSum, 0 ); //new
    m_heightReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new
    //m_visibilityReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new
    m_vxWorldReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new
    m_vyWorldReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new
    m_vzWorldReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new
    m_dvRadialReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new
    m_dvLateralReflection.resize( m_numberOfReflectionsSum, 0.0 ); //new


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
    // messages specific to CRadar
    o_yawAngleEgoObstacle.init( CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ) );

    /*
     * Output messages: reflections
     */
    o_xWorldReflection.init( CFloatVector( 0.0, m_numberOfReflectionsSum ) );
    o_yWorldReflection.init( CFloatVector( 0.0, m_numberOfReflectionsSum ) );
    o_zWorldReflection.init( CFloatVector( 0.0, m_numberOfReflectionsSum ) );
    o_visibilityReflection.init( CFloatVector( 0.0, m_numberOfReflectionsSum ) );

    /*
     * Output messages: locations
     */
    o_xRadarLocation.init( CFloatVector( 0.0, m_numberOfLocations ) );
    o_yRadarLocation.init( CFloatVector( 0.0, m_numberOfLocations ) );
    o_zRadarLocation.init( CFloatVector( 0.0, m_numberOfLocations ) );
    o_alphaRadarLocation.init( CFloatVector( 0.0, m_numberOfLocations ) );
    o_distanceLocation.init( CFloatVector( 0.0, m_numberOfLocations ) );
    o_vLateralRadarLocation.init( CFloatVector( 0.0, m_numberOfLocations ) );
    o_vRadialRadarLocation.init( CFloatVector( 0.0, m_numberOfLocations ) );
    o_visibilityLocation.init( CFloatVector( 0.0, m_numberOfLocations ) );
    o_rcsCenterLocation.init( CFloatVector( 0.0, m_numberOfLocations ) );
    o_rcsUpLocation.init( CFloatVector( 0.0, m_numberOfLocations ) );
    o_elevationAngleLocation.init( CFloatVector( 0.0, m_numberOfLocations ) );
    o_prioIndexLocation.init( CIntVector( CInt( 0 ), m_numberOfLocations ) );
    o_meanPowerInd.init( CIntVector( CInt( 0 ), m_numberOfLocations ) );
    o_elevationInd.init( CIntVector( CInt( 0 ), m_numberOfLocations ) );
    o_multipathInd.init( CIntVector( CInt( 0 ), m_numberOfLocations ) );
    o_detectionInd.init( CIntVector( CInt( 0 ), m_numberOfLocations ) );
    o_microDopplerPwr.init( CFloatVector( 0.0, m_numberOfLocations ) );
    // priority of the locations will be updated in 'calc' later
    for( long int index = 0; index < m_numberOfLocations; index++ )
    {
        o_prioIndexLocation[index] = index;
    }


    /*
     * Member variables
     */
    m_counter = 1;

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

    if( p_maxNumberOfReflectionsPerObstacles < 1 )
    {
        p_maxNumberOfReflectionsPerObstacles.init( 1 );
        ::std::cerr << "Error <CRadar::init>: p_maxNumberOfReflectionsPerObstacles < 1; Set to 1 instead!!!" << ::std::endl;
    }

}


void CRadar::calc( CFloat f_dT, CFloat f_time )
{
    if( p_angleRollPitchYawVehicleMounting[0] != 0 )
    {
        ::std::cerr << "ERROR <CRadar::calc> rotation over x-axis not supported!" << ::std::endl;
    }

    /* Call parent's calc for sensor coordinates, orientation, view segment output, and velocity from rotation. */
    CSensor::calc( f_dT, f_time );

    m_counter = ( m_counter < p_meanPowerIndCycle ? m_counter + 1 : 1 );

    //simulate radar measurement program
    if( ( p_sensorConfiguration == -1 or p_sensorConfiguration == 1 )
        and getExternTrigger() )
    {
        /*
         * Calculate visibilities and update IndexList for static and dynamic obstacles, respectively.
         * First, iterate through static objects.
         */
        for( size_t l_index = 0; l_index < i_xyzWorldObstacleStatic.size() ; l_index++ )
        {
            CFloat l_visibility = 0.0; // standard for EObstacleTyp::INVISIBLE type or visibility = 0 obstacles
            /* now, change l_visibility for other type and visibility > 0 obstacles */
            if( i_typeObstacleStatic[l_index] != 0 and i_visibilityObstacleStatic[l_index] > 0 )
            {
                for( auto& segment :  m_viewSegment_a ) // loop through segments, retrieve maximum visibility
                {
                    l_visibility = ::sim::max( l_visibility, segment.checkInRange( i_xWorldContourObstacleStatic[l_index], i_yWorldContourObstacleStatic[l_index], i_zWorldContourObstacleStatic[l_index] ) );
                }
            }
            m_obstacleStaticVisibility[l_index] = l_visibility; // set static object visibility
        }
        /* update sorted index list according to calculated visibilities */
        heapSortWithComparsionCriterion( m_obstacleStaticVisibilityIndexList, m_obstacleStaticVisibility );

        /*
         * Now, iterate through dynamic objects.
         */
        for( size_t l_index = 0; l_index < i_xyzWorldObstacleDynamic.size() ; l_index++ )
        {
            CFloat l_visibility = 0.0; // standard for EObstacleTyp::INVISIBLE type or visibility = 0 obstacles
            /* now, change l_visibility for other type and visibility > 0 obstacles */
            if( i_typeObstacleDynamic[l_index] != 0 and i_visibilityObstacleDynamic[l_index] > 0 )
            {
                for( auto& segment :  m_viewSegment_a ) // loop through segments, retrieve maximum visibility
                {
                    l_visibility = ::sim::max( l_visibility, segment.checkInRange( i_xWorldContourObstacleDynamic[l_index], i_yWorldContourObstacleDynamic[l_index], i_zWorldContourObstacleDynamic[l_index] ) );
                }
            }
            m_obstacleDynamicVisibility[l_index] = l_visibility; // set dynamic object visibility
        }
        /* update sorted index list according to calculated visibilities */
        heapSortWithComparsionCriterion( m_obstacleDynamicVisibilityIndexList, m_obstacleDynamicVisibility );

        /*
         * Loop through the 'maxNumberOfRelevantObstacles' most relevant obstacles,
         * update the respective entries in 'm_obstacle_a', and calculate reflection
         * and obstacle properties.
         * m_obstacle_a is sorted by visibility, irrespective of the static/dynamic character
         * of obstacles.
         */
        CInt l_indexDynamic = 0;
        CInt l_indexStatic = 0;
        CInt l_indexReflection = 0;
        for( CInt index = 0; index < p_maxNumberOfRelevantObstacles; index++ )
        {
            CFloat l_visibilityDynamic = m_obstacleDynamicVisibility[m_obstacleDynamicVisibilityIndexList[l_indexDynamic]];
            CFloat l_visibilityStatic = m_obstacleStaticVisibility[m_obstacleStaticVisibilityIndexList[l_indexStatic]];
            if( l_visibilityStatic > 0 and l_visibilityStatic > l_visibilityDynamic and i_staticSimulation == false )
            {
                // Static obstacle, but simulation not set to static:
                //  - set negative obstacle index
                //  - set obstacle velocities and acceleration = 0
                CInt t_indexVisibility = m_obstacleStaticVisibilityIndexList[l_indexStatic];

                m_obstacle_a[index].init( -t_indexVisibility - 1,
                                          o_xyzWorldSensor,
                                          m_velocityXYZWorldSensor,
                                          i_aWorldVehicle,
                                          i_angleRollPitchYawVehicle,
                                          p_angleRollPitchYawVehicleMounting,
                                          i_xyzWorldObstacleStatic[t_indexVisibility],
                                          CFloatVectorXYZ( 0.0, 0.0, 0.0 ), // velocity
                                          0, // acceleration (obstacle x direction)
                                          i_yawAngleObstacleStatic[t_indexVisibility],
                                          i_typeObstacleStatic[t_indexVisibility],
                                          CFloatVector( { i_depthObstacleStatic[t_indexVisibility], i_heightObstacleStatic[t_indexVisibility], i_widthObstacleStatic[t_indexVisibility] } ),
                                          i_visibilityObstacleStatic[t_indexVisibility],
                                          i_xWorldContourObstacleStatic[t_indexVisibility], i_yWorldContourObstacleStatic[t_indexVisibility], i_zWorldContourObstacleStatic[t_indexVisibility] );

                m_obstacle_a[index].calcProperties();

                l_indexStatic++;
            }
            else if( l_visibilityDynamic > 0 )
            {
                //  Dynamic obstacle:
                //   - set positive obstacle index
                //   - pass current obstacle velocities and acceleration
                CInt t_indexVisibility = m_obstacleDynamicVisibilityIndexList[l_indexDynamic];

                m_obstacle_a[index].init( t_indexVisibility + 1,
                                          o_xyzWorldSensor,
                                          m_velocityXYZWorldSensor,
                                          i_aWorldVehicle,
                                          i_angleRollPitchYawVehicle,
                                          p_angleRollPitchYawVehicleMounting,
                                          i_xyzWorldObstacleDynamic[t_indexVisibility],
                                          i_vWorldObstacleDynamic[t_indexVisibility], // CFloatVector( { i_vxWorldObstacleDynamic[t_indexVisibility], i_vyWorldObstacleDynamic[t_indexVisibility], i_vzWorldObstacleDynamic[t_indexVisibility] } ),
                                          i_aObstacleDynamic[t_indexVisibility],
                                          i_yawAngleObstacleDynamic[t_indexVisibility],
                                          i_typeObstacleDynamic[t_indexVisibility],
                                          CFloatVector( { i_depthObstacleDynamic[t_indexVisibility], i_heightObstacleDynamic[t_indexVisibility], i_widthObstacleDynamic[t_indexVisibility] } ),
                                          i_visibilityObstacleDynamic[t_indexVisibility],
                                          i_xWorldContourObstacleDynamic[t_indexVisibility], i_yWorldContourObstacleDynamic[t_indexVisibility], i_zWorldContourObstacleDynamic[t_indexVisibility] );

                m_obstacle_a[index].calcProperties();

                l_indexDynamic++;
            }
            else
            {
                // Invalid or invisible obstacle:
                // - set index and visibility to zero
                m_obstacle_a[index].init();
            }

            /*
             * Calculate reflections and update CRadar reflection member variables
             * for further processing below.
             */
            l_indexReflection = m_obstacle_a[index].calcReflections( l_indexReflection, p_angleSeparationSensor, p_maxNumberOfReflectionsPerObstacles,
                                                                     o_xWorldReflection, o_yWorldReflection, o_zWorldReflection,
                                                                     m_xRadarReflection, m_yRadarReflection, m_zRadarReflection, m_alphaRadarReflection,
                                                                     m_dRadarReflection, m_heightReflection,
                                                                     m_vxWorldReflection, m_vyWorldReflection, m_vzWorldReflection,
                                                                     m_dvRadialReflection, m_dvLateralReflection,
                                                                     m_typReflection, o_visibilityReflection );
            /*
             * Update obstacle output messages
             */
            m_obstacle_a[index].updateObstacleMessages( o_indexObstacle[index], o_typeObstacle[index], o_referenceSurfaceObstacle[index], o_visibilityObstacle[index],
                                                        o_xSensorObstacle[index], o_ySensorObstacle[index], o_zSensorObstacle[index],
                                                        o_alphaSensorObstacle[index], o_yawAngleSensorObstacle[index],
                                                        o_heightSensorObstacle[index], o_widthSensorObstacle[index], o_depthSensorObstacle[index],
                                                        o_vXSensorObstacle[index], o_vYSensorObstacle[index], o_vZSensorObstacle[index],
                                                        o_aXVehicleObstacle[index], o_aYVehicleObstacle[index], o_aZVehicleObstacle[index],
                                                        o_distanceSensorObstacle[index],
                                                        p_referenceSurfaceObstacleFixed,
                                                        o_yawAngleEgoObstacle[index]
                                                      );
        }

        /*
         * Fill unused reflections with zeros.
         */
        for( CInt index = l_indexReflection; index < m_numberOfReflectionsSum; index++ )
        {
            o_xWorldReflection[index] = 0;
            o_yWorldReflection[index] = 0;
            o_zWorldReflection[index] = 0;
            m_xRadarReflection[index] = 0;
            m_yRadarReflection[index] = 0;
            m_zRadarReflection[index] = 0;
            m_alphaRadarReflection[index] = 0;
            m_dRadarReflection[index] = 0;
            m_heightReflection[index] = 0;
            m_vxWorldReflection[index] = 0;
            m_vyWorldReflection[index] = 0;
            m_vzWorldReflection[index] = 0;
            m_dvRadialReflection[index] = 0;
            m_dvLateralReflection[index] = 0;
            m_typReflection[index] = 0;
            o_visibilityReflection[index] = 0;
        }

        /*
         * Now, we calculate two locations per reflection and update output messages.
         * Ultimately, update visibility-sorting of locations (heapsort).
         *
         * TODO This calculation is very lengthy; consider rewriting/wrapping into
         * separate function
         */
        // simulation over-the-air
        for( long int indexReflection = 0; indexReflection < m_numberOfReflectionsSum ; indexReflection ++ )
        {
            long long int l_indexLocation = indexReflection * 2;
            //main reflection
            o_xRadarLocation[l_indexLocation] = m_xRadarReflection[indexReflection];
            o_yRadarLocation[l_indexLocation] = m_yRadarReflection[indexReflection];
            o_zRadarLocation[l_indexLocation] = m_zRadarReflection[indexReflection];

            // error offset
            o_xRadarLocation[l_indexLocation] = o_xRadarLocation[l_indexLocation] + p_xRadarVehicleOffset;
            o_yRadarLocation[l_indexLocation] = o_yRadarLocation[l_indexLocation] + p_yRadarVehicleOffset;

            o_distanceLocation[l_indexLocation] = m_dRadarReflection[indexReflection];

            if( o_distanceLocation[l_indexLocation] > 0 )
            {
                long double l_xDelta = ::sim::sqrt( ::sim::pow( o_distanceLocation[l_indexLocation], 2 ) + ( ::sim::pow( m_heightReflection[indexReflection] / 2.0 + p_xyzVehicleMountingPos[2], 2 ) ) ) - o_distanceLocation[l_indexLocation];
                long double l_lamda = 299792458 / ( 76.5 * ::sim::pow( 10, 9 ) ) / 2; //halbe Wellenlänge
                long double l_factor = ( ( ( ::sim::fmod( l_xDelta, l_lamda ) ) / l_lamda ) - 0.5 ); //factor [-0.5;0.5] to be considered by 2.0 * m_heightReflection/2.0
                if( ( m_typReflection[indexReflection ] == EObstacleTyp::PEDESTRIAN ) || ( m_typReflection[indexReflection] == EObstacleTyp::BICYCLE ) )
                {
                    l_factor *= 1.8;
                }
                else
                {
                    l_factor *= 0.8;
                }
                long double numerator = o_zRadarLocation[l_indexLocation] + l_factor * m_heightReflection[indexReflection];
                long double divisor = o_distanceLocation[l_indexLocation];
                
                // divisor is always positive as this is the "distance". That is checked some lines before in an if.
                long double result = 1.0;

                // check the numerator vs divisor
                // if the numerator is bigger than the divisor 
                // then set the result to -1 or 1 as the asin is only defined in [-1, 1]
                // otherwise set the result to numerator / divisor
                if (numerator > divisor)
                {
                    result = 1.0;
                }
                else if (numerator < -divisor)
                {
                    result = -1.0;
                }
                else
                {
                    result = numerator / divisor;
                }

                o_elevationAngleLocation[l_indexLocation] = ::sim::max( ::sim::min( ::std::asin(result), 25.0L / 180.0L * M_PI), -25.0L / 180.0L * M_PI);

                // check for NaN
                assert(o_elevationAngleLocation[l_indexLocation] == o_elevationAngleLocation[l_indexLocation] );
            }
            else
            {
                o_elevationAngleLocation[l_indexLocation] = M_PI;
            }
            o_alphaRadarLocation[l_indexLocation] = m_alphaRadarReflection[indexReflection];

            // obstacle info
            if( i_staticSimulation == false )
            {
                o_vLateralRadarLocation[l_indexLocation] = m_dvLateralReflection[indexReflection];
                o_vRadialRadarLocation[l_indexLocation]  = m_dvRadialReflection[indexReflection] + p_vObstacleRadarOffset;
            }
            else
            {
                o_vLateralRadarLocation[l_indexLocation] = 0;
                o_vRadialRadarLocation[l_indexLocation]  = 0 + p_vObstacleRadarOffset;
            }

            // object visibility?
            CFloat l_visibility = 0;
            for( auto& segment :  m_viewSegment_a )
            {
                l_visibility = segment.checkInRange( o_xWorldReflection[indexReflection], o_yWorldReflection[indexReflection], o_zWorldReflection[indexReflection] );
                if( l_visibility > 0 )
                {
                    break;
                }
            }
            if(
                ( l_visibility > 0 )
            )
            {
                if( m_dRadarReflection[indexReflection] > 1 )
                {
                    o_visibilityLocation[l_indexLocation] = o_visibilityReflection[indexReflection] / m_dRadarReflection[indexReflection];
                }
                else
                {
                    o_visibilityLocation[l_indexLocation] = o_visibilityReflection[indexReflection];
                }
                CFloat l_mdPwrEgo = 0.0;
                if( ( m_typReflection[indexReflection ] == EObstacleTyp::PEDESTRIAN ) || ( m_typReflection[indexReflection] == EObstacleTyp::BICYCLE ) )
                {
                    //moving PEDESTRIAN or BICYCLE
                    //Et VW_PF_28 o_rcsCenterLocation[l_indexLocation] = 121.0 + 0.8 * NormalRCS( Generator ); //PF28 121.0 Factor 0 Delta 0;  PF30:127.0 Factor: 1/20.0 Delta -8
                    o_rcsCenterLocation[l_indexLocation] = p_pedRcsBaseLocation + 0.8 * NormalRCS( Generator ) + o_distanceLocation[l_indexLocation] * p_pedRcsDistanceFactor;
                    o_rcsUpLocation[l_indexLocation] = o_rcsCenterLocation[l_indexLocation] + p_pedDeltaRcsUpLocation;
                    if( m_vyWorldReflection[indexReflection] > 0.01 )
                    {
                        //if the distance to the obstacle is > 1 m calculate the pwr
                        if( o_distanceLocation[l_indexLocation] >= 1 )
                        {
                            //set the power according to the distance and the angle
                            l_mdPwrEgo = ::sim::abs( ( 100.0L * ::sim::sin( o_alphaRadarLocation[l_indexLocation] ) ) / o_distanceLocation[l_indexLocation] );
                        }
                        else
                        {
                            l_mdPwrEgo = 0.00;
                        }
                        if( l_mdPwrEgo >= 0.9 ) l_mdPwrEgo = 0.9;
                        o_microDopplerPwr[l_indexLocation] = l_mdPwrEgo;
                    }
                    else
                    {
                        o_microDopplerPwr[l_indexLocation] = 0.0;
                    }
                }
                else
                {
                    o_microDopplerPwr[l_indexLocation] = 0.0;
                    o_rcsUpLocation[l_indexLocation] = p_vehicleRcsBaseLocation + p_vehicleDeltaRcsUpLocation /*+ NormalRCS( Generator )*/;
                    o_rcsCenterLocation[l_indexLocation] = p_vehicleRcsBaseLocation /*+ NormalRCS( Generator )*/;
                }
            }
            else
            {
                o_visibilityLocation[l_indexLocation] = 0.0;
                o_visibilityReflection[indexReflection] = 0.0;
                o_rcsUpLocation[l_indexLocation] = 0.0;
                o_rcsCenterLocation[l_indexLocation] = 0.0;
                o_microDopplerPwr[l_indexLocation] = 0.0;
            }

            // consider p_sensorConfiguration = -1 or 1 for lateral offset and lateral angle
            o_yRadarLocation[l_indexLocation] = p_sensorConfiguration * o_yRadarLocation[l_indexLocation];
            o_alphaRadarLocation[l_indexLocation] = p_sensorConfiguration * o_alphaRadarLocation[l_indexLocation];

            // indicators for relevant obstacles in close range
            if( o_xRadarLocation[l_indexLocation] > p_closeRange )
            {
                o_meanPowerInd[l_indexLocation] = 0;
                o_elevationInd[l_indexLocation] = 0;
                o_multipathInd[l_indexLocation] = 0;
                o_detectionInd[l_indexLocation] = 0;
            }
            else
            {
                o_meanPowerInd[l_indexLocation] = static_cast<CInt>( m_counter <= p_meanPowerIndDuty ? ( 0.9 * 254 ) : 255 );
                o_elevationInd[l_indexLocation] = 0; //not used
                o_multipathInd[l_indexLocation] = static_cast<CInt>(0.2 * 254);
                o_detectionInd[l_indexLocation] = static_cast<CInt>(0.9 * 254);
            }

            //double reflection
            o_xRadarLocation[l_indexLocation + 1] = 2 * o_xRadarLocation[l_indexLocation];
            o_yRadarLocation[l_indexLocation + 1] = 2 * o_yRadarLocation[l_indexLocation];
            o_zRadarLocation[l_indexLocation + 1] = 2 * o_zRadarLocation[l_indexLocation];
            o_alphaRadarLocation[l_indexLocation + 1] = o_alphaRadarLocation[l_indexLocation];
            o_distanceLocation[l_indexLocation + 1] =  2 * o_distanceLocation[l_indexLocation];
            o_vLateralRadarLocation[l_indexLocation + 1] = 2 * o_vLateralRadarLocation[l_indexLocation];
            o_vRadialRadarLocation[l_indexLocation + 1] = 2 * o_vRadialRadarLocation[l_indexLocation];
            if( o_distanceLocation[l_indexLocation] > p_closeRange )
            {
                o_visibilityLocation[l_indexLocation + 1] = 0.0;
                o_rcsCenterLocation[l_indexLocation + 1] = 0.0;
                o_rcsUpLocation[l_indexLocation + 1] = 0.0;
                o_microDopplerPwr[l_indexLocation + 1] = 0.0;
            }
            else
            {
                o_visibilityLocation[l_indexLocation + 1] = o_visibilityLocation[l_indexLocation] / 2;
                o_rcsCenterLocation[l_indexLocation + 1] = o_rcsCenterLocation[l_indexLocation];
                o_rcsUpLocation[l_indexLocation + 1] = o_rcsUpLocation[l_indexLocation];
                o_microDopplerPwr[l_indexLocation + 1] = 0.0;
            }
            o_meanPowerInd[l_indexLocation + 1] = o_meanPowerInd[l_indexLocation];
            o_elevationInd[l_indexLocation + 1] = o_elevationInd[l_indexLocation];
            o_multipathInd[l_indexLocation + 1] = o_multipathInd[l_indexLocation];
            o_detectionInd[l_indexLocation + 1] = o_detectionInd[l_indexLocation];
            o_elevationAngleLocation[l_indexLocation + 1] = o_elevationAngleLocation[l_indexLocation];
        }

        // sort o_prioIndexLocation array into descending order, use o_visibilityLocation as comparison criterion
        heapSortWithComparsionCriterion( o_prioIndexLocation, o_visibilityLocation );
    }
}


////*********************************
//// CObstacleRadar
////*********************************
CObstacleRadar::CObstacleRadar():
    NormalCar( 0.0, 0.06 ),
    NormalPedestrian( 0.0, 0.55 ),
    NormalCyclist( 0.0, 0.65 ),
    Normal_p( nullptr )
{}

CObstacleRadar::~CObstacleRadar()
{}

//     /*!
//      * TODO!!! Update the obstacle output message description: as in CSensor, but additionally f_yawAngleEgoObstacle

/*!
 * TODO!!! Update the obstacle output messages
 * @param[in]  ...
 * @param[out] ...
 */
CBool CObstacleRadar::updateObstacleMessages( CInt& f_indexObstacle_r, CInt& f_typeObstacle_r, CInt& f_referenceSurfaceObstacle_r, CFloat& f_visibilityObstacle_r,
                                              CFloat& f_xSensorObstacle_r, CFloat& f_ySensorObstacle_r, CFloat& f_zSensorObstacle_r,
                                              CFloat& f_azimuthSensorObstacle_r, CFloat& f_yawAngleSensorObstacle_r,
                                              CFloat& f_heightSensorObstacle_r, CFloat& f_widthSensorObstacle_r, CFloat& f_lengthSensorObstacle_r,
                                              CFloat& f_vXSensorObstacle_r, CFloat& f_vYSensorObstacle_r, CFloat& f_vZSensorObstacle_r,
                                              CFloat& f_aXVehicleObstacle_r, CFloat& f_aYVehicleObstacle_r, CFloat& f_aZVehicleObstacle_r,
                                              CFloat& f_distanceSensorObstacle_r,
                                              CInt f_referenceSurfaceObstacleFixed,
                                              CFloat& f_yawAngleEgoObstacle_r

                                            )
{
    // first, call parent's updateObstacleMessages() for generic messages
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
    // then, update CRadar specific object output "o_yawAngleEgoObstacle"
    if( l_visible )
    {
        f_yawAngleEgoObstacle_r = ::sim::normalizeAnglePosNegPI( m_yawAngleObstacle - m_angleRollPitchYawEgo[2] );
    }
    else
    {
        f_yawAngleEgoObstacle_r = 0;
    }
    return l_visible;
}


CInt CObstacleRadar::calcReflections( CInt f_startindex, CFloat f_angleSeparation, CInt f_maxNoOfReflectionsObstacle,
                                      CFloatVector& f_xWorldReflection, CFloatVector& f_yWorldReflection, CFloatVector& f_zWorldReflection,
                                      CFloatVector& f_xRadarReflection, CFloatVector& f_yRadarReflection, CFloatVector& f_zRadarReflection, CFloatVector& f_alphaRadarReflection,
                                      CFloatVector& f_dRadarReflection, CFloatVector& f_heightReflection,
                                      CFloatVector& f_vxWorldReflection, CFloatVector& f_vyWorldReflection, CFloatVector& f_vzWorldReflection,
                                      CFloatVector& f_vRadialRadarReflection, CFloatVector& f_vLateralRadarReflection,
                                      CIntVector& f_typReflection, CFloatVector& f_visibilityReflection )
{
    CInt l_indexReflection = f_startindex;
    if( m_visibilityObstacle > 0 and m_typeObstacle != EObstacleTyp::INVISIBLE )
    {
        CInt l_maxNoOfReflectionsBottom = ( ( f_maxNoOfReflectionsObstacle & 0x01 ) == 0 ? 1 : 0 );
        CInt l_maxNoOfReflectionsContour = ( f_maxNoOfReflectionsObstacle - l_maxNoOfReflectionsBottom );
        CFloat l_minDistance = ::sim::sin( f_angleSeparation ) * m_dSensorContourPoint[m_indexNearestPoint];//only a rough estimation
        CFloat l_contourLength = 0;
        for( CInt l_contourindex : m_contourPoints_a )
        {
            l_contourLength += ::sim::sqrt( ::sim::pow( m_xWorldContourLine[l_contourindex], 2 ) + ::sim::pow( m_yWorldContourLine[l_contourindex], 2 ) + ::sim::pow( m_zWorldContourLine[l_contourindex], 2 ) );
        }
        CInt l_maxNoOfReflectionsPerMinDistance = static_cast<CInt>( ::sim::max( l_contourLength / l_minDistance, 1.0L ));
        CFloat l_drContour = 2.0L / ::sim::min( l_maxNoOfReflectionsPerMinDistance, l_maxNoOfReflectionsContour );
        CFloat l_factor = ( m_rMainReference - m_rMin ) / l_drContour;
        CFloat l_rMinNew = m_rMainReference - ::sim::floor( l_factor ) * l_drContour;
        if( ( m_typeObstacle == EObstacleTyp::PEDESTRIAN ) )
        {
            Normal_p = &NormalPedestrian;
        }
        else if( ( m_typeObstacle == EObstacleTyp::BICYCLE ) )
        {
            Normal_p = &NormalCyclist;
        }
        else
        {
            Normal_p = &NormalCar;
        }

        CInt l_contourindex = 0;
        CFloat l_r =  l_rMinNew;
        while( l_r <= 1 )
        {
            CFloat t_r = ::sim::max( ::sim::min( l_r + l_drContour * ( *Normal_p )( Generator ), 1.0L ), m_rMin ); //Gaussian bell curve for measurement points
            if( t_r < 0 )
            {
                l_contourindex = m_contourPoints_a[1];
                t_r = 1 + t_r;
            }
            else
            {
                l_contourindex = m_contourPoints_a[0];
            }
            //P = A + r*AB
            //WORLD coordinates
            f_xWorldReflection[l_indexReflection] = ( *m_xWorldContourPoint_p )[l_contourindex] + t_r * m_xWorldContourLine[l_contourindex];
            f_yWorldReflection[l_indexReflection] = ( *m_yWorldContourPoint_p )[l_contourindex] + t_r * m_yWorldContourLine[l_contourindex];
            f_zWorldReflection[l_indexReflection] = ( *m_zWorldContourPoint_p )[l_contourindex] + t_r * m_zWorldContourLine[l_contourindex];
            //f_alphaWorldReflection[l_indexReflection] = ::sim::atan2( f_yWorldReflection[l_indexReflection], f_xWorldReflection[l_indexReflection] );
            //RADAR coordinates
            f_xRadarReflection[l_indexReflection] = m_xSensorContourPoint[l_contourindex] + t_r * m_xSensorContourLine[l_contourindex];
            f_yRadarReflection[l_indexReflection] = m_ySensorContourPoint[l_contourindex] + t_r * m_ySensorContourLine[l_contourindex];
            f_zRadarReflection[l_indexReflection] = m_zSensorContourPoint[l_contourindex] + t_r * m_zSensorContourLine[l_contourindex];
            f_alphaRadarReflection[l_indexReflection] = ::sim::atan2( f_yRadarReflection[l_indexReflection], f_xRadarReflection[l_indexReflection] );

            f_dRadarReflection[l_indexReflection] = ::sim::sqrt( ::sim::pow( f_xRadarReflection[l_indexReflection], 2 ) + ::sim::pow( f_yRadarReflection[l_indexReflection], 2 ) + ::sim::pow( f_zRadarReflection[l_indexReflection], 2 ) );
            f_heightReflection[l_indexReflection] =  m_depthHeightWidthObstacle[1];

            f_vxWorldReflection[l_indexReflection] = m_vXYZWorldObstacle[0]; //m_vxWorldObstacle; //ToDo: consider yawRate obstacle
            f_vyWorldReflection[l_indexReflection] = m_vXYZWorldObstacle[1]; //m_vyWorldObstacle; //ToDo: consider yawRate obstacle
            f_vzWorldReflection[l_indexReflection] = m_vXYZWorldObstacle[2]; //m_vzWorldObstacle; //ToDo: consider yawRate obstacle

            CFloat l_dvXWorldObstacleReflection = f_vxWorldReflection[l_indexReflection] - m_vXYZWorldSensor[0]; //m_vxWorldRadar;
            CFloat l_dvYWorldObstacleReflection = f_vyWorldReflection[l_indexReflection] - m_vXYZWorldSensor[1]; //m_vyWorldRadar;
            CFloat l_angle = m_yawAngle + f_alphaRadarReflection[l_indexReflection]; //ToDo: yawAngle only valid for small pitch and roll angles
            f_vRadialRadarReflection[l_indexReflection]  =  ::sim::cos( l_angle ) * l_dvXWorldObstacleReflection + ::sim::sin( l_angle ) * l_dvYWorldObstacleReflection;
            f_vLateralRadarReflection[l_indexReflection] = -::sim::sin( l_angle ) * l_dvXWorldObstacleReflection + ::sim::cos( l_angle ) * l_dvYWorldObstacleReflection;
            f_typReflection[l_indexReflection] = m_typeObstacle;
            f_visibilityReflection[l_indexReflection] = m_visibilityObstacle;
            l_r += l_drContour;
            l_indexReflection++;
        }

        //Reflection in the middle of the car for length simulation
        if( m_depthHeightWidthObstacle[0] > 1.2 and m_depthHeightWidthObstacle[2] > 1.2 and l_maxNoOfReflectionsBottom > 0 )
        {
            //// ## mid-size and large obstacles
            //ToDo consider l_maxNoOfRefelctionsBottom for more than one reflection on the bottom
            f_xWorldReflection[l_indexReflection] = m_xyzWorldObstacle[0];
            f_yWorldReflection[l_indexReflection] = m_xyzWorldObstacle[1];
            f_zWorldReflection[l_indexReflection] = m_xyzWorldObstacle[2];
            //f_alphaWorldReflection[l_indexReflection] = ::sim::atan2( f_yWorldReflection[l_indexReflection], f_xWorldReflection[l_indexReflection] );
            //RADAR coordinates
            f_xRadarReflection[l_indexReflection] = m_xyzSensorObstacle[0];
            f_yRadarReflection[l_indexReflection] = m_xyzSensorObstacle[1];
            f_zRadarReflection[l_indexReflection] = m_xyzSensorObstacle[2];
            f_alphaRadarReflection[l_indexReflection] = ::sim::atan2( f_yRadarReflection[l_indexReflection], f_xRadarReflection[l_indexReflection] );

            f_dRadarReflection[l_indexReflection] = ::sim::sqrt( ::sim::pow( f_xRadarReflection[l_indexReflection], 2 ) + ::sim::pow( f_yRadarReflection[l_indexReflection], 2 ) + ::sim::pow( f_zRadarReflection[l_indexReflection], 2 ) );
            f_heightReflection[l_indexReflection] =  m_depthHeightWidthObstacle[1];

            f_vxWorldReflection[l_indexReflection] = m_vXYZWorldObstacle[0];
            f_vyWorldReflection[l_indexReflection] = m_vXYZWorldObstacle[1];
            f_vzWorldReflection[l_indexReflection] = m_vXYZWorldObstacle[2];

            CFloat l_dvXWorldObstacleReflection = f_vxWorldReflection[l_indexReflection] - m_vXYZWorldSensor[0]; //m_vxWorldRadar;
            CFloat l_dvYWorldObstacleReflection = f_vyWorldReflection[l_indexReflection] - m_vXYZWorldSensor[1]; //m_vyWorldRadar;
            CFloat l_angle = m_yawAngle + f_alphaRadarReflection[l_indexReflection]; //ToDo: yawAngle only valid for small pitch and roll angles
            f_vRadialRadarReflection[l_indexReflection]  =  ::sim::cos( l_angle ) * l_dvXWorldObstacleReflection + ::sim::sin( l_angle ) * l_dvYWorldObstacleReflection;
            f_vLateralRadarReflection[l_indexReflection] = -::sim::sin( l_angle ) * l_dvXWorldObstacleReflection + ::sim::cos( l_angle ) * l_dvYWorldObstacleReflection;
            f_typReflection[l_indexReflection] = m_typeObstacle;
            f_visibilityReflection[l_indexReflection] = m_visibilityObstacle;
            l_indexReflection++;
        }
    }
    return l_indexReflection;
}

