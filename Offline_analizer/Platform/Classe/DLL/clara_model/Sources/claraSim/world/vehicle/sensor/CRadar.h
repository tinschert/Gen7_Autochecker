#ifndef CRADAR_H
#define CRADAR_H
/*!
********************************************************************************
@class CRadar
@ingroup sensor
@brief  simulation of a radar sensor (ACC1, ACC2, LRR3, LRR4, MRR, GEN5)

@author Andreas Brunner, bnr2lr
@author Robert Erhart, ett2si (08.07.2005, 31.05.2016)
@copyright (c) Robert Bosch GmbH 2005-2024. All rights reserved.
********************************************************************************
@remark
- obstacle box
@verbatim
          LF           RF
            ____________
           |\          .\
      P3-->| \         .<--P2
           |. \ . . . ..  \
           \   \           \
      depth \   \___________\
             \  |   o       | height
           P0-->|  x  x  x  |<--P1
               \|___________|
                    width
               LR           RR

  o = zero-point (coordinate origin) =~ course line
  x = reflection points
  P0 to P3 = contour points (center of vertical box edges)
  obstacle side 'i' spans between contour point P_i and P_i+1
@endverbatim

- course width
@verbatim
                #--------0--------#
                 width/2   width/2
  0 = zero-point =~  course line
@endverbatim

For a general description of underlying "object sensor" model, see parent class
"CSensor".

Specific to the CRadar sensor model is its calculation of "reflections" and
"locations". This is reflected in additional parameters - like the maximum number of
detectable reflections - and outputs that reflect the simulated reflection and
location properties.

For Gen4 projects the location output is used, while for Gen5 projects the
object output is used in the respective bypassing interface.


********************************************************************************
@param[in,out] various generic sensor inputs and outputs - see CSensor.h!

********************************************************************************
- Reflections
@param[out] o_xWorldReflection      [m]     (vector) x position radar reflection (world coordinate system)
@param[out] o_yWorldReflection      [m]     (vector) y position radar reflection (world coordinate system)
@param[out] o_zWorldReflection      [m]     (vector) z position radar reflection (world coordinate system)
@param[out] o_visibilityReflection     [0..1]  (vector) visibility reflection; 1.0:=fully visibility

- Locations
@param[out] o_xRadarLocation        [m]     (vector) x position radar location (sensor coordinate system)
@param[out] o_yRadarLocation        [m]     (vector) y position radar location (sensor coordinate system)
@param[out] o_zRadarLocation        [m]     (vector) z position radar location (sensor coordinate system)
@param[out] o_alphaRadarLocation    [rad]   (vector) angle between sensor-axis and location (x-y plane)
@param[out] o_distanceLocation      [m]     (vector) distance between radar and location
@param[out] o_vLateralRadarLocation [m/s]   (vector) lateral velocity between radar and location
@param[out] o_vRadialRadarLocation  [m/s]   (vector) radial velocity between radar and location
@param[out] o_visibilityLocation       [%/100] (vector) visibility of object. 1.0:=fully visibility
@param[out] o_rcsCenterLocation     [dBm²]  (vector) radar-cross-section in dB
@param[out] o_rcsUpLocation         [dBm²]  (vector) radar-cross-section in dB
@param[out] o_elevationAngleLocation[rad]   (vector) which correlates (over time and distance)
                                                    with an estimated elevation angle for each location.
                                                    A single snapshot is highly influenced by multipath reflection over ground
                                                    therefore the value has to be filtered over distance.
@param[out] o_prioIndexLocation     []      (vector) indexes of locations sorted by prio
@param[out] o_meanPowerInd          []      (vector) mean power indicator for classification
@param[out] o_elevationInd          []      (vector) elevation indicator for classification
@param[out] o_multipathInd          []      (vector) multipath indicator for classification
@param[out] o_detectionInd          []      (vector) detection indicator for classification
@param[out] o_microDopplerPwr       []      (vector) micro doppler power for classification

- Obstacle
@param[out] o_yawAngleEgoObstacle      [rad]   (vector) relative yaw angle between object-box and ego vehicle

********************************************************************************
- Configuration
@param[in,out] p_xRadarVehicleOffset       [m]     additional longitudinal offset (sensor coordinate system)
@param[in,out] p_yRadarVehicleOffset       [m]     additional lateral offset (sensor coordinate system)
@param[in,out] p_vObstacleRadarOffset      [m/s²]  additional velocity offset (sensor coordinate system)
@param[in,out] p_closeRange                [m]     define close range for double reflections (0-x)
@param[in,out] p_meanPowerIndDuty          []      PWM-Parameter
@param[in,out] p_meanPowerIndCycle         []      PWM-Parameter
@param[in,out] p_maxNumberOfReflectionsPerObstacles [] maximum number of reflections. if number is even a underfloor reflection is generated
@param[in,out] p_angleSeparationSensor     [rad]   angle separation of the radar sensor
@param[in,out] p_vehicleRcsBaseLocation    [dBm²]  vehicle RCS base";
@param[in,out] p_vehicleRcsDistanceFactor  []      vehicle RCS distance factor";
@param[in,out] p_vehicleDeltaRcsUpLocation [dBm²]  vehicle RCS up delta from base";
@param[in,out] p_pedRcsBaseLocation        []      pedestrian RCS base
@param[in,out] p_pedRcsDistanceFactor      []      pedestrian RCS distance factor
@param[in,out] p_pedDeltaRcsUpLocation     []      pedestrian RCS up delta from base
@param[in,out] p_probHasBeenObservedMoving [%/100] probability that the obstacle has been observed as moving. Currently, either '1' or '0'. Default = '1', because obstacle will be recognized as 'stopped'.
@param[in,out] p_dirAngleVar               [deg]    A factor that is used to stimulate the object direction angle variance.
                                                    The object direction angle is the angle between the ego vehicle direction
                                                    and the object vehicle direction.
@param[in,out] p_xVar                       [m]     A factor that is used to stimulate the object x-distance variance.
@param[in,out] p_yVar                       [m]     A factor that is used to stimulate the object y-distance variance.
@param[in,out] p_spdXVar                    [m²/s²] A factor that is used to stimulate the object's speed variance in x-direction.
@param[in,out] p_spdYVar                    [m²/s²] A factor that is used to stimulate the object's speed variance in y-direction.

********************************************************************************
@ToDo: calculate seeming obstacle velocity from sensor rotation (when output is in sensor coordinates)
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CRadarDoc
{
    const auto o_xWorldReflection = "[m] (vector) x position radar reflection (world coordinate system)";
    const auto o_yWorldReflection = "[m] (vector) y position radar reflection (world coordinate system)";
    const auto o_zWorldReflection = "[m] (vector) z position radar reflection (world coordinate system)";
    const auto o_visibilityReflection = "[0..1] (vector) visibility reflection; 1.0:=fully visibility";
    const auto o_xRadarLocation = "[m] (vector) x position radar location (sensor coordinate system)";
    const auto o_yRadarLocation = "[m] (vector) y position radar location (sensor coordinate system)";
    const auto o_zRadarLocation = "[m] (vector) z position radar location (sensor coordinate system)";
    const auto o_alphaRadarLocation = "[rad] (vector) angle between radar-axis and location (x-y plane)";
    const auto o_distanceLocation = "[m] (vector) distance between radar and location";
    const auto o_vLateralRadarLocation = "[m/s] (vector) lateral velocity between radar and location";
    const auto o_vRadialRadarLocation = "[m/s] (vector) radial velocity between radar and location";
    const auto o_rcsCenterLocation = "[dBm²] (vector) radar-cross-section in dB";
    const auto o_rcsUpLocation = "[dBm²] (vector) radar-cross-section in dB";
    const auto o_visibilityLocation = "[%/100] (vector) visibility of object. 1.0:=fully visibility";
    const auto o_elevationAngleLocation = "(vector) which correlates (over time and distance); with an estimated elevation angle for each location; A single snapshot is highly influenced by multipath reflection over ground; therefore the value has to be filtered over distance.";
    const auto o_prioIndexLocation = "(vector) indexes of locations sorted by prio";
    const auto o_meanPowerInd = "(vector) mean power indicator for classification";
    const auto o_elevationInd = "(vector) elevation indicator for classification";
    const auto o_multipathInd = "(vector) multipath indicator for classification";
    const auto o_detectionInd = "(vector) detection indicator for classification";
    const auto o_microDopplerPwr = "(vector) micro doppler power for classification";

    const auto o_yawAngleEgoObstacle = "[rad] (vector) relative yaw angle between object-box and ego vehicle";

    const auto p_xRadarVehicleOffset = "[m] additional longitudinal offset (sensor coordinate system)";
    const auto p_yRadarVehicleOffset = "[m] additional lateral offset (sensor coordinate system)";
    const auto p_vObstacleRadarOffset = "[m/s²] additional velocity offset (sensor coordinate system)";
    const auto p_closeRange = "[m] define close range for double reflections (0-x)";
    const auto p_meanPowerIndDuty = "[] PWM-Parameter";
    const auto p_meanPowerIndCycle = "[] PWM-Parameter";
    const auto p_maxNumberOfReflectionsPerObstacles = "[] maximum number of reflections. if number is even a underfloor reflection is generated";
    const auto p_angleSeparationSensor = "[rad] angle separation of the radar sensor";

    const auto p_vehicleRcsBaseLocation = "[dBm²] vehicle RCS base";
    const auto p_vehicleRcsDistanceFactor = "[] vehicle RCS distance factor";
    const auto p_vehicleDeltaRcsUpLocation = "[dBm²] vehicle RCS up delta from base";

    const auto p_pedRcsBaseLocation = "[dBm²] pedestrian RCS base";
    const auto p_pedRcsDistanceFactor = "[] pedestrian RCS distance factor";
    const auto p_pedDeltaRcsUpLocation = "[dBm²] pedestrian RCS up delta from base";

    const auto p_probHasBeenObservedMoving = "[%/100] probability that the obstacle has been observed as moving. Currently, either '1' or '0'. Default = '1', because obstacle will be recognized as 'stopped'.";
    const auto p_dirAngleVar = "[deg] A factor that is used to stimulate the object direction angle variance. The object direction angle is the angle between the ego vehicle direction and the object vehicle direction.";
    const auto p_xVar = "[m²] A factor that is used to stimulate the object x-distance variance.";
    const auto p_yVar = "[m²] A factor that is used to stimulate the object y-distance variance.";
    const auto p_spdXVar = "[m²/s²] A factor that is used to stimulate the object's speed variance in x-direction..";
    const auto p_spdYVar = "[m²/s²] A factor that is used to stimulate the object's speed variance in y-direction..";
}

#include "CSensor.h"
#include <claraSim/world/obstacle/CObstacles.h>
#include <vector>
#include <random>

//forward declaration
class CObstacleRadar;

////*********************************
//// CRadar
////*********************************
class CRadar : public CSensor
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CRadar();
    virtual ~CRadar();

    //*******************************
    //classes
    //*******************************
private:
    ::std::vector<CObstacleRadar> m_obstacle_a;
    ::std::normal_distribution<CFloat> NormalRCS;
    ::std::mt19937 Generator;

    //*******************************
    //messages
    //*******************************
public:
    //reflection
    CMessageOutput<CFloatVector> o_xWorldReflection, o_yWorldReflection, o_zWorldReflection;
    CMessageOutput<CFloatVector> o_visibilityReflection;
    //location
    CMessageOutput<CFloatVector> o_xRadarLocation, o_yRadarLocation, o_zRadarLocation;
    CMessageOutput<CFloatVector> o_alphaRadarLocation;
    CMessageOutput<CFloatVector> o_distanceLocation;
    CMessageOutput<CFloatVector> o_visibilityLocation;

    CMessageOutput<CFloatVector> o_vLateralRadarLocation, o_vRadialRadarLocation;
    CMessageOutput<CFloatVector> o_rcsCenterLocation, o_rcsUpLocation;
    CMessageOutput<CFloatVector> o_elevationAngleLocation;
    CMessageOutput<CIntVector> o_prioIndexLocation;
    CMessageOutput<CIntVector> o_meanPowerInd;
    CMessageOutput<CIntVector> o_elevationInd;
    CMessageOutput<CIntVector> o_multipathInd;
    CMessageOutput<CIntVector> o_detectionInd;
    CMessageOutput<CFloatVector> o_microDopplerPwr;
    //objects
    CMessageOutput<CFloatVector> o_yawAngleEgoObstacle;

    // sensor properties
    CMessageParameter<CFloat> p_xRadarVehicleOffset;
    CMessageParameter<CFloat> p_yRadarVehicleOffset;
    CMessageParameter<CFloat> p_vObstacleRadarOffset;
    CMessageParameter<CFloat> p_closeRange;
    CMessageParameter<CInt>   p_meanPowerIndDuty;
    CMessageParameter<CInt>   p_meanPowerIndCycle;
    CMessageParameter<CInt>   p_maxNumberOfReflectionsPerObstacles;

    CMessageParameter<CFloat> p_vehicleRcsBaseLocation;
    CMessageParameter<CFloat> p_vehicleRcsDistanceFactor;
    CMessageParameter<CFloat> p_vehicleDeltaRcsUpLocation;

    CMessageParameter<CFloat> p_pedRcsBaseLocation;
    CMessageParameter<CFloat> p_pedRcsDistanceFactor;
    CMessageParameter<CFloat> p_pedDeltaRcsUpLocation;

    CMessageParameter<CFloat> p_angleSeparationSensor;
    CMessageParameter<CFloatVector> p_probHasBeenObservedMoving;
    CMessageParameter<CFloatVector> p_dirAngleVar;
    CMessageParameter<CFloatVector> p_xVar;
    CMessageParameter<CFloatVector> p_yVar;
    CMessageParameter<CFloatVector> p_spdXVar;
    CMessageParameter<CFloatVector> p_spdYVar;


private:
    // input messages defined in CSensor

    //*******************************
    // methods
    //*******************************
public:
    /*!
     * Initialization of CRadar object.
     *
     * @param[in] f_{x,y,z}World              ego vehicle position vector (world coordinates)
     * @param[in] f_veclocity{X,Y,Z}World     ego vehicle velocity vector (world coordinates)
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

    // //*******************************
    // //variables
    // //*******************************
public:
private:
    CInt m_numberOfObstaclesDynamic;
    CInt m_numberOfReflectionsDynamic;
    CInt m_numberOfObstaclesStatic;
    CInt m_numberOfReflectionsStatic;
    CInt m_numberOfReflectionsSum;
    CInt m_numberOfLocations;
    CInt m_counter;

    CFloatVector m_obstacleDynamicVisibility;           // (unsorted) visibilities of dynamic obstacles
    CIntVector m_obstacleDynamicVisibilityIndexList;
    CFloatVector m_obstacleStaticVisibility;
    CIntVector m_obstacleStaticVisibilityIndexList;

    CFloatVector m_xRadarReflection;
    CFloatVector m_yRadarReflection;
    CFloatVector m_zRadarReflection;
    CFloatVector m_alphaRadarReflection;
    CFloatVector m_dRadarReflection;
    CIntVector m_typReflection;
    CFloatVector m_heightReflection;
    CFloatVector m_vxWorldReflection;
    CFloatVector m_vyWorldReflection;
    CFloatVector m_vzWorldReflection;
    CFloatVector m_dvRadialReflection;
    CFloatVector m_dvLateralReflection;

    // CFloatVector m_velocityXYZWorldSensor;   // sensor velocity in world coordinates
};

/*!
********************************************************************************
@class CObstacleRadar
@ingroup sensor
@brief  Obstacle object holding sensor and obstacle properties for calculation in radar sensor model.
@remark See CRadar's 'm_obstacle_a' vector.

Robert Erhart (ett2si), Andreas Brunner (bnr2lr) [08.07.2005, 31.05.2016, 04.06.2020]
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************/

