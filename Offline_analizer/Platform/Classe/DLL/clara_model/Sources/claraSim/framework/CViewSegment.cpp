/*******************************************************************************
author Robert Erhart, ett2si (11.07.2016)
author (c) Copyright Robert Bosch GmbH 2016.  All rights reserved.
*******************************************************************************/

#include "CViewSegment.h"


CViewSegment::CViewSegment():
    m_A( 3 ), m_B( 3 ), m_C( 3 ), m_AB( 3 ), m_AC( 3 ), m_divTerm( 0 )
{}

CViewSegment::~CViewSegment()
{}

void CViewSegment::init( CFloat f_alphaLeft, CFloat f_openingAngle, CFloat f_visibilityRange,
                         CFloat f_rollAngle, CFloat f_pitchAngle, CFloat f_yawAngle,
                         CFloat f_x, CFloat f_y, CFloat f_z,
                         CFloat& f_Ax_r, CFloat& f_Ay_r, CFloat& f_Az_r,
                         CFloat& f_Bx_r, CFloat& f_By_r, CFloat& f_Bz_r,
                         CFloat& f_Cx_r, CFloat& f_Cy_r, CFloat& f_Cz_r )
{
    f_Ax_r = m_A[x] = f_x;
    f_Ay_r = m_A[y] = f_y;
    f_Az_r = m_A[z] = f_z;

    CFloat l_alphaLeft  = f_alphaLeft;
    CFloat l_alphaRight = f_alphaLeft - f_openingAngle;

    m_AB[x] = f_visibilityRange * ::sim::cos( l_alphaLeft );
    m_AB[y] = f_visibilityRange * ::sim::sin( l_alphaLeft );
    m_AB[z] = 0;
    ::sim::coordinateRotation( f_rollAngle, f_pitchAngle, f_yawAngle,
                        m_AB[x], m_AB[y], m_AB[z],
                        m_AB[x], m_AB[y], m_AB[z] );
    f_Bx_r = m_B[x] = f_x + m_AB[x]; // m_AB = m_B - m_A
    f_By_r = m_B[y] = f_y + m_AB[y]; // m_AB = m_B - m_A
    f_Bz_r = m_B[z] = f_z + m_AB[z]; // m_AB = m_B - m_A

    m_AC[x] = f_visibilityRange * ::sim::cos( l_alphaRight );
    m_AC[y] = f_visibilityRange * ::sim::sin( l_alphaRight );
    m_AC[z] = 0;
    ::sim::coordinateRotation( f_rollAngle, f_pitchAngle, f_yawAngle,
                        m_AC[x], m_AC[y], m_AC[z],
                        m_AC[x], m_AC[y], m_AC[z] );
    f_Cx_r = m_C[x] = f_x + m_AC[x]; // m_AC = m_C - m_A
    f_Cy_r = m_C[y] = f_y + m_AC[y]; // m_AC = m_C - m_A
    f_Cz_r = m_C[z] = f_z + m_AC[z]; // m_AC = m_C - m_A

    m_divTerm = ( m_AC[y] * m_AB[x] - m_AC[x] * m_AB[y] );
}

CFloat CViewSegment::checkInRange( const CFloat f_x, const CFloat f_y, const CFloat f_z )
{
    //A + r*AB + s*AC = P
    // check if Contour points in the x-y level of the segment
    CFloat l_s = ( m_AB[x] * ( f_y - m_A[y] ) - m_AB[y] * ( f_x - m_A[x] ) ) / m_divTerm;
    CFloat l_r = ( f_x - m_A[x] - l_s * m_AC[x] ) / m_AB[x];
    CBool l_inRange = ( ( l_s >= 0 ) and ( l_r >= 0 ) and ( ( l_s + l_r ) <= 1 ) );
    return ( l_inRange ? 1 - l_s - l_r : 0 );
}


