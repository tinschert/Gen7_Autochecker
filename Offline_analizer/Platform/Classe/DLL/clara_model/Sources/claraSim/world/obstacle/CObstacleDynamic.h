#ifndef CObstacleDynamic_H_
#define CObstacleDynamic_H_
/*!
********************************************************************************
@class CObstacleDynamic
@ingroup obstacle
@brief calculate vehicle position in the absolute Cartesian coordinate system

@author Robert Erhart, ett2si (05.03.2007, 11.03.2016)
@copyright (c) Robert Bosch GmbH 2007-2024. All rights reserved.
********************************************************************************
@remark
- obstacle box definition
@verbatim
          LF           RF
            ____________
           |\          .\
      P4-->| \         .<--P3
           |. \ . . . ..  \
           \   \           \
      depth \   \___________\
             \  |   o       | height
           P1-->|           |<--P2
               \|___________|
                    width
               LR           RR

  o = zero-point (coordinate origin) =~ course line
  P1 to P4 = contour points (center of vertical box edges)
@endverbatim
- course width
@verbatim
               #--------0--------#
                width/2   width/2

  0 = zero-point =~  course line
@endverbatim
********************************************************************************
param[in]   i_staticSimulation      [-]
********************************************************************************
@param[out] o_acceleration          [m/s^2]  current acceleration of the obstacle
@param[out] o_x                     [m]      x-position of obstacle in world coordinate-system (center of gravity of obstacle) (use o_xyzWorld; only needed for report visualisation)
@param[out] o_y                     [m]      y-position of obstacle in world coordinate-system (center of gravity of obstacle) (use o_xyzWorld; only needed for report visualisation)
@param[out] o_z                     [m]      z-position of obstacle in world coordinate-system (bottom of obstacle) (use o_xyzWorld; only needed for report visualisation)
@param[out] o_xyzWorld              [m]      (vector, [m],[m],[m]) x,y,z-position of obstacle in world coordinate-system (x,y: CoG; z: bottom of obstacle)
@param[out] o_vWorld                [m/s]    velocity vector of obstacle in world coordinates
@param[out] o_yawAngle              [rad]    world coordinate-system
@param[out] o_rollAngle             [rad]    local (obstacle) coordinate-system ToDo: change messageName to xxxlocal
@param[out] o_pitchAngle            [rad]    local (obstacle) coordinate-system ToDo: change messageName to xxxlocal
@param[out] o_trackWidthBack        [m]      track width of the back of the obstacle
@param[out] o_trackWidthFront       [m]      track width of the front of the obstacle
@param[out] o_coursePosition        [m]      course position of the obstacle
@param[out] o_vxCourse              [m/s]    velocity of obstacle in course coordinates
@param[out] o_vyCourse              [m/s]    velocity of obstacle in course coordinates
@param[out] o_xWorldContour         [m]      ([m],[m],[m],[m]) x-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system
@param[out] o_yWorldContour         [m]      ([m],[m],[m],[m]) y-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system
@param[out] o_zWorldContour         [m]      ([m],[m],[m],[m]) z-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system
@param[out] o_lateralOffset         [m]      lateral offset from the course line of the lane
********************************************************************************
@param[in,out] p_coursePosition      [m]     override current course position
@param[in,out] p_lateralOffset       [m]     override current lateral offset from course line
@param[in,out] p_xCourseVelocity     [m/s]   override longitudinal course velocity (x direction)
@param[in,out] p_targetVelocity      [m/s]   target velocity of obstacle
@param[in,out] p_targetLateralOffset [m]     target lateral offset from course line
@param[in,out] p_lateralVelocity     [m/s]   lateral velocity for lane change
@param[in,out] p_lateralMovementType [int]   [0: linear, 1: sigmoid, 2: direct jump] determines lateral movement type towards p_targetLateralOffset and during lane change
@param[in,out] p_alignWithVelocity   [bool]  align obstacle orientation with its effective (longitudinal + lateral) velocity?
@param[in,out] p_acceleration        [m/s^2] longitudinal acceleration of the obstacle towards p_targetVelocity (unsigned)
@param[in,out] p_type                [enum]  obstacle type. Types see "EObstacleTyp" in "CObstacles.h".
@param[in,out] p_depth               [m]     length of the obstacle
@param[in,out] p_height              [m]     height of the obstacle
@param[in,out] p_width               [m]     width of the obstacle
@param[in,out] p_offsetPos           [m]     add offset to current course position
@param[in,out] p_road;               []      position information relative to road <x> and lane <y>; @ref p_lane
@param[in,out] p_lane;               []      position information relative to road <x> and lane <y>; @ref p_road
@param[in,out] p_visibility          [%/100] visibility of object. 1.0:=fully visibility
********************************************************************************
@todo agent mode for autonomous driving e.g. CTable m_velocityTimeTable
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CObstacleDynamicDoc
{
    const auto o_acceleration = "[m/s^2] current acceleration of the obstacle";
    const auto o_xyzWorld = "(vector, [m],[m],[m]) x,y,z-position of obstacle in world coordinate-system (x,y: CoG; z: bottom of obstacle)";
    const auto o_xWorldContour = "([m],[m],[m],[m]) x-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system";
    const auto o_yWorldContour = "([m],[m],[m],[m]) y-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system";
    const auto o_zWorldContour = "([m],[m],[m],[m]) z-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system";
    const auto o_vWorld = "([m/s],[m/s],[m/s]) velocity vector of obstacle in world coordinates";
    const auto o_yawAngle = "[rad] world coordinate-system";
    const auto o_rollAngle = "[rad] local (obstacle) coordinate-system";
    const auto o_pitchAngle = "[rad] local (obstacle) coordinate-system";
    const auto o_trackWidthBack = "[m] track width of the back of the obstacle";
    const auto o_trackWidthFront = "[m] track width of the front of the obstacle";
    const auto o_coursePosition = "[m] course position of the obstacle";
    const auto o_vxCourse = "[m/s] velocity x of obstacle in course coordinates";
    const auto o_vyCourse = "[m/s] velocity y of obstacle in course coordinates";
    const auto o_lateralOffset = "[m] lateral offset from the course line of the lane";

    const auto p_coursePosition = "[m] override current course position";
    const auto p_lateralOffset = "[m] override current lateral offset from course line";
    const auto p_xCourseVelocity = "[m/s] override longitudinal course velocity (x direction)";
    const auto p_targetVelocity = "[m/s] target velocity of obstacle";
    const auto p_targetLateralOffset = "[m] target lateral offset from course line";
    const auto p_lateralVelocity = "[m/s] linear lane change: lateral velocity for lane change. sigmoid-type lane change: maximum lateral velocity";
    const auto p_lateralMovementType = "[0: linear, 1: sigmoid, 2: jump] determines lateral movement type towards p_targetLateralOffset and during lane change: linear, sigmoid-like, or direct jump.";
    const auto p_alignWithVelocity = "[bool]  align obstacle orientation with its effective (longitudinal + lateral) velocity?";
    const auto p_acceleration = "[m/s^2] longitudinal acceleration of the obstacle towards p_targetVelocity (unsigned)";
    const auto p_type = "[enum] obstacle type";
    const auto p_depth = "[m] length of the obstacle";
    const auto p_height = "[m] height of the obstacle";
    const auto p_width = "[m] width of the obstacle";
    const auto p_visibility = "[%/100] visibility of object. 1.0:=fully visibility";
    const auto p_offsetPos = "[m] add offset to current course position";
    const auto p_road = "[] position information relative to road <x> and lane <y>";
    const auto p_lane = "[] position information relative to road <x> and lane <y>";
}


#include <claraSim/framework/CModule.h>
#include <claraSim/world/roadNetwork/CRoadNetwork.h>

class CObstacleDynamic : public CModule<3, 1>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CObstacleDynamic();
    virtual ~CObstacleDynamic();


    //*******************************
    //classes
    //*******************************
private:
    CRoadNetwork* m_roadNetwork_p;


    //*******************************
    //messages
    //*******************************
public:
    CMessageOutput<CFloat> o_acceleration;
    CMessageOutput<CFloat, 10000> o_x; //world coordinates
    CMessageOutput<CFloat, 10000> o_y; //world coordinates
    CMessageOutput<CFloat, 10000> o_z; //world coordinates
    CMessageOutput<CFloatVectorXYZ> o_xyzWorld;
    CMessageOutput<CFloatVector> o_xWorldContour; //world coordinates
    CMessageOutput<CFloatVector> o_yWorldContour; //world coordinates
    CMessageOutput<CFloatVector> o_zWorldContour; //world coordinates
    CMessageOutput<CFloatVectorXYZ> o_vWorld;
    CMessageOutput<CFloat> o_yawAngle;
    CMessageOutput<CFloat> o_rollAngle;
    CMessageOutput<CFloat> o_pitchAngle;
    CMessageOutput<CFloat> o_trackWidthBack;
    CMessageOutput<CFloat> o_trackWidthFront;

    CMessageOutput<CFloat> o_coursePosition;
    CMessageOutput<CFloat> o_vxCourse;
    CMessageOutput<CFloat> o_vyCourse;
    CMessageOutput<CFloat> o_lateralOffset;

    /* parameter */
    CMessageParameter<CFloat> p_coursePosition;
    CMessageParameter<CFloat> p_lateralOffset;

    CMessageParameter<CFloat> p_xCourseVelocity;
    CMessageParameter<CFloat> p_targetVelocity;
    CMessageParameter<CFloat> p_targetLateralOffset;
    CMessageParameter<CFloat> p_lateralVelocity;
    CMessageParameter<CInt> p_lateralMovementType;
    CMessageParameter<CBool> p_alignWithVelocity;
    CMessageParameter<CFloat> p_acceleration;
    CMessageParameter<CInt, 10000> p_type;
    CMessageParameter<CFloat> p_depth;
    CMessageParameter<CFloat> p_height;
    CMessageParameter<CFloat> p_width;
    CMessageParameter<CFloat> p_visibility;
    CMessageParameter<CFloat> p_offsetPos;
    CMessageParameter<CInt> p_road;
    CMessageParameter<CInt> p_lane;
