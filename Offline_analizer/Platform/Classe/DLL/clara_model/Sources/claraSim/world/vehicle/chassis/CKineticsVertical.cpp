/*******************************************************************************
author Robert Erhart, ett2si (04.07.2005 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2005-2024. All rights reserved.
*******************************************************************************/

#include "CKineticsVertical.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CKineticsVertical::CKineticsVertical()
{
    /* Initialization messages */
    addMessageInput( i_angleRollPitchYawSuspension, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_rateRollPitchYawChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_zChassis, 0.0 );
    addMessageInput( i_vChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_x, 0.0 );
    addMessageInput( i_y, 0.0 );

    addMessageOutput( o_zSuspension, 0.2, CKineticsVerticalDoc::o_zSuspension );
    addMessageOutput( o_vZsuspension, 0.0, CKineticsVerticalDoc::o_vZsuspension );
}

CKineticsVertical::~CKineticsVertical()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CKineticsVertical::init( IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSuspension,
                              IMessage<CFloatVectorXYZ>& f_rateRollPitchYawChassis,
                              IMessage<CFloat>& f_zChassis,
                              IMessage<CFloatVectorXYZ>& f_vChassis,
                              IMessage<CFloat>& f_x,
                              IMessage<CFloat>& f_y )
{
    /* Connect input with internal variables */
    i_angleRollPitchYawSuspension.link( f_angleRollPitchYawSuspension );
    i_rateRollPitchYawChassis.link( f_rateRollPitchYawChassis );
    i_zChassis.link( f_zChassis );
    i_vChassis.link( f_vChassis );
    i_x.link( f_x );
    i_y.link( f_y );

    /* Initialization messages */
    initializationMessages();
}

/*------------------*/
/* private methods */
/*------------------*/
void CKineticsVertical::calc( CFloat f_dT, CFloat f_time )
{
    /*  positiver Winkel nach rechte Hand Regel
     *  im Bezug auf das Fahrzeugkoordinatensystem */
    o_zSuspension = i_zChassis
                    - i_x * sin( i_angleRollPitchYawSuspension.Y() )  // anglePitchChassis
                    + i_y * sin( i_angleRollPitchYawSuspension.X() ); // angleRollChassis
    o_vZsuspension = i_vChassis.Z()
                     - i_x * i_rateRollPitchYawChassis.Y() // omegaPitchChassis
                     + i_y * i_rateRollPitchYawChassis.X(); // omegaRollChassis;
}

