#ifndef CSensor_H
#define CSensor_H
/*!
********************************************************************************
@class CSensor
@ingroup sensor
@brief  base class for different sensor types

@author Andreas Brunner, bnr2lr
@author Robert Erhart, ett2si (08.04.2020)
@copyright (c) Robert Bosch GmbH 2020-2024. All rights reserved.
********************************************************************************
@TODO: update output message description for doxygen
@TODO: split calculation of properties for object sensor and vertex type sensor
@TODO: change 'depthHeightWidthObstacle' variables to XYZ convention (depthWidthHeight) in CObstacleSensor and whereever its 'init' method is called
@remark
- obstacle box
@verbatim

3D view:
          LF           RF
            ____________
           |\          .\
      P3-->| \         .<--P2
           |. \ . . . ..  \
           \   \           \
      depth \   \___________\
             \  |   o       | height
           P0-->|           |<--P1
               \|___________|
                    width
               LR           RR

  o = zero-point (coordinate origin) =~ course line
  P0 to P3 = contour points (center of vertical box edges)
  obstacle side 'i' spans between contour point P_i and P_i+1

top view:

     P3 --> . . . . . . . <-- P2
            :           :
            :           :
            :     o     :
            :           :
            :           :
     P0 --> .___________. <-- P1
                 ^
                 |
            contour line (connecting P0 and P1)

The CSensor sensor model is parametrized using the CSensor parameter messages.
Here, the sensor position and orientation in the vehicle can be set, as well as
the field of view (divided into multiple segments), the maximum number of
detectable obstacles and so on.

INPUTS to the sensor model are related to the ego vehicle as well as static,
and dynamic obstacles. Examples are their respective positions, velocities, and
rotation angles (in world coordinates), as well as obstacle type, visibilities,
and dimensions.

OUTPUTS are related to the sensor itself (position, orientation) or its
measurement results. In the radar model, output of reflections, locations, and
obstacles (objects) is supported.


- Ego input variables

@param[in] i_xyzWorldVehicle                [m/s]   x,y,z position vector of ego vehicle (world coordinate system)
@param[in] i_vWorldVehicle                  [m/s]   x,y,z velocity vector of ego vehicle (world coordinate system)
@param[in] i_aWorldVehicle                  [m/s]   x,y,z acceleration vector of ego vehicle (vehicle coordinate system)
@param[in] i_angleRollPitchYawVehicle       [rad]  (vector) of ego vehicle's roll, pitch, and yaw angles
@param[in] i_yawRateVehicle                 [rad/s] yaw rate ego vehicle
@param[in] i_staticSimulation               [bool] static or dynamic simulation

extracted from f_obstacles_r input argument:

@param[in] i_xyzWorldObstacleDynamic        [m]    (vector) (no. of obstacles, 3) x,y,z-world coordinates obstacles
@param[in] i_vWorldObstacleDynamic          [m/s] (vector) (no. of obstacles, 3) obstacles' velocities (world coordinates)
@param[in] i_aObstacleDynamic               [m/s²] (vector) acceleration obstacle coordinates
@param[in] i_yawAngleObstacleDynamic        [rad]  (vector) yaw-world coordinates obstacle
@param[in] i_typeObstacleDynamic            [INVISIBLE, POINT, CAR, MOTORBIKE, TRUCK, BUS, BICYCLE, PEDESTRIAN, DELINEATOR] (vector)
@param[in] i_depthObstacleDynamic           [m]    (vector) length of obstacle
@param[in] i_heightObstacleDynamic          [m]    (vector) height of obstacle
@param[in] i_widthObstacleDynamic           [m]    (vector) width of obstacle
@param[in] i_visibilityObstacleDynamic      [m]    (vector) visibility of obstacle; may be used to suppress obstacle visibility, fade it out, ...

@param[in] i_xWorldContourObstacleDynamic   [m]    (vector) Contour x-points of obstacle
@param[in] i_yWorldContourObstacleDynamic   [m]    (vector) Contour y-points of obstacle
@param[in] i_zWorldContourObstacleDynamic   [m]    (vector) Contour z-points of obstacle

@param[in] i_xyzWorldObstacleStatic         [m]    (vector) (no. of obstacles, 3) x,y,z-world coordinates obstacles
@param[in] i_yawAngleObstacleStatic         [rad]  (vector) yaw-world coordinates obstacle
@param[in] i_typeObstacleStatic             [INVISIBLE, POINT, CAR, MOTORBIKE, TRUCK] (vector)
@param[in] i_depthObstacleStatic            [m]    (vector) length of obstacle
@param[in] i_heightObstacleStatic           [m]    (vector) height of obstacle
@param[in] i_widthObstacleStatic            [m]    (vector) width of obstacle
@param[in] i_visibilityObstacleStatic       [m]    (vector) visibility of obstacle; may be used to suppress obstacle visibility, fade it out, ...
@param[in] i_xWorldContourObstacleStatic    [m]    (vector) Contour x-points of obstacle
@param[in] i_yWorldContourObstacleStatic    [m]    (vector) Contour y-points of obstacle
@param[in] i_zWorldContourObstacleStatic    [m]    (vector) Contour z-points of obstacle


- Sensor: all these output messages are only used for drawing the GUI!

@param[out] o_xyzWorldSensor            [m]     (vector) Sensor x,y,z position vector (world coordinate system)
@param[out] o_rotationWorld             [rad]   (vector) Sensor rotation angle vector (x-, y-, z-axis) w.r.t. world coordinate system
@param[out] o_xViewSegment              [m]     (vector) x-Info for view segments [[x1View1,x2View1,x3View1],[x1View2,x2View2,x3View2], ...]
@param[out] o_yViewSegment              [m]     (vector) y-Info for view segments [[y1View1,y2View1,y3View1],[y1View2,y2View2,y3View2], ...]
@param[out] o_zViewSegment              [m]     (vector) z-Info for view segments [[z1View1,z2View1,z3View1],[z1View2,z2View2,z3View2], ...]

@param[out] o_indexObstacle             [-n..+m] (vector) obstacle index: 0=invalid, [-n, -1]=static obstacle, [1, m]=dynamic obstacle
@param[out] o_typeObstacle              [enum] (vector) obstacle type
@param[out] o_visibilityObstacle        [%/100] (vector) visibility of object. 1.0:=fully visibility
@param[out] o_yawAngleSensorObstacle    [rad] (vector) relative yaw angle between sensor and object-box
@param[out] o_referenceSurfaceObstacle  [0..4] (vector) invalid = 0, rearView = 1, rightView = 2, frontView = 3, leftView = 4

@param[out] o_xSensorObstacle           [m] (vector) x position of the middle of the relevant object side (sensor coordinate system). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.
@param[out] o_ySensorObstacle           [m] (vector) y position of the middle of the relevant object side (sensor coordinate system). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.
@param[out] o_zSensorObstacle           [m] (vector) z position of the middle of the relevant object side (sensor coordinate system). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.
@param[out] o_vXSensorObstacle          [m/s] (vector) obstacle X velocity (sensor coordinate system)
@param[out] o_vYSensorObstacle          [m/s] (vector) obstacle Y velocity (sensor coordinate system)
@param[out] o_vZSensorObstacle          [m/s] (vector) obstacle Z velocity (sensor coordinate system)
@param[out] o_aXVehicleObstacle         [m/s]   (vector) relative acceleration x (ego coordinate system)
@param[out] o_aYVehicleObstacle         [m/s]   (vector) relative acceleration y (ego coordinate system)
@param[out] o_aZVehicleObstacle         [m/s]   (vector) relative acceleration z (ego coordinate system)

@param[out] o_widthSensorObstacle       [m] (vector) width of relevant object side (as detected by sensor). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.
@param[out] o_depthSensorObstacle       [m] (vector) depth of relevant object side (as detected by sensor). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.
@param[out] o_heightSensorObstacle      [m] (vector) height of relevant object side (as detected by sensor). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.
@param[out] o_alphaSensorObstacle       [rad]  (vector) angle between sensor x-axis and center of the relevant object side (projection to x-y plane). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.
@param[out] o_distanceSensorObstacle    [m] (vector) distance between sensor and obstacle


- Configuration

@param[in,out] p_xyzVehicleMountingPos         [m]     mounting position vector (x,y,z) of sensor (vehicle coordinate system)
@param[in,out] p_angleRollPitchYawVehicleMounting [rad]   mounting angle vector (0, elevation angle:-pi/2 to +pi/2 , azimuth angle) of sensor (vehicle coordinate system)
@param[in,out] p_anglesFieldOfViewSegments     [rad] (vector) Edge angles of the sensor field of view segments. For N view segments, N+1 angles need to be defined here.
@param[in,out] p_maxRangesFieldOfViewSegments  [m]   (vector) Maximum range of vision of each individual sensor field of view segment. For N view segments, N max ranges need to be defined here.
@param[in,out] p_minRangesFieldOfViewSegments  [m]   (vector) Minimum range of vision of each individual sensor field of view segment. For N view segments, N min ranges need to be defined here.

@param[in,out] p_sensorConfiguration           []      connector 1:down / -1: up / 0:no Sensor
@param[in,out] p_maxNumberOfRelevantObstacles  [] maximum number of obstacles

@param[in,out] p_referenceSurfaceObstacleFixed      [0..4] default = 0 ,reference surface is calculated dynamically otherwise reference fixed to rearView = 1, rightView = 2, frontView = 3, leftView = 4. USE ONLY FOR OBJECT SENSORS!

********************************************************************************

*/