private:
    CMessageInput<CBool> i_staticSimulation;


    //*******************************
    // methods
    //*******************************
public:
    void init( CRoadNetwork& f_roadNetwork_r,
               IMessage<CBool>& f_staticSimulation );

private:
    //! Change to a new lane.
    //! For this, the new lane course position is numerically determined and the lane change mechanism started.
    //! @param[in]  f_newLaneID  [CInt]  ID of the new lane; index refers to "roadNetwork.roads[p_road].lanes" array.
    void changeLane( CInt f_newLaneID );

    CFloatVector& ddt( CFloatVector& state );
    void calcPre( CFloat f_dT, CFloat f_time );
    void calcPost( CFloat f_dT, CFloat f_time );


    //*******************************
    //variables
    //*******************************
private:
    CFloatVector m_xLocalContour;
    CFloatVector m_yLocalContour;
    CFloatVector m_zLocalContour;
    CFloat m_targetLateralOffset;
    CFloat m_initialLateralOffset;
    CInt m_lane_K1; // Lane index from previous calculation. Used for lane change detection.
    CInt m_road_K1;

    enum
    {
        NumberOfIntegrationSteps = 1
    };
    enum
    {
        COURSE_POSITION, COURSE_VELOCITY, LATERAL_OFFSET, NumberOfStates
    };
};

#endif /*CObstacleDynamic_H_*/
