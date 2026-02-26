/*******************************************************************************
author Robert Erhart, ett2si (27.06.2007)
author (c) Copyright Robert Bosch GmbH 2007-2024. All rights reserved.
*******************************************************************************/

#include "CDashboard.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CDashboard::CDashboard()
{
    k1_accMainSwitchToggle = false;
    m_time      = 0;
    m_accel = 0., m_SW = 0., m_deltaAccel = 0., m_deltaSW = 0., m_maxChangeAccel = 0., m_maxChangeSW = 0.,

    /* Initialization messages */
    addMessageInput( i_acceleratorDriver, 0.0 );
    addMessageInput( i_brakepedalDriver, 0.0 );
    addMessageInput( i_angleSteeringWheelDriver, 0.0 );
    addMessageInput( i_angleSteeringWheel, 0.0 );
    addMessageInput( i_nEngine, 0.0 );
    addMessageInput( i_vChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );

    addMessageOutput( o_accelerator, 0.0, CDashboardDoc::o_accelerator );
    addMessageOutput( o_brakepedal, 0.0, CDashboardDoc::o_brakepedal );
    addMessageOutput( o_angleSteeringWheel, 0.0, CDashboardDoc::o_angleSteeringWheel );
    addMessageOutput( o_angleSteeringWheelTarget, 0.0, CDashboardDoc::o_angleSteeringWheelTarget );
    addMessageOutput( o_nEngine, 0.0, CDashboardDoc::o_nEngine );
    addMessageOutput( o_velocityDisplay, 0.0, CDashboardDoc::o_velocityDisplay );

    addMessageParameter( p_accelerator, 0.0, CDashboardDoc::p_accelerator );
    addMessageParameter( p_brakepedal, 0.0, CDashboardDoc::p_brakepedal );
    addMessageParameter( p_clutch, 0.0, CDashboardDoc::p_clutch );
    addMessageParameter( p_parkingBrake, 0.0, CDashboardDoc::p_parkingBrake );
    addMessageParameter( p_gearStick, 5, CDashboardDoc::p_gearStick );
    addMessageParameter( p_angleSteeringWheelTarget, 0.0, CDashboardDoc::p_angleSteeringWheelTarget );
    addMessageParameter( p_angleSteeringWheelAuto, true, CDashboardDoc::p_angleSteeringWheelAuto );
    addMessageParameter( p_acceleratorAuto, false, CDashboardDoc::p_acceleratorAuto );
    addMessageParameter( p_brakepedalAuto, false, CDashboardDoc::p_brakepedalAuto );
    addMessageParameter( p_angleSteeringWheelChangeRate, 9999.0, CDashboardDoc::p_angleSteeringWheelChangeRate );
    addMessageParameter( p_acceleratorChangeRate, std::numeric_limits<CFloat>::max(), CDashboardDoc::p_acceleratorChangeRate );

    addMessageParameter( p_blinker, 0, CDashboardDoc::p_blinker );
    addMessageParameter( p_wiper, 0, CDashboardDoc::p_wiper );
    addMessageParameter( p_light, 0, CDashboardDoc::p_light );
    addMessageParameter( p_kl15, true, CDashboardDoc::p_kl15 );
    addMessageParameter( p_accMainSwitch, true, CDashboardDoc::p_accMainSwitch );
    addMessageParameter( p_accMainSwitchToggle, false, CDashboardDoc::p_accMainSwitchToggle );
    addMessageParameter( p_accOff, false, CDashboardDoc::p_accOff );
    addMessageParameter( p_accMode, false, CDashboardDoc::p_accMode );
    addMessageParameter( p_accOnOff, false, CDashboardDoc::p_accOnOff );
    addMessageParameter( p_accResume, false, CDashboardDoc::p_accResume );
    addMessageParameter( p_accSet, false, CDashboardDoc::p_accSet );
    addMessageParameter( p_accTipUp, false, CDashboardDoc::p_accTipUp );
    addMessageParameter( p_accTipDown, false, CDashboardDoc::p_accTipDown );
    addMessageParameter( p_accTipUp2Step, false, CDashboardDoc::p_accTipUp2Step );
    addMessageParameter( p_accTipDown2Step, false, CDashboardDoc::p_accTipDown2Step );
    addMessageParameter( p_accSetPlusTime, false, CDashboardDoc::p_accSetPlusTime );
    addMessageParameter( p_accSetMinusTime, false, CDashboardDoc::p_accSetMinusTime );
    addMessageParameter( p_accLIM, false, CDashboardDoc::p_accLIM );
    addMessageParameter( p_accVSet, 0.0, CDashboardDoc::p_accVSet );
    addMessageParameter( p_accTimeGap, 0.0, CDashboardDoc::p_accTimeGap );
    addMessageParameter( p_accTargetObject, false, CDashboardDoc::p_accTargetObject );
    addMessageParameter( p_lrrStatus1, 0.0, CDashboardDoc::p_lrrStatus1 );
    addMessageParameter( p_lrrStatus2, 0.0, CDashboardDoc::p_lrrStatus2 );
    addMessageParameter( p_lrrStatus3, 0.0, CDashboardDoc::p_lrrStatus3 );
    addMessageParameter( p_lrrStatusXcp, 0.0, CDashboardDoc::p_lrrStatusXcp );
    addMessageParameter( p_lrrStatusPrj, 0.0, CDashboardDoc::p_lrrStatusPrj );
    addMessageParameter( p_velocityDisplayDelta, 0.0, CDashboardDoc::p_velocityDisplayDelta );

}
CDashboard::~CDashboard()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CDashboard::init( IMessage<CFloat>& f_acceleratorDriver,
                       IMessage<CFloat>& f_brakepedalDriver,
                       IMessage<CFloat>& f_angleSteeringWheelDriver,
                       IMessage<CFloat>& f_angleSteeringWheel,
                       IMessage<CFloat>& f_nEngine,
                       IMessage<CFloatVectorXYZ>& f_vChassis )