// online documentation of the messages for the scene generator
namespace CSensorDoc
{
    const auto o_xyzWorldSensor = "[m] (vector) Sensor x,y,z position vector (world coordinate system)";
    const auto o_rotationWorld = "[rad] (vector) Sensor rotation angle vector (x-, y-, z-axis) w.r.t. world coordinate system";
    // view segment coordinate messages are only used for drawing the GUI
    const auto o_xViewSegment = "[m] (vector) x-Info for view segments [[x1View1,x2View1,x3View1],[x1View2,x2View2,x3View2], ...]";
    const auto o_yViewSegment = "[m] (vector) y-Info for view segments [[y1View1,y2View1,y3View1],[y1View2,y2View2,y3View2], ...]";
    const auto o_zViewSegment = "[m] (vector) z-Info for view segments [[z1View1,z2View1,z3View1],[z1View2,z2View2,z3View2], ...]";

    const auto o_indexObstacle =        "[-n..+m] (vector) obstacle index: 0=invalid, [-n, -1]=static obstacle, [1, m]=dynamic obstacle";
    const auto o_typeObstacle =         "[enum] (vector) obstacle type";
    const auto o_visibilityObstacle =   "[%/100] (vector) visibility of object. 1.0:=fully visibility";
    const auto o_yawAngleSensorObstacle = "[rad] (vector) relative yaw angle between sensor and object-box";

