/*******************************************************************************
author Robert Erhart, ett2si (12.10.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004-2024. All rights reserved.
*******************************************************************************/

#include "CAirResistance.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CAirResistance::CAirResistance()
{
    /* Initialization messages */
    addMessageParameter( p_dragCoefficient, 0.29, CAirResistanceDoc::p_dragCoefficient );     // c_w value
    addMessageParameter( p_crossSectionalArea, 2.07, CAirResistanceDoc::p_crossSectionalArea );  // A
    addMessageParameter( p_airDensity, 1.22, CAirResistanceDoc::p_airDensity );         // air density at 20°C

    addMessageInput( i_velocity, 0.0 );

    addMessageOutput( o_FairResistance, 0.0, CAirResistanceDoc::o_FairResistance );
}
CAirResistance::~CAirResistance()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CAirResistance::init( IMessage<CFloat>& f_velocity )
{

    /* Connect input with internal variables */
    i_velocity.link( f_velocity );

    /* Initialization messages */
    initializationMessages();

    /* Initialization variable */
}

/*------------------*/
/* private methods */
/*------------------*/
void CAirResistance::calc( CFloat f_dT, CFloat f_time )
{
    o_FairResistance = - ::sim::sign_of( i_velocity ) * p_dragCoefficient * p_crossSectionalArea
                       * p_airDensity / 2
                       * i_velocity * i_velocity;
}

