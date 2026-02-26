/*******************************************************************************
@author Robert Erhart, ett2si (03.07.2015)
@copyright (c) Robert Bosch GmbH 2015-2024. All rights reserved.
*******************************************************************************/

#include "CRoad.h"
#include <claraSim/world/obstacle/CObstacles.h>

#include <iostream>
#include <map>
#include <list>

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CRoad::CRoad( void* numberOfLanes_p ):
    lanes( *static_cast<uint32_t*>( numberOfLanes_p ) )
{
    m_stepSize = 2;           //[m] max distance between two points in the spline
    o_lengthOfCourse = 0.0;
    // start point (m , m, m)
    CFloatVector t_startPoint {0, 0, 0, 0}; //-M_PI_2
    CFloatVector t_startPointRelative {-1, -1, -1};

    // default altitude (length, start gradient, end gradient) * x
    CFloatVector t_gradientVector {1000, 0, 0, 20, 0, 4, 2000, 4, 4};//, 20, 4, 0, 20, 0, 0, 500, 0, 0, 30, 0, 0, 1000, 0, 0};

    // default crossfall (length, start crossfall, end crossfall) * x
    CFloatVector t_crossfallVector {500, 0, 0, 50, 0, 0.05, 200, 0.05, 0.1, 50, 0.1, 0, 50, 0, 0};

    // default clothoid ( length, start bend, end bend ) * x
    CFloatVector t_clothoidVector {1000, 0, 0, 20, 0, 0.002, 2000, 0.002, 0.002, 20, 0.002, 0, 20, 0, -0.006, 1000, -0.006, -0.006, 30, -0.006, 0, 1000, 0, 0};

    // default laneWidth ( NrOfLanes, indexLane1, indexLane2 lengthSegmentLaneO, startWidth, endWidth,
    //                                                                           startWidth, endWidth,
    //                                                                           startWidth, endWidth, ...
    //                                                       lengthSegmentLaneO, startWidth, endWidth,
    //                                                                           startWidth, endWidth,
    //                                                                           startWidth, endWidth, ...
    //                                                       ...
    CFloatVector t_laneVector {4, -1, 0, 1, 2,      500,  3.5, 3.5,   3.75, 3.75,   3.5, 3.5,   3.5, 3.5,
                               10,  3.5, 3.5,   3.75, 3.75,   3.5, 3.5,   3.5, 3.5,
                               100, 3.5, 3.5,   3.75, 3.75,   3.5, 3.5,   3.5, 3.5
                              };

//  roadBoundary
//  [ lengthRoadSegment, type, distance, side, p_depth, p_height, p_width]
//                                              [m]    length road segment
//                                              [enum] type
//                                              [m]    distance between boundaries
//                                              [enum] side 0:no 1:left, 2:right,  3:both
//                                              [m]    length of the obstacle
//                                              [m]    height of the obstacle
//                                              [m]    width of the obstacle
    CFloatVector t_roadBoundaryVector { 5000, EObstacleTyp::DELINEATOR, 50, 3, 0.12, 1.0, 0.12 };

    // NOTE:
    // The parameter and output messages of CRoad are NOT intended to be dynamic during a test run.
    // Therefore, addMessageParameter and addMessageOutput are not called here.
    p_startPoint.setMessageDescription( CRoadDoc::p_startPoint );
    p_startPoint.init( t_startPoint );
    p_startPointRelative.setMessageDescription( CRoadDoc::p_startPointRelative );
    p_startPointRelative.init( t_startPointRelative );
    p_clothoidLine.setMessageDescription( CRoadDoc::p_clothoidLine );
    p_clothoidLine.init( t_clothoidVector );
    p_gradientLine.setMessageDescription( CRoadDoc::p_gradientLine );
    p_gradientLine.init( t_gradientVector );
    p_crossfallLine.setMessageDescription( CRoadDoc::p_crossfallLine );
    p_crossfallLine.init( t_crossfallVector );
    p_lanes.setMessageDescription( CRoadDoc::p_lanes );
    p_lanes.init( t_laneVector );
    p_roadBoundary.setMessageDescription( CRoadDoc::p_roadBoundary );
    p_roadBoundary.init( t_roadBoundaryVector );
}

CRoad::~CRoad()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CRoad::initStartPoints()
{
    p_startPoint.copyValueInit();
    p_startPointRelative.copyValueInit();
}

