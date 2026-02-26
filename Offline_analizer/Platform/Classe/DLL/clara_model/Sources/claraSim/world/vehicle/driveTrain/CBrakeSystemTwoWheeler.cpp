/*******************************************************************************
author Robert Erhart, ett2si (23.11.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2019-2024. All rights reserved.
*******************************************************************************/

#include "CBrakeSystemTwoWheeler.h"


/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CBrakeSystemTwoWheeler::CBrakeSystemTwoWheeler()
{
    lowPass.setInit( 0.1, 1.0 ); //lowPass2ndOrder.setInit( 0.1, 0.1, 1.0 );

    /* Initialization messages */
    addMessageParameter( p_CfrontWheel, 0.00029217045, CBrakeSystemTwoWheelerDoc::p_CfrontWheel );
    addMessageParameter( p_CrearWheel, 0.000144967, CBrakeSystemTwoWheelerDoc::p_CrearWheel );
    addMessageParameter( p_MmaxParkingBrake, 300, CBrakeSystemTwoWheelerDoc::p_MmaxParkingBrake );
    addMessageParameter( p_pMaxBrake, 30000000, CBrakeSystemTwoWheelerDoc::p_pMaxBrake );
    addMessageParameter( p_pBrakeRequest, 0.0, CBrakeSystemTwoWheelerDoc::p_pBrakeRequest );
    addMessageParameter( p_pBrakeRequestEnable, false, CBrakeSystemTwoWheelerDoc::p_pBrakeRequestEnable );
    addMessageParameter( p_aBrakeRequest, 0.0, CBrakeSystemTwoWheelerDoc::p_aBrakeRequest );
    addMessageParameter( p_aBrakeRequestEnable, false, CBrakeSystemTwoWheelerDoc::p_aBrakeRequestEnable );
    addMessageParameter( p_MBrakeRequest, 0.0, CBrakeSystemTwoWheelerDoc::p_MBrakeRequest );
    addMessageParameter( p_MBrakeRequestEnable, false, CBrakeSystemTwoWheelerDoc::p_MBrakeRequestEnable );
    addMessageParameter( p_pBrakeGradientDriver, std::numeric_limits<CFloat>::max(), CBrakeSystemTwoWheelerDoc::p_pBrakeGradientDriver );

    addMessageInput( i_brakepedal, 0.0 );
    addMessageInput( i_parkingBrake, 0.0 );
    addMessageInput( i_FChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_FvRChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_m, 0.0 );
    addMessageInput( i_rWheelFront, 0.0 );
    addMessageInput( i_rWheelRear, 0.0 );
    addMessageInput( i_aBrakeRequest, 0.0 );
    addMessageInput( i_aBrakeRequestEnable, false );
    addMessageInput( i_pBrakeRequest, 0.0 );
    addMessageInput( i_pBrakeRequestEnable, false );
    addMessageInput( i_sailingRequest, false );

    addMessageOutput( o_MWheelFront, 0.0, CBrakeSystemTwoWheelerDoc::o_MWheelFront );
    addMessageOutput( o_MWheelRear, 0.0, CBrakeSystemTwoWheelerDoc::o_MWheelRear );
    addMessageOutput( o_pBrakeDriver, 0.0, CBrakeSystemTwoWheelerDoc::o_pBrakeDriver );
    addMessageOutput( o_pBrake, 0.0, CBrakeSystemTwoWheelerDoc::o_pBrake );
    addMessageOutput( o_brakeLight, false, CBrakeSystemTwoWheelerDoc::o_brakeLight );
    addMessageOutput( o_driverOverride, false, CBrakeSystemTwoWheelerDoc::o_driverOverride );

    m_pBrakeFront  = 0.0;
    m_pBrakeRear   = 0.0;
    m_MparkingBrake    = 0.0;
}

CBrakeSystemTwoWheeler::~CBrakeSystemTwoWheeler()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CBrakeSystemTwoWheeler::init( IMessage<CFloat>& f_brakepedal,
                                   IMessage<CFloat>& f_parkingBrake,
                                   IMessage<CFloatVectorXYZ>& f_FChassis,
                                   IMessage<CFloatVectorXYZ>& f_FvRChassis,
                                   IMessage<CFloat>& f_m,
                                   IMessage<CFloat>& f_rWheelFront,
                                   IMessage<CFloat>& f_rWheelRear,
                                   IMessage<CFloat>& f_aBrakeRequest,
                                   IMessage<CBool>&  f_aBrakeRequestEnable,
                                   IMessage<CFloat>& f_pBrakeRequest,
                                   IMessage<CBool>&  f_pBrakeRequestEnable,
                                   IMessage<CBool>&  f_sailingRequest )
{
    /* Connect input with internal variables */
    i_brakepedal.link( f_brakepedal );
    i_parkingBrake.link( f_parkingBrake );
    i_FChassis.link( f_FChassis );
    i_FvRChassis.link( f_FvRChassis );
    i_m.link( f_m );
    i_rWheelFront.link( f_rWheelFront );
    i_rWheelRear.link( f_rWheelRear );
    i_aBrakeRequest.link( f_aBrakeRequest );
    i_aBrakeRequestEnable.link( f_aBrakeRequestEnable );
    i_pBrakeRequest.link( f_pBrakeRequest );
    i_pBrakeRequestEnable.link( f_pBrakeRequestEnable );
    i_sailingRequest.link( f_sailingRequest );

    /* Initialization messages */
    initializationMessages();

    lowPass.init( 0.0 ); //lowPass2ndOrder.init( 0.0 );
    DeadTime.init( 100, 0 );

    /* Initialization internal variables */
    m_pBrakeFront  = 0.0;
    m_pBrakeRear   = 0.0;
    m_MparkingBrake    = 0.0;
}

