#ifndef CVIDEO_H
#define CVIDEO_H
/*!
********************************************************************************
@class CVideo
@ingroup sensor
@brief  simulation of a Video sensor

@author Robert Erhart, ett2si (19.08.2008)
@copyright (c) Robert Bosch GmbH 2008-2024. All rights reserved.
********************************************************************************
@remark
- video obstacle:
@verbatim
            LF   front  RF
             ____________
            |\           \P2
          P3| \     o     \
            |  \___________\
            \   |           |
  left depth \P0|  rear     |P1  height right
              \ |           |
                -------------
               LR   width  RR

  0 = zero-point =~ course line
@endverbatim

- course width
@verbatim
                #--------0--------#
                 width/2   width/2
  0 = zero-point =~  course line
@endverbatim

- video line
@verbatim
  ego vehicle : o
  Lane ID      :       +2    +1     0    -1
  relativeLine:    +2    +1    -1    -2    -3
                    |     |     |     |     |
                    |     |     |     |     |
                    |     |     |     |     |
                    |     |     |     |     |
                    |     |  o  |     |     |
                    |     |     |     |     |
                    |     |     |     |     |
@endverbatim
********************************************************************************
@param[in,out] various generic inputs and outputs - see CSensor.h!

@param[in] i_currentRoadIndex             [int]  Index of road the ego is currently on
@param[in] i_currentLaneID             [int]  ID of lane the ego is currently on
@param[in] i_searchIDLane              [int]  ID of nearest lane to the ego

extracted from f_obstacles_r input parameter:

@param[in] i_trackWidthBackObstacleDynamic  [m]  Track width at the back of the obstacle
@param[in] i_lateralOffsetCourseObstacleDynamic [m] Ego's lateral offset from the course line of the lane

extracted from f_roadNetwork_r input parameter:

@param[in] i_lengthOfCourseRoad             [m] Length of the course
@param[in] i_numberOfLanesReferencePoints   [-] Number of reference x,y,z points of lane zero
@param[in] i_numberOfLanesRoad              [-] Number of lanes of the road
@param[in] i_numberOfLanesLeftRoad          [-] Number of lanes to the left of reference lane (index 0)
@param[in] i_numberOfLanesRightRoad         [-] Number of lanes to the right of reference lane (index 0)
@param[in] i_indexOfRightmostLaneRoad       [-] Index of the rightmost lane
@param[in] i_indexOfLeftmostLaneRoad        [-] Index of the leftmost lane

********************************************************************************
- Obstacle
@param[out] o_xVideoLeftEdgeObstacle      [m]     (vector) x position of the left edge of the relevant object side (sensor coordinate system)
@param[out] o_yVideoLeftEdgeObstacle      [m]     (vector) y position of the left edge of the relevant object side (sensor coordinate system)
@param[out] o_zVideoLeftEdgeObstacle      [m]     (vector) z position of the left edge of the relevant object side (sensor coordinate system)
@param[out] o_xVideoRightEdgeObstacle     [m]     (vector) x position of the right edge of the relevant object side (sensor coordinate system)
@param[out] o_yVideoRightEdgeObstacle     [m]     (vector) y position of the right edge of the relevant object side (sensor coordinate system)
@param[out] o_zVideoRightEdgeObstacle     [m]     (vector) z position of the right edge of the relevant object side (sensor coordinate system)
@param[out] o_visibilityObstacle             [%/100] (vector) visibility of object. 1.0:=fully visibility
@param[out] o_alphaVideoLeftBorderObstacle                [rad]  (vector) angle between video-axis and left edge
@param[out] o_alphaVideoRightBorderObstacle               [rad]  (vector) angle between video-axis and right edge
@param[out] o_alphaVideoLeftBorderObstacleRightCourseLine [rad]  (vector) angle between left edge of the object and right course line
@param[out] o_alphaVideoRightBorderObstacleLeftCourseLine [rad]  (vector) angle between right edge of the object and left course line

- Video lines
@param[out] o_typeLine                      [see object] (vector) see CLine type in CLane
@param[out] o_arcLength                    [m]          (vector) length of curvature
@param[out] o_indexLine                    [-x 0 y]     (vector) see remark relativeLine
@param[out] o_xVideoLineStart              [m]          (vector) x video-coordinate system
@param[out] o_yVideoLineStart              [m]          (vector) y video-coordinate system
@param[out] o_zVideoLineStart              [m]          (vector) z video-coordinate system
@param[out] o_gammaVideoLineStart          [rad]        (vector) gradient angle in video-coordinate system
@param[out] o_xVideoLineEnd                [m]          (vector) x video-coordinate system
@param[out] o_yVideoLineEnd                [m]          (vector) y video-coordinate system
@param[out] o_zVideoLineEnd                [m]          (vector) z video-coordinate system
@param[out] o_curvatureLineStart           [1/m]        (vector) curvature at line start point
@param[out] o_curvatureDerivativeLineStart []           (vector) curvature derivative between line start and end point
********************************************************************************
- Configuration
@param[in,out] p_sensorBlind               []          enable/disable video validation
@param[in,out] p_dMinVideo                 [m]         min radar view
@param[in,out] p_dMaxVideo                 [m]         max radar view
@param[in,out] p_alphaLeftVideo            [rad]       field of view left
@param[in,out] p_alphaRightVideo           [rad]       field of view right
@param[in,out] p_angleFieldOfViewArray     [rad]       (vector) future--> will replace p_alphaLeftVideo and p_alphaRightVideo
@param[in,out] p_maxRangeFieldOfViewArray  [m]         (vector) future--> will replace p_alphaLeftVideo and p_alphaRightVideo
@param[in,out] p_maxNumberOfRelevantLines     [0..x]   max number of video lines
********************************************************************************
@ToDo: derive from CSensor class
@ToDo: unify naming: "edge" <-> "boarder"
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CVideoDoc
{
    const auto o_xVideoLeftEdgeObstacle = "[m] (vector) x position of the left edge of the relevant object side (sensor coordinate system)";
    const auto o_yVideoLeftEdgeObstacle = "[m] (vector) y position of the left edge of the relevant object side (sensor coordinate system)";
    const auto o_zVideoLeftEdgeObstacle = "[m] (vector) z position of the left edge of the relevant object side (sensor coordinate system)";
    const auto o_xVideoRightEdgeObstacle = "[m] (vector) x position of the right edge of the relevant object side (sensor coordinate system)";
    const auto o_yVideoRightEdgeObstacle = "[m] (vector) y position of the right edge of the relevant object side (sensor coordinate system)";
    const auto o_zVideoRightEdgeObstacle = "[m] (vector) z position of the right edge of the relevant object side (sensor coordinate system)";
    const auto o_alphaVideoLeftBorderObstacle = "[rad] (vector) angle between video-axis and left edge";
    const auto o_alphaVideoRightBorderObstacle = "[rad] (vector) angle between video-axis and right edge";
    const auto o_alphaVideoLeftBorderObstacleRightCourseLine = "[rad] (vector) angle between left edge of the object and right course line";
    const auto o_alphaVideoRightBorderObstacleLeftCourseLine = "[rad] (vector) angle between right edge of the object and left course line";
    const auto o_typeLine = "(vector) see CLine type in CLane";
    const auto o_arcLength = "[m] (vector) length of curvature";
    const auto o_indexLine = "(vector) see remark relativeLine";
    const auto o_xVideoLineStart = "[m] (vector) x video-coordinate system";
    const auto o_yVideoLineStart = "[m] (vector) y video-coordinate system";
    const auto o_zVideoLineStart = "[m] (vector) z video-coordinate system";
    const auto o_gammaVideoLineStart = "[rad] (vector) gradient angle in video-coordinate system";
    const auto o_xVideoLineEnd = "[m] (vector) x video-coordinate system";
    const auto o_yVideoLineEnd = "[m] (vector) y video-coordinate system";
    const auto o_zVideoLineEnd = "[m] (vector) z video-coordinate system";
    const auto o_curvatureLineStart = "[1/m] (vector) curvature at line start point";
    const auto o_curvatureDerivativeLineStart = "[1/m] (vector) curvature derivative between line start and end point";
    const auto p_sensorBlind = "enable/disable video validation";
    const auto p_maxNumberOfRelevantLines = "max number of video lines";
}

#include "CSensor.h"
#include <claraSim/framework/CModuleVector.h>
#include <claraSim/framework/CViewSegment.h>
#include <claraSim/world/obstacle/CObstacles.h>
#include <claraSim/world/roadNetwork/CRoadNetwork.h>
#include <claraSim/framework/CLine.h>
#include <vector>

//forward declaration
class CObstacleVideo;
class CLineVideo;

////*********************************
//// CVideo
////*********************************
class CVideo : public CSensor
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CVideo();
    virtual ~CVideo();

    //*******************************
    //classes
    //*******************************
private:
    ::std::vector<CObstacleVideo> m_obstacle_a;
    ::std::vector<CLineVideo> m_videoLine_a;
    CRoadNetwork* m_roadNetwork_p;

    //*******************************
    //messages
    //*******************************
public:
    CMessageOutput<CFloatVector> o_xVideoLeftEdgeObstacle, o_yVideoLeftEdgeObstacle, o_zVideoLeftEdgeObstacle;
    CMessageOutput<CFloatVector> o_xVideoRightEdgeObstacle, o_yVideoRightEdgeObstacle, o_zVideoRightEdgeObstacle;
    CMessageOutput<CFloatVector> o_alphaVideoLeftBorderObstacle, o_alphaVideoRightBorderObstacle;
    CMessageOutput<CFloatVector> o_alphaVideoLeftBorderObstacleRightCourseLine, o_alphaVideoRightBorderObstacleLeftCourseLine;

    //// Line objects
    CMessageOutput<CIntVector>   o_typeLine;
    CMessageOutput<CFloatVector> o_arcLength;
    CMessageOutput<CIntVector>   o_indexLine;
    CMessageOutput<CFloatVector> o_xVideoLineStart, o_yVideoLineStart, o_zVideoLineStart;
    CMessageOutput<CFloatVector> o_gammaVideoLineStart;
    CMessageOutput<CFloatVector> o_xVideoLineEnd, o_yVideoLineEnd, o_zVideoLineEnd;
    CMessageOutput<CFloatVector> o_curvatureLineStart;
    CMessageOutput<CFloatVector> o_curvatureDerivativeLineStart;

    // sensor properties
    CMessageParameter<CBool>  p_sensorBlind; // enable/disable video validation
    CMessageParameter<CInt>   p_maxNumberOfRelevantLines;
private:
    CMessageInput<CInt>   i_currentRoadIndex;
    CMessageInput<CInt>   i_currentLaneID;
    CMessageInput<CInt>   i_searchIDLane;

    CMessageInput<CFloat, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_lateralOffsetCourseObstacleDynamic;
    CMessageInput<CFloat, CObstacleDynamic, CModuleVector<CObstacleDynamic> > i_trackWidthBackObstacleDynamic;

    CMessageInput<CFloat, CRoad, CModuleVector<CRoad> > i_lengthOfCourseRoad;
    CMessageInput<CInt, CRoad, CModuleVector<CRoad> > i_numberOfLanesReferencePoints;
    CMessageInput<CInt, CRoad, CModuleVector<CRoad> > i_numberOfLanesRoad;
    CMessageInput<CInt, CRoad, CModuleVector<CRoad> > i_numberOfLanesLeftRoad;
    CMessageInput<CInt, CRoad, CModuleVector<CRoad> > i_numberOfLanesRightRoad;
    CMessageInput<CInt, CRoad, CModuleVector<CRoad> > i_indexOfLeftmostLaneRoad;
    CMessageInput<CInt, CRoad, CModuleVector<CRoad> > i_indexOfRightmostLaneRoad;


    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloatVectorXYZ>& f_xyzWorld,
               IMessage<CFloatVectorXYZ>& f_velocityXYZWorld,
               IMessage<CFloatVectorXYZ>& f_accelerationXYZVehicleEgo,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYawEgo,
               IMessage<CFloat>& f_yawRateEgo,
               CObstacles& f_obstacles_r,
               IMessage<CBool>& f_staticSimulation,
               IMessage<CInt>&   f_currentRoadIndex,
               IMessage<CInt>&   f_currentLaneIndex,
               IMessage<CInt>& f_searchIndexLane,
               CRoadNetwork& f_roadNetwork_r );
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

    bool findIntersectionVideoLineAndFieldOfView( CLine& f_laneBoundary_r, CFloat& f_sStart, CFloat& f_sEnd );

    bool findIntersectionVideoLineAndFieldOfView( CLine& f_laneBoundary_r, CFloat& f_sStart, CFloat& f_sEnd, CInt f_noOfReferencePoints, CInt f_startIndex );

    //*******************************
    //variables
    //*******************************
public:
private:
    CFloatVector m_obstacleDynamicVisibility;
    CIntVector m_obstacleDynamicVisibilityIndexList;
    CFloatVector m_obstacleStaticVisibility;
    CIntVector m_obstacleStaticVisibilityIndexList;
    CInt m_egoLaneID; // lane ID in signed notation (see CRoad.h)


    CFloat m_xWorldLeftEdgeObstacle;
    CFloat m_yWorldLeftEdgeObstacle;
    CFloat m_zWorldLeftEdgeObstacle;
    CFloat m_xWorldRightEdgeObstacle;
    CFloat m_yWorldRightEdgeObstacle;
    CFloat m_zWorldRightEdgeObstacle;
};


////*********************************
//// CObstacleVideo
////*********************************
class CObstacleVideo : public CObstacleSensor
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CObstacleVideo();
    virtual ~CObstacleVideo();
    //*******************************
    // methods
    //*******************************
public:
    /*!
    * Calculate the video obstacle information
    * @param[in]  ...
    * @param[out] ...
    */
    CBool updateObstacleMessages(
        // generic messages
        CInt& f_indexObstacle_r, CInt& f_typeObstacle_r, CInt& f_referenceSurfaceObstacle_r, CFloat& f_visibilityObstacle_r,
        CFloat& f_xSensorObstacle_r, CFloat& f_ySensorObstacle_r, CFloat& f_zSensorObstacle_r,
        CFloat& f_azimuthVideoObstacle_r, CFloat& f_yawAngleSensorObstacle_r,
        CFloat& f_heightSensorObstacle_r, CFloat& f_widthSensorObstacle_r, CFloat& f_lengthSensorObstacle_r,
        CFloat& f_vXSensorObstacle_r, CFloat& f_vYSensorObstacle_r, CFloat& f_vZSensorObstacle_r,
        CFloat& f_aXVehicleObstacle_r, CFloat& f_aYVehicleObstacle_r, CFloat& f_aZVehicleObstacle_r,
        CFloat& f_distanceSensorObstacle_r,
        CInt f_referenceSurfaceObstacleFixed,
        // CVideo specific messages
        CFloat& f_xWorldLeftEdgeObstacle_r, CFloat& f_yWorldLeftEdgeObstacle_r, CFloat& f_zWorldLeftEdgeObstacle_r,
        CFloat& f_xWorldRightEdgeObstacle_r, CFloat& f_yWorldRightEdgeObstacle_r, CFloat& f_zWorldRightEdgeObstacle_r,
        CFloat& f_xVideoLeftEdgeObstacle_r, CFloat& f_yVideoLeftEdgeObstacle_r, CFloat& f_zVideoLeftEdgeObstacle_r,
        CFloat& f_xVideoRightEdgeObstacle_r, CFloat& f_yVideoRightEdgeObstacle_r, CFloat& f_zVideoRightEdgeObstacle_r,
        CFloat& f_azimuthSensorLeftBorderObstacle_r,
        CFloat& f_azimuthSensorRightBorderObstacle_r
    );