void CRoad::init()         // use only, if simulation is stopped
{
    // default altitude (length, start gradient, end gradient) * x
    p_gradientLine.copyValueInit();
    // default crossfall (length, start crossfall, end crossfall) * x
    p_crossfallLine.copyValueInit(); //not used
    // default clothoid ( length, start bend, end bend ) * x
    p_clothoidLine.copyValueInit();
    // default lane ( length, start bend, end bend ) * x
    p_lanes.copyValueInit();
    // default roadBoundary ( length, start bend, end bend ) * x
    p_roadBoundary.copyValueInit();

    calcCourse(); //calls 'init' method of lanes, amongst others

    unsigned int i = 0;
    o_lengthOfCourse = 0;
    while( i < p_clothoidLine.size() )
    {
        o_lengthOfCourse = o_lengthOfCourse + p_clothoidLine[i];
        i = i + 3;
    }
    o_lengthOfCourse.copyValueWorkToCom( -1 );

    o_numberOfLanes.init( m_numberOfLanes );
    o_numberOfLanesLeft.init( m_numberOfLeftLanes );
    o_numberOfLanesRight.init( m_numberOfRightLanes );
    o_indexOfLeftmostLane.init( o_numberOfLanesLeft );
    o_indexOfRightmostLane.init( getLaneArrayIndex( -m_numberOfRightLanes, true ) );
    o_numberOfLanesReferencePoints.init( lanes[0].o_numberOfLaneReferencePoints.get() );
}


bool CRoad::isValidLaneID( CInt f_laneID )
{
    return ::sim::in_range( f_laneID, -m_numberOfRightLanes, m_numberOfLeftLanes );
}

bool CRoad::isValidLaneArrayIndex( CInt f_laneArrayIndex )
{
    if( ::sim::in_range( f_laneArrayIndex, 0, m_numberOfLeftLanes ) ) return true;     // ref lane or left lanes
    else if( ::sim::in_range( f_laneArrayIndex, lanes.size() - m_numberOfRightLanes, lanes.size() - 1 ) ) return true; // right lanes
    else return false;
}

CInt CRoad::getLaneArrayIndex( CInt f_laneID, bool f_showError )
{
    if( isValidLaneID( f_laneID ) ) // valid laneID
    {
        if( f_laneID >= 0 )  return f_laneID; // positive IDs are equivalent to array index
        else                return lanes.size() + f_laneID; // negative IDs: indexing from right hand side
    }
    else
    {
        if( f_showError ) std::cerr << "ERROR <CRoad::getLaneArrayIndex>: argument 'f_laneID' is out of range." << std::endl;
        return ::std::numeric_limits<int>::min();
    }
}

//! Get the signed lane ID from CRoad.lanes array index (positive: left of reference lane, negative: right of reference lane)
CInt CRoad::getLaneID( CInt f_laneArrayIndex, bool f_showError )
{
    if( isValidLaneArrayIndex( f_laneArrayIndex ) ) //  (f_laneArrayIndex < m_numberOfLanes) // valid laneArrayIndex
    {
        if( f_laneArrayIndex <= m_numberOfLeftLanes )    return f_laneArrayIndex; // array index is equivalent to ID
        else                                            return ( f_laneArrayIndex - lanes.size() );
    }
    else
    {
        if( f_showError ) std::cerr << "ERROR <CRoad::getLaneID>: argument 'f_laneArrayIndex' is out of range." << std::endl;
        return ::std::numeric_limits<int>::min();
    }
}

/*------------------*/
/* private methods */
/*------------------*/

void CRoad::calc( CFloat f_dT, CFloat f_time )
{
    /* calculate road components */
    lanes.process( f_dT, f_time );
}

