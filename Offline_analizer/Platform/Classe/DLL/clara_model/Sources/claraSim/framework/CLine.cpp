/*******************************************************************************
@author Robert Erhart, ett2si (03.07.2015)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
*******************************************************************************/

#include "CLine.h"
//#include <iostream>

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CLine::CLine():
    xSplineCoordinate(),
    ySplineCoordinate(),
    zSplineCoordinate(),
    typLeftBoundary( 0 ),
    m_errorTolerance( 0.001 ), //[m] tolerance for finding function minimum
    m_indexSearch( 0 ),
    m_lengthOfLine( 0 ),
    m_numberOfLineReferencePoints( 0 )
{
//    m_indexSearch = 0;
//    CFloat t_values[] = {0, 1};
//    CFloat t_values0[] = {0, 0};
//    CFloatVector l_sVector( t_values, 2 );
//    CFloatVector l_xVector( t_values0, 2 );
//    CFloatVector l_yVector( t_values0, 2 );
//    CFloatVector l_zVector( t_values0, 2 );
//    CFloatVector l_trackWidth( t_values0, 2 );
//    CFloatVector l_crossfall( t_values0, 2 );
//    init( l_sVector, l_xVector, l_yVector, l_zVector );
}

CLine::~CLine()
{}


/*------------------*/
/* public methods  */
/*------------------*/
void CLine::init( CFloatVector& f_sVector_r, CFloatVector& f_xVector_r, CFloatVector& f_yVector_r, CFloatVector& f_zVector_r ) // use only, if simulation is stopped
{
    //::std::cerr << "xSplineCoordinate" << ::std::endl;
    xSplineCoordinate.init( &f_sVector_r[0], &f_xVector_r[0], f_xVector_r.size(), false );
    //::std::cerr << "ySplineCoordinate" << ::std::endl;
    ySplineCoordinate.init( &f_sVector_r[0], &f_yVector_r[0], f_yVector_r.size(), false );
    //::std::cerr << "zSplineCoordinate" << ::std::endl;
    zSplineCoordinate.init( &f_sVector_r[0], &f_zVector_r[0], f_zVector_r.size(), false );
    //::std::cerr << "trackWidthSpline" << ::std::endl;
    m_lengthOfLine = *( ::std::end( f_sVector_r ) - 1 ); // std::end for valarray is a pointer to one past the last element.
    m_numberOfLineReferencePoints = f_sVector_r.size();
}

void CLine::init( CLine& f_firstLine_r, CLine& f_secondLine_r )
{
    auto combineCFloatVectors = []( const CFloatVector & f_first_r, const CFloatVector & f_second_r, CFloatVector & f_combined_r, bool addOffset = false )
    {
        CInt l_firstSize = f_first_r.size();
        CInt l_secondSize = f_second_r.size();
        CInt l_combinedSize = l_firstSize + l_secondSize;

        // ATTENTION:
        // We are assuming directly adjoint lines.
        // This means the last element of array1 and the first of array2 should be identical.
        // Therefore we are discarding the first element of second array.
        f_combined_r.resize( l_combinedSize - 1 );

        for( int32_t l_index = 0; l_index < l_firstSize; l_index++ )
        {
            f_combined_r[l_index] = f_first_r[l_index];
        }
        for( int32_t l_index = 1; l_index < l_secondSize; l_index++ )
        {
            f_combined_r[l_firstSize + l_index - 1] = f_second_r[l_index] + ( addOffset ? f_first_r[l_firstSize - 1] : 0 );
        }
    };

    CFloatVector l_sCombined, l_xCombined, l_yCombined, l_zCombined;

    combineCFloatVectors( *( f_firstLine_r.getSLineVector() ), *( f_secondLine_r.getSLineVector() ), l_sCombined, true );
    combineCFloatVectors( *( f_firstLine_r.getXLineVector() ), *( f_secondLine_r.getXLineVector() ), l_xCombined );
    combineCFloatVectors( *( f_firstLine_r.getYLineVector() ), *( f_secondLine_r.getYLineVector() ), l_yCombined );
    combineCFloatVectors( *( f_firstLine_r.getZLineVector() ), *( f_secondLine_r.getZLineVector() ), l_zCombined );

    init( l_sCombined, l_xCombined, l_yCombined, l_zCombined );
}

void CLine::getXYZ( CFloat f_s, CFloat& f_x, CFloat& f_y, CFloat& f_z )
{
    f_x = xSplineCoordinate.Eval( f_s );
    f_y = ySplineCoordinate.Eval( f_s );
    f_z = zSplineCoordinate.Eval( f_s );
}