    const auto o_referenceSurfaceObstacle = "[0..4] (vector) invalid = 0, rearView = 1, rightView = 2, frontView = 3, leftView = 4";

    const auto o_xSensorObstacle = "[m] (vector) x position of the middle of the relevant object side (sensor coordinate system). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.";
    const auto o_ySensorObstacle = "[m] (vector) y position of the middle of the relevant object side (sensor coordinate system). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.";
    const auto o_zSensorObstacle = "[m] (vector) z position of the middle of the relevant object side (sensor coordinate system). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.";

    const auto o_vXSensorObstacle = "[m/s] (vector) obstacle X velocity (sensor coordinate system)";
    const auto o_vYSensorObstacle = "[m/s] (vector) obstacle Y velocity (sensor coordinate system)";
    const auto o_vZSensorObstacle = "[m/s] (vector) obstacle Z velocity (sensor coordinate system)";

    const auto o_aXVehicleObstacle = "[m/s]   (vector) relative acceleration x (ego coordinate system)";
    const auto o_aYVehicleObstacle = "[m/s]   (vector) relative acceleration y (ego coordinate system)";
    const auto o_aZVehicleObstacle = "[m/s]   (vector) relative acceleration z (ego coordinate system)";

    const auto o_widthSensorObstacle = "[m] (vector) width of relevant object side (as detected by sensor). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.";
    const auto o_depthSensorObstacle = "[m] (vector) depth of relevant object side (as detected by sensor). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.";
    const auto o_heightSensorObstacle = "[m] (vector) height of relevant object side (as detected by sensor). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.";

    const auto o_alphaSensorObstacle =      "[rad]  (vector) angle between sensor x-axis and center of the relevant object side (projection to x-y plane). The side can be determined using the 'o_referenceSurfaceObstacle' parameter.";

    const auto o_distanceSensorObstacle = "[m] (vector) distance between sensor and obstacle";