void CRoad::calcCourse()
{
    // number of lanes
    m_numberOfLanes = static_cast<CInt>( p_lanes[0] );
    if( p_lanes[0] <= 0 or static_cast<size_t>(m_numberOfLanes) > lanes.size() )
    {
        //::std::cerr << "ERROR <CRoad::calcCourse>: Number of lanes must be > 0" << ::std::endl;
        return;
    }

    //number of segments per lane:
    CInt l_numberOfSegments = ( p_lanes.size() - m_numberOfLanes - 1 ) / ( m_numberOfLanes * 2 + 1 ); // see definition of p_lanes in header

    if( l_numberOfSegments < 1 )
    {
        ::std::cerr << "ERROR <CRoad::calcCourse>: l_numberOfSegments < 1" << ::std::endl;
        return;
    }

    //local variables
    CFloatVector x, y, sk;
    CFloatVector z, zNew, sh;
    CFloatVector trackWidth, trackWidthNew, sTrackWidth;
    CFloatVector crossfall, crossfallNew, sCrossfall;
    CSplineAkima l_zSplineCoordinate, l_trackWidthSpline, l_crossfallSpline;
    ::std::map <CInt, CInt> l_laneIDtoArray; // no malloc problem here, since 'calcCourse' is not called in real time context, but only during init.
    std::list<CInt> l_laneIDlist;

    //! Helper function: Find p_lanes array index corresponding to 'laneID' input; -1 return value if not found
    auto findIndex = [this]( CInt laneID )
    {
        for( CInt i = 1; i < m_numberOfLanes + 1; i++ )
        {
            if( static_cast<CInt>( p_lanes[i] ) == laneID )  return i;
        }
        return CInt( -1 ); //
    };

    // Input p_lane vector analysis
    m_numberOfLeftLanes = 0;
    m_numberOfRightLanes = 0;

    for( CInt laneID = 0; laneID > -m_numberOfLanes; )
    {
        CInt l_arrayIndex = findIndex( laneID );

        if( l_arrayIndex >= 1 ) // laneID was found in array
        {
            l_laneIDtoArray[laneID] = l_arrayIndex;
            l_laneIDlist.push_back( laneID );

            if( laneID > 0 ) m_numberOfLeftLanes++;
            if( laneID < 0 ) m_numberOfRightLanes++;
        }

        // Increment step
        // Increment 'laneID' from zero to m_numberOfLanes-1.
        // If 'laneID' reached m_numberOfLanes-1, switch to negative sign_of (laneID=-1).
        // If 'laneID'<0: decrement, until for loop ends
        if( ::sim::in_range( laneID, 0, m_numberOfLanes - 2 ) )
        {
            laneID++;
        }
        else if( laneID == m_numberOfLanes - 1 )
        {
            laneID = -1;
        }
        else
        {
            laneID--;
        }
    }

    //**********************************************************************
    //*                     create reference lane
    //**********************************************************************
    m_laneReference.resize( l_numberOfSegments * 3 ); // target structure: [lengthSegmentA, startWidth_iA, stopWidth_iA, lengthSegmentB, startWidth_iB, stopWidth_iB, ...]
    uint32_t l_index = 0;

    // Start by initializing unused lanes with default initializer. This will be overwritten for used lanes below.
    for( size_t l_indexLane = 0; l_indexLane < lanes.size(); ++l_indexLane )
    {
        if( not isValidLaneArrayIndex( l_indexLane ) )
        {
            lanes[l_indexLane].init();
        }

    }


    for( CInt l_laneID : l_laneIDlist )
    {
        if( l_laneIDtoArray.count( l_laneID ) > 0 ) // lane was defined in p_lanes, should be the case for every element of l_laneIDlist
        {
            if( l_laneID == 0 ) // reference lane
            {
                m_laneReference.resize( l_numberOfSegments * 3 ); // target structure: [lengthSegmentA, startWidth_iA, stopWidth_iA, lengthSegmentB, startWidth_iB, stopWidth_iB, ...]
                l_index = 0;
                CInt l_arrayIndexLane = l_laneIDtoArray[l_laneID];

                for( size_t t_indexSegment = static_cast<size_t>(p_lanes[0]) + 1; t_indexSegment < p_lanes.size() - 2; t_indexSegment +=  2 * static_cast<CInt>(p_lanes[0]) + 1 )
                {
                    m_laneReference[l_index] =  p_lanes[t_indexSegment];  // segment length
                    l_index++;
                    m_laneReference[l_index] =  p_lanes[t_indexSegment + 1 + ( l_arrayIndexLane - 1 ) * 2]; // segment startWidth
                    l_index++;
                    m_laneReference[l_index] =  p_lanes[t_indexSegment + 2 + ( l_arrayIndexLane - 1 ) * 2]; // segment stopWidth
                    l_index++;
                }

                if( calcCourseClothoidSamplingPoints( x, y, sk ) )
                {
                    calcCourseGradientSamplingPoints( p_gradientLine, z, sh );
                    calcLinearSamplingPoints( m_laneReference, trackWidth, sTrackWidth );
                    calcLinearSamplingPoints( p_crossfallLine, crossfall, sCrossfall );
                    if( x.size() > 1 and z.size() > 0 )
                    {
                        zNew.resize( sk.size() );
                        trackWidthNew.resize( sk.size() );
                        crossfallNew.resize( sk.size() );
                        l_zSplineCoordinate.init( &sh[0], &z[0], z.size(), false );
                        l_trackWidthSpline.init( &sTrackWidth[0], &trackWidth[0], trackWidth.size(), false );
                        l_crossfallSpline.init( &sCrossfall[0], &crossfall[0], crossfall.size(), false );
                        //recalculate SamplingPoints
                        for( uint32_t l_index = 0; l_index < sk.size(); ++l_index )
                        {
                            zNew[l_index] = l_zSplineCoordinate.Eval( sk[l_index] );
                            trackWidthNew[l_index] = l_trackWidthSpline.Eval( sk[l_index] );
                            crossfallNew[l_index] = l_crossfallSpline.Eval( sk[l_index] );
                        }
                        lanes[0].init( sk, x, y, zNew, trackWidthNew, crossfallNew );
                        //::std::cout << "DEBUG <CRoad::calcCourse>: new course set" << ::std::endl;
                    }
                    else
                    {
                        //::std::cout << "DEBUG <CRoad::calcCourse>: no new course set" << ::std::endl;
                        return;
                    }
                }
                else
                {
                    //::std::cout << "DEBUG <CRoad::calcCourse>: no new course set" << ::std::endl;
                    return;
                }
            }

            else
            {
                uint32_t l_index = 0;
                CInt l_arrayIndexLane = l_laneIDtoArray[l_laneID];
                CFloatVector l_neighborLane( l_numberOfSegments * 3 );

                for( size_t t_indexSegment = static_cast<size_t>(p_lanes[0]) + 1; t_indexSegment < p_lanes.size(); t_indexSegment += 2 * static_cast<CInt>(p_lanes[0]) + 1 ) // for each segment
                {
                    l_neighborLane[l_index] =  p_lanes[t_indexSegment]; // segment length
                    l_index++;
                    l_neighborLane[l_index] =  p_lanes[t_indexSegment + 1 + ( l_arrayIndexLane - 1 ) * 2]; // startWidth of segment
                    l_index++;
                    l_neighborLane[l_index] =  p_lanes[t_indexSegment + 2 + ( l_arrayIndexLane - 1 ) * 2]; // stopWidth of segment
                    l_index++;
                }

                calcLinearSamplingPoints( l_neighborLane, trackWidth, sTrackWidth );
                //crossfall use the same values!!!
                //calc new x y z values mit crossfall berücksichtigung
                //calcNeighborVectors(bool f_leftRight ,CFloatVector& f_xBoundary, CFloatVector& f_yBoundary, CFloatVector& f_zBoundary, CFloatVector& f_sBoundary)
                l_trackWidthSpline.init( &sTrackWidth[0], &trackWidth[0], trackWidth.size(), false );
                l_crossfallSpline.init( &sCrossfall[0], &crossfall[0], crossfall.size(), false );
                calcNeighborVectors( l_laneID, l_trackWidthSpline, x, y, z, sk );
                //recalculate SamplingPoints
                for( uint32_t l_index = 0; l_index < sk.size(); ++l_index )
                {
                    trackWidthNew[l_index] = l_trackWidthSpline.Eval( sk[l_index] );
                    crossfallNew[l_index] = l_crossfallSpline.Eval( sk[l_index] );
                }
                lanes[l_laneID].init( sk, x, y, z, trackWidthNew, crossfallNew );
            }
        }
        else
        {
            print( "<CRoad.cpp> undefined lane" );
        }
    }
}