CFloat CViewSegment::checkInRange( const CFloatVector& f_x, const CFloatVector& f_y, const CFloatVector& f_z )
{
    //A + r*AB + s*AC = P
    // check, if contour points are in the x-y level of the segment
    bool l_inRange = false;
    CFloat l_visibility = 0;
    for( uint32_t l_index = 0; l_index < f_x.size(); l_index++ )
    {
        l_visibility = ::sim::max( l_visibility, checkInRange( f_x[l_index], f_y[l_index], f_z[l_index] ) );
    }

    //check for crossing point of line P1P3 and P2P4 with line AB
    //ToDO: AC check missing, but this is only for rare cases relevant ( really huge objects and small field of view)
    //A + s1*AB = P1 + s2* P1P3
    if( l_visibility == 0 )
    {
        CInt l_numberOfCrossing = f_x.size() / 2;
        for( auto l_index = 0; l_index < l_numberOfCrossing; l_index++ )
        {
            CFloat l_x1 = f_x[l_index];
            CFloat l_y1 = f_y[l_index];
            CFloat l_x2 = f_x[l_index + l_numberOfCrossing];
            CFloat l_y2 = f_y[l_index + l_numberOfCrossing];
            CFloat l_s2 = ( m_AB[x] * ( m_A[y] - l_y1 ) + m_AB[y] * ( l_x1 - m_A[x] ) ) / ( ( l_y2 - l_y1 ) * m_AB[x] - ( l_x2 - l_x1 ) * m_AB[y] );
            CFloat l_s1 = ( l_x1 - m_A[x] + l_s2 * ( l_x2 - l_x1 ) ) / m_AB[x];
            l_inRange |= ( ( l_s1 >= 0 ) and ( l_s2 >= 0 ) and ( l_s1 <= 1 ) and ( l_s2 <= 1 ) );
            if( l_inRange )
            {
                l_visibility = ::sim::max( l_visibility, 1 - l_s1 );
            }
        }
    }
    return l_visibility;
}

CBool CViewSegment::findIntersectionWithLine( CInt f_boundryLine, CFloat f_x1, CFloat f_y1, CFloat f_x2, CFloat f_y2, CFloat& f_sLine )
{
    CFloat f_sViewSegement;
    switch( f_boundryLine )
    {
        case 1:
            //A + sViewSegement*AB = P1 + sLine* P1P3
            f_sLine = ( m_AB[x] * ( m_A[y] - f_y1 ) + m_AB[y] * ( f_x1 - m_A[x] ) ) / ( ( f_y2 - f_y1 ) * m_AB[x] - ( f_x2 - f_x1 ) * m_AB[y] );
            f_sViewSegement = ( f_x1 - m_A[x] + f_sLine * ( f_x2 - f_x1 ) ) / m_AB[x];
            return ( ( f_sViewSegement >= 0 ) and ( f_sLine >= 0 ) and ( f_sViewSegement <= 1 ) and ( f_sLine <= 1 ) );
        case -1:
            //A + sViewSegement*AC = P1 + sLine* P1P3
            f_sLine = ( m_AC[x] * ( m_A[y] - f_y1 ) + m_AC[y] * ( f_x1 - m_A[x] ) ) / ( ( f_y2 - f_y1 ) * m_AC[x] - ( f_x2 - f_x1 ) * m_AC[y] );
            f_sViewSegement = ( f_x1 - m_A[x] + f_sLine * ( f_x2 - f_x1 ) ) / m_AC[x];
            return( ( f_sViewSegement >= 0 ) and ( f_sLine >= 0 ) and ( f_sViewSegement <= 1 ) and ( f_sLine <= 1 ) );
        case 0:
            //A + r1*AB + r2 AC = P1 + sLine* P1P3
            //r1+r2 = 1
            f_sLine = ( ( m_AB[y] - m_AC[y] ) * ( m_A[x] + m_AC[x] - f_x1 ) - ( m_AB[x] - m_AC[x] ) * ( m_A[y] + m_AC[y] - f_y1 ) ) / ( ( f_x2 - f_x1 ) * ( m_AB[y] - m_AC[y] ) - ( ( f_y2 - f_y1 ) * ( m_AB[x] - m_AC[x] ) ) );
            f_sViewSegement = ( f_y1 + f_sLine * ( f_y2 - f_y1 ) - m_A[y] - m_AC[y] ) / ( m_AB[y] - m_AC[y] );
            return ( f_sViewSegement >= 0 and f_sLine >= 0  and ( f_sViewSegement <= 1 ) and ( f_sLine <= 1 ) );
        default:
            return false;
    }
}
