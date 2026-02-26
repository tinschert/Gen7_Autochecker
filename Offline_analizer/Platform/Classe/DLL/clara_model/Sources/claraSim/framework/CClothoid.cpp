/*******************************************************************************
author Robert Erhart, ett2si (19.02.2007)
author (c) Copyright Robert Bosch GmbH 2007.  All rights reserved.
*******************************************************************************/

#include "CClothoid.h"
#include <iostream>

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CClothoid::CClothoid() : CClass_ct<NumberOfStates>()
{
    /* Init parameter */

    state[0] = 0.0;
    state[1] = 0.0;
    state[2] = 0.0;
    state[3] = 0.0;
    ddtState = state;
}

CClothoid::~CClothoid()
{}

/*------------------*/
/* public methodes  */
/*------------------*/
void CClothoid::init( CFloat s1, CFloat s2, CFloat k1, CFloat k2, CFloat a1, CFloat x1, CFloat y1 )
{
    m_s1 = s1;
    m_s2 = s2;
    m_k1 = k1;
    m_a1 = a1;
    m_x1 = x1;
    m_y1 = y1;
    m_dk = ( k2 - m_k1 ) / ( m_s2 - m_s1 );
    state[X] = m_x1;
    state[Y] = m_y1;
    state[S] = m_s1;
    state[ALPHA] = m_a1;
    ddtState = 0.0;
}

void CClothoid::init( CFloat s, CFloat k1, CFloat dk, CFloat a1, CFloat x1, CFloat y1 )
{
    m_s1 = 0;
    m_s2 = s;
    m_k1 = k1;
    m_a1 = a1;
    m_x1 = x1;
    m_y1 = y1;
    m_dk = dk;
    state[X] = m_x1;
    state[Y] = m_y1;
    state[S] = m_s1;
    state[ALPHA] = m_a1;
    ddtState = 0.0;
}

void CClothoid::getXY( CFloat stepSize,  CFloat& s, CFloat& x, CFloat& y )
{
    x = state[X];
    y = state[Y];
    s = state[S];
    process( stepSize, -1 );
}

void CClothoid::getXY( CFloat stepSize, CFloatVector& s, CFloatVector& x, CFloatVector& y, CFloatVector& alpha )
{
    /* resize input vectors */
    unsigned int size = ( unsigned int )( ( m_s2 - m_s1 ) / stepSize );
    size += 2;
    x.resize( size, 0.0 );
    y.resize( size, 0.0 );
    s.resize( size, 0.0 );
    alpha.resize( size, 0.0 );

    /* calc new stepSize */
    m_stepSize = ( m_s2 - m_s1 ) / ( size - 1 );

    /* fill vectors */
    unsigned int index = 0;
    for( CFloat sValue = m_s1; sValue <= m_s2 + m_stepSize / 2.0 ; sValue += m_stepSize )  // m_stepSize/2 for float calc errors
    {
        x[index] = state[X];
        y[index] = state[Y];
        //::std::cout << sValue << " ; " << state[S] << ::std::endl;
        s[index] = state[S];
        alpha[index] = state[ALPHA];
        index++;
        process( m_stepSize, -1 );
    }
}


/*------------------*/
/* private methodes */
/*------------------*/
CFloatVector& CClothoid::ddt( CFloatVector& state )
{
    /*************************************************************************
     * dalpha = k(s) * ds
     * alpha ist bezogen auf die auf xy - Ebene
     * k(s1) = k1 and k(s2) = k2 and k(s) = 1/c * s
     * alpha'(s) = k(s) = k1 + ((k2-k1)/(s2-s1)) * (s - s1)
     * Start    "equation of state
     *  s'(s) = 1
     *  alpha(s) analytisch lösbar: Integral_k(s) = k1*s + ((k2-k1)/(s2-s1)) * (1/2 * s^2 - s1*s)
     *                              alpha(s) = m_a1 + Integral_k(s) - Integral_k(s1)
     *  x'(s) = cos(a1 + k1*s + ((k2-k1)/(s2-s1)) * (1/2 * s^2 - s1*s) = dx/ds
     *  y'(s) = sin(a1 + k1*s + ((k2-k1)/(s2-s1)) * (1/2 * s^2 - s1*s) = dy/ds
     ************************************************************************/
    ddtState[S] = 1;
    //state[ALPHA] = m_a1 + m_k1 * ( state[S] - m_s1 ) + (( m_k2 - m_k1 ) / ( m_s2 - m_s1 ) ) * ( 0.5 * state[S] * state[S] - m_s1 * state[S] + 0.5 * m_s1 * m_s1 );
    ddtState[ALPHA] = m_k1 + m_dk * ( state[S] - m_s1 );
    ddtState[X] = ::sim::cos( state[ALPHA] );
    ddtState[Y] = ::sim::sin( state[ALPHA] );
    /* End      "equation of state */

    return ddtState;
}
