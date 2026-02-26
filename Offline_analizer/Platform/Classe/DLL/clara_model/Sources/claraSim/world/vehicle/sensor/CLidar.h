#ifndef CLidar_H
#define CLidar_H
/*!
********************************************************************************
@class CLidar
@ingroup sensor
@brief  simulation of a Lidar sensor (ACC)

@author Robert Erhart, ett2si (06.07.2016)
@copyright (c) Robert Bosch GmbH 2016-2024. All rights reserved.
********************************************************************************
@TODO : check computation of o_dvLateralLidarObstacle and o_dvRadialLidarObstacle
@remark
- obstacle box
@verbatim
            LF          RF
             ____________
            |\           \
          P3| \     o   P2\
            |  \___________\
            \   |           |
      depth  \P0| x  x  x   |P1  height
              \ |           |
                -------------
               LR   width  RR

  0 = zero-point =~ course line
  x = 1st reflection point
@endverbatim

- course width
@verbatim
                #--------0--------#
                 width/2   width/2
  0 = zero-point =~  course line
@endverbatim
********************************************************************************
@param[in,out] various generic sensor inputs and outputs - see CSensor.h!

********************************************************************************
- Vertices
@param[out] o_xWorldVertex                [m]     (vector) x position sensor vertex (world coordinate system)
@param[out] o_yWorldVertex                [m]     (vector) y position sensor vertex (world coordinate system)
@param[out] o_zWorldVertex                [m]     (vector) z position sensor vertex (world coordinate system)
@param[out] o_xLidarVertex                [m]     (vector) x position sensor vertex (sensor coordinate system)
@param[out] o_yLidarVertex                [m]     (vector) y position sensor vertex (sensor coordinate system)
@param[out] o_zLidarVertex                [m]     (vector) z position sensor vertex (sensor coordinate system)
@param[out] o_alphaLidarVertex            [rad]   (vector) angle between sensor-axis and location (x-y plane)
@param[out] o_dLidarVertex                [m]     (vector) distance between sensor and vertex
@param[out] o_dvRadialVertex              [m/s]   (vector) relative radial velocity obstacle (sensor coordinate system)
@param[out] o_dvLateralVertex             [m/s]   (vector) relative lateral velocity obstacle (sensor coordinate system)
@param[out] o_typeVertex                  [enum]  (vector) obstacle type
@param[out] o_visibilityVertex            [0..1]  (vector) visibility vertex; 1.0:=fully visibility
@param[out] o_prioIndexVertex             []      (vector) indexes of vertex sorted by prio

- Obstacle
@param[out] o_xWorldObstacle              [m]     (vector) x position of the middle of the relevant object side (world coordinate system)
@param[out] o_yWorldObstacle              [m]     (vector) y position of the middle of the relevant object side (world coordinate system)
@param[out] o_zWorldObstacle              [m]     (vector) z position of the middle of the relevant object side (world coordinate system)";
@param[out] o_dvLateralLidarObstacle      [m/s]   (vector) relative lateral velocity obstacle (sensor coordinate system)
@param[out] o_dvRadialLidarObstacle       [m/s]   (vector) relative radial velocity between Lidar and object-box (sensor coordinate system)
@param[out] o_prioIndexObstacle           []      (vector) indexes of obstacle sorted by prio

********************************************************************************
- Configuration
@param[in,out] p_maxNumberOfVerticesPerObstacles []  maximum number of reflections. if number is even a underfloor reflection is generated
@param[in,out] p_angleSeparationSensor           [rad]    angle separation of the lidar sensor
@param[in,out] p_angleStartFieldOfView           [rad]    start angle of field of view in radar coordinates (left is positive)
@param[in,out] p_angleFieldOfViewArray           [rad]    (vector) array of field of view segment angles
@param[in,out] p_maxRangeFieldOfViewArray        [m]      (vector) array of field of view segment max ranges
********************************************************************************
@ToDo: derive from CSensor (to be developed) class
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CLidarDoc
{
    const auto o_xWorldVertex = "[m] (vector) x position sensor vertex (world coordinate system)";
    const auto o_yWorldVertex = "[m] (vector) y position sensor vertex (world coordinate system)";
    const auto o_zWorldVertex = "[m] (vector) z position sensor vertex (world coordinate system)";
    const auto o_xLidarVertex = "[m] (vector) x position sensor vertex (sensor coordinate system)";
    const auto o_yLidarVertex = "[m] (vector) y position sensor vertex (sensor coordinate system)";
    const auto o_zLidarVertex = "[m] (vector) z position sensor vertex (sensor coordinate system)";
    const auto o_alphaLidarVertex = "[rad] (vector) angle between sensor-axis and location (x-y plane)";
    const auto o_dLidarVertex = "[m] (vector) distance between sensor and vertex";
    const auto o_dvRadialVertex = "[m/s] (vector) relative radial velocity obstacle (sensor coordinate system)";
    const auto o_dvLateralVertex = "[m/s] (vector) relative lateral velocity obstacle (sensor coordinate system)";
    const auto o_typeVertex = "[enum] (vector) obstacle type";
    const auto o_visibilityVertex = "[0..1] (vector) visibility vertex; 1.0:=fully visibility";
    const auto o_prioIndexVertex = "[] (vector) indexes of vertex sorted by prio";

    const auto o_xWorldObstacle = "[m] (vector) x position of the middle of the relevant object side (world coordinate system)";
    const auto o_yWorldObstacle = "[m] (vector) y position of the middle of the relevant object side (world coordinate system)";
    const auto o_zWorldObstacle = "[m] (vector) z position of the middle of the relevant object side (world coordinate system)";

    const auto o_dvLateralLidarObstacle = "[m/s] (vector) relative lateral velocity obstacle (sensor coordinate system)";
    const auto o_dvRadialLidarObstacle = "[m/s] (vector) relative radial velocity between Lidar and object-box (sensor coordinate system)";
    const auto o_prioIndexObstacle = "[] (vector) indexes of obstacle sorted by prio";

    const auto p_maxNumberOfVerticesPerObstacles = "[] maximum number of reflections. if number is even a underfloor reflection is generated";
    const auto p_angleSeparationSensor = "[rad] angle separation of the lidar sensor";
}

#include "CSensor.h"
#include <claraSim/world/obstacle/CObstacles.h>
#include <vector>


//forward declaration
class CObstacleLidar;

////*********************************
//// CLidar
////*********************************
class CLidar : public CSensor
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CLidar();
    virtual ~CLidar();

    //*******************************
    //classes
    //*******************************
    ::std::vector<CObstacleLidar> m_obstacle_a;

    //*******************************
    //messages
    //*******************************
public:
    CMessageOutput<CFloatVector> o_xWorldVertex;
    CMessageOutput<CFloatVector> o_yWorldVertex;
    CMessageOutput<CFloatVector> o_zWorldVertex;

    CMessageOutput<CFloatVector> o_xLidarVertex;
    CMessageOutput<CFloatVector> o_yLidarVertex;
    CMessageOutput<CFloatVector> o_zLidarVertex;
    CMessageOutput<CFloatVector> o_alphaLidarVertex;
    CMessageOutput<CFloatVector> o_dLidarVertex;
    CMessageOutput<CFloatVector> o_dvRadialVertex;
    CMessageOutput<CFloatVector> o_dvLateralVertex;
    CMessageOutput<CIntVector> o_typeVertex;
    CMessageOutput<CFloatVector> o_visibilityVertex;
    CMessageOutput<CIntVector> o_prioIndexVertex;

    CMessageOutput<CFloatVector> o_xWorldObstacle;
    CMessageOutput<CFloatVector> o_yWorldObstacle;
    CMessageOutput<CFloatVector> o_zWorldObstacle;

    CMessageOutput<CFloatVector> o_dvLateralLidarObstacle;
    CMessageOutput<CFloatVector> o_dvRadialLidarObstacle;
    CMessageOutput<CIntVector> o_prioIndexObstacle;
    CMessageParameter<CInt>   p_maxNumberOfVerticesPerObstacles;
    CMessageParameter<CFloat> p_angleSeparationSensor;

private:
    // input messages defined in CSensor

    //*******************************
    // methods
    //*******************************
public:
    /*!
     * Initialization of CLidar object.
     *
     * @param[in] f_{x,y,z}World              ego vehicle position vector (world coordinates)
     * @param[in] f_velocity{X,Y,Z}World     ego vehicle velocity vector (world coordinates)
     * @param[in] f_accelerationXYZVehicleEgo ego vehicle acceleration vector (ego coordinates)
     * @param[in] f_Angles{roll,pitch,yaw}Ego ego vehicle orientation vector (world coordinates)
     * @param[in] f_yawRateEgo                ego vehicle yaw rate
     * @param[in] f_obstacles_r               CObstacles object for definition of detectable objects
     * @param[in] f_staticSimulation          bool: switch sensor update behaviour (static sim: not p or dynamic simulation
     *
     */
    void init( IMessage<CFloatVectorXYZ>& f_xyzWorld,
               IMessage<CFloatVectorXYZ>& f_velocityXYZWorld,
               IMessage<CFloatVectorXYZ>& f_accelerationXYZVehicleEgo,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYawEgo,
               IMessage<CFloat>& f_yawRateEgo,
               CObstacles& f_obstacles_r,
               IMessage<CBool>& f_staticSimulation );

