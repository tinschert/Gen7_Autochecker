/*******************************************************************************
@author Robert Erhart, ett2si (03.07.2015)
@copyright (c) Robert Bosch GmbH 2015-2024. All rights reserved.
*******************************************************************************/

#include "CLane.h"

//*********************************
// constructor/destructor/copy/move
//*********************************
CLane::CLane():
    CourseLine(),
    BoundaryLine( 2 ),
    m_errorTolerance( 0.001 ), //[m] tolerance for finding function minimum
    m_indexSearch( 0 )
{
    addMessageOutput( o_lengthOfCourse, 0.0, CLaneDoc::o_lengthOfCourse );
    addMessageOutput( o_numberOfLaneReferencePoints, 0LL, CLaneDoc::o_numberOfLaneReferencePoints );

    // NOTE: remove addMessageParameter, since they should not be dynamic during runtime?
    addMessageParameter( p_connections, CFloatVector( -1, 3 ), CLaneDoc::p_connections );
    init();
}

CLane::~CLane()
{}


/*------------------*/
/* public methods  */
/*------------------*/
void CLane::init() // use only, if simulation is stopped
{
    m_indexSearch = 0;
    CFloat t_values[] = {0, 1};
    CFloat t_values0[] = {0, 0};
    CFloatVector l_sVector( t_values, 2 );
    CFloatVector l_xVector( t_values0, 2 );
    CFloatVector l_yVector( t_values0, 2 );
    CFloatVector l_zVector( t_values0, 2 );
    CFloatVector l_trackWidth( t_values0, 2 );
    CFloatVector l_crossfall( t_values0, 2 );
    init( l_sVector, l_xVector, l_yVector, l_zVector, l_trackWidth, l_crossfall );
}

void CLane::init( CFloatVector& f_sVector_r, CFloatVector& f_xVector_r, CFloatVector& f_yVector_r, CFloatVector& f_zVector_r, CFloatVector& f_trackWidth_r, CFloatVector& f_crossfall_r ) // use only, if simulation is stopped
{
    CourseLine.init( f_sVector_r, f_xVector_r, f_yVector_r, f_zVector_r );
    trackWidthSpline.init( &f_sVector_r[0], &f_trackWidth_r[0], f_trackWidth_r.size(), false );
    crossfallSpline.init( &f_sVector_r[0], &f_crossfall_r[0], f_crossfall_r.size(), false );

    CFloatVector xBoundary, yBoundary, zBoundary, sBoundary;
    //left boundary
    calcBoundaryVectors( true, xBoundary, yBoundary, zBoundary, sBoundary );
    BoundaryLine[left].init( sBoundary, xBoundary, yBoundary, zBoundary );
    //right boundary
    calcBoundaryVectors( false, xBoundary, yBoundary, zBoundary, sBoundary );
    BoundaryLine[right].init( sBoundary, xBoundary, yBoundary, zBoundary );

    o_lengthOfCourse.init( *( end( f_sVector_r ) - 1 ) ); // std::end for valarray is a pointer to one past the last element.
    o_numberOfLaneReferencePoints.init( f_sVector_r.size() );

    p_connections.copyValueInit();

    // TODO: handle for more than one connection!
    if( p_connections[2] < 0 )
    {
        p_connections.init( CFloatVector( {p_connections[0], p_connections[1], o_lengthOfCourse} ) );
    }
}

CFloat CLane::getTrackWidth( CFloat f_s )
{
    return trackWidthSpline.Eval( f_s );
}

CFloat CLane::getCrossfall( CFloat f_s )
{
    return crossfallSpline.Eval( f_s );
}

SCoursePositionInfo CLane::findCoursePositionInfo( CFloat f_x, CFloat f_y, CInt& f_index )
{
    SCoursePositionInfo l_positionCourseInfo;
    CourseLine.findLinePositionInfo( f_x, f_y, l_positionCourseInfo.s, l_positionCourseInfo.lateralOffset,
                                     l_positionCourseInfo.x, l_positionCourseInfo.y, l_positionCourseInfo.z,
                                     l_positionCourseInfo.dx, l_positionCourseInfo.dy, l_positionCourseInfo.dz, f_index );
    //l_positionCourseInfo.xyz = CFloatVector( {l_positionCourseInfo.x, l_positionCourseInfo.y, l_positionCourseInfo.z} );

    //transform to course coordinate system
    CFloat l_alphaTrack = ::sim::atan2( l_positionCourseInfo.dy, l_positionCourseInfo.dx );
    CFloat l_alphaOffset = ::sim::atan2( f_y - l_positionCourseInfo.y, f_x - l_positionCourseInfo.x );
    // Get relative yaw angle between
    //      - position offset vector from course line
    //      - track orientation
    // to determine direction (sign) of lateralOffset.
    l_positionCourseInfo.lateralOffset *= ::sim::sig( ::sim::sin( l_alphaOffset - l_alphaTrack ) );

    l_positionCourseInfo.crossfallAngleLocal = getCrossfall( l_positionCourseInfo.s );

    l_positionCourseInfo.slopeAngleLocal = ::sim::atan( l_positionCourseInfo.dz );
    l_positionCourseInfo.gammaAngle = ::sim::atan2( l_positionCourseInfo.dy, l_positionCourseInfo.dx );
    l_positionCourseInfo.trackwidth = getTrackWidth( l_positionCourseInfo.s );
    l_positionCourseInfo.indexLast = f_index;
    return l_positionCourseInfo;
}