    const auto p_xyzVehicleMountingPos = "[m]    (vector) Sensor's mounting position vector (x,y,z) of sensor (vehicle coordinate system)";
    const auto p_angleRollPitchYawVehicleMounting = "[rad]  (vector) Sensor's mounting angle vector (0, pitch angle = negative (!) elevation angle:-pi/2 to +pi/2, azimuth angle) of sensor (vehicle coordinate system)";

    const auto p_anglesFieldOfViewSegments = "[rad] (vector) Edge angles of the sensor field of view segments. For N view segments, N+1 angles need to be defined here.";
    const auto p_maxRangesFieldOfViewSegments  = "[m]   (vector) Maximum range of vision of each individual sensor field of view segment. For N view segments, N max ranges need to be defined here.";
    const auto p_minRangesFieldOfViewSegments  = "[m]   (vector) Minimum range of vision of each individual sensor field of view segment. For N view segments, N min ranges need to be defined here.";

    const auto p_sensorConfiguration = "[-1, 0, 1] connector 1:down / -1: up / 0:no Sensor";
    const auto p_maxNumberOfRelevantObstacles = "[] maximum number of obstacles";

    const auto p_referenceSurfaceObstacleFixed = "[0..4] default = 0 ,reference surface is calculated dynamically otherwise reference fixed to rearView = 1, rightView = 2, frontView = 3, leftView = 4. USE ONLY FOR OBJECT SENSORS!";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/framework/CViewSegment.h>
#include <claraSim/world/obstacle/CObstacleStatic.h>
#include <claraSim/world/obstacle/CObstacleDynamic.h>
#include <claraSim/world/obstacle/CObstacles.h>
#include <vector>

//forward declaration
class CObstacleSensor;

////*********************************
//// CSensor
////*********************************
class CSensor : public CModule<0, 2, true>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CSensor();
    virtual ~CSensor();

    //*******************************
    // classes
    //*******************************
private:
protected:
public:

    //*******************************
    // messages
    //*******************************
public:
    // sensor information
    CMessageOutput<CFloatVectorXYZ> o_xyzWorldSensor;
    CMessageOutput<CFloatVectorXYZ> o_rotationWorld;
    CMessageOutput<CFloatVector> o_xViewSegment, o_yViewSegment, o_zViewSegment;

    CMessageOutput<CIntVector> o_indexObstacle;
    CMessageOutput<CIntVector> o_typeObstacle;
    CMessageOutput<CFloatVector> o_visibilityObstacle;
    CMessageOutput<CFloatVector> o_distanceSensorObstacle;
    CMessageOutput<CFloatVector> o_xSensorObstacle, o_ySensorObstacle, o_zSensorObstacle;
    CMessageOutput<CFloatVector> o_vXSensorObstacle, o_vYSensorObstacle, o_vZSensorObstacle;
    CMessageOutput<CFloatVector> o_aXVehicleObstacle, o_aYVehicleObstacle, o_aZVehicleObstacle;

    CMessageOutput<CFloatVector> o_yawAngleSensorObstacle;
    CMessageOutput<CFloatVector> o_alphaSensorObstacle;
    CMessageOutput<CIntVector> o_referenceSurfaceObstacle;

    CMessageOutput<CFloatVector> o_widthSensorObstacle, o_depthSensorObstacle, o_heightSensorObstacle;

    // sensor properties
    CMessageParameter<CFloatVectorXYZ> p_xyzVehicleMountingPos;
    CMessageParameter<CFloatVectorXYZ> p_angleRollPitchYawVehicleMounting;

    CMessageParameter<CFloatVector> p_anglesFieldOfViewSegments;
    CMessageParameter<CFloatVector> p_maxRangesFieldOfViewSegments;
    CMessageParameter<CFloatVector> p_minRangesFieldOfViewSegments;

    CMessageParameter<CInt>   p_sensorConfiguration;
    CMessageParameter<CInt>   p_maxNumberOfRelevantObstacles;
    CMessageParameter<CInt>   p_referenceSurfaceObstacleFixed;

protected:
    // to use these input messages in derived classes, "protected" declaration is needed
    CMessageInput<CFloatVectorXYZ> i_xyzWorldVehicle;
    CMessageInput<CFloatVectorXYZ> i_vWorldVehicle;
    CMessageInput<CFloatVectorXYZ> i_aWorldVehicle;
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYawVehicle;
    CMessageInput<CFloat>          i_yawRateVehicle;
    CMessageInput<CBool>           i_staticSimulation;