bool CRoad::calcCourseClothoidSamplingPoints( CFloatVector& x, CFloatVector& y, CFloatVector& s )
{
    //CFloatVector x, y, s;
    CFloatVector alpha, xTemp, yTemp, sTemp, alphaTemp;
    CFloat s1, s2, a1, k1, k2, x1, y1 = 0;

    /* init the start point of the course*/
    s1 = 0;
    a1 = p_startPoint[3];
    x1 = p_startPoint[0];
    y1 = p_startPoint[1];

    /* init the first point for the spline course */
    x.resize( 1 );
    x[0] = x1;
    y.resize( 1 );
    y[0] = y1;
    s.resize( 1 );
    s[0] = s1;
    alpha.resize( 1 );
    alpha[0] = a1;

    /* Iterate through all clothoid segments in p_clothoidLine, create clothoid, and update argument point lists (x,y,s) */
    for( unsigned int index = 0 ; index < p_clothoidLine.size() ; index = index + 3 )
    {
        /* calc values of clothoid segment */
        s2 = s1 + p_clothoidLine[index];
        k1 = p_clothoidLine[index + 1];
        k2 = p_clothoidLine[index + 2];

        /* check for valid data */
        if( s1 == s2 )
        {
            //::std::cout << "WARNING <CRoad::calcCourseClothoid>: no valid clothoid data => no new course set" << ::std::endl;
            return false;
        }

        /* get x, y, s, alpha of the new segment */
        clothoid.init( s1, s2, k1, k2, a1, x1, y1 );
        clothoid.getXY( m_stepSize, sTemp, xTemp, yTemp, alphaTemp );

        /* expand and fill course data with new segment data */
        size_t sizeOld = x.size();
        size_t sizeNew = x.size() + xTemp.size() - 1; // the first and last values of the segments are the same
        resizeVector( x, sizeNew );
        resizeVector( y, sizeNew );
        resizeVector( s, sizeNew );
        resizeVector( alpha, sizeNew );
        // Update values in resized x, y, s, alpha arrays.
        for( size_t i = sizeOld ; i < sizeNew ; i++ )
        {
            x[i] = xTemp[i - sizeOld + 1]; // ignore first value of the new segment
            y[i] = yTemp[i - sizeOld + 1];
            s[i] = sTemp[i - sizeOld + 1];
            alpha[i] = alphaTemp[i - sizeOld + 1];
        }

        /* set start values for next clothoid segment*/
        s1 = s2;
        a1 = alphaTemp[alphaTemp.size() - 1];
        x1 = xTemp[xTemp.size() - 1];
        y1 = yTemp[yTemp.size() - 1];
    }

    return true;
}

