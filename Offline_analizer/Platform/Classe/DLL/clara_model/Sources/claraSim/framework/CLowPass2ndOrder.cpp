/*******************************************************************************
author Robert Erhart, ett2si (20.10.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004, 2005.  All rights reserved.
*******************************************************************************/

#include "CLowPass2ndOrder.h"

/* constructor / destructor */
CLowPass2ndOrder::CLowPass2ndOrder() : CClass_ct<NumberOfStates>()
{
    setInit( 0.0, 0.0, 0.0 );
    init();
}

CLowPass2ndOrder::~CLowPass2ndOrder()
{}

/* init methode */
void CLowPass2ndOrder::setInit( CFloat aInput, CFloat bInput, CFloat vInput )
{
    /* Init filter Parameter */
    m_aInit = aInput;
    m_bInit = bInput;
    m_vInit = vInput;
}

void CLowPass2ndOrder::init( CFloat f_initState )
{
    init( m_aInit, m_bInit, m_vInit, f_initState );
}

void CLowPass2ndOrder::init( CFloat aInput, CFloat bInput, CFloat vInput, CFloat f_initState )
{
    /* Init filter Parameter */
    m_a = aInput;
    m_b = bInput;
    m_v = vInput;

    /* Init state variable */
    state[Y1] = f_initState;
    state[Y2] = 0.0;
    ddtState = 0.0;
}

/* set filter parameter */
void CLowPass2ndOrder::setFilterParameter( CFloat aInput, CFloat bInput, CFloat vInput )
{
    /* set the filter paramter */
    m_a = aInput;
    m_b = bInput;
    m_v = vInput;
}

/* direct calculation of CLowPass2ndOrder */
CFloat CLowPass2ndOrder::get( CFloat xInput, CFloat f_dT )
{
    m_x = xInput;
    process( f_dT, -1 );
    return state[Y1];
}

/* ddt */
CFloatVector& CLowPass2ndOrder::ddt( CFloatVector& state )
{
    /*************************************************************************
     * Start    "equation of state
     *  y1'(t) = y2(t)
     *  y2'(t) = (c*x(t) - a*y2(t) - y1(t) ) / b
     ************************************************************************/
    ddtState[Y1] = state[Y2];
    ddtState[Y2] = ( m_v * m_x - m_a * state[Y2] - state[Y1] ) / m_b;
    /* End      "equation of state */

    return ddtState;
}