SCoursePositionInfo CLane::getCoursePositionInfo( CFloat f_s, CFloat f_lateralOffset )
{
    SCoursePositionInfo l_positionCourseInfo;
    l_positionCourseInfo.s = f_s;
    l_positionCourseInfo.lateralOffset = f_lateralOffset;
    CourseLine.getXYZ( f_s, l_positionCourseInfo.x, l_positionCourseInfo.y, l_positionCourseInfo.z,
                       l_positionCourseInfo.dx, l_positionCourseInfo.dy, l_positionCourseInfo.dz );

    l_positionCourseInfo.gammaAngle = ::sim::atan2( l_positionCourseInfo.dy, l_positionCourseInfo.dx );
    l_positionCourseInfo.crossfallAngleLocal = getCrossfall( f_s );
    l_positionCourseInfo.slopeAngleLocal = ::sim::atan( l_positionCourseInfo.dz );

    //course point coordinate system
    CFloat l_x = 0;
    CFloat l_y = f_lateralOffset;
    CFloat l_z = 0;

    ::sim::coordinateRotation( -l_positionCourseInfo.crossfallAngleLocal, -l_positionCourseInfo.slopeAngleLocal, l_positionCourseInfo.gammaAngle,
                        l_x, l_y, l_z,
                        l_x, l_y, l_z );
    l_positionCourseInfo.x += l_x;
    l_positionCourseInfo.y += l_y;
    l_positionCourseInfo.z += l_z;
    //l_positionCourseInfo.xyz = // malloc problem CFloatVector( {l_positionCourseInfo.x, l_positionCourseInfo.y, l_positionCourseInfo.z} );
    l_positionCourseInfo.trackwidth = getTrackWidth( f_s );
    return l_positionCourseInfo;
}

SPositionInfo CLane::findLeftBoundaryPositionInfo( CFloat f_x, CFloat f_y, CInt& f_index )
{
    SPositionInfo l_positionInfo;
    BoundaryLine[left].findLinePositionInfo( f_x, f_y, l_positionInfo.s, l_positionInfo.distanceSplinePoint,
                                             l_positionInfo.x, l_positionInfo.y, l_positionInfo.z,
                                             l_positionInfo.dx, l_positionInfo.dy, l_positionInfo.dz, f_index );
    //l_positionInfo.xyz = CFloatVector( {l_positionInfo.x, l_positionInfo.y, l_positionInfo.z} );
    l_positionInfo.indexLast = f_index;
    return l_positionInfo;
}

SPositionInfo CLane::findRightBoundaryPositionInfo( CFloat f_x, CFloat f_y, CInt& f_index )
{
    SPositionInfo l_positionInfo;
    BoundaryLine[right].findLinePositionInfo( f_x, f_y, l_positionInfo.s, l_positionInfo.distanceSplinePoint,
                                              l_positionInfo.x, l_positionInfo.y, l_positionInfo.z,
                                              l_positionInfo.dx, l_positionInfo.dy, l_positionInfo.dz, f_index );
    //l_positionInfo.xyz = CFloatVector( {l_positionInfo.x, l_positionInfo.y, l_positionInfo.z} );
    l_positionInfo.indexLast = f_index;
    return l_positionInfo;
}


void CLane::calcBoundaryVectors( bool f_leftRight, CFloatVector& f_xBoundary, CFloatVector& f_yBoundary, CFloatVector& f_zBoundary, CFloatVector& f_sBoundary )
{
    CFloat x, y, z, dx, dy, dz;
    CFloatVector& l_sVector = *CourseLine.getSLineVector(); //ySplineCoordinate.getXVector();
    CInt l_vectorSize = l_sVector.size();
    f_xBoundary.resize( l_vectorSize );
    f_yBoundary.resize( l_vectorSize );
    f_zBoundary.resize( l_vectorSize );
    f_sBoundary.resize( l_vectorSize );
    CFloat l_deltaGamma, l_gamma_K1, ds;
    CourseLine.getXYZ( 0, x, y, z, dx, dy, dz );
    l_gamma_K1  = ::sim::atan2( dy, dx );
    ds = 0;
    for( CInt t_index = 0 ; t_index < l_vectorSize; ++t_index )
    {
        CFloat l_s = l_sVector[t_index];
        CourseLine.getXYZ( l_s, x, y, z, dx, dy, dz );
        long double l_gamma = ::sim::atan2( dy, dx ); //::sim::sign_of( dy ) * acos( dx / sqrt( dx * dx + dy * dy ) );
        long double l_crossfall = crossfallSpline.Eval( l_s );
        //course point coordinate system
        CFloat l_x = 0;
        CFloat l_y = ( f_leftRight ? 1 : -1 ) * trackWidthSpline.Eval( l_s ) / 2;
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
        CFloat l_x1 = + l_x;
        CFloat l_y1 = + l_y * ::sim::cos( l_crossfall ) + l_z * ::sim::sin( l_crossfall );
        CFloat l_z1 = - l_y * ::sim::sin( l_crossfall ) + l_z * ::sim::cos( l_crossfall );

        //3 Step: transform in world coordinate system: rotation (z-axis) and translation
        f_xBoundary[t_index] = x + l_x1 * ::sim::cos( l_gamma ) - l_y1 * ::sim::sin( l_gamma );
        f_yBoundary[t_index] = y + l_x1 * ::sim::sin( l_gamma ) + l_y1 * ::sim::cos( l_gamma );
        f_zBoundary[t_index] = z + l_z1;
        // calculate new sNew = deltaR*deltaAlpha + s //ToDo not needed
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
        f_sBoundary[t_index] = l_s + ds;
        l_gamma_K1 = l_gamma;
        //f_sBoundary[t_index] = l_s;
    }
}

