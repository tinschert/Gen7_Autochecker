/*******************************************************************************
author Robert Erhart, ett2si (13.04.2005 - 00:00:00)
author Andreas Brunner, bnr2lr (26.07.2019)
author (c) Copyright Robert Bosch GmbH 2019-2024. All rights reserved.
*******************************************************************************/

#include "CSteeringSystemTwoWheeler.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CSteeringSystemTwoWheeler::CSteeringSystemTwoWheeler(): CModule<>(),
    m_angleSteeringWheel_K1( 0 )
{
    /* Initialization messages */
    addMessageParameter( p_angleWheelFrontMax, 0.698, CSteeringSystemTwoWheelerDoc::p_angleWheelFrontMax );  //~40°
    addMessageParameter( p_angleWheelFrontMin, -0.698, CSteeringSystemTwoWheelerDoc::p_angleWheelFrontMin );  //~40°

    addMessageOutput( o_angleWheelFront, 0.0, CSteeringSystemTwoWheelerDoc::o_angleWheelFront );
    addMessageOutput( o_angleWheelRear, 0.0, CSteeringSystemTwoWheelerDoc::o_angleWheelRear );
    addMessageOutput( o_angleSteeringWheelVelocity, 0.0, CSteeringSystemTwoWheelerDoc::o_angleSteeringWheelVelocity );
    addMessageOutput( o_angleSteeringWheel, 0.0, CSteeringSystemTwoWheelerDoc::o_angleSteeringWheel );

    addMessageInput( i_angleSteeringWheel, 0.0 );
}

CSteeringSystemTwoWheeler::~CSteeringSystemTwoWheeler()
{}

/*------------------*/
/* public methods   */
/*------------------*/
void CSteeringSystemTwoWheeler::init( IMessage<CFloat>& f_angleSteeringWheel )

{
    /* init of internal variables */
    m_angleSteeringWheel_K1 = 0.0;

    /* Connect input with internal variables */
    i_angleSteeringWheel.link( f_angleSteeringWheel );

    /* Initialization messages */
    initializationMessages();
}

/*------------------*/
/* private methods  */
/*------------------*/
void CSteeringSystemTwoWheeler::calc( CFloat f_dT, CFloat f_time )
{
    // calculate front wheel angle
    o_angleWheelFront = ::sim::limit( i_angleSteeringWheel, p_angleWheelFrontMin, p_angleWheelFrontMax );
    o_angleWheelRear = 0.0;

    if( f_dT > 0 )
    {
        o_angleSteeringWheelVelocity = ( i_angleSteeringWheel - m_angleSteeringWheel_K1 ) / f_dT;
        m_angleSteeringWheel_K1 = i_angleSteeringWheel;
    }
    o_angleSteeringWheel = i_angleSteeringWheel; // just a back loop from dashboard
}
