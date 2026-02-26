#ifndef CRoad_H
#define CRoad_H
/*!
********************************************************************************
@class CRoad
@ingroup roadNetwork
@brief road with n lanes and road boundaries

@author Robert Erhart, ett2si (03.07.2015)
@copyright (c) Robert Bosch GmbH 2015-2024. All rights reserved.
********************************************************************************
@remark
- road is horizontal projection of halfway line in x(s)-y(s) plane and addition of elevator profile z(s)
@verbatim
                    |    |    |    |    |
                    |    |    |    |    |
                    |    |    |    |    |
                    |    | x  |    |    |
                    |    |    |    |    |
lane ID               +1   +0   -1   -2
index (lanes[i])      1     0    3    2   (assuming roadNetwork.o_NumberOfLanes==4)
index (lanes[i])      1     0    5    4   (assuming roadNetwork.o_NumberOfLanes==6)

CRoad member 'lanes' array indices are always positive. The above example indicates array index assignment.

lane ID 0:   reference lane for clothoide, gradient and crossfall
positive ID: to the left of reference lane
negative ID: to the right of reference lane
x:           ego vehicle

Course definition can be split into course segments.
These segments may be defined INDEPENDENTLY for different (independent) properties of the course, like horizontal shape and lane widths.
This means 'lengthSegmentA' does not need to match between p_clothoidLine, p_lanes, ... in the examples below.

- clothoidLine:  horizontal projection of the course, defined by Clothoids of reference lane. I.e. [ [lengthSegmentA, curvatureInA, curvatureOutA],  [lengthSegmentB, curvatureInB, curvatureOutB], ... ]
- gradientLine:  slope of the course Z profile in percent. I.e. [ [lengthSegmentA, slopeInA, slopeOutA], [lengthSegmentB, slopeInB, slopeOutB], ...]
- crossfallLine: crossfall of the road in radians. I.e. [ [lengthSegmentA, crossfallInA, crossfallOutA], [lengthSegmentB, crossfallInB, crossfallOutB], ...]
- lanes:         number of lanes, lane IDs, and lane width definition in meters. Technical syntax given below.
                 A lane segment is defined by its length (e.g. 'lengthSegmentA' below) and start/end width of each lane.
                 Linear interpolation is used for the transition from start to end width along the segment length.
@endverbatim
********************************************************************************
@param[out] o_lengthOfCourse       [m]   length of Course
@param[out] o_numberOfLanes        [-]   number of lanes
@param[out] o_numberOfLanesLeft    [-]   number of left lanes from reference lane with index 0
@param[out] o_numberOfLanesRight   [-]   number of right lanes from reference lane with index 0
@param[out] o_indexOfLeftmostLane  [-]   index of the left most lane
@param[out] o_indexOfRightmostLane [-]   index of the right most lane
@param[out] o_numberOfLaneReferencePoints [] Number of reference x,y,z points of lane zero
********************************************************************************
@param[in,out] p_startPoint    [x [m], y [m], z [m], phi [rad]] start position in world coordinate system
@param[in,out] p_startPointRelative [ roadIndex [int], laneIndex [int], s [float] ] *relative* start position in roadNetowork parameters
@param[in,out] p_clothoidLine  [LIST[length [m], in [1/R], out [1/R]]]
@param[in,out] p_gradientLine  [LIST[length [m], in [%],   out [%]  ]]
@param[in,out] p_crossfallLine [LIST[length [m], in [rad], out [rad]]]  positive: left banked turn (Steilkurve links)
@param[in,out] p_lanes         [NrOfLanes, indexLane0, indexLane1, ..., lengthSegmentA, startWidth0, endWidth0,
                                                                                        startWidth1, endWidth1,
                                                                                        startWidth2, endWidth2, ...
                                                                        lengthSegmentB, startWidth0, endWidth0,
                                                                                        startWidth1, endWidth1,
                                                                                        startWidth2, endWidth2, ...]
                               Parameter      | Unit     | Description
                               ---------------|----------|----------------
                               NrOfLanes      | 1..n     | number of lanes
                               indexLane1     | +-number | left or right from reference lane 0
                               indexLaneX     | +-number | left or right from reference lane 0
                               lengthSegmentA | [m]      | length of the course segment
                               startWidth0    | [m]      | start track width of the segment (reference lane)
                               endWidth0      | [m]      | start track width of the segment (reference lane)
                               startWidthN    | [m]      | start track width of the segment (lane with indexLaneN)
                               endWidthN      | [m]      | start track width of the segment (lane with indexLaneN)

                               Remark: Reference lane needs to be enclosed in segment track width definition ( => startWidth0, endWidth0).
                                       Its index (=0) therefore must be part of the "indexLaneN" list.
                                       All lane widths are listed in the order of lane indices (indexLaneN) in the segment definition.

@param[in,out] p_roadBoundary  [ lengthRoadSegment, type, distance, side, p_depth, p_height, p_width ]
                               Parameter         | Unit   | Description
                               ------------------|--------|----------------
                               lengthRoadSegment | [m]    | length road segment
                               type              | [enum] | type\n
                               distance          | [m]    | distance between boundaries
                               side              | [enum] | side 0:no 1:left, 2:right, 3:both
                               p_depth           | [m]    | depth of the obstacle
                               p_height          | [m]    | height of the obstacle
                               p_width           | [m]    | width of the obstacle
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CRoadDoc
{
    const auto p_startPoint = "[x [m], y [m], z [m], phi [rad]] start position in world coordinate system";
    const auto p_startPointRelative = "[ roadIndex [int], laneIndex [int], s [float] ] *relative* start position in roadNetwork parameters";
    const auto p_clothoidLine = "[LIST[length [m], in [1/R], out [1/R]]]";
    const auto p_gradientLine = "[LIST[length [m], in [%], out [%] ]]";
    const auto p_crossfallLine = "[LIST[length [m], in [rad], out [rad]]]  positive: left banked turn (Steilkurve links)";
    const auto p_lanes = "[[NrOfLanes, indexLane1, indexLane2, ...], [lengthSegmentA, startWidth0, endWidth0, startWidth1, endWidth1, startWidth2, endWidth2], [lengthSegmentB, startWidth0, endWidth0, startWidth1, endWidth1, startWidth2, endWidth2], ...]";
    const auto p_roadBoundary = "[lengthRoadSegment, type, distance, side, p_depth, p_height, p_width ]";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/framework/CModuleVector.h> // for vectors with negative index access
#include <claraSim/framework/CSplineAkima.h>
#include <claraSim/framework/CClothoid.h>
#include "CLane.h"

class CRoad : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CRoad( void* numberOfLanes_p );
    virtual ~CRoad();

    //*******************************
    //classes
    //*******************************
public:
    CModuleVector<CLane> lanes;
private:
    CClothoid clothoid;


    //*******************************
    //messages
    //*******************************
public:
    CMessageParameter<CFloatVector> p_startPoint;
    CMessageParameter<CFloatVector> p_startPointRelative;
    CMessageParameter<CFloatVector> p_clothoidLine;
    CMessageParameter<CFloatVector> p_gradientLine;
    CMessageParameter<CFloatVector> p_crossfallLine;
    CMessageParameter<CFloatVector> p_lanes;
    CMessageParameter<CFloatVector> p_roadBoundary;

    CMessageOutput<CFloat> o_lengthOfCourse;
    CMessageOutput<CInt> o_numberOfLanesReferencePoints;
    CMessageOutput<CInt> o_numberOfLanes;
    CMessageOutput<CInt> o_numberOfLanesLeft;
    CMessageOutput<CInt> o_numberOfLanesRight;
    CMessageOutput<CInt> o_indexOfLeftmostLane;
    CMessageOutput<CInt> o_indexOfRightmostLane;


    //*******************************
    // methods
    //*******************************
public:
    //! Calculate the course. Use only while simulation is stopped!
    void init();

    //! Copy init values of p_startPoint and p_startPointRelative
    void initStartPoints();

    //! Check whether 'f_laneID' is a valid lane ID of this CRoad instance.
    bool isValidLaneID( CInt f_laneID );

    //! Check whether 'f_laneArrayIndx' is a valid array index for this CRoad instance
    bool isValidLaneArrayIndex( CInt f_laneArrayIndex );

    //! Get the CRoad.lanes array index of lane from a signed laneID.
    //! Produces error message if invalid laneID was supplied and showError==true.
    CInt getLaneArrayIndex( CInt f_laneID, bool f_showError = true );

    //! Get the signed lane ID from CRoad.lanes array index (positive: left of reference lane, negative: right of reference lane)
    CInt getLaneID( CInt f_laneArrayIndex, bool f_showError = true );



private:
    void calc( CFloat f_dT, CFloat f_time );
    void calcCourse();

    //! Updates argument CFloatVectors (x,y,s) using Spline sampling points derived from the course Clothoid.
    //! The course Clothoid is defined stepwise (in segments) in p_clothoidLine.
    //! Sampling step size is given by member variable 'm_stepSize'.
    //! returns 'true' if error-free.
    bool calcCourseClothoidSamplingPoints( CFloatVector& x, CFloatVector& y, CFloatVector& s );

    //! Calculate linear interpolation points of a segmented gradient profile input. Output consists of 'independent variable' s and 'dependent variable' z = z(s)
    //! returns 'true' if error-free.
    //! @param[in]   f_gradientSegmentList_r  [CFloatVector&]  segmented gradient profile input, required format: [length(Seg0), z_grad_start(Seg0), z_grad_end(Seg0), length(Seg1), z_grad_start(Seg1), z_grad_end(Seg1), ..., z_grad_end(SegN)]
    //! @param[out]  f_z_r           [CFloatVector&]  interpolated profile output, i.e. a vector of form: [z_start(Seg0), z_start(Seg0)+delta, z_start(Seg0)+2*delta, ..., z_end(Seg0), z_start(Seg1), z_start(Seg1)+delta, ..., z_end(SegN)]
    //! @param[out]  f_s_r           [CFloatVector&]  independent variable interpolation output, i.e. a vector of form: [0, 0+delta_s, ..., length(Seg0), length(Seg0)+delta_s, ..., sum_i( length(Seg_i) )]
    bool calcCourseGradientSamplingPoints( const CFloatVector& f_inputValue_r, CFloatVector& f_z_r, CFloatVector& f_s_r );

    //! Calculate linear interpolation points of a segmented profile input. Output consists of 'independent variable' s and 'dependent variable' z = z(s)
    //! returns 'true' if error-free.
    //! @param[in]   f_inputSegmentList_r  [CFloatVector&]  segmented profile input, required format: [length(Seg0), z_start(Seg0), z_end(Seg0), length(Seg1), z_start(Seg1), z_end(Seg1), ..., z_end(SegN)]
    //! @param[out]  f_z_r           [CFloatVector&]  interpolated profile output, i.e. a vector of form: [z_start(Seg0), z_start(Seg0)+delta, z_start(Seg0)+2*delta, ..., z_end(Seg0), z_start(Seg1), z_start(Seg1)+delta, ..., z_end(SegN)]
    //! @param[out]  f_s_r           [CFloatVector&]  independent variable interpolation output, i.e. a vector of form: [0, 0+delta_s, ..., length(Seg0), length(Seg0)+delta_s, ..., sum_i( length(Seg_i) )]
    bool calcLinearSamplingPoints( const CFloatVector& f_inputValue_r, CFloatVector& f_z_r, CFloatVector& f_s_r );

    void calcNeighborVectors( CInt f_laneID, CSplineAkima& f_trackWidthSpline_r, CFloatVector& f_xBoundary_r, CFloatVector& f_yBoundary_r, CFloatVector& f_zBoundary_r, CFloatVector& f_sBoundary_r );
    void resizeVector( CFloatVector& vector, size_t size ) const;

    //*******************************
    //variables
    //*******************************
private:
    CFloatVector m_laneReference;
    CInt m_numberOfLanes = 0;
    CInt m_numberOfLeftLanes = 0;
    CInt m_numberOfRightLanes = 0;
    CFloat m_stepSize;
};

#endif // CRoad_H
