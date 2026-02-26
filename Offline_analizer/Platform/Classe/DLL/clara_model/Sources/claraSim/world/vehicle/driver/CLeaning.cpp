/*******************************************************************************
author Andreas Brunner, bnr2lr (18.07.2019)
author (c) Copyright Robert Bosch GmbH 2019-2024. All rights reserved.
*******************************************************************************/

#include "CLeaning.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CLeaning::CLeaning()
{
    /* Initialization messages */
    addMessageParameter( p_TLowPass, 2., CLeaningDoc::p_TLowPass );

    addMessageOutput( o_rollAngle, 0.0, CLeaningDoc::o_rollAngle );

    addMessageInput( i_steeringAngle, 0.0 );
    addMessageInput( i_vChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_angleRollPitchYaw, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_xFront, 0.0 );
    addMessageInput( i_xRear, 0.0 );
    addMessageInput( i_sideslipAngleFront, 0.0 );
    addMessageInput( i_sideslipAngleRear, 0.0 );
    addMessageInput( i_casterAngle, 0.0 );
}

CLeaning::~CLeaning()
{}

/*------------------*/
/* public methods   */
/*------------------*/
void CLeaning::init( IMessage<CFloat>& f_steeringAngle,
                     IMessage<CFloatVectorXYZ>& f_vChassis,
                     IMessage<CFloatVectorXYZ>& f_angleRollPitchYaw,
                     IMessage<CFloat>& f_xFront,
                     IMessage<CFloat>& f_xRear,
                     IMessage<CFloat>& f_sideslipAngleFront,
                     IMessage<CFloat>& f_sideslipAngleRear,
                     IMessage<CFloat>& f_casterAngle )
{
    /* init of internal variables */

    /* Connect input with internal variables */
    i_steeringAngle.link( f_steeringAngle );
    i_vChassis.link( f_vChassis );
    i_angleRollPitchYaw.link( f_angleRollPitchYaw );
    i_xFront.link( f_xFront );
    i_xRear.link( f_xRear );
    i_sideslipAngleFront.link( f_sideslipAngleFront ),
                               i_sideslipAngleRear.link( f_sideslipAngleRear ),
                               i_casterAngle.link( f_casterAngle );

    /* Initialization messages */
    initializationMessages();

    // init filter a filter time constant; v amplification factor; f_initState
    LowPassTheta.init( p_TLowPass, 1.0, 0.0 );
}

/*------------------*/
/* private methods  */
/*------------------*/

void CLeaning::calc( CFloat f_dT, CFloat f_time )
{
    // get current roll angle (track + chassis)
    m_thetaTrack    = i_angleRollPitchYaw.X();

    if( ( i_xFront - i_xRear ) > 0 )
    {
        // minus sign to convert roll
        CFloat l_arg1  = - ::sim::pow( i_vChassis.X(), 2. ) * ( i_steeringAngle - i_sideslipAngleFront + i_sideslipAngleRear ) * ::sim::cos( i_casterAngle );
        CFloat l_arg2  = ( 9.81 * ( i_xFront - i_xRear ) );
        m_thetaLean = ::sim::atan2( l_arg1, l_arg2 );
    }
    else // invalid wheelbase
    {
        m_thetaLean = 0.;
    }

    // target roll angle output
    m_thetaLean = ::sim::limit( m_thetaLean, -M_PI / 3, M_PI / 3 ); // ToDo: hard-coded max leaning angle
    o_rollAngle = LowPassTheta.get( m_thetaLean - m_thetaTrack, f_dT ); // output roll angle is chassis(!) roll
}

void CLeaning::calcPre( CFloat f_dT, CFloat f_time )
{}

void CLeaning::calcPost( CFloat f_dT, CFloat f_time )
{}