void CLine::getXYZ( CFloat f_s, CFloat& f_x, CFloat& f_y, CFloat& f_z, CFloat& f_dx, CFloat& f_dy, CFloat& f_dz )
{
    xSplineCoordinate.EvalDeriv1( f_s, f_x, f_dx );
    ySplineCoordinate.EvalDeriv1( f_s, f_y, f_dy );
    zSplineCoordinate.EvalDeriv1( f_s, f_z, f_dz );
}

void CLine::getXYZ( CFloat s, CFloat& x, CFloat& y, CFloat& z, CFloat& dx, CFloat& dy, CFloat& dz, CFloat& ddx, CFloat& ddy, CFloat& ddz )
{
    xSplineCoordinate.EvalDeriv2( s, x, dx, ddx );
    ySplineCoordinate.EvalDeriv2( s, y, dy, ddy );
    zSplineCoordinate.EvalDeriv2( s, z, dz, ddz );
}

void CLine::getXYZVector( CFloat f_stepSizeMax, CFloatVector& f_x, CFloatVector& f_y, CFloatVector& f_z )
{
    /* resize input vectors */
    unsigned int l_size = ( unsigned int )( ( m_lengthOfLine ) / f_stepSizeMax ) + 2;
    f_x.resize( l_size, 0.0 );
    f_y.resize( l_size, 0.0 );
    f_z.resize( l_size, 0.0 );

    /* calc new stepSize */
    long double l_stepSize = ( m_lengthOfLine ) / ( l_size - 1 );
    long double l_position = 0;
    for( unsigned int l_index = 0; l_index < l_size ; l_index++ )
    {
        getXYZ( l_position, f_x[l_index], f_y[l_index], f_z[l_index] );
        l_position += l_stepSize;
    }
}

CInt CLine::getType( CFloat s )
{
    return 0;
}

CFloat CLine::getLengthOfLine()
{
    return m_lengthOfLine;
}

CInt CLine::getNumberOfLineReferencePoints()
{
    return m_numberOfLineReferencePoints;
}

CFloatVector* CLine::getXLineVector()
{
    return &xSplineCoordinate.getYVector();
}

CFloatVector* CLine::getYLineVector()
{
    return &ySplineCoordinate.getYVector();
}

CFloatVector* CLine::getZLineVector()
{
    return &zSplineCoordinate.getYVector();
}

CFloatVector* CLine::getSLineVector()
{
    return &ySplineCoordinate.getXVector();
}

CIntVector* CLine::getTypLineVector()
{
    return &typLeftBoundary;
}