{
    /* Connect input with internal variables */
    i_acceleratorDriver.link( f_acceleratorDriver );
    i_brakepedalDriver.link( f_brakepedalDriver );
    i_angleSteeringWheelDriver.link( f_angleSteeringWheelDriver );
    i_angleSteeringWheel.link( f_angleSteeringWheel );
    i_nEngine.link( f_nEngine );
    i_vChassis.link( f_vChassis );

    /* Initialization messages */
    initializationMessages();

    /* Defines communication between objects */
}

/*------------------*/
/* private methods */
/*------------------*/
void CDashboard::calc( CFloat f_dT, CFloat f_time )
{
    /* calculate chassis components */

    /* output */
    o_nEngine = i_nEngine * 1.0;
    o_velocityDisplay = i_vChassis.X() * 1.0  + p_velocityDisplayDelta;

    // driverOverride: state flag for driver override.
    // Override driver acceleration & braking if Dashboard input from either accelerator, brakepedal, or parking brake is active.
    bool driverOverride = ( p_accelerator != 0 ) || ( p_brakepedal != 0 ) || ( p_parkingBrake != 0 );

    /*************** calculate accelerator output ***************
     * Based on p_acceleratorAuto, set output accelerator value
     * to driver's value (i_...) or GUI/ext. input value (p_...).
     * Limit accelerator adjustment to max. allowed rate.
     ************************************************************/
    // m_accel = ( ( p_acceleratorAuto == true ) && ( p_accelerator == 0 ) ) ? i_acceleratorDriver : p_accelerator;
    m_accel = ( ( p_acceleratorAuto == true ) && !driverOverride ) ? i_acceleratorDriver : p_accelerator;


    m_deltaAccel        = m_accel - o_accelerator;
    m_maxChangeAccel    = p_acceleratorChangeRate * f_dT;

    if( ::sim::abs( m_deltaAccel ) > 0 )
    {
        // if not overshooting: add accelerator change; else: set o_accelerator = m_accel
        o_accelerator   = ( ::sim::abs( m_deltaAccel ) > ::sim::abs( m_maxChangeAccel ) )
                          ? ( o_accelerator + ::sim::sign_of( m_deltaAccel ) * m_maxChangeAccel )
                          :  m_accel;
    }   // else: do nothing, already at target accelerator state


    /*************** calculate brakepedal output ***************
     * Based on p_brakepedalAuto, set output brakepedal value
     * to driver's value (i_...) or GUI/ext. input value (p_...).
     ************************************************************/
    o_brakepedal    = ( ( p_brakepedalAuto == true ) && !driverOverride ) ? i_brakepedalDriver : p_brakepedal;


    /************ calculate steering wheel angle output ***********
     * Based on p_angleSteeringWheelAuto, set output SW angle value
     * to driver's value (i_...) or GUI/ext. input value (p_...).
     * Limit SW angle adjustment to max. allowed rate.
     ************************************************************/
    if( p_angleSteeringWheelAuto == true )
    {
        m_SW = i_angleSteeringWheelDriver;
        p_angleSteeringWheelTarget.init( 0 );
    }
    else
    {
        m_SW = p_angleSteeringWheelTarget;
    }


    m_deltaSW       = m_SW - o_angleSteeringWheelTarget;
    m_maxChangeSW   = p_angleSteeringWheelChangeRate * f_dT;
    if( ::sim::abs( m_deltaSW ) > 0 )
    {
        // if not overshooting: add SW angle change; else: set o_angleSteeringWheelTarget = m_SW
        o_angleSteeringWheelTarget = ( ( ::sim::abs( m_deltaSW ) > ::sim::abs( m_maxChangeSW ) )
                                       ? ( o_angleSteeringWheelTarget + ::sim::sign_of( m_deltaSW ) * m_maxChangeSW )
                                       :  m_SW );
    }   // else: do nothing, already at target SW angle
    o_angleSteeringWheel = i_angleSteeringWheel; // from steering system : used for GUI


    if( p_accMainSwitchToggle == true )
    {
        m_time = f_dT;
    }

    if( m_time > 0 )
    {
        if( m_time < 0.500 )
        {
            m_time = m_time + f_dT;
        }
        else
        {
            m_time = 0;
            p_accMainSwitchToggle.set( 0 );
        }
    }
}