bool CRoad::calcCourseGradientSamplingPoints( const CFloatVector& f_gradientSegmentList_r, CFloatVector& f_z_r, CFloatVector& f_s_r )
{
    /* Get height profile:
     *     z(s) = Integral( gradient(s) )
     * Analytic solution:
     *     Integral(gradient(s)) = k1*s + ((k2-k1)/(s2-s1)) * (1/2 * s^2 - s1*s)
     *     z(s) = m_z1 + Integral(gradient(s)) - Integral(gradient(s1))
     */
    CFloatVector alpha, zTemp, sTemp;
    CFloat s1, s2, k1, k2, z1 = 0;

    /* init the start point of the course*/
    s1 = 0;
    z1 = p_startPoint[2];

    /* init the first point for the spline course */
    unsigned int size = 1;
    f_z_r.resize( size );
    f_z_r[0] = z1;
    f_s_r.resize( size );
    f_s_r[0] = s1;


    for( unsigned int index = 0 ; index < f_gradientSegmentList_r.size() ; index = index + 3 )
    {
        /* calc values of gradient segment */
        s2 = s1 + f_gradientSegmentList_r[index];
        k1 = f_gradientSegmentList_r[index + 1] / 100.0;
        k2 = f_gradientSegmentList_r[index + 2] / 100.0;

        /* check for valid data */
        if( s1 == s2 )
        {
            //::std::cout << "WARNING <CRoad::calcCourseGradientSamplingPoints>: no valid height profile data => no new height profile set" << ::std::endl;
            return false;
        }

        /* get f_z_r of the new segment */
        unsigned int sizeSeg = ( unsigned int )( ( s2 - s1 ) / m_stepSize );
        sizeSeg += 2;
        unsigned int indexSeg = size;
        size = size + sizeSeg - 1;
        resizeVector( f_z_r, size );
        resizeVector( f_s_r, size );
        // calc new stepSize
        CFloat stepSizeSeg = ( s2 - s1 ) / ( sizeSeg - 1 );
        // from s1+step to s2 fill z[i] and s[i]
        for( CFloat sValue = s1 + stepSizeSeg; sValue <= s2 + stepSizeSeg / 2.0 ; sValue += stepSizeSeg )  // m_stepSize/2 for float calc errors
        {
            f_z_r[indexSeg] = z1 + k1 * ( sValue - s1 ) + ( ( k2 - k1 ) / ( s2 - s1 ) ) * ( 0.5 * sValue * sValue - s1 * sValue + 0.5 * s1 * s1 );
            f_s_r[indexSeg] = sValue;
            indexSeg++;
        }
        /* set values for next segment*/
        s1 = s2;
        z1 = f_z_r[f_z_r.size() - 1];
    }
    return true;
}