private:
    /*!
     * "calc" first calls CSensor's "calc" gets sensor coordinates, velocities, and orientation in the
     *  world from input messages. This updates overall sensor and viewSegments output.
     *
     * Second, it calculates obstacle visibilities and sorts obstacles accordingly.
     * Finally, it calculates output messages for obstacles, reflections, and
     * locations.
     */
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
    CInt m_numberOfObstaclesDynamic;
    CInt m_numberOfVerticesDynamic;
    CInt m_numberOfObstaclesStatic;
    CInt m_numberOfVerticesStatic;
    size_t m_numberOfVertices;

    CFloatVector m_obstacleDynamicVisibility;
    CIntVector m_obstacleDynamicVisibilityIndexList;
    CFloatVector m_obstacleStaticVisibility;
    CIntVector m_obstacleStaticVisibilityIndexList;
};


////*********************************
//// CObstacleLidar
////*********************************
class CObstacleLidar : public CObstacleSensor
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CObstacleLidar();
    virtual ~CObstacleLidar();
    //*******************************
    //classes
    //*******************************
public:
private:

    //*******************************
    // methods
    //*******************************
public:
    /*!
     * Calculate the obstacle infos
     * @param[in]  ...
     * @param[out] ...
     * @param[out] ...
     */
    CBool updateObstacleMessages( CInt& f_indexObstacle, CInt& f_typeObstacle_r, CInt& f_referenceSurfaceObstacle_r, CFloat& f_visibilityObstacle_r,
                                  CFloat& f_xSensorObstacle_r, CFloat& f_ySensorObstacle_r, CFloat& f_zSensorObstacle_r,
                                  CFloat& f_azimuthSensorObstacle_r, CFloat& f_yawAngleSensorObstacle,
                                  CFloat& f_heightSensorObstacle_r, CFloat& f_widthSensorObstacle_r, CFloat& f_lengthSensorObstacle_r,
                                  CFloat& f_vXSensorObstacle_r, CFloat& f_vYSensorObstacle_r, CFloat& f_vZSensorObstacle_r,
                                  CFloat& f_aXVehicleObstacle_r, CFloat& f_aYVehicleObstacle_r, CFloat& f_aZVehicleObstacle_r,
                                  CFloat& f_distanceSensorObstacle_r,
                                  CInt f_referenceSurfaceObstacleFixed,
                                  CFloat& f_xWorldObstacle_r, CFloat& f_yWorldObstacle_r, CFloat& f_zWorldObstacle_r,
                                  CFloat& f_dvRadialLidar_r, CFloat& f_dvLateralLidar_r );

    /*!
     * Calculate the reflections of the obstacle
     * @param[in]  ...
     * @param[out] f_heightVertex_a [m] height of the reflection surface
     * @param[out] ...
     */
    size_t calcVertices( CInt f_startIndex, CFloat f_angleSeparation, CInt f_maxNoOfVertices,
                       CFloatVector& f_xWorldVertex, CFloatVector& f_yWorldVertex, CFloatVector& f_zWorldVertex,
                       CFloatVector& f_xLidarVertex, CFloatVector& f_yLidarVertex, CFloatVector& f_zLidarVertex, CFloatVector& f_alphaLidarVertex,
                       CFloatVector& f_dLidarVertex, CFloatVector& f_dvRadialVertex, CFloatVector& f_dvLateralVertex,
                       CIntVector& f_typeVertex, CFloatVector& f_visibilityVertex );

private:
    CFloat calcIntersectionPoint( CInt f_contourIndex );
    //*******************************
    //classes
    //*******************************
public:
private:
    //*******************************
    //variables
    //*******************************
private:
    /* CLidar-specific members */
};

#endif // CLidar_H