    CMessageInput<CFloatVectorXYZ, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_xyzWorldObstacleDynamic;
    CMessageInput<CFloatVectorXYZ, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_vWorldObstacleDynamic;
    CMessageInput<CFloat, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_aObstacleDynamic;
    CMessageInput<CFloat, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_yawAngleObstacleDynamic;
    CMessageInput<CInt,   CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_typeObstacleDynamic;
    CMessageInput<CFloat, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_depthObstacleDynamic;
    CMessageInput<CFloat, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_heightObstacleDynamic;
    CMessageInput<CFloat, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_widthObstacleDynamic;
    CMessageInput<CFloat, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_visibilityObstacleDynamic;

    CMessageInput<CFloatVector, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_xWorldContourObstacleDynamic;
    CMessageInput<CFloatVector, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_yWorldContourObstacleDynamic;
    CMessageInput<CFloatVector, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_zWorldContourObstacleDynamic;

    CMessageInput<CFloatVectorXYZ, CObstacleStatic, CModuleVector<CObstacleStatic> > i_xyzWorldObstacleStatic;
    CMessageInput<CFloat, CObstacleStatic, CModuleVector<CObstacleStatic> > i_yawAngleObstacleStatic;
    CMessageInput<CInt,   CObstacleStatic, CModuleVector<CObstacleStatic> > i_typeObstacleStatic;
    CMessageInput<CFloat, CObstacleStatic, CModuleVector<CObstacleStatic> > i_depthObstacleStatic;
    CMessageInput<CFloat, CObstacleStatic, CModuleVector<CObstacleStatic> > i_heightObstacleStatic;
    CMessageInput<CFloat, CObstacleStatic, CModuleVector<CObstacleStatic> > i_widthObstacleStatic;
    CMessageInput<CFloat, CObstacleStatic, CModuleVector<CObstacleStatic> > i_visibilityObstacleStatic;
    CMessageInput<CFloatVector, CObstacleStatic, CModuleVector<CObstacleStatic> > i_xWorldContourObstacleStatic;
    CMessageInput<CFloatVector, CObstacleStatic, CModuleVector<CObstacleStatic> > i_yWorldContourObstacleStatic;
    CMessageInput<CFloatVector, CObstacleStatic, CModuleVector<CObstacleStatic> > i_zWorldContourObstacleStatic;

    //*******************************
    // methods
    //*******************************
public:
    /*!
     * Initialization of CSensor object.
     *
     * @param[in] f_xyzWorld                ego vehicle position vector (world coordinates)
     * @param[in] f_velocityXYZWorld       ego vehicle velocity vector (world coordinates)
     * @param[in] f_accelerationXYZVehicle  Ego ego vehicle acceleration vector (ego coordinates)
     * @param[in] f_angleRollPitchYawEgo   ego vehicle orientation vector (world coordinates)
     * @param[in] f_yawRateEgo              ego vehicle yaw rate
     * @param[in] f_obstacles_r             CObstacles vector pointer for definition of detectable objects
     * @param[in] f_staticSimulation        bool: switch sensor update behaviour (static sim: not p or dynamic simulation
     *
     */
    void init( IMessage<CFloatVectorXYZ>& f_xyzWorld,
               IMessage<CFloatVectorXYZ>& f_velocityXYZWorld,
               IMessage<CFloatVectorXYZ>& f_accelerationXYZVehicleEgo,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYawEgo,
               IMessage<CFloat>& f_yawRateEgo,
               CObstacles& f_obstacles_r,
               IMessage<CBool>& f_staticSimulation );
protected:
    /*!
     * Sort 'indexVector' with respect to the values given in 'prioVector'.
     *
     * @param f_indexVector_r vector of integer indices to be sorted
     * @param f_prioVector_r  vector of priorities, used as sorting criterion
     *
     * \warning Note that indexVector may contain only numbers from zero to prioVector.size()-1.
     * \warning Otherwise undefined behaviour can occur.
     */
    void heapSortWithComparsionCriterion( CIntVector& f_indexVector_r, const CFloatVector& f_prioVector_r );

    /*!
     * 'calc' first gets sensor coordinates, velocities, and orientation in the
     *  world from input messages. It updates overall sensor and viewSegments output.
     *
     * Individual part so far:
     * Second, it calculates obstacle visibilities and sorts obstacles accordingly.
     * Finally, it calculates output messages for obstacles, reflections, and
     * locations.
     */
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************

private:

