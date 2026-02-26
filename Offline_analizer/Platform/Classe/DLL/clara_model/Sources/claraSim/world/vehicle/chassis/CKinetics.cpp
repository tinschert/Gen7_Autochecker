/*******************************************************************************
author Robert Erhart, ett2si (12.10.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004-2024. All rights reserved.
*******************************************************************************/

#include "CKinetics.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CKinetics::CKinetics():
    m_vX( 0 ),
    m_vY( 0 )
{
    /* Initialization messages */
    addMessageInput( i_vVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_rateRollPitchYaw, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_wheelAngle, 0.0 );
    addMessageInput( i_x, 0.0 );
    addMessageInput( i_y, 0.0 );

    addMessageOutput( o_alpha, 0.0, CKineticsDoc::o_alpha );
    addMessageOutput( o_vXwheel, 0.0, CKineticsDoc::o_vXwheel );
    addMessageOutput( o_vYwheel, 0.0, CKineticsDoc::o_vYwheel );
}

CKinetics::~CKinetics()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CKinetics::init( IMessage<CFloatVectorXYZ>& f_vVehicle,
                      IMessage<CFloatVectorXYZ>& f_rateRollPitchYaw,
                      IMessage<CFloat>& f_wheelAngle,
                      IMessage<CFloat>& f_x,
                      IMessage<CFloat>& f_y )
{
    /* Connect input with internal variables */
    i_vVehicle.link( f_vVehicle );
    i_rateRollPitchYaw.link( f_rateRollPitchYaw );
    i_wheelAngle.link( f_wheelAngle );
    i_x.link( f_x );
    i_y.link( f_y );

    /* Initialization messages */
    initializationMessages();

    /* Initialization variable */
    m_vX = 0;
    m_vY = 0;
}

/*------------------*/
/* private methods */
/*------------------*/
void CKinetics::calc( CFloat f_dT, CFloat f_time )
{
    /* ************************************************************************
     *   front
     *   o---o    |x
     *     |      |
     *     x   y---
     *     |
     *   o---o
     *    rear
     *
     *    vX = velocity * cos(beta) - y * yawRate
     *    vY = velocity * sin(beta) + x * yawRate
     **************************************************************************/
    m_vX = i_vVehicle.X() - i_y * i_rateRollPitchYaw.Z();
    m_vY = i_vVehicle.Y() + i_x * i_rateRollPitchYaw.Z();
    if( ::sim::abs( m_vX ) > 0.001 )
    {
        o_alpha = ::sim::sign_of( m_vX ) * ( i_wheelAngle - ::sim::atan( m_vY / m_vX ) );
    }
    else
    {
        o_alpha = 0;
    }
    o_vXwheel = m_vX * ::sim::cos( i_wheelAngle ) + m_vY * ::sim::sin( i_wheelAngle );
    o_vYwheel = m_vY * ::sim::cos( i_wheelAngle ) - m_vX * ::sim::sin( i_wheelAngle );
}