private:
    CFloat calcIntersectionPoint( CInt f_contourIndex );

    //*******************************
    //variables
    //*******************************
private:
};


//////*********************************
////// CLineVideo
//////*********************************
class CLineVideo
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CLineVideo();
    virtual ~CLineVideo();
    //*******************************
    // methods
    //*******************************
public:
    void init();
    void init( CInt f_indexLine,
               CFloat f_rollAngle, CFloat f_pitchAngle, CFloat f_yawAngle,
               CFloat f_x, CFloat f_y, CFloat f_z,
               CLine& f_line_r,
               CFloat f_sStart, CFloat f_sEnd );

    // initialization of connected lanes video line
    void init( CInt f_indexLine,
               CFloat f_rollAngle, CFloat f_pitchAngle, CFloat f_yawAngle,
               CFloat f_x, CFloat f_y, CFloat f_z,
               CLine& f_firstLine_r,
               CLine& f_secondLine_r,
               CFloat f_sStart, CFloat f_sConnection, CFloat f_sEnd );
    /*!
    * Update the video line messages by member variables
    * @param[in]  ...
    * @param[out] ...
    */
    CInt updateVideoLineMessages(
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
    );

    //*******************************
    //variables
    //*******************************
private:
    CInt m_indexLine;
    CLine* m_lineObject_p;
    CInt m_typeLine;
    CFloat m_arcLength;
    CFloat m_xVideoLineStart;
    CFloat m_yVideoLineStart;
    CFloat m_zVideoLineStart;
    CFloat m_gammaVideoLineStart;
    CFloat m_xVideoLineEnd;
    CFloat m_yVideoLineEnd;
    CFloat m_zVideoLineEnd;
    CFloat m_gammaVideoLineEnd;
    CFloat m_xWorldLineStart;
    CFloat m_yWorldLineStart;
    CFloat m_zWorldLineStart;
    CFloat m_dxWorldLineStart;
    CFloat m_dyWorldLineStart;
    CFloat m_dzWorldLineStart;
    CFloat m_ddxWorldLineStart;
    CFloat m_ddyWorldLineStart;
    CFloat m_ddzWorldLineStart;
    CFloat m_xWorldLineEnd;
    CFloat m_yWorldLineEnd;
    CFloat m_zWorldLineEnd;
    CFloat m_dxWorldLineEnd;
    CFloat m_dyWorldLineEnd;
    CFloat m_dzWorldLineEnd;
    CFloat m_ddxWorldLineEnd;
    CFloat m_ddyWorldLineEnd;
    CFloat m_ddzWorldLineEnd;
    CFloat m_gammaWorldLineStart;
    CFloat m_curvatureLineStart;
    CFloat m_curvatureLineEnd;
    CFloat m_curvatureDerivativeLineStart;
};

#endif // CVIDEO_H