bool CRoad::calcLinearSamplingPoints( const CFloatVector& f_inputSegmentList_r, CFloatVector& f_z_r, CFloatVector& f_s_r )
{
    /* z(s) = Integral(f(s))
     * analytisch lösbar: Integral(gradient(s)) = k1*s + ((k2-k1)/(s2-s1)) * (1/2 * s^2 - s1*s)
     *                    z(s) = m_z1 + Integral(gradient(s)) - Integral(gradient(s1))
     */
    CFloatVector alpha, zTemp, sTemp;
    CFloat s1, s2, k1, k2, z1 = 0;

    /* init the start point of the course*/
    s1 = 0;

    /* init the first point for the spline course */
    unsigned int size = 1;
    f_z_r.resize( size );
    f_z_r[0] = f_inputSegmentList_r[1];
    f_s_r.resize( size );
    f_s_r[0] = s1;

    for( unsigned int index = 0 ; index < f_inputSegmentList_r.size() ; index = index + 3 )
    {
        /* calc values of segment */
        s2 = s1 + f_inputSegmentList_r[index];
        k1 = f_inputSegmentList_r[index + 1];
        k2 = f_inputSegmentList_r[index + 2];
        z1 = k1;

        /* check for valid data */
        if( s1 == s2 )
        {
            //::std::cout << "WARNING <CRoad::calcLinearSamplingPoints>: no valid profile data => no new profile set" << ::std::endl;
            return false;
        }

        /* get f_z_r of the new segment */
        unsigned int sizeSeg = ( unsigned int )( ( s2 - s1 ) / m_stepSize );
        sizeSeg += 2;
        unsigned int indexSeg = size;
        size = size + sizeSeg - 1;
        resizeVector( f_z_r, size );
        resizeVector( f_s_r, size );
        // calc new stepSize
        CFloat stepSizeSeg = ( s2 - s1 ) / ( sizeSeg - 1 );
        // from s1+step to s2 fill z[i] and s[i]
        for( CFloat sValue = s1 + stepSizeSeg; sValue <= s2 + stepSizeSeg / 2.0 ; sValue += stepSizeSeg )  // m_stepSize/2 for float calc errors
        {
            f_z_r[indexSeg] = z1 + ( ( k2 - k1 ) / ( s2 - s1 ) ) * ( sValue - s1 );
            f_s_r[indexSeg] = sValue;
            indexSeg++;
        }
        /* set values for next linear segment*/
        s1 = s2;
    }
    return true;
}

