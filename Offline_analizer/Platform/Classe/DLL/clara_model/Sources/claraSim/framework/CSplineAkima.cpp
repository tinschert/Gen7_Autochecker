/*******************************************************************************
@author Robert Erhart, ett2si (13.02.2007)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
*******************************************************************************/

#include "CSplineAkima.h"
//#include <stdio.h> //DEBUG

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CSplineAkima::CSplineAkima():
    m_size( 0 ),
    m_gradient( 0 ),
    m_x( 0 ),
    m_a( 0 ),
    m_b( 0 ),
    m_c( 0 ),
    m_d( 0 )
{}

CSplineAkima::~CSplineAkima()
{}

/*------------------*/
/* public methodes  */
/*------------------*/
int CSplineAkima::init( const long double x[], const long double y[], size_t size_array, bool periodic )
{
    if( size_array < 2 )
    {
        ::std::cerr << "Error CSplineAkima: size_array < 2\n";
        //ToDo: generate valid valarrays for eval => no segmentation fault
        return -1;
    }
    m_size = size_array;
    m_gradient.resize( m_size + 4 );
    m_x.resize( m_size );
    m_a.resize( m_size );
    m_b.resize( m_size );
    m_c.resize( m_size );
    m_d.resize( m_size );

    long double* gradient = &m_gradient[0] + 2; // offset, so -1, -2 indices are possible

    /* calc gradient and check for increasing x values */
    for( signed long i = 0; i < ( static_cast<signed long>( size_array ) - 1 ); i++ )
    {
        long double xDiff = x[i + 1] - x[i];
        if( xDiff <= 0.0 )
        {
            ::std::cout << "WARNING CSplineAkima: x values are not increasing => no new content: x[" << i << "] " << x[i] << "; x[" << i + 1 << "] " << x[i + 1] << ::std::endl  ;
            return -1;
        }
        gradient[i] = ( y[i + 1] - y[i] ) / xDiff;
    }
    if( periodic )
    {
        gradient[-2] = gradient[size_array - 3];
        gradient[-1] = gradient[size_array - 2];
        gradient[size_array - 1] = gradient[0];
        gradient[size_array]   = gradient[1];
    }
    else
    {
        gradient[-2] = 3.0 * gradient[0] - 2.0 * gradient[1];
        gradient[-1] = 2.0 * gradient[0] -       gradient[1];
        gradient[size_array - 1] = 2.0 * gradient[size_array - 2] -       gradient[size_array - 3];
        gradient[size_array]   = 3.0 * gradient[size_array - 2] - 2.0 * gradient[size_array - 3];
    }

    /* calc akima coefficient */
    for( unsigned int i = 0  ; i < size_array ; i++ )
    {
        m_x[i] = x[i];
        m_a[i] = y[i];
    }

    for( signed long i = 0; i < ( static_cast<signed long>( size_array ) - 1 ); i++ )
    {
        long double denominator = ::sim::abs( gradient[i + 1] - gradient[i] ) + ::sim::abs( gradient[i - 1] - gradient[i - 2] );
        if( denominator == 0.0 )
        {
            m_b[i] = gradient[i];
            m_c[i] = 0.0;
            m_d[i] = 0.0;
        }
        else
        {
            long double h_i = x[i + 1] - x[i];
            long double denominator_next = ::sim::abs( gradient[i + 2] - gradient[i + 1] ) + ::sim::abs( gradient[i] - gradient[i - 1] );
            long double alpha_i = ::sim::abs( gradient[i - 1] - gradient[i - 2] ) / denominator;
            long double tL_ip1;
            long double alpha_ip1;
            if( denominator_next == 0.0 )
            {
                tL_ip1 = gradient[i];

            }
            else
            {
                alpha_ip1 = ::sim::abs( gradient[i] - gradient[i - 1] ) / denominator_next;
                tL_ip1 = ( 1.0 - alpha_ip1 ) * gradient[i] + alpha_ip1 * gradient[i + 1];
            }
            m_b[i] = ( 1.0 - alpha_i ) * gradient[i - 1] + alpha_i * gradient[i];
            m_c[i] = ( 3.0 * gradient[i] - 2.0 * m_b[i] - tL_ip1 ) / h_i;
            m_d[i] = ( m_b[i] + tL_ip1 - 2.0 * gradient[i] ) / ( h_i * h_i );
        }
    }

    return 0;
}


long double CSplineAkima::Eval( long double x ) const
{
    size_t index = findInterval( x );
    long double xDiff = x - m_x[index];
    return ( ( m_d[index] * xDiff + m_c[index] ) * xDiff + m_b[index] ) * xDiff + m_a[index];
}

void CSplineAkima::EvalDeriv1( long double x, long double& y, long double& dy ) const
{
    size_t index = findInterval( x );
    long double xDiff = x - m_x[index];
    y = ( ( m_d[index] * xDiff + m_c[index] ) * xDiff + m_b[index] ) * xDiff + m_a[index];
    dy = ( ( 3.0 * m_d[index] * xDiff + 2.0 * m_c[index] ) * xDiff + m_b[index] );
}

void CSplineAkima::EvalDeriv2( long double x, long double& y, long double& dy, long double& ddy ) const
{
    size_t index = findInterval( x );
    long double xDiff = x - m_x[index];
    y = ( ( m_d[index] * xDiff + m_c[index] ) * xDiff + m_b[index] ) * xDiff + m_a[index];
    dy = ( ( 3.0 * m_d[index] * xDiff + 2.0 * m_c[index] ) * xDiff + m_b[index] );
    ddy = 6.0 * m_d[index] * xDiff + 2.0 * m_c[index];
}

long double CSplineAkima::getX( size_t index ) const
{
    if( index < m_size )
    {
        return m_x[index];
    }
    else
    {
        ::std::cerr << "ERROR CSplineAkima.getx: index out of bound\n";
        return 0;
    }
}

long double CSplineAkima::getY( size_t index ) const
{
    if( index < m_size )
    {
        return m_a[index];
    }
    else
    {
        ::std::cerr << "ERROR CSplineAkima.getY: index out of bound\n";
        return 0;
    }
}

CFloatVector& CSplineAkima::getXVector()
{
    return m_x;
}

CFloatVector& CSplineAkima::getYVector()
{
    return m_a;
}

CInt CSplineAkima::NumberOfElements() const
{
    return m_size;
}

/*------------------*/
/* private methodes */
/*------------------*/
size_t CSplineAkima::findInterval( long double x ) const
{
    // ToDo: Bug if m_size == 0
    size_t index_low = 0;
    size_t index_high = m_size - 1;
    while( index_high > index_low + 1 )
    {
        size_t index = ( index_low + index_high ) / 2;
        if( m_x[index] > x )
            index_high = index;
        else
            index_low = index;
    }
    return index_low;
}