void CLine::findLinePositionInfo( CFloat f_x, CFloat f_y,
                                  CFloat& f_sSpline, CFloat& f_distancePointSpline,
                                  CFloat& f_xSpline, CFloat& f_ySpline, CFloat& f_zSpline,
                                  CFloat& f_dxSpline, CFloat& f_dySpline, CFloat& f_dzSpline,
                                  CInt& f_index )
{
    //    /* find segment (slow solution) */
    //    long double minDistance = ( f_x-xSplineCoordinate.getY( 0 ) )*( f_x-xSplineCoordinate.getY( 0 ) ) + ( f_y-ySplineCoordinate.getY( 0 ) )*( f_y-ySplineCoordinate.getY( 0 ) );
    //    unsigned long minDistanceIndex = 1; // golden section method search between index-1 and index+1
    //    for ( unsigned long index = 1 ; index < xSplineCoordinate.NumberOfElements() ; index++ )
    //    {
    //        long double distance = ( f_x-xSplineCoordinate.getY( index ) )*( f_x-xSplineCoordinate.getY( index ) ) + ( f_y-ySplineCoordinate.getY( index ) )*( f_y-ySplineCoordinate.getY( index ) );
    //        if ( distance < minDistance )
    //        {
    //            minDistance = distance;
    //            minDistanceIndex = index;
    //        }
    //    }
    /* find segment (fast solution) Caution: find only a local minimum*/
    if( 1 > f_index or xSplineCoordinate.NumberOfElements() < f_index )
    {
        f_index = 1;
    }
    //long double minDistance = ( f_x - f_xSpline.getY( f_index ) ) * ( f_x - f_xSpline.getY( f_index ) ) + ( f_y - ySplineCoordinate.getY( f_index ) ) * ( f_y - ySplineCoordinate.getY( f_index ) );
    long double minDistance = ::sim::pow( ( f_x - xSplineCoordinate.getY( f_index ) ), 2 ) + ::sim::pow( ( f_y - ySplineCoordinate.getY( f_index ) ), 2 );
    while( f_index < ( xSplineCoordinate.NumberOfElements() - 2 ) )
    {
        f_index++;
        long double distance = ::sim::pow( ( f_x - xSplineCoordinate.getY( f_index ) ), 2 ) + ::sim::pow( ( f_y - ySplineCoordinate.getY( f_index ) ), 2 );
        if( distance < minDistance )
        {
            minDistance = distance;
        }
        else
        {
            f_index--;
            break;
        }
    }
    while( f_index > 1 )
    {
        f_index--;
        long double distance = ::sim::pow( ( f_x - xSplineCoordinate.getY( f_index ) ), 2 ) + ::sim::pow( ( f_y - ySplineCoordinate.getY( f_index ) ), 2 );
        if( distance < minDistance )
        {
            minDistance = distance;
        }
        else
        {
            f_index++;
            break;
        }
    }

    /* find minimum distance to spline segments s[index-1] - s[index+1]:
     * using golden section search "Numerical Recipes in C" [page 401]   */
    CInt& minDistanceIndex = f_index; // golden section method search between index-1 and index+1
    long double deltaS = xSplineCoordinate.getX( minDistanceIndex + 1 ) - xSplineCoordinate.getX( minDistanceIndex - 1 );

    const CFloat R = 0.61803399;
    const CFloat C = 1 - R;
    unsigned int numberOfIteration = 1 + ( unsigned int )( ::sim::log10( deltaS / m_errorTolerance ) / ::sim::log10( 1 / R ) );
    //f_sSpline = xSplineCoordinate.getX( minDistanceIndex );

    CFloat f1, f2, s0, s1, s2, s3;

    s0 = xSplineCoordinate.getX( minDistanceIndex - 1 );
    s1 = xSplineCoordinate.getX( minDistanceIndex );
    s3 = xSplineCoordinate.getX( minDistanceIndex + 1 );
    if( ::sim::abs( s3 - s1 ) > ::sim::abs( s1 - s0 ) )  // make s0 to s1 the smaller segment
    {
        s2 = s1 - C * ( s3 - s1 );
    }
    else
    {
        s2 = s1;
        s1 = s1 - C * ( s3 - s0 );
    }
    //f1 = distanceSquare( f_x, f_y, s1 ); //The initial function evaluations
    f1 = ::sim::pow( f_x - xSplineCoordinate.Eval( s1 ), 2 ) + ::sim::pow( f_y - ySplineCoordinate.Eval( s1 ), 2 );
    //f2 = distanceSquare( f_x, f_y, s2 );
    f2 = ::sim::pow( f_x - xSplineCoordinate.Eval( s2 ), 2 ) + ::sim::pow( f_y - ySplineCoordinate.Eval( s2 ), 2 );
    for( unsigned long index = 0 ; index < numberOfIteration ; index++ )
    {
        if( f2 < f1 )
        {
            s0 = s1;
            s1 = s2;
            s2 = R * s1 + C * s3;
            f1 = f2;
            //f2 = distanceSquare( f_x, f_y, s2 );
            f2 = ::sim::pow( f_x - xSplineCoordinate.Eval( s2 ), 2 ) + ::sim::pow( f_y - ySplineCoordinate.Eval( s2 ), 2 );
        }
        else
        {
            s3 = s2;
            s2 = s1;
            s1 = R * s2 + C * s0;
            f2 = f1;
            //f1 = distanceSquare( f_x, f_y, s1 );
            f1 = ::sim::pow( f_x - xSplineCoordinate.Eval( s1 ), 2 ) + ::sim::pow( f_y - ySplineCoordinate.Eval( s1 ), 2 );
        }
    }
    if( f1 < f2 )   //Output the best of the two current values
    {
        f_sSpline = s1;
        f_distancePointSpline = ::sim::sqrt( f1 );
    }
    else
    {
        f_sSpline = s2;
        f_distancePointSpline = ::sim::sqrt( f2 );
    }
    xSplineCoordinate.EvalDeriv1( f_sSpline, f_xSpline, f_dxSpline );
    ySplineCoordinate.EvalDeriv1( f_sSpline, f_ySpline, f_dySpline );
    zSplineCoordinate.EvalDeriv1( f_sSpline, f_zSpline, f_dzSpline );
}