////*********************************
//// CObstacleRadar
//// Obstacle object holding sensor and obstacle properties for calculation in
//// radar sensor model. See CRadar's 'm_obstacle_a' vector.
////*********************************
class CObstacleRadar : public CObstacleSensor
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CObstacleRadar();
    virtual ~CObstacleRadar();

    //*******************************
    // methods
    //*******************************
public:
    CBool updateObstacleMessages(
        // generic messages
        CInt& f_indexObstacle_r, CInt& f_typeObstacle_r, CInt& f_referenceSurfaceObstacle_r, CFloat& f_visibilityObstacle_r,
        CFloat& f_xSensorObstacle_r, CFloat& f_ySensorObstacle_r, CFloat& f_zSensorObstacle_r,
        CFloat& f_azimuthSensorObstacle_r, CFloat& f_yawAngleSensorObstacle_r,
        CFloat& f_heightSensorObstacle_r, CFloat& f_widthSensorObstacle_r, CFloat& f_lengthSensorObstacle_r,
        CFloat& f_vXSensorObstacle_r, CFloat& f_vYSensorObstacle_r, CFloat& f_vZSensorObstacle_r,
        CFloat& f_aXVehicleObstacle_r, CFloat& f_aYVehicleObstacle_r, CFloat& f_aZVehicleObstacle_r,
        CFloat& f_distanceSensorObstacle_r,
        CInt f_referenceSurfaceObstacleFixed,
        // CRadar specific messages
        CFloat& f_yawAngleEgoObstacle_r );
    /*!
    * Calculate the reflections of the obstacle
    * TODO more description, params
    * @param[in]  ...
    * @param[out] f_heightReflection_a [m] height of the reflection surface
    * @param[out] ...
    */
    CInt calcReflections( CInt f_startIndex, CFloat f_angleSeparation, CInt f_maxNoOfReflections,
                          CFloatVector& f_xWorld, CFloatVector& f_yWorld, CFloatVector& f_zWorld,
                          CFloatVector& f_xRadar, CFloatVector& f_yRadar, CFloatVector& f_zRadar, CFloatVector& f_alphaRadar,
                          CFloatVector& f_dRadarReflection, CFloatVector& f_heightReflection,
                          CFloatVector& f_vxWorldReflection, CFloatVector& f_vyWorldReflection, CFloatVector& f_vzWorldReflection,
                          CFloatVector& f_vRadialRadarReflection, CFloatVector& f_vLateralRadarReflection,
                          CIntVector& f_typReflection, CFloatVector& f_visibilityReflection );

private:
    /*!
    *
    */
    // CFloat calcIntersectionPoint( CInt f_contourIndex );
    //*******************************
    //classes
    //*******************************
public:
    enum { invalid = 0, rearView = 1, rightView = 2, frontView = 3, leftView = 4 };

private:
    ::std::normal_distribution<CFloat> NormalCar;
    ::std::normal_distribution<CFloat> NormalPedestrian;
    ::std::normal_distribution<CFloat> NormalCyclist;
    ::std::normal_distribution<CFloat>* Normal_p;
    ::std::mt19937 Generator;
    //*******************************
    //variables
    //*******************************
private:
};

#endif // CRADAR_H