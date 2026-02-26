/*******************************************************************************
@author Andreas Brunner, bnr2lr
@author Robert Erhart, ett2si (08.04.2020)
@copyright (c) Robert Bosch GmbH 2020-2024. All rights reserved.
*******************************************************************************/

#include "CSensor.h"

//*********************************
// constructor/destructor/copy/move
//*********************************
CSensor::CSensor():
    m_velocityXYZWorldSensor(),
    m_sensorVelocityFromRotation(),
    m_angleXYZVehicle(),
    m_viewSegment_a( 0 )
{
    /* Initialization messages */

    /* Input */
    addMessageInput( i_xyzWorldVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_vWorldVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_aWorldVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_angleRollPitchYawVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_yawRateVehicle, 0.0 );
    addMessageInput( i_staticSimulation, false );

    //dynamic objects
    addMessageInput( i_xyzWorldObstacleDynamic );
    addMessageInput( i_vWorldObstacleDynamic );
    addMessageInput( i_aObstacleDynamic );
    addMessageInput( i_yawAngleObstacleDynamic );

    addMessageInput( i_typeObstacleDynamic );
    addMessageInput( i_depthObstacleDynamic );
    addMessageInput( i_heightObstacleDynamic );
    addMessageInput( i_widthObstacleDynamic );
    addMessageInput( i_visibilityObstacleDynamic );

    addMessageInput( i_xWorldContourObstacleDynamic );
    addMessageInput( i_yWorldContourObstacleDynamic );
    addMessageInput( i_zWorldContourObstacleDynamic );

    //static objects
    addMessageInput( i_xyzWorldObstacleStatic );
    addMessageInput( i_yawAngleObstacleStatic );
    addMessageInput( i_typeObstacleStatic );
    addMessageInput( i_depthObstacleStatic );
    addMessageInput( i_heightObstacleStatic );
    addMessageInput( i_widthObstacleStatic );
    addMessageInput( i_visibilityObstacleStatic );

    addMessageInput( i_xWorldContourObstacleStatic );
    addMessageInput( i_yWorldContourObstacleStatic );
    addMessageInput( i_zWorldContourObstacleStatic );

    /* Parameter */
    addMessageParameter( p_xyzVehicleMountingPos, CFloatVectorXYZ( 2.0, 0.0, 0.3 ), CSensorDoc::p_xyzVehicleMountingPos );
    addMessageParameter( p_angleRollPitchYawVehicleMounting,  CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CSensorDoc::p_angleRollPitchYawVehicleMounting );

    addMessageParameter( p_anglesFieldOfViewSegments, ::sim::to_radians( {+30, -30} ), CSensorDoc::p_anglesFieldOfViewSegments );   // +-30 degrees field of view
    addMessageParameter( p_maxRangesFieldOfViewSegments, CFloatVector( {150.} ), CSensorDoc::p_maxRangesFieldOfViewSegments );
    addMessageParameter( p_minRangesFieldOfViewSegments, CFloatVector( {0.1} ), CSensorDoc::p_minRangesFieldOfViewSegments );

    addMessageParameter( p_sensorConfiguration, 0, CSensorDoc::p_sensorConfiguration );  // -1: connector up, 0: no Sensor; 1: connector down
    addMessageParameter( p_maxNumberOfRelevantObstacles, 166, CSensorDoc::p_maxNumberOfRelevantObstacles );

    addMessageParameter( p_referenceSurfaceObstacleFixed, 0, CSensorDoc::p_referenceSurfaceObstacleFixed );

    /* Output */
    addMessageOutput( o_xyzWorldSensor, p_xyzVehicleMountingPos, CSensorDoc::o_xyzWorldSensor );
    addMessageOutput( o_rotationWorld, p_angleRollPitchYawVehicleMounting, CSensorDoc::o_rotationWorld );
    addMessageOutput( o_xViewSegment, CFloatVector( 0.0, 5 * 3 ), CSensorDoc::o_xViewSegment );
    addMessageOutput( o_yViewSegment, CFloatVector( 0.0, 5 * 3 ), CSensorDoc::o_yViewSegment );
    addMessageOutput( o_zViewSegment, CFloatVector( 0.0, 5 * 3 ), CSensorDoc::o_zViewSegment );

    addMessageOutput( o_indexObstacle, CIntVector( CInt( 0 ), p_maxNumberOfRelevantObstacles ), CSensorDoc::o_indexObstacle );
    addMessageOutput( o_typeObstacle, CIntVector( CInt( 0 ), p_maxNumberOfRelevantObstacles ), CSensorDoc::o_typeObstacle );
    addMessageOutput( o_visibilityObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_visibilityObstacle );

    addMessageOutput( o_distanceSensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_distanceSensorObstacle );
    addMessageOutput( o_xSensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_xSensorObstacle );
    addMessageOutput( o_ySensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_ySensorObstacle );
    addMessageOutput( o_zSensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_zSensorObstacle );

    addMessageOutput( o_vXSensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_vXSensorObstacle );
    addMessageOutput( o_vYSensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_vYSensorObstacle );
    addMessageOutput( o_vZSensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_vZSensorObstacle );

    addMessageOutput( o_aXVehicleObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_aXVehicleObstacle );
    addMessageOutput( o_aYVehicleObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_aYVehicleObstacle );
    addMessageOutput( o_aZVehicleObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_aZVehicleObstacle );

    addMessageOutput( o_yawAngleSensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_yawAngleSensorObstacle );
    addMessageOutput( o_alphaSensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_alphaSensorObstacle );
    addMessageOutput( o_referenceSurfaceObstacle, CIntVector( CInt( 0 ), p_maxNumberOfRelevantObstacles ), CSensorDoc::o_referenceSurfaceObstacle );

    addMessageOutput( o_widthSensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_widthSensorObstacle );
    addMessageOutput( o_depthSensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_depthSensorObstacle );
    addMessageOutput( o_heightSensorObstacle, CFloatVector( 0.0, p_maxNumberOfRelevantObstacles ), CSensorDoc::o_heightSensorObstacle );
}