/*------------------*/
/* private methods */
/*------------------*/
void CBrakeSystemTwoWheeler::calc( CFloat f_dT, CFloat f_time )
{
    /* calculate handbrake torque */
    m_MparkingBrake = i_parkingBrake * p_MmaxParkingBrake;

    /* calculate main-brake cyclinder pressure */
    if( p_pBrakeRequestEnable /*and !i_sailingRequest*/ )
    {
        /* brake pressure request */
        o_pBrake = p_pBrakeRequest;
    }
    else if( i_pBrakeRequestEnable )
    {
        /* brake pressure request */
        o_pBrake = i_pBrakeRequest;
    }
    else if( ( p_aBrakeRequestEnable || i_aBrakeRequestEnable ) /*and !i_sailingRequest*/ )
    {
        /* deceleration request */
        CFloat l_aBrakeRequest = 0;
        if( p_aBrakeRequestEnable )    l_aBrakeRequest = p_aBrakeRequest;
        if( i_aBrakeRequestEnable ) l_aBrakeRequest = i_aBrakeRequest;

        CFloat FbrakeRequestChange = i_FChassis.X() + i_FvRChassis.X() - i_m * l_aBrakeRequest;
        CFloat pBrakeChange =   FbrakeRequestChange
                                / ( p_CfrontWheel / i_rWheelFront
                                    + p_CrearWheel  / i_rWheelRear );
        o_pBrake = o_pBrake + pBrakeChange;
    }
    else if( p_MBrakeRequestEnable /*and !i_sailingRequest*/ )
    {
        o_pBrake = p_MBrakeRequest / ( 2 * p_CfrontWheel + 2 * p_CrearWheel );
    }
    else
    {
        o_pBrake = 0;
    }

    DeadTime.push( ( CFloat )o_pBrake );
    o_pBrake = DeadTime.pop();

    o_pBrake = lowPass.get( o_pBrake, f_dT );

    /* brake pedal override other requests */
    CFloat pBrakeDriver       = ::sim::pow( i_brakepedal, 2.0L ) * p_pMaxBrake;
    CFloat pBrakeDriverChange = p_pBrakeGradientDriver * f_dT;
    if( pBrakeDriver > o_pBrakeDriver )
    {
        o_pBrakeDriver = o_pBrakeDriver + ( ( ( pBrakeDriver - o_pBrakeDriver ) > pBrakeDriverChange ) ? pBrakeDriverChange : pBrakeDriver - o_pBrakeDriver );
    }
    else if( pBrakeDriver < o_pBrakeDriver )
    {
        o_pBrakeDriver = o_pBrakeDriver - ( ( ( o_pBrakeDriver - pBrakeDriver ) > pBrakeDriverChange ) ? pBrakeDriverChange : o_pBrakeDriver - pBrakeDriver );
    }

    if( o_pBrakeDriver > o_pBrake and o_pBrake > 0.01 and o_pBrakeDriver > 0 )
    {
        o_driverOverride = true;
    }
    else
    {
        o_driverOverride = false;
    }

    o_pBrake = ::sim::max( o_pBrake, o_pBrakeDriver );

    /* 0 <= pBrake <= pMaxBrake */
    o_pBrake = ::sim::limit( o_pBrake, 0., p_pMaxBrake );

    /* calculate wheel-brake cylinder pressure */
    m_pBrakeFront  = o_pBrake;
    m_pBrakeRear   = o_pBrake;

    /*************************************************************************
     * calculate brake system Torque
     *  M = 2 * � * r * A * p
     *  with C = 2 * � * r * A
     *  M = C * p
     *************************************************************************/
    o_MWheelFront  = p_CfrontWheel * m_pBrakeFront;
    o_MWheelRear   = ( p_CrearWheel * m_pBrakeRear + m_MparkingBrake );

    // brake light
    if( o_MWheelFront > 0.001
        || o_MWheelRear > 0.001 )
    {
        o_brakeLight = true;
    }
    else
    {
        o_brakeLight = false;
    }
}

