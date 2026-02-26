#ifndef CLane_H
#define CLane_H
/*!
********************************************************************************
@class CLane
@ingroup roadNetwork
@brief lane of a road with a corresponding course line in the middle

@author Robert Erhart, ett2si (03.07.2015)
@copyright (c) Robert Bosch GmbH 2015-2024. All rights reserved.
********************************************************************************
@remark
- lane is horizontal projection of halfway line in x(s)-y(s) plane and addition of elevator profile z(s)
********************************************************************************
@param[out] p_connections                 [index, index, m, ...]   (vector)  array of information on connected lanes indices: [roadIndex1, laneIndex1, courseDistance1, roadIndex2, ...].
@param[out] o_lengthOfCourse              [m]   length of course line of the lane
@param[out] o_numberOfLaneReferencePoints []    number of reference x,y,z points of the lane
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CLaneDoc
{
    const auto p_connections                = "(vector)  array of information on connected lanes indices: [roadIndex1, laneIndex1, courseDistance1, roadIndex2, ...]."; //Negative road index indicates 'no connection'.";
    const auto o_lengthOfCourse             = "[m] length of course line of the lane";
    const auto o_numberOfLaneReferencePoints = "[] number of reference x,y,z points of the lane";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/framework/CSplineAkima.h>
#include <claraSim/framework/CClothoid.h>
#include <claraSim/framework/CTable.h>
#include <claraSim/framework/CLine.h>
#include <vector>

// Information on a position relative to the course. Position is parametrized by path length 's' and lateral offset:
//  s:              [m] path parameter
//  lateralOffset:  [m] lateral offset
//  x:              [m] x position
//  y:              [m] y position
//  z:              [m] z position
//  xyz:            [m] position vector
//  dx:             [m] derivative of the course in x direction
//  dy:             [m] derivative of the course in y direction
//  dz:             [m] derivative of the course in z direction
//  gammaAngle      [rad] angle of the course in x-y plane
//  crossfallAngleLocal [rad] crossfall angle (transverse slope) of the course
//  slopeAngleLocal [rad] slope angle (longitudinal slope) of the course
//  trackwidth      [m] width of the course
//  indexLast       [m] index of the Akima segment the previous position was related to
struct SCoursePositionInfo
{
    CFloat s;
    CFloat lateralOffset;
    CFloat x;
    CFloat y;
    CFloat z;
    //CFloatVector xyz;
    CFloat dx;
    CFloat dy;
    CFloat dz;
    CFloat gammaAngle;
    CFloat crossfallAngleLocal;
    CFloat slopeAngleLocal;
    CFloat trackwidth;
    CInt indexLast;
};

struct SPositionInfo
{
    CFloat s;
    CFloat distanceSplinePoint;
    CFloat x;
    CFloat y;
    CFloat z;
    //CFloatVector xyz;
    CFloat dx;
    CFloat dy;
    CFloat dz;
    CInt indexLast;
};

class CLane : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CLane();
    virtual ~CLane();
private:
    CLane( const CLane& f_module ) = delete;


    //*******************************
    //classes
    //*******************************
public:
    enum { left = 0, right = 1};
    CLine CourseLine;
    ::std::vector<CLine> BoundaryLine;
private:
    CClothoid clothoid;
    CSplineAkima trackWidthSpline;
    CSplineAkima crossfallSpline;


    //*******************************
    //messages
    //*******************************
public:
    CMessageParameter<CFloatVector> p_connections;

    CMessageOutput<CFloat> o_lengthOfCourse;
    CMessageOutput<CInt> o_numberOfLaneReferencePoints;


    //*******************************
    // methods
    //*******************************
public:
    SCoursePositionInfo findCoursePositionInfo( CFloat f_x, CFloat f_y, CInt& f_index );
    SCoursePositionInfo getCoursePositionInfo( CFloat f_s, CFloat f_lateralOffset );
    SPositionInfo findLeftBoundaryPositionInfo( CFloat f_x, CFloat f_y, CInt& f_index );
    SPositionInfo findRightBoundaryPositionInfo( CFloat f_x, CFloat f_y, CInt& f_index );
    CFloat getTrackWidth( CFloat f_s );
    CFloat getCrossfall( CFloat f_s );

    void init();
    void init( CFloatVector& f_sVector_r, CFloatVector& f_xVector_r, CFloatVector& f_yVector_r, CFloatVector& f_zVector_r,
               CFloatVector& f_trackWidth_r, CFloatVector& f_crossfall_r ); // initLane; /* use only, if simulation is stopped */

private:
    void calcBoundaryVectors( bool f_leftRight, CFloatVector& f_xBoundary, CFloatVector& f_yBoundary, CFloatVector& f_zBoundary, CFloatVector& f_sBoundary );
    void calc( CFloat f_dT, CFloat f_time ) {}; //not used in CLane; overload abstract method of class CClass


    //*******************************
    //variables
    //*******************************
private:
    CFloat m_errorTolerance;
    uint32_t m_indexSearch;
};

#endif // CLane_H
