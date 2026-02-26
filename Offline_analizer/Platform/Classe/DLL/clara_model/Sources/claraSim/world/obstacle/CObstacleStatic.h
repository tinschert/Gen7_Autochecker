#ifndef CObstacleStatic_H_
#define CObstacleStatic_H_
/*!
********************************************************************************
@class CObstacleStatic
@ingroup obstacle
@brief calculate vehicle position in the absolute Cartesian coordinate system

@author Robert Erhart, ett2si (11.03.2016)
@copyright (c) Robert Bosch GmbH 2016-2024. All rights reserved.
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
********************************************************************************
@param[in] f_roadNetwork_r          [-]    reference to a roadNetwork
********************************************************************************
@param[out] o_x                     [m]    x-position of obstacle in world coordinate-system (center of gravity of obstacle) // (use o_xyzWorld; only needed for report visualisation)
@param[out] o_y                     [m]    y-position of obstacle in world coordinate-system (center of gravity of obstacle) // (use o_xyzWorld; only needed for report visualisation)
@param[out] o_z                     [m]    z-position of obstacle in world coordinate-system (bottom of obstacle) // (use o_xyzWorld; only needed for report visualisation)
@param[out] o_xyzWorld              [m]    (vector, [m],[m],[m]) x,y,z-position of obstacle in world coordinate-system (x,y: CoG; z: bottom of obstacle)
@param[out] o_coursePosition        [m]    course position of the obstacle
@param[out] o_xWorldContour         [m]    ([m],[m],[m],[m]] x-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system
@param[out] o_yWorldContour         [m]    ([m],[m],[m],[m]] y-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system
@param[out] o_zWorldContour         [m]    ([m],[m],[m],[m]] z-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system
@param[out] o_yawAngle              [rad]  yaw angle in world coordinate-system
@param[out] o_rollAngle             [rad]  roll angle in local (obstacle) coordinate-system ToDo: change messageName to xxxlocal
@param[out] o_pitchAngle            [rad]  pitch angle in local (obstacle) coordinate-system ToDo: change messageName to xxxlocal
********************************************************************************
@param[in,out] p_coursePosition     [m]     relative course position to road <x> and lane <y>; only be used if p_road >= 0
@param[in,out] p_lateralOffset      [m]     relative lateral course position to road <x> and lane <y>; only be used if p_road >= 0
@param[in,out] p_type               [enum]  obstacle type
@param[in,out] p_depth              [m]     length of the obstacle
@param[in,out] p_height             [m]     height of the obstacle
@param[in,out] p_width              [m]     width of the obstacle
@param[in,out] p_visibility            [%/100] visibility of object. 1.0:=fully visibility
@param[in,out] p_road               []      -1 : obstacle position absolute in world coordinated defined (o_x, ...)
                                            >=0: position information relative to road <x> and lane <y>; @ref p_lane
                                            p_coursePosition and p_lateralOffset used
@param[in,out] p_lane               []      position information relative to road <x> and lane <y>; @ref p_lane;
                                            only be used if p_road >= 0
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CObstacleStaticDoc
{
    const auto o_xyzWorld = "(vector, [m],[m],[m]) x,y,z-position of obstacle in world coordinate-system (x,y: CoG; z: bottom of obstacle)";
    const auto o_coursePosition = "[m] course position of the obstacle";
    const auto o_xWorldContour = "[m] [(P1,P2,P3,P4),...] x-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system";
    const auto o_yWorldContour = "[m] [(P1,P2,P3,P4),...] y-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system";
    const auto o_zWorldContour = "[m] [(P1,P2,P3,P4),...] z-position values of the obstacle contour P1, P2, P3 and P4 in world coordinate-system";
    const auto o_yawAngle = "[rad] yaw angle in world coordinate-system";
    const auto o_rollAngle = "[rad] roll angle in local (obstacle) coordinate-system";
    const auto o_pitchAngle = "[rad] pitch angle in local (obstacle) coordinate-system";

    const auto p_coursePosition = "[m] relative course position to road <x> and lane <y>; only be used if p_road >= 0";
    const auto p_lateralOffset = "[m] relative lateral course position to road <x> and lane <y>; only be used if p_road >= 0";
    const auto p_type = "[enum] obstacle type";
    const auto p_depth = "[m] length of the obstacle";
    const auto p_height = "[m] height of the obstacle";
    const auto p_width = "[m] width of the obstacle";
    const auto p_visibility = "[%/100] visibility of object. 1.0:=fully visibility";
    const auto p_road = "-1 : obstacle position absolute in world coordinated defined (o_x, ...); >=0: position information relative to road <x> and lane <y>";
    const auto p_lane = "position information relative to road <x> and lane <y>; only be used if p_road >= 0";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/world/roadNetwork/CRoadNetwork.h>

class CObstacleStatic : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CObstacleStatic();
    virtual ~CObstacleStatic();


    //*******************************
    //classes
    //*******************************
private:
    CRoadNetwork* m_roadNetwork_p;


    //*******************************
    //messages
    //*******************************
public:
    CMessageOutput<CFloat> o_x;
    CMessageOutput<CFloat> o_y;
    CMessageOutput<CFloat> o_z;
    CMessageOutput<CFloatVectorXYZ> o_xyzWorld;
    CMessageOutput<CFloat> o_coursePosition;
    CMessageOutput<CFloatVector> o_xWorldContour;
    CMessageOutput<CFloatVector> o_yWorldContour;
    CMessageOutput<CFloatVector> o_zWorldContour;
    CMessageOutput<CFloat> o_yawAngle;
    CMessageOutput<CFloat> o_rollAngle;
    CMessageOutput<CFloat> o_pitchAngle;

    /* parameter */
    CMessageParameter<CFloat> p_coursePosition;
    CMessageParameter<CFloat> p_lateralOffset;
    CMessageParameter<CInt> p_type;
    CMessageParameter<CFloat> p_depth;
    CMessageParameter<CFloat> p_height;
    CMessageParameter<CFloat> p_width;
    CMessageParameter<CFloat> p_visibility;
    CMessageParameter<CInt> p_road;
    CMessageParameter<CInt> p_lane;
private:


    //*******************************
    // methods
    //*******************************
public:
    void init( CRoadNetwork& f_roadNetwork_r );
private:
    void calc( CFloat f_dT, CFloat f_time );


    //*******************************
    //variables
    //*******************************
    CFloatVector m_xLocalContour;
    CFloatVector m_yLocalContour;
    CFloatVector m_zLocalContour;
    CFloatVector m_xWorldContour;
    CFloatVector m_yWorldContour;
    CFloatVector m_zWorldContour;

};

#endif /*CObstacleStatic_H_*/
