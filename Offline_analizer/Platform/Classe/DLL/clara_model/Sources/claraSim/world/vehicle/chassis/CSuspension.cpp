/*******************************************************************************
author Robert Erhart, ett2si (04.07.2005 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2005-2024. All rights reserved.
*******************************************************************************/

#include "CSuspension.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CSuspension::CSuspension()
{
    /* Initialization messages */
    addMessageParameter( p_CSpring, 40000.0, CSuspensionDoc::p_CSpring );
    addMessageParameter( p_KDamper, 11000.0, CSuspensionDoc::p_KDamper );
    addMessageParameter( p_zMax, 0.4, CSuspensionDoc::p_zMax );

    addMessageInput( i_vZsuspension, 0.0 );
    addMessageInput( i_zSuspension, 0.0 );

    addMessageOutput( o_FSuspensionChassis, 0.0, CSuspensionDoc::o_FSuspensionChassis );
    addMessageOutput( o_FSuspensionWheel, 0.0, CSuspensionDoc::o_FSuspensionWheel );
}

CSuspension::~CSuspension()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CSuspension::init( IMessage<CFloat>& f_vZsuspension,
                        IMessage<CFloat>& f_zSuspension )
{
    /* Connect input with internal variables */
    i_vZsuspension.link( f_vZsuspension );
    i_zSuspension.link( f_zSuspension );

    /* Initialization messages */
    initializationMessages();
}

/*------------------*/
/* private methods */
/*------------------*/
void CSuspension::calc( CFloat f_dT, CFloat f_time )
{
    if( i_zSuspension <= p_zMax ) // standard regime
    {
        o_FSuspensionChassis = + p_CSpring * ( p_zMax - i_zSuspension )
                               - p_KDamper * i_vZsuspension;
    }
    else // zSusp exceeds zMax: spring not loaded, loss of road contact
    {
        o_FSuspensionChassis = 0;
    }

    /* correct special cases:
     * - In standard regime, if road is not steady, vZSupension might dominate and yield F < 0.
     * - If spring is parametrized too soft, negative zSusp can lead to F > Cspring * zMax.
     *   Allow this, but limit to 3 * Cspring * zMax.
     */
    o_FSuspensionChassis = ::sim::limit( o_FSuspensionChassis, 0, 3 * p_CSpring * p_zMax );

    o_FSuspensionWheel = - o_FSuspensionChassis;
}