//! Calculate a lane's course line position (x, y, z) and arclength (s) CFloatVectors using reference
//! lane data (lanes[0]) and the current lane's trackWidth spline (f_trackWidthSpline_r).
//! The lane ID is an input parameter ('f_laneID').
void CRoad::calcNeighborVectors( CInt f_laneID, CSplineAkima& f_trackWidthSpline_r, CFloatVector& f_xBoundary_r, CFloatVector& f_yBoundary_r, CFloatVector& f_zBoundary_r, CFloatVector& f_sBoundary_r )
{
    CFloat x, y, z, dx, dy, dz, ds;
    CFloat l_deltaGamma, l_gamma, l_gamma_K1, l_crossfall;

    // Get reference lane's 's' parameter vector; i.e. 's_i' values for all Spline support points p_i = (s_i, y(s_i))
    // Resize output CFloatVectors accordingly.
    CFloatVector& l_sVector = *lanes[0].CourseLine.getSLineVector();
    CInt l_vectorSize = l_sVector.size();
    f_xBoundary_r.resize( l_vectorSize );
    f_yBoundary_r.resize( l_vectorSize );
    f_zBoundary_r.resize( l_vectorSize );
    f_sBoundary_r.resize( l_vectorSize );

    // Get reference lane's initial (s=0) coordinates and derivatives, and calculate x-y orientation angle (l_gamma_K1)
    lanes[0].CourseLine.getXYZ( 0, x, y, z, dx, dy, dz );
    l_gamma_K1  = ::sim::atan2( dy, dx );

    ds = 0;
    // Iterate through 's' vector. For each discretized 'l_s':
    // Get local position and coordinates, and calculate current lane position by
    //   - adding up track widths between ref. and current lane (f_laneID) for local offset
    //   - performing coordinate transform and adding local offset to global coordinates
    for( int32_t t_index = 0 ; t_index < l_vectorSize; ++t_index )
    {
        CFloat l_s = l_sVector[t_index];
        lanes[0].CourseLine.getXYZ( l_s, x, y, z, dx, dy, dz );
        l_gamma  = ::sim::atan2( dy, dx ); //::sim::sign_of( dy ) * acos( dx / sqrt( dx * dx + dy * dy ) ); // /
        l_crossfall = lanes[0].getCrossfall( l_s );
        //course point coordinate system

        // Sum up track widths between reference lane (0) and current lane (f_laneID)
        // Start with reference and target lanes' half trackwidths.
        CFloat l_x = 0;
        CFloat l_y = ::sim::sign_of( f_laneID ) * ( lanes[0].getTrackWidth( l_s ) + f_trackWidthSpline_r.Eval( l_s ) ) / 2;

        // For all intermediate lanes [between reference lane (0) and 'f_laneID', excluding both], add trackWidth to l_y
        for( int64_t t_IDiterator = 1; t_IDiterator < ::sim::abs( f_laneID ); t_IDiterator++ )
        {
            if( f_laneID < 0 )  l_y -= lanes[ - t_IDiterator ].getTrackWidth( l_s );
            else if( f_laneID > 0 )  l_y += lanes[   t_IDiterator ].getTrackWidth( l_s );
        }

        CFloat l_z = 0;

        //1 Step: transform in world coordinate system: rotation (y-axis)
        //slope is not relevant for l_x = 0 and l_z = 0
        //o_x = l_x * cos( slope ) - l_z * sin( slope );
        //o_y = l_y;
        //o_z = l_x * sin( slope ) + l_z * cos( slope );

        //2 Step: transform in world coordinate system: rotation (x-axis) => crossfall
        // ( x=0 , y=LATERALOFFSET * cos( crossfall ), z=LATERALOFFSET * sin( crossfall) )
        //m_yObstacle = state[LATERALOFFSET] * cos( crossfall );
        //m_zObstacle = state[LATERALOFFSET] * sin( crossfall );
        CFloat l_x1 = l_x;
        CFloat l_y1 = l_y * ::sim::cos( l_crossfall ) + l_z * ::sim::sin( l_crossfall );
        CFloat l_z1 = -l_y * ::sim::sin( l_crossfall ) + l_z * ::sim::cos( l_crossfall );

        //3 Step: transform in world coordinate system: rotation (z-axis) and translation
        f_xBoundary_r[t_index] = x + l_x1 * ::sim::cos( l_gamma ) - l_y1 * ::sim::sin( l_gamma );
        f_yBoundary_r[t_index] = y + l_x1 * ::sim::sin( l_gamma ) + l_y1 * ::sim::cos( l_gamma );
        f_zBoundary_r[t_index] = z + l_z1;

        // calculate new sNew = deltaR*deltaAlpha + s
        l_deltaGamma = ( l_gamma - l_gamma_K1 );
        if( l_deltaGamma > M_PI )
        {
            l_deltaGamma -= 2 * M_PI;
        }
        else if( l_deltaGamma < -M_PI )
        {
            l_deltaGamma += 2 * M_PI;
        }
        ds += - l_y * l_deltaGamma;
        f_sBoundary_r[t_index] = l_s + ds;
        l_gamma_K1 = l_gamma;
    }
}

void CRoad::resizeVector( CFloatVector& f_vector, size_t f_size ) const
{
    /* workaround for bug of valarray implementation */
    /* only works, if vector.size < size */
    CFloatVector temp( f_vector.size() );
    temp = f_vector;
    f_vector.resize( f_size );
    for( unsigned int i = 0 ; i < temp.size() ; i++ )
    {
        f_vector[i] = temp[i];
    }
}

