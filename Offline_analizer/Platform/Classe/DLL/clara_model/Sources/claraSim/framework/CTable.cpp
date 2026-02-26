/*******************************************************************************
author Robert Erhart, ett2si (26.10.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004, 2005.  All rights reserved.
*******************************************************************************/

#include "CTable.h"

/* constructor / destructor */
CTable::CTable()
{
    init( 0, 0 );
}
CTable::~CTable()
{}

/* init */
void CTable::init( CInt size, CInt type )
{
    /* set interpolation type */
    m_interpolationTyp = type;

    /* Initialization of the internal memory for the curve */
    m_x.resize( size, 0 );
    m_y.resize( size, 0 );
}

void CTable::init( CFloatVector xInput, CFloatVector yInput, CInt type )
{
    /* set interpolation type */
    m_interpolationTyp = type;

    /* Initialization of the internal memory for the curve */
    m_x.resize( xInput.size(), 0 );
    m_y.resize( xInput.size(), 0 );

    setX( xInput );
    setY( yInput );
}

void CTable::init( CInt f_size, CFloat* f_xInput, CFloat* f_yInput, CInt f_typ )
{
    CFloatVector xVector( f_xInput, f_size );
    CFloatVector yVector( f_yInput, f_size );

    init( xVector, yVector, f_typ );
}

/* calculate interpolated y value of the characteristic curve */
CFloat CTable::get( CFloat f_xInput )
{
    switch( m_interpolationTyp )
    {
        case 0:
            return getLinear( f_xInput );
        default:
            ::std::cerr << "ERROR <CTable::get>: wrong interpolation type" << ::std::endl;
            break;
    }
    return -1;
}

/* set the x axis of the characteristic curve */
void CTable::setX( CFloatVector f_xInput )
{
    /* check of the proper size of the vector */
    if( f_xInput.size() == m_x.size() )
    {
        m_x = f_xInput;
    }
    else
    {
        ::std::cerr << "ERROR <CTable::setX>: wrong size of input vector" << ::std::endl;
    }

    /* check oft the proper structure of the vector x:
     * increasing values from left to right (x-axis) */
    for( uint32_t i = 0 ; i < ( m_x.size() - 1 ); i++ )
    {
        if( m_x[i] > m_x[i + 1] )
        {
            ::std::cerr << "ERROR <CTable::setX>: illegal input vector; No increasing values from left to right (x-axis)" << ::std::endl;
        }
    }
}

/* set the y axis of the characteristic curve */
void CTable::setY( CFloatVector yInput )
{
    /* check of the proper size of the vector */
    if( yInput.size() == m_y.size() )
    {
        m_y = yInput;
    }
    else
    {
        ::std::cerr << "ERROR <CTable::setY>: wrong size of input vector" << ::std::endl;
    }
}

/*******************************************************************************
 *  linear interpolation function
 * x = x(n) + rho * (x(n+1) - x(n))
 * rho = (x - x(n)) / (x(n+1) - x(n))
 * y(x) = y(n) + rho*(y(n+1) - y(n) )
 ******************************************************************************/
CFloat CTable::getLinear( CFloat f_xInput )
{
    CFloat yValue;
    uint32_t index = 0;
    /* getting the index of the closest vector entry of xInput */
    while( ( index < m_x.size() )
           && ( f_xInput > m_x[index] ) )
    {
        index++;
    }

    /* linear interpolation function */
    if( index == m_x.size() )
    {
        /* xInput > xMax */
        yValue = m_y[index - 1];
    }
    else if( index == 0 )
    {
        /* xInput <= xMin */
        yValue = m_y[0];
    }
    else
    {
        yValue = ( m_y[index - 1] +
                   ( f_xInput - m_x[index - 1] ) / ( m_x[index] - m_x[index - 1] ) * ( m_y[index] - m_y[index - 1] ) );
    }

    return yValue;
}
