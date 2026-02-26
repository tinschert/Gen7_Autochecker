/*******************************************************************************
author Robert Erhart, ett2si (12.10.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004-2024. All rights reserved.
*******************************************************************************/

#include "CDynamic.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CDynamic::CDynamic() : CModule<NumberOfStates>(),
    m_F( 0.0, 0.0, 0.0 ),
    m_FxDestructive( false ), m_FyDestructive( false ), m_FzDestructive( false ),
    m_M( 0.0, 0.0, 0.0 ),
    m_MyawDestructive( false ), m_MrollDestructive( false ), m_MpitchDestructive( false ),
    m_VELOCITYxK1( 0 ), m_VELOCITYyK1( 0 ),
    m_YAWRATEK1( 0 ), m_rollAngleK1( 0 )
{
    /* Initialization messages */
    addMessageParameter( p_overrideDynamic, false, CDynamicDoc::p_overrideDynamic );
    addMessageParameter( p_velocityXStatic, 0, CDynamicDoc::p_velocityXStatic );
    addMessageParameter( p_forceRollAngle, false, CDynamicDoc::p_forceRollAngle );

    addMessageInput( i_FChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_FvRChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_MRollPitchYawChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_MvRRollPitchYawChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_m, 0.0 );
    addMessageInput( i_JRollPitchYawChassis, CFloatVectorXYZ( 3000.0, 3000.0, 3000.0 ) );
    addMessageInput( i_setRollAngle, 0.0 );
    addMessageInput( i_staticSimulation, false );

    addMessageOutput( o_zChassis, 0.2, CDynamicDoc::o_zChassis );
    addMessageOutput( o_vChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CDynamicDoc::o_vChassis );
    addMessageOutput( o_aChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CDynamicDoc::o_aChassis );
    addMessageOutput( o_angleRollPitchYawSuspension, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CDynamicDoc::o_angleRollPitchYawSuspension );
    addMessageOutput( o_beta, 0.0, CDynamicDoc::o_beta );
    addMessageOutput( o_velocity, 10.0, CDynamicDoc::o_velocity );
    addMessageOutput( o_acceleration, 10.0, CDynamicDoc::o_acceleration );
    addMessageOutput( o_rateRollPitchYawChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CDynamicDoc::o_rateRollPitchYawChassis );
}

CDynamic::~CDynamic()
{}

/*------------------*/
/* public methods  */
/*------------------*/

void CDynamic::init( IMessage<CFloatVectorXYZ>& f_FChassis,
                     IMessage<CFloatVectorXYZ>& f_FvRChassis,
                     IMessage<CFloatVectorXYZ>& f_MRollPitchYawChassis,
                     IMessage<CFloatVectorXYZ>& f_MvRRollPitchYawChassis,
                     IMessage<CFloat>& f_m,
                     IMessage<CFloatVectorXYZ>& f_JRollPitchYawChassis,
                     IMessage<CFloat>& f_setRollAngle,
                     IMessage<CBool>& f_staticSimulation )
{
    /* connect input with internal variables */
    i_FChassis.link( f_FChassis );
    i_FvRChassis.link( f_FvRChassis );
    i_MRollPitchYawChassis.link( f_MRollPitchYawChassis );
    i_MvRRollPitchYawChassis.link( f_MvRRollPitchYawChassis );
    i_m.link( f_m );
    i_JRollPitchYawChassis.link( f_JRollPitchYawChassis );
    i_setRollAngle.link( f_setRollAngle );
    i_staticSimulation.link( f_staticSimulation );

    /* Initialization messages */
    initializationMessages();

    /* init state variables */
    state[ZChassis]   = o_zChassis;
    state[VELOCITYx]  = o_vChassis.X();
    state[VELOCITYy]  = o_vChassis.Y();
    state[VELOCITYz]  = o_vChassis.Z();
    state[ROLLRATE]   = o_rateRollPitchYawChassis.X();
    state[PITCHRATE]  = o_rateRollPitchYawChassis.Y();
    state[YAWRATE]    = o_rateRollPitchYawChassis.Z();
    state[ROLLANGLE]  = o_angleRollPitchYawSuspension.X();
    state[PITCHANGLE] = o_angleRollPitchYawSuspension.Y();
    ddtState = 0.0;
}

/*------------------*/
/* private methods */
/*------------------*/
void CDynamic::calcPre( CFloat f_dT, CFloat f_time )
{
    m_F = i_FChassis + i_FvRChassis;
    m_M = i_MRollPitchYawChassis + i_MvRRollPitchYawChassis;

    // check destructive overall character of forces
    m_FxDestructive = ( ::sim::abs( i_FChassis.X() ) < ::sim::abs( i_FvRChassis.X() ) ? true : false );
    m_FyDestructive = ( ::sim::abs( i_FChassis.Y() ) < ::sim::abs( i_FvRChassis.Y() ) ? true : false );
    m_FzDestructive = ( ::sim::abs( i_FChassis.Z() ) < ::sim::abs( i_FvRChassis.Z() ) ? true : false );

    m_MrollDestructive  = ( ::sim::abs( i_MRollPitchYawChassis.X() ) < ::sim::abs( i_MvRRollPitchYawChassis.X() ) ? true : false );
    m_MpitchDestructive = ( ::sim::abs( i_MRollPitchYawChassis.Y() ) < ::sim::abs( i_MvRRollPitchYawChassis.Y() ) ? true : false );
    m_MyawDestructive   = ( ::sim::abs( i_MRollPitchYawChassis.Z() ) < ::sim::abs( i_MvRRollPitchYawChassis.Z() ) ? true : false );

    m_VELOCITYxK1 = state[VELOCITYx];
    m_VELOCITYyK1 = state[VELOCITYy];
    m_YAWRATEK1   = state[YAWRATE];
    // TODO: add case handling of destructive character of Fy, Fz, Myaw, Mroll, Mpitch
}