    //*******************************
    //variables
    //*******************************
public:


protected:
    // CFloatVector m_ABxSensor, m_ABySensor, m_ABzVideo;
    CFloatVectorXYZ m_velocityXYZWorldSensor;   // sensor velocity in world coordinates
    CFloatVectorXYZ m_sensorVelocityFromRotation;
    CFloatVectorXYZ m_angleXYZVehicle;
    ::std::vector<CViewSegment> m_viewSegment_a;
private:
};


/*!
********************************************************************************
@class CObstacleSensor
@ingroup sensor
@brief  Obstacle object holding sensor and obstacle properties for calculation in sensor model.
@remark See derived sensor classes' 'm_obstacle_a' vector.
@remark 'init()' updates the CObstacleSensor internal variables with given input values.
        'calcProperties()' performes calculations based on these values.
        'updateObstacleMessages()' updates the CObstacleSensor's output messages.

@author Robert Erhart (ett2si), Andreas Brunner (bnr2lr) [08.07.2005, 31.05.2016, 02.06.2020]
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************/

class CObstacleSensor
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CObstacleSensor();
    virtual ~CObstacleSensor();
    //*******************************
    // methods
    //*******************************
public:
    void init();

    /*!
     * Initialize CObstacleSensor object and update member variables (vectorized input version).
     *
     * @param[in]  f_indexObstacle          new object index
     * @param[in]  f_xyz                    Sensor position (world coordinates)
     *      * ... TODO: add full description
     * @param[out] ...
     */
    void init( CInt f_indexObstacle,
               CFloatVector f_xyzPositionWorldSensor,
               CFloatVector f_xyzVelocityWorldSensor,
               CFloatVector f_xyzAccelerationVehicleEgo,
               CFloatVector f_rollPitchYawAnglesEgo,
               CFloatVector f_sensorMountingAngles,
               CFloatVector f_xyzPositionObstacle, CFloatVector f_xyzVelocityWorldObstacle,
               CFloat f_aObstacle, CFloat f_yawAngleObstacle, CInt f_typeObstacle,
               CFloatVector f_depthHeightWidthObstacle,
               CFloat f_visibilityObstacle,
               CFloatVector& f_xWorldContourObstacle, CFloatVector& f_yWorldContourObstacle, CFloatVector& f_zWorldContourObstacle );

    /*!
     * Perform internal computations on CObstacleSensor object.
     * TODO: split calculation of properties for object sensor and vertex type sensor
     */
    void calcProperties();

    /*!
     * Update CObstacleSensor object information. Calculate sensor <-> obstacle distance
     * and angles based on current member variables (m_indexRelevantSide etc.)
     *
     * @param[out] f_indexObstacle_r                  current object index
     * @param[out] f_typeObstacle_r                   object type
     * @param[out] f_referenceSurfaceObstacle_r       ref. surface index (cf. enum)
     * @param[out] f_visibilityObstacle_r             visibility of the object
     * @param[out] f_{x,y,z}SensorObstacle_r          distances to ref. surface center
     * @param[out] f_azimuthSensorObstacle_r            sensor <-> object connection angle in x-y plane
     * @param[out] f_yawAngleSensorObstacle_r         relative yaw angle (sensor <-> object)
     * @param[out] f_{height,width,length}Obstacle_r  object dimensions, assigned w.r.t reference surface
     * @param[out] f_v{X,Y}SensorObstacle_r           relative velocities (sensor <-> obstacle center of gravity)
     * @param[out] f_distanceSensorObstacle_r         absolute distance (sensor <-> ref. surface)
     */
    CBool updateObstacleMessages( CInt& f_indexObstacle_r, CInt& f_typeObstacle_r, CInt& f_referenceSurfaceObstacle_r, CFloat& f_visibilityObstacle_r,
                                  CFloat& f_xSensorObstacle_r, CFloat& f_ySensorObstacle_r, CFloat& f_zSensorObstacle_r,
                                  CFloat& f_azimuthSensorObstacle_r, CFloat& f_yawAngleSensorObstacle_r, // CFloat& f_yawAngleEgoObstacle_r,
                                  CFloat& f_heightObstacle_r, CFloat& f_widthObstacle_r, CFloat& f_lengthObstacle_r,
                                  CFloat& f_vXSensorObstacle_r, CFloat& f_vYSensorObstacle_r, CFloat& f_vZSensorObstacle_r,
                                  CFloat& f_aXVehicleObstacle_r, CFloat& f_aYVehicleObstacle_r, CFloat& f_aZVehicleObstacle_r,
                                  CFloat& f_distanceSensorObstacle_r,
                                  CInt f_referenceSurfaceObstacleFixed
                                );

