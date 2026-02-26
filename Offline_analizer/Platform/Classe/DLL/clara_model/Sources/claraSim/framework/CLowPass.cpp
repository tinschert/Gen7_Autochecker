/*******************************************************************************
author Robert Erhart, ett2si (22.10.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004, 2005.  All rights reserved.
*******************************************************************************/

#include "CLowPass.h"

/* constructor / destructor */
CLowPass::CLowPass() : CClass_ct<NumberOfStates>()
{
    setInit( 0.0, 0.0 );
    init();
}

CLowPass::~CLowPass()
{}

/* init methode */
void CLowPass::setInit( CFloat f_aInput, CFloat f_vInput )
{
    /* Init filter Parameter */
    m_aInit = f_aInput;
    m_vInit = f_vInput;
}

void CLowPass::init( CFloat f_initState )
{
    init( m_aInit, m_vInit, f_initState );
}

void CLowPass::init( CFloat f_aInput, CFloat f_vInput, CFloat f_initState )
{
    /* Init filter Parameter */
    m_a = f_aInput;
    m_v = f_vInput;

    /* Init state variable */
    state[Y1] = f_initState;
    ddtState = 0.0;
}

/* set filter parameter */
void CLowPass::setFilterParameter( CFloat f_aInput, CFloat f_vInput )
{
    /* set the filter paramter */
    m_a = f_aInput;
    m_v = f_vInput;
}

/* get low pass filtered value of x */
CFloat CLowPass::get( CFloat f_xInput, CFloat f_dT )
{
    m_x = f_xInput;
    process( f_dT, -1 );
    return state[0];
}

/* ddt */
CFloatVector& CLowPass::ddt( CFloatVector& state )
{
    /*************************************************************************
     * Start    "equation of state
     *  y'(t) = (c*x(t) - y1(t) ) / a
     ************************************************************************/
    ddtState[0] = ( m_v * m_x - state[0] ) / m_a;
    /* End      "equation of state */

    return ddtState;
}