CSensor::~CSensor()
{}

void CSensor::init( IMessage<CFloatVectorXYZ>& f_xyzWorld,
                    IMessage<CFloatVectorXYZ>& f_velocityXYZWorld,
                    IMessage<CFloatVectorXYZ>& f_accelerationXYZVehicleEgo,
                    IMessage<CFloatVectorXYZ>& f_angleRollPitchYawEgo,
                    IMessage<CFloat>& f_yawRateEgo,
                    CObstacles& f_obstacles_r,
                    IMessage<CBool>& f_staticSimulation )
{
    /* link input messages */

    /*
     * Ego vehicle information
     */
    i_xyzWorldVehicle.link( f_xyzWorld );
    i_vWorldVehicle.link( f_velocityXYZWorld );
    i_angleRollPitchYawVehicle.link( f_angleRollPitchYawEgo );
    i_aWorldVehicle.link( f_accelerationXYZVehicleEgo );
    i_yawRateVehicle.link( f_yawRateEgo );

    i_staticSimulation.link( f_staticSimulation );

    /*
     * Dynamic obstacles' properties
     */

    i_xyzWorldObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::o_xyzWorld );
    i_vWorldObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::o_vWorld );
    i_aObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::o_acceleration );
    i_yawAngleObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::o_yawAngle );

    i_typeObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::p_type );
    i_depthObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::p_depth );
    i_heightObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::p_height );
    i_widthObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::p_width );
    i_visibilityObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::p_visibility );

    i_xWorldContourObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::o_xWorldContour );
    i_yWorldContourObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::o_yWorldContour );
    i_zWorldContourObstacleDynamic.link( f_obstacles_r.ObstacleDynamic, &CObstacleDynamic::o_zWorldContour );

    /*
     * Static obstacles' properties
     */
    i_xyzWorldObstacleStatic.link( f_obstacles_r.ObstacleStatic, &CObstacleStatic::o_xyzWorld );
    i_yawAngleObstacleStatic.link( f_obstacles_r.ObstacleStatic, &CObstacleStatic::o_yawAngle );

    i_typeObstacleStatic.link( f_obstacles_r.ObstacleStatic, &CObstacleStatic::p_type );
    i_depthObstacleStatic.link( f_obstacles_r.ObstacleStatic, &CObstacleStatic::p_depth );
    i_heightObstacleStatic.link( f_obstacles_r.ObstacleStatic, &CObstacleStatic::p_height );
    i_widthObstacleStatic.link( f_obstacles_r.ObstacleStatic, &CObstacleStatic::p_width );
    i_visibilityObstacleStatic.link( f_obstacles_r.ObstacleStatic, &CObstacleStatic::p_visibility );

    i_xWorldContourObstacleStatic.link( f_obstacles_r.ObstacleStatic, &CObstacleStatic::o_xWorldContour );
    i_yWorldContourObstacleStatic.link( f_obstacles_r.ObstacleStatic, &CObstacleStatic::o_yWorldContour );
    i_zWorldContourObstacleStatic.link( f_obstacles_r.ObstacleStatic, &CObstacleStatic::o_zWorldContour );



    /*
     * Output messages: sensor info
     */
    o_xyzWorldSensor.init( p_xyzVehicleMountingPos + i_xyzWorldVehicle );
    o_rotationWorld.init( i_angleRollPitchYawVehicle + p_angleRollPitchYawVehicleMounting );




    /* Initialization messages:
     *
     * linking to input messages affects all(!) messages for which "addMessageInput/Output/Parameter"
     * was called. In a child class, these might be more than what is defined in CSensor.
     * For this reason, we cannot call "initializationMessages" here, but need to call it in the child
     * classes.
     */

    // initializationMessages();

}



//*******************************
// methods
//******************************
void CSensor::heapSortWithComparsionCriterion( CIntVector& f_indexVector_r, const CFloatVector& f_prioVector_r )
{
    /********************************************************************************************
     * Sorts 'f_indexVector_r' array into descending order with respect to the comparison
     * criterion (="values to be sorted") defined by 'f_prioVector_r'. f_prioVector_r is
     * NOT changed.
     * The implementation uses an inverse Heapsort (invented by J.W.J. Williams).
     *
     * An example:
     *      prioVector = [0.1, 0.33, 0.05, 0.8] and
     *      indexVector = numbers 0 to 3 in any order
     *      will lead to a sorted indexVector [3, 1, 0, 2].
     *      This is expected, since the correct ordering of prioVector = 'pV' is given by
     *      the sorted indexVector = 'iV' as:
     *
     *              pV[ iV[0] ] >= pV[ iV[1] ] >= pV[ iV[2] ] >= pV[ iV[3] ]
     *
     * Note that indexVector may contain only numbers from zero to prioVector.size()-1.
     * Otherwise undefined behaviour will occur.
     *******************************************************************************************/

    ::std::size_t n = f_indexVector_r.size();
    // plausibility checks: array sizes
    if( n != f_prioVector_r.size() )
    {
        ::std::cerr << "Error <CSensor::heapSortWithComparsionCriterion>: array sizes don't match!" << ::std::endl;
        return;
    }
    // plausibility checks: indexVector entries
    if( f_indexVector_r.max() > static_cast<CInt>( n - 1 ) )
    {
        std::cerr << "DEBUG: <CSensor::heapSortWithComparsionCriterion>: maximum indexVector value too high - undefined sorting behavior." << std::endl;
    }

    if( n > 1 )
    {
        size_t indexI, indexR, indexJ, indexL;
        CInt sortValueTemp = 0;
        indexL = ( n >> 1 ) + 1;
        indexR = n;
        while( true )
        {
            if( indexL > 1 )
            {
                // hiring phase
                indexL--;
                sortValueTemp = f_indexVector_r[indexL - 1];
            }
            else
            {
                // retirement-and-promotion phase
                sortValueTemp = f_indexVector_r[indexR - 1];
                f_indexVector_r[indexR - 1] = f_indexVector_r[0];
                indexR--;
                if( indexR == 1 )
                {
                    f_indexVector_r[0] = sortValueTemp;
                    break;
                }
            }
            indexI = indexL;
            indexJ = indexL + indexL;
            while( indexJ <= indexR )
            {
                // Now, use the comparison criterion (prioVector) to realize sorting.
                // Implicitly, indexVector entries between 0 and prioVector.size()-1 are assumed here.
                if( indexJ < indexR &&
                    f_prioVector_r[ f_indexVector_r[indexJ - 1] ] > f_prioVector_r[ f_indexVector_r[indexJ] ] )
                {
                    indexJ++;
                }
                if( f_prioVector_r[ sortValueTemp ] > f_prioVector_r[ f_indexVector_r[indexJ - 1] ] )
                {
                    f_indexVector_r[indexI - 1] = f_indexVector_r[indexJ - 1];
                    indexI = indexJ;
                    indexJ = indexJ << 1;
                }
                else
                {
                    indexJ = indexR + 1;
                }
            }
            f_indexVector_r[indexI - 1] = sortValueTemp;
        }
    }
}


void CSensor::calc( CFloat f_dT, CFloat f_time )
{
    //************************************************************************************
    //* Update sensor coordinate, orientation, and view segment output messages
    //************************************************************************************

    // angle between x-axis sensor and x-axis world
    o_rotationWorld = i_angleRollPitchYawVehicle + p_angleRollPitchYawVehicleMounting;

    /* calculate sensor position (world coordinates) from current roll, pitch, yaw angles and mounting position */
    ::sim::coordinateRotation( i_angleRollPitchYawVehicle,
                        p_xyzVehicleMountingPos,
                        o_xyzWorldSensor );

    /* ... and add ego position as offset */
    o_xyzWorldSensor = o_xyzWorldSensor + i_xyzWorldVehicle;

    /* update field of view */
    for( auto& segment :  m_viewSegment_a )
    {
        auto index = ( &segment - &m_viewSegment_a[0] );
        auto index3 = index * 3;
        CFloat l_openingAngleSegment = p_anglesFieldOfViewSegments[index] - p_anglesFieldOfViewSegments[index + 1];
        segment.init( p_anglesFieldOfViewSegments[index], l_openingAngleSegment, p_maxRangesFieldOfViewSegments[index],
                      i_angleRollPitchYawVehicle[0], o_rotationWorld[1], o_rotationWorld[2],
                      o_xyzWorldSensor[0], o_xyzWorldSensor[1], o_xyzWorldSensor[2],
                      o_xViewSegment[index3], o_yViewSegment[index3], o_zViewSegment[index3],
                      o_xViewSegment[index3 + 1], o_yViewSegment[index3 + 1], o_zViewSegment[index3 + 1],
                      o_xViewSegment[index3 + 2], o_yViewSegment[index3 + 2], o_zViewSegment[index3 + 2] );
    }


    /************************************************************************************
     * Transform ego vehicle rotation velocity to sensor movement.
     ************************************************************************************
     *
     * In ego coordinates, this is calculated in vector notation by
     *
     *      v_rot,sensor  =  yawRate *  ê_ax  (x)  p_sensor
     *
     * with "ê_ax" the rotation axis unit vector, "p_sensor" the sensor coordinate vector,
     * and (x) the cross product.
     *
     * Note: We limit the calculation to include sensor MOVEMENT from chassis rotation only,
     *       but not sensor ROTATION. When outputting obstacle velocity in sensor coordinates
     *       (like ""), rotation of the sensor (-> sensor coordinate system)
     *       might have a strong impact for distant objects' velocities.
     *       Output quantities in WORLD COORDINATES are not affected.
     *       In our target scenarios, i.e. stable driving situations with small yaw rates
     *       this simplification is justified.
     */

    //CFloatVectorXYZ l_sensorVelocityFromRotation( 0.0, 0.0, 0.0 );
    m_angleXYZVehicle.XYZ( 0., 0., i_yawRateVehicle );
    ::sim::crossProduct( m_sensorVelocityFromRotation,
                  m_angleXYZVehicle,
                  p_xyzVehicleMountingPos );

    m_velocityXYZWorldSensor = m_sensorVelocityFromRotation + i_vWorldVehicle;

}




////*********************************
//// CObstacleSensor
////*********************************
CObstacleSensor::CObstacleSensor():
    m_xSensorContourLine( 4 ), m_ySensorContourLine( 4 ), m_zSensorContourLine( 4 ),
    m_xWorldContourLine( 4 ), m_yWorldContourLine( 4 ), m_zWorldContourLine( 4 ),
    m_yawAngle( 0 ),
    m_angleRollPitchYawEgo( ),
    m_angleRollPitchYawTemp( ),
    m_sensorMountingAngles( ),
    m_xyzWorldSensor( ),
    m_vXYZWorldSensor( ),
    m_aXYZVehicleEgo( ),
    m_indexObstacle( 0 ),
    m_typeObstacle( 0 ),
    m_visibilityObstacle( 0 ),
    m_xyzWorldObstacle( ),
    m_vXYZWorldObstacle( ),
    m_aObstacle( 0 ),
    m_yawAngleObstacle( 0 ),
    m_xWorldContourPoint_p( nullptr ), m_yWorldContourPoint_p( nullptr ), m_zWorldContourPoint_p( nullptr ),
    m_depthHeightWidthObstacle( ),
    m_xyzSensorObstacle( ),
    m_vXYZSensorObstacle( ),
    m_aXYZVehicleObstacle( ),
    m_aXYZObstacle( ),
    m_xSensorContourPoint( 4 ), m_ySensorContourPoint( 4 ), m_zSensorContourPoint( 4 ),
    m_dSensorContourPoint( 4 ),
    m_azimuthSensorContourPoint( 4 ),
    m_indexRelevantSide( 0 ), m_indexRelevantSideNext( 0 ),
    m_indexNearestPoint( 0 ),
    m_rMainReference( 0 ),
    m_rMin( 0 )
{
    m_contourPoints_a.reserve( 2 );
    m_contourPoints_a.resize( 0 );
}

CObstacleSensor::~CObstacleSensor()
{}

void CObstacleSensor::init()
{
    m_visibilityObstacle = 0;
    m_indexObstacle = 0;
}

/*
* Initialize CObstacleSensor object and update member variables (vectorized input version).
*/

void
CObstacleSensor::init( CInt f_indexObstacle,
                       CFloatVector f_xyzPositionWorldSensor,
                       CFloatVector f_xyzVelocityWorldSensor,
                       CFloatVector f_xyzAccelerationVehicleEgo,
                       CFloatVector f_rollPitchYawAnglesEgo,
                       CFloatVector f_sensorMountingAngles,
                       CFloatVector f_xyzPositionObstacle,
                       CFloatVector f_xyzVelocityWorldObstacle,
                       CFloat f_aObstacle, CFloat f_yawAngleObstacle, CInt f_typeObstacle,
                       CFloatVector f_depthHeightWidthObstacle,
                       CFloat f_visibilityObstacle,
                       CFloatVector& f_xWorldContourObstacle, CFloatVector& f_yWorldContourObstacle, CFloatVector& f_zWorldContourObstacle )
{
    // fill member variables:  ego angles and acceleration, sensor position, velocity, and mounting angles
    m_yawAngle              = f_rollPitchYawAnglesEgo[2] + f_sensorMountingAngles[2];
    m_angleRollPitchYawEgo = f_rollPitchYawAnglesEgo;
    m_xyzWorldSensor         = f_xyzPositionWorldSensor;
    m_vXYZWorldSensor        = f_xyzVelocityWorldSensor;
    m_sensorMountingAngles = f_sensorMountingAngles;
    m_aXYZVehicleEgo        = f_xyzAccelerationVehicleEgo;

    // fill member variables: obstacle type and dimensions, acceleration and yaw angle
    m_indexObstacle             = f_indexObstacle;
    m_yawAngleObstacle          = f_yawAngleObstacle;
    m_depthHeightWidthObstacle  = f_depthHeightWidthObstacle;
    m_typeObstacle              = f_typeObstacle;
    m_visibilityObstacle        = f_visibilityObstacle;

    m_xyzWorldObstacle      = f_xyzPositionObstacle;
    m_vXYZWorldObstacle     = f_xyzVelocityWorldObstacle;
    m_aObstacle             = f_aObstacle; // scalar, in obstacle's x direction

    //contour points
    m_xWorldContourPoint_p = &f_xWorldContourObstacle;
    m_yWorldContourPoint_p = &f_yWorldContourObstacle;
    m_zWorldContourPoint_p = &f_zWorldContourObstacle;
}

/*
* Update CObstacleSensor object information. Calculate Sensor <-> obstacle distance
* and angles based on current member variables (m_indexRelevantSide etc.)
*/
void
CObstacleSensor::calcProperties()
{
    /**************************************************************************
     * Calculate distance sensor <-> obstacle in sensor coordinates.
     *    1. calculate distance in world coordinates
     *    2. transform to sensor coordinate system
     *************************************************************************/
    m_xyzSensorObstacle = m_xyzWorldObstacle - m_xyzWorldSensor;

    /* ... now transform to sensor coordinates. */
    // world to ego coordinate system (coordinate origin = sensor location)
    ::sim::coordinateRotationInv( m_angleRollPitchYawEgo,
                           m_xyzSensorObstacle,
                           m_xyzSensorObstacle );


    // ego to sensor coordinate system
    ::sim::coordinateRotationInv( m_sensorMountingAngles,
                           m_xyzSensorObstacle,
                           m_xyzSensorObstacle );

    /**************************************************************************
     * Calculate relative velocity in sensor coordinate system. Used in
     * 'updateObstacleMessages' to get o_vXSensorObstacle.
     ***************************************************************************/
    // rel. velocity obstacle <-> sensor (world coordinates)
    m_vXYZSensorObstacle = m_vXYZWorldObstacle - m_vXYZWorldSensor;

    // world to ego
    ::sim::coordinateRotationInv( m_angleRollPitchYawEgo,
                           m_vXYZSensorObstacle,
                           m_vXYZSensorObstacle );

    // ego to sensor
    ::sim::coordinateRotationInv( m_sensorMountingAngles,
                           m_vXYZSensorObstacle,
                           m_vXYZSensorObstacle );


    /**************************************************************************
     * Calculate obstacle acceleration in vehicle coordinate system:
     *          o_a{X,Y}VehicleObstacle
     ***************************************************************************/
    /* transform obstacle acceleration from obstacle to world coordinates (considers yaw angle only!) */
    ::sim::coordinateRotation( m_angleRollPitchYawTemp.XYZ( 0, 0., m_yawAngleObstacle ),
                        m_aXYZObstacle.XYZ( m_aObstacle, 0, 0 ),
                        m_aXYZVehicleObstacle );

    /* transform obstacle acceleration from world to vehicle coordinates (considers yaw angle only!) */
    ::sim::coordinateRotationInv( m_angleRollPitchYawTemp.XYZ( 0, 0., m_angleRollPitchYawEgo[2] ),
                           m_aXYZVehicleObstacle,
                           m_aXYZVehicleObstacle );

    /* subtract ego acceleration  */
    m_aXYZVehicleObstacle = m_aXYZVehicleObstacle - m_aXYZVehicleEgo;

    /**************************************************************************
     * calculate all obstacle contour points and their Azimuth angles, then
     * nearest contour point and distance (all in sensor coordinates).
     ***************************************************************************/
    CFloat l_distance = ::std::numeric_limits<CFloat>::max();
    m_indexNearestPoint = 0;
    for( auto index = 0; index < 4; index++ )
    {
        //coordinate transformation world -> sensor coordinates
        m_xSensorContourPoint[index] = ( *m_xWorldContourPoint_p )[index] - m_xyzWorldSensor[0];
        m_ySensorContourPoint[index] = ( *m_yWorldContourPoint_p )[index] - m_xyzWorldSensor[1];
        m_zSensorContourPoint[index] = ( *m_zWorldContourPoint_p )[index] - m_xyzWorldSensor[2];

        // world to ego
        ::sim::coordinateRotationInv( m_angleRollPitchYawEgo,
                               m_xSensorContourPoint[index], m_ySensorContourPoint[index], m_zSensorContourPoint[index],
                               m_xSensorContourPoint[index], m_ySensorContourPoint[index], m_zSensorContourPoint[index] );

        // ego to sensor
        ::sim::coordinateRotationInv( m_sensorMountingAngles,
                               m_xSensorContourPoint[index], m_ySensorContourPoint[index], m_zSensorContourPoint[index],
                               m_xSensorContourPoint[index], m_ySensorContourPoint[index], m_zSensorContourPoint[index] );

        m_azimuthSensorContourPoint[index] = ::sim::atan2( m_ySensorContourPoint[index], m_xSensorContourPoint[index] );
        //calculation of distance array (for each contour point) and minimal distance point index
        m_dSensorContourPoint[index] = ::sim::sqrt( ::sim::pow( m_xSensorContourPoint[index], 2 ) + ::sim::pow( m_ySensorContourPoint[index], 2 ) + ::sim::pow( m_zSensorContourPoint[index], 2 ) );
        if( m_dSensorContourPoint[index] < l_distance )
        {
            m_indexNearestPoint = index;
            l_distance = m_dSensorContourPoint[index];
        }
    }

    /**************************************************************************
     * calculate obstacle contour lines
     ***************************************************************************/
    for( auto index = 0; index < 4; index++ )
    {
        CInt l_indexNextContourPoint = ( index + 1 ) & 0x3;
        m_xWorldContourLine[index] = ( *m_xWorldContourPoint_p )[l_indexNextContourPoint] - ( *m_xWorldContourPoint_p )[index];
        m_yWorldContourLine[index] = ( *m_yWorldContourPoint_p )[l_indexNextContourPoint] - ( *m_yWorldContourPoint_p )[index];
        m_zWorldContourLine[index] = ( *m_zWorldContourPoint_p )[l_indexNextContourPoint] - ( *m_zWorldContourPoint_p )[index];

        m_xSensorContourLine[index] = m_xSensorContourPoint[l_indexNextContourPoint] - m_xSensorContourPoint[index];
        m_ySensorContourLine[index] = m_ySensorContourPoint[l_indexNextContourPoint] - m_ySensorContourPoint[index];
        m_zSensorContourLine[index] = m_zSensorContourPoint[l_indexNextContourPoint] - m_zSensorContourPoint[index];
    }

    /****************************************************************************************
     * Calculate relevant obstacle side using obstacle contour points' Azimuth angles.
     * Using 'calcIntersectionPoint()', calculate "MainReference" position on this side.
     *
     * - 'm_indexRelevantSide' is used by object type and reflection/vertex type sensors.
     * - 'm_rMin' and 'm_rMainReference' are used by reflection/vertex type sensors only.
     ***************************************************************************************/
    CInt l_leftContourPoint = ( m_indexNearestPoint - 1 ) & 0x3;
    CInt l_rightContourPoint = ( m_indexNearestPoint + 1 ) & 0x3;

    if( m_azimuthSensorContourPoint[l_leftContourPoint] <= m_azimuthSensorContourPoint[m_indexNearestPoint] )
    {
        m_contourPoints_a.resize( 1 );
        m_contourPoints_a[0] = m_indexNearestPoint;
        m_rMainReference = calcIntersectionPoint( m_indexNearestPoint );
        m_rMin = 0;
        m_indexRelevantSide = m_indexNearestPoint;
    }
    else if( m_azimuthSensorContourPoint[m_indexNearestPoint] <= m_azimuthSensorContourPoint[l_rightContourPoint] )
    {
        m_contourPoints_a.resize( 1 );
        m_contourPoints_a[0] = l_leftContourPoint;
        m_rMainReference = calcIntersectionPoint( l_leftContourPoint );
        m_rMin = 0;
        m_indexRelevantSide = l_leftContourPoint;
    }
    else
    {
        m_contourPoints_a.resize( 2 );
        m_contourPoints_a[0] = m_indexNearestPoint;
        m_contourPoints_a[1] = l_leftContourPoint;
        m_rMainReference = calcIntersectionPoint( l_leftContourPoint );
        if( m_rMainReference > 1 or m_rMainReference < 0 )
        {
            m_rMainReference = calcIntersectionPoint( m_indexNearestPoint );
            m_indexRelevantSide =  m_indexNearestPoint;
        }
        else
        {
            m_rMainReference = -1 + m_rMainReference;
            m_indexRelevantSide =  l_leftContourPoint;
        }
        m_rMin = -1;
    }

    m_indexRelevantSideNext = ( m_indexRelevantSide + 1 ) & 0x3;
}

CFloat
CObstacleSensor::calcIntersectionPoint( CInt f_contourindex )
{
    /*
    Calculate the intersection of two lines: contour line P0->P1 and sensor-obstacle line (origin->B)

    Sketch (top view):

             .............
    OBSTACLE=>:           :
    box       :     o <--- B
             :      \    :
      P0 --> .______(x)__. <-- P1
               ^      \
             . |     . \
      contour line      \
             .       .   \
                          \
             .       .     O <-- SENSOR (coordinate origin)
             |<--s ->|

    P0, P1: contour points
    B:      obstacle center of gravity
    X:      intersection point
    s:      distance along contour line (=P1-P0) to reach intersection point
        s = p * (P1-P0)
    p:      relative distance (units of side length (P1-P0) to reach intersection point

    Equation for intersection point (solve for p)
        P0 + p * (P1-P0) = q * B

    Solution:
                B_x * P0_y  -  B_y * P0_x          num
        p = ----------------------------------  =  ----
             By * (P1-P0)_y - Bx * (P1-P0)_x)      den


    Associated member variables:
    B             = m_xyzSensorObstacle
    Pi            = m_{x,y}SensorContourPoint[i]
    P_i+1 - P_i   = m_{x,y}SensorContourLine[i]
    */

    CFloat l_num = ( m_xyzSensorObstacle.Y() * m_xSensorContourPoint[f_contourindex] - m_xyzSensorObstacle.X() * m_ySensorContourPoint[f_contourindex] );
    CFloat l_den = ( m_xyzSensorObstacle.X() * m_ySensorContourLine[f_contourindex]  - m_xyzSensorObstacle.Y() * m_xSensorContourLine[f_contourindex] );

    return ( l_den != 0 ) ? l_num / l_den : std::numeric_limits<CFloat>::max();
}

/*!
 * TODO!!! Update the obstacle output messages
 * @param[in]  ...
 * @param[out] ...
 */
CBool
CObstacleSensor::updateObstacleMessages( CInt& f_indexObstacle_r, CInt& f_typeObstacle_r,  CInt& f_referenceSurfaceObstacle_r, CFloat& f_visibilityObstacle_r,
                                         CFloat& f_xSensorObstacle_r, CFloat& f_ySensorObstacle_r, CFloat& f_zSensorObstacle_r,
                                         CFloat& f_azimuthSensorObstacle_r, CFloat& f_yawAngleSensorObstacle_r, // CFloat& f_yawAngleEgoObstacle_r,
                                         CFloat& f_heightSensorObstacle_r, CFloat& f_widthSensorObstacle_r, CFloat& f_lengthSensorObstacle_r,
                                         CFloat& f_vXSensorObstacle_r, CFloat& f_vYSensorObstacle_r, CFloat& f_vZSensorObstacle_r,
                                         CFloat& f_aXVehicleObstacle_r, CFloat& f_aYVehicleObstacle_r, CFloat& f_aZVehicleObstacle_r,
                                         CFloat& f_distanceSensorObstacle_r,
                                         CInt f_referenceSurfaceObstacleFixed
                                       )
{
    if( m_visibilityObstacle > 0 and m_typeObstacle != EObstacleTyp::INVISIBLE )
    {
        //static obstacle [-inf, -1]; dynamic obstacle [1,inf]; 0: invalid
        f_indexObstacle_r = m_indexObstacle;
        f_typeObstacle_r = m_typeObstacle;

        // referenceSurface
        CInt l_indexRelevantSide = 0;
        if( f_referenceSurfaceObstacleFixed != 0 ) // use fixed relevant side parameter CSensor::p_referenceSurfaceObstacleFixed
        {
            l_indexRelevantSide = f_referenceSurfaceObstacleFixed - 1;
        }
        else // use dynamic relevant side
        {
            l_indexRelevantSide = m_indexRelevantSide;
        }

        switch( l_indexRelevantSide )
        {
            case 0:
                f_referenceSurfaceObstacle_r = rearView;
                f_widthSensorObstacle_r = m_depthHeightWidthObstacle[2];
                f_lengthSensorObstacle_r = m_depthHeightWidthObstacle[0];
                break;
            case 1:
                f_referenceSurfaceObstacle_r = rightView;
                f_widthSensorObstacle_r = m_depthHeightWidthObstacle[0];
                f_lengthSensorObstacle_r = m_depthHeightWidthObstacle[2];
                break;
            case 2:
                f_referenceSurfaceObstacle_r = frontView;
                f_widthSensorObstacle_r = m_depthHeightWidthObstacle[2];
                f_lengthSensorObstacle_r = m_depthHeightWidthObstacle[0];
                break;
            case 3:
                f_referenceSurfaceObstacle_r = leftView;
                f_widthSensorObstacle_r = m_depthHeightWidthObstacle[0];
                f_lengthSensorObstacle_r = m_depthHeightWidthObstacle[2];
                break;
            default:
                throw;
        }
        f_heightSensorObstacle_r = m_depthHeightWidthObstacle[1];
        // CRadar: height; CVideo: width

        //obstacle position in the middle of the relevant view of the obstacle
        f_xSensorObstacle_r = m_xSensorContourPoint[l_indexRelevantSide] + 0.5 * m_xSensorContourLine[l_indexRelevantSide];
        f_ySensorObstacle_r = m_ySensorContourPoint[l_indexRelevantSide] + 0.5 * m_ySensorContourLine[l_indexRelevantSide];
        f_zSensorObstacle_r = m_zSensorContourPoint[l_indexRelevantSide] + 0.5 * m_zSensorContourLine[l_indexRelevantSide];
        f_azimuthSensorObstacle_r = ::sim::atan2( f_ySensorObstacle_r, f_xSensorObstacle_r );
        f_yawAngleSensorObstacle_r = ::sim::normalizeAnglePosNegPI( m_yawAngleObstacle - m_yawAngle );
        // f_yawAngleEgoObstacle_r = ::sim::normalizeAnglePosNegPI( m_yawAngleObstacle - m_angleRollPitchYawEgo[2] );
        f_distanceSensorObstacle_r = ::sim::sqrt( ::sim::pow( f_xSensorObstacle_r, 2 ) + ::sim::pow( f_ySensorObstacle_r, 2 ) + ::sim::pow( f_zSensorObstacle_r, 2 ) );

        f_vXSensorObstacle_r = m_vXYZSensorObstacle.X();
        f_vYSensorObstacle_r = m_vXYZSensorObstacle.Y();
        f_vZSensorObstacle_r = m_vXYZSensorObstacle.Z();
        f_visibilityObstacle_r = m_visibilityObstacle;

        f_aXVehicleObstacle_r = m_aXYZVehicleObstacle.X();
        f_aYVehicleObstacle_r = m_aXYZVehicleObstacle.Y();
        f_aZVehicleObstacle_r = m_aXYZVehicleObstacle.Z();

        return true;
    }
    else
    {
        f_indexObstacle_r = 0;
        f_visibilityObstacle_r = 0.0;
        f_typeObstacle_r = 0;
        f_referenceSurfaceObstacle_r = 0;
        f_widthSensorObstacle_r  = 0;
        f_lengthSensorObstacle_r = 0;
        f_heightSensorObstacle_r = 0;

        f_xSensorObstacle_r = 0;
        f_ySensorObstacle_r = 0;
        f_zSensorObstacle_r = 0;
        f_distanceSensorObstacle_r = 0;

        f_azimuthSensorObstacle_r = 0;
        f_yawAngleSensorObstacle_r = 0;

        f_vXSensorObstacle_r = 0;
        f_vYSensorObstacle_r = 0;
        f_vZSensorObstacle_r = 0;

        f_aXVehicleObstacle_r = 0;
        f_aYVehicleObstacle_r = 0;
        f_aZVehicleObstacle_r = 0;

        return false;
    }
    return false; //avoid compiler warning
}