protected:
    /*!
     * Calculate intersection point between obstacle contour line and connection sensor <-> obstacle.
     * Returns fraction of contour line to reach this point.
     */
    inline CFloat calcIntersectionPoint( CInt f_contourIndex );
    //*******************************
    //classes
    //*******************************
public:
    enum { invalid = 0, rearView = 1, rightView = 2, frontView = 3, leftView = 4 };
    //*******************************
    //variables
    //*******************************
protected:
    //*************************************
    //  sensor and ego related quantities
    //*************************************

    // "m_{x,y,z}{Sensor,World}ContourLine" are the dimension of contour lines (=distance between
    // contour points) in Sensor and World coordinates, respectively.
    CFloatVector m_xSensorContourLine, m_ySensorContourLine, m_zSensorContourLine;
    CFloatVector m_xWorldContourLine, m_yWorldContourLine, m_zWorldContourLine;

    CFloat m_yawAngle;  // sensor's yaw angle in world coordinate system
    CFloatVectorXYZ m_angleRollPitchYawEgo;
    CFloatVectorXYZ m_angleRollPitchYawTemp;
    CFloatVectorXYZ m_sensorMountingAngles;
    CFloatVectorXYZ m_xyzWorldSensor;
    CFloatVectorXYZ m_vXYZWorldSensor;
    CFloatVectorXYZ m_aXYZVehicleEgo; // replaces m_aXVehicleObstacle, m_aYVehicleObstacle;

    //*************************************
    //  obstacle related quantities
    //*************************************
    // -- directly defined from CObstacleDynamic or CObstacleStatic properties (stores their value)
    CInt m_indexObstacle;
    CInt   m_typeObstacle; // stores p_type (car, pedestrian etc.)
    CFloat m_visibilityObstacle; // stores p_visibility
    CFloatVectorXYZ m_xyzWorldObstacle; // stores position
    CFloatVectorXYZ m_vXYZWorldObstacle; // stores velocity
    CFloat m_aObstacle;         // stores acceleration in obstacle's x direction
    CFloat m_yawAngleObstacle;   // stores the obstacle's yaw angle (in world coordinate system)
    CFloatVector* m_xWorldContourPoint_p; // obstacle's contour point positions
    CFloatVector* m_yWorldContourPoint_p;
    CFloatVector* m_zWorldContourPoint_p;
    CFloatVectorXYZ m_depthHeightWidthObstacle; // obstacle dimensions

    // -- derived (calculated) quantities
    CFloatVectorXYZ m_xyzSensorObstacle; //
    CFloatVectorXYZ m_vXYZSensorObstacle;
    CFloatVectorXYZ m_aXYZVehicleObstacle; //
    CFloatVectorXYZ m_aXYZObstacle; //
    // CFloat m_vxWorldObstacle, m_vyWorldObstacle, m_vzWorldObstacle;
    // CFloat m_vxWorldSensor, m_vyWorldSensor, m_vzWorldSensor;
    CFloatVector m_xSensorContourPoint, m_ySensorContourPoint, m_zSensorContourPoint; // position array of contour points (sensor coordinates)
    CFloatVector m_dSensorContourPoint; // distance array of obstacle contour points (sensor coordinate system)
    CFloatVector m_azimuthSensorContourPoint; // Azimuth angle of obstacle contour points (sensor coordinate system's horizontal plane)
    CInt m_indexRelevantSide; // index of the contour side considered relevant (=closest to sensor)
    CInt m_indexRelevantSideNext; // index of the contour side next to the relevant side (index +1 mod 3)
    uint8_t m_indexNearestPoint;

    // CFloat m_aXVehicleEgo, m_aYVehicleEgo;
    CFloat m_rMainReference;
    CFloat m_rMin;
    ::std::vector<CInt> m_contourPoints_a;
};

#endif // CSensor_H