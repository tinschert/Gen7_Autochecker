/*******************************************************************************
author Robert Erhart, ett2si (20.10.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004, 2005.  All rights reserved.
*******************************************************************************/

#include "CLowPass3rdOrder.h"

/* constructor / destructor */
CLowPass3rdOrder::CLowPass3rdOrder() : CClass_ct<NumberOfStates>()
{
    setInit( 0.0, 0.0, 0.0, 0.0 );
    init();
}

CLowPass3rdOrder::~CLowPass3rdOrder()
{}

/* init methode */
void CLowPass3rdOrder::setInit( CFloat aInput, CFloat bInput, CFloat cInput, CFloat vInput )
{
    /* Init filter Parameter */
    m_aInit = aInput;
    m_bInit = bInput;
    m_cInit = cInput;
    m_vInit = vInput;
}

void CLowPass3rdOrder::init( CFloat f_initState )
{
    init( m_aInit, m_bInit, m_cInit, m_vInit, f_initState );
}

void CLowPass3rdOrder::init( CFloat aInput, CFloat bInput, CFloat cInput, CFloat vInput, CFloat f_initState )
{
    /* Init filter Parameter */
    m_a = aInput;
    m_b = bInput;
    m_c = cInput;
    m_v = vInput;

    /* Init state variable */
    state[Y1] = f_initState;
    state[Y2] = 0.0;
    state[Y3] = 0.0;
    ddtState  = 0.0;
}

/* set filter parameter */
void CLowPass3rdOrder::setFilterParameter( CFloat aInput, CFloat bInput, CFloat cInput, CFloat vInput )
{
    /* set the filter parameter */
    m_a = aInput;
    m_b = bInput;
    m_c = cInput;
    m_v = vInput;
}

/* direct calculation of CLowPass3rdOrder */
CFloat CLowPass3rdOrder::get( CFloat xInput, CFloat f_dT )
{
    m_x = xInput;
    process( f_dT, -1 );
    return state[Y1];
}

/* ddt */
CFloatVector& CLowPass3rdOrder::ddt( CFloatVector& state )
{
    /*************************************************************************
     *  y1'(t) = y2(t)
     *  y2'(t) = y3(t)
     *  y3'(t) = (v * x(t) - y1(t) - a * y2(t) - b * y3(t)) / c
     ************************************************************************/
    ddtState[Y1] = state[Y2];
    ddtState[Y2] = state[Y3];
    ddtState[Y3] = ( m_v * m_x - state[Y1] - m_a * state[Y2] - m_b * state[Y3] ) / m_c;

    return ddtState;
}