CFloatVector& CDynamic::ddt( CFloatVector& state )
{
    /* Start    "equation of state */
    /*       vX_ddt = Fx/m + yawRate * vY
     *       vY_ddt = Fy/m - yawRate * vX
     *       yawRate_ddt = Msp / J
     */
    if( i_staticSimulation == false and p_overrideDynamic == false )
    {
        ddtState[VELOCITYx] = m_F.X() / i_m + state[YAWRATE] * state[VELOCITYy];
        ddtState[VELOCITYy] = m_F.Y() / i_m - state[YAWRATE] * state[VELOCITYx];

        CFloatVectorXYZ l_ddtAngle = m_M / i_JRollPitchYawChassis;

        ddtState[ROLLRATE] = l_ddtAngle.X();
        ddtState[PITCHRATE] = l_ddtAngle.Y();
        ddtState[YAWRATE]  = l_ddtAngle.Z();

        /* vertical state:
         * ... velocity and acceleration,
         */
        ddtState[VELOCITYz] = m_F.Z() / i_m;
        ddtState[ZChassis]  = state[VELOCITYz];

        /* ... roll angle, */
        ddtState[ROLLANGLE] = state[ROLLRATE];

        /* ... pitch angle */
        ddtState[PITCHANGLE] = state[PITCHRATE];

    }
    else
    {
        ddtState[VELOCITYx] = 0;
        ddtState[VELOCITYy] = 0;
        ddtState[VELOCITYz] = 0;
        ddtState[ZChassis]  = 0;
        ddtState[ROLLRATE]  = 0;
        ddtState[PITCHRATE] = 0;
        ddtState[YAWRATE]   = 0;
        ddtState[ROLLANGLE] = 0;
        ddtState[PITCHANGLE] = 0;
    }

    return ddtState;
}

void CDynamic::calcPost( CFloat f_dT, CFloat f_time )
{
    // TODO: add case handling of destructive character of Fz, Fy, Myaw, Mroll, Mpitch
    // m_MrollDestructive or m_MpitchDestructive or m_MyawDestructive

    // In reality, destructive torques are all velocity-related:
    //     air resistance, brake torque, lateral wheel force (computed using side slip angle -> velocity)
    // In our model, destructive brake forces would lead to chassis pitch even when standing still.
    //
    // To avoid this, the following cases are considered.
    //  - When standing and destructive torques dominate: use constructive torques only.
    //  - When moving: destructive + constructive torques


    if( m_FxDestructive
        and ( ( ::sim::sig( state[VELOCITYx] ) != ::sim::sig( m_VELOCITYxK1 ) )
              or ( state[VELOCITYx] == 0 ) )
      )
    {
        //holding force
        state[VELOCITYx]    = 0;
        ddtState[VELOCITYx] = 0;
        state[VELOCITYy]    = 0;
        ddtState[VELOCITYy] = 0;
        state[YAWRATE]      = 0;
        ddtState[YAWRATE]   = 0;
        state[ROLLRATE]     = 0;
        ddtState[ROLLRATE]  = 0;
        state[PITCHRATE]    = 0;
        ddtState[PITCHRATE] = 0;
        //state[ZChassis]     = 0;
        ddtState[ZChassis]  = 0;
        state[ROLLANGLE]    = 0;
        ddtState[ROLLANGLE] = 0;
        state[PITCHANGLE]   = 0;
        ddtState[PITCHANGLE] = 0;
    }

    if( p_forceRollAngle ) // externally forced roll angle
    {
        state[ROLLANGLE] = i_setRollAngle;

        if( f_dT > 0 )
        {
            state[ROLLRATE]     = ( i_setRollAngle - m_rollAngleK1 ) / f_dT;
            ddtState[ROLLANGLE] = state[ROLLRATE];
            ddtState[ROLLRATE]  = 0;
        }
    }

    /******************************************************************
     *           vertical dynamics output
     ******************************************************************/
    if( p_overrideDynamic == false )
    {
        o_vChassis.XYZ( state[VELOCITYx], state[VELOCITYy], state[VELOCITYz] );
        o_aChassis.XYZ( ddtState[VELOCITYx], ddtState[VELOCITYy], ddtState[VELOCITYz] );
        o_rateRollPitchYawChassis.XYZ( state[ROLLRATE], state[PITCHRATE], state[YAWRATE] );
    }
    else
    {
        o_vChassis.XYZ( p_velocityXStatic, 0.0, 0.0 );
        o_aChassis.XYZ( 0.0, 0.0, 0.0 );
        o_rateRollPitchYawChassis.XYZ( state[ROLLRATE], state[PITCHRATE], 0.0 );
    }
    o_velocity = ::sim::sqrt( ::sim::pow( o_vChassis.X(), 2 ) + ::sim::pow( o_vChassis.Y(), 2 ) );
    o_acceleration = ::sim::sqrt( ::sim::pow( o_aChassis.X(), 2 ) + ::sim::pow( o_aChassis.Y(), 2 ) + ::sim::pow( o_aChassis.Z(), 2 ) );
    o_beta = ::sim::atan2( o_vChassis.Y(), o_vChassis.X() );
    m_rollAngleK1   = state[ROLLANGLE];
    o_angleRollPitchYawSuspension.XYZ( state[ROLLANGLE], state[PITCHANGLE],  0.0 );
    o_zChassis      = state[ZChassis];
}
