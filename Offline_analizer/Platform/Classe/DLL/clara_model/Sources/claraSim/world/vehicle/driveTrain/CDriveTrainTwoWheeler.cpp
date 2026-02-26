/*******************************************************************************
 $Source: CDriveTrainTwoWheeler.cpp $
 $Date: 2017/01/24 15:38:43CET $
 $Revision: 1.22 $

 author Robert Erhart, ett2si (18.11.2004 - 00:00:00)
 author (c) Copyright Robert Bosch GmbH 2019-2024. All rights reserved.
 *******************************************************************************/

#include "CDriveTrainTwoWheeler.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CDriveTrainTwoWheeler::CDriveTrainTwoWheeler()
{
    /* Initialization messages */
    addMessageParameter( p_frontWheelDrive, true, CDriveTrainTwoWheelerDoc::p_frontWheelDrive );
    addMessageParameter( p_rearWheelDrive, false, CDriveTrainTwoWheelerDoc::p_rearWheelDrive );
    addMessageParameter( p_sailingRequest, false, CDriveTrainTwoWheelerDoc::p_sailingRequest );
    addMessageParameter( p_deltaMUnstressed, 10, CDriveTrainTwoWheelerDoc::p_deltaMUnstressed );
    /* TSK */
    addMessageParameter( p_holdConfirmationOverride, false, CDriveTrainTwoWheelerDoc::p_holdConfirmationOverride );
    addMessageParameter( p_aTargetACCEnable, false, CDriveTrainTwoWheelerDoc::p_aTargetACCEnable );
    addMessageParameter( p_aTargetACC, 0.0, CDriveTrainTwoWheelerDoc::p_aTargetACC );
    addMessageParameter( p_aTargetPSSEnable, false, CDriveTrainTwoWheelerDoc::p_aTargetPSSEnable );
    addMessageParameter( p_aTargetPSS, 0.0, CDriveTrainTwoWheelerDoc::p_aTargetPSS );

    addMessageParameter( p_holdRequestPSS, false, CDriveTrainTwoWheelerDoc::p_holdRequestPSS );
    addMessageParameter( p_holdRequestACC, false, CDriveTrainTwoWheelerDoc::p_holdRequestACC );
    addMessageParameter( p_holdRelease, false, CDriveTrainTwoWheelerDoc::p_holdRelease );
    addMessageParameter( p_pBrakeHoldPressure, 30000000, CDriveTrainTwoWheelerDoc::p_pBrakeHoldPressure );

    addMessageOutput( o_MWheelFront, 0.0, CDriveTrainTwoWheelerDoc::o_MWheelFront );
    addMessageOutput( o_MWheelRear, 0.0, CDriveTrainTwoWheelerDoc::o_MWheelRear );
    addMessageOutput( o_RvMWheelFront, 0.0, CDriveTrainTwoWheelerDoc::o_RvMWheelFront );
    addMessageOutput( o_RvMWheelRear, 0.0, CDriveTrainTwoWheelerDoc::o_RvMWheelRear );

    addMessageOutput( o_sailing, false, CDriveTrainTwoWheelerDoc::o_sailing );
    addMessageOutput( o_unstressed, true, CDriveTrainTwoWheelerDoc::o_unstressed );

    addMessageOutput( o_holdConfirmation, false, CDriveTrainTwoWheelerDoc::o_holdConfirmation );
    addMessageOutput( o_holdTransition, false, CDriveTrainTwoWheelerDoc::o_holdTransition );
    addMessageOutput( o_aBrakeRequest, 0.0, CDriveTrainTwoWheelerDoc::o_aBrakeRequest );
    addMessageOutput( o_aBrakeRequestEnable, false, CDriveTrainTwoWheelerDoc::o_aBrakeRequestEnable );
    addMessageOutput( o_pBrakeRequest, 0.0, CDriveTrainTwoWheelerDoc::o_pBrakeRequest );
    addMessageOutput( o_pBrakeRequestEnable, false, CDriveTrainTwoWheelerDoc::o_pBrakeRequestEnable );
    addMessageOutput( o_MtorqueRequest, 0.0, CDriveTrainTwoWheelerDoc::o_MtorqueRequest );
    addMessageOutput( o_MtorqueRequestEnable, false, CDriveTrainTwoWheelerDoc::o_MtorqueRequestEnable );

    addMessageInput( i_accelerator, 0.0 );
    addMessageInput( i_nWheelFront, 0.0 );
    addMessageInput( i_nWheelRear, 0.0 );
    addMessageInput( i_clutch, 0.0 );
    addMessageInput( i_gearStick, 0 );
    addMessageInput( i_brakepedal, 0.0 );
    addMessageInput( i_parkingBrake, 0.0 );
    addMessageInput( i_FChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_FvRChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_VehicleMass, 0.0 );
    addMessageInput( i_rWheelFront, 0.0 );
    addMessageInput( i_rWheelRear, 0.0 );
    addMessageInput( i_angleRollPitchYaw, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );

    // input via internal modules
    addMessageInput( i_MWheelFrontBrakeSystem, 0.0 );
    addMessageInput( i_MWheelRearBrakeSystem, 0.0 );
    addMessageInput( i_MdTransmission, 0.0 );
    addMessageInput( i_gearRatioTransmission, 0.0 );
    addMessageInput( i_MMinEngine, 0.0 );
    addMessageInput( i_MFrictionEngine, 0.0 );

    m_anhaltenState = 0;
    m_HystBrakeEngine = -2;
    m_HystSailing = 0;

}

CDriveTrainTwoWheeler::~CDriveTrainTwoWheeler()
{
}

/*------------------*/
/* public methods  */
/*------------------*/
void CDriveTrainTwoWheeler::init( IMessage<CFloat>& f_accelerator,
                                  IMessage<CFloat>& f_nWheelFront,
                                  IMessage<CFloat>& f_nWheelRear,
                                  IMessage<CFloat>& f_clutch,
                                  IMessage<CInt>& f_gearStick,
                                  IMessage<CFloat>& f_brakepedal,
                                  IMessage<CFloat>& f_parkingBrake,
                                  IMessage<CFloatVectorXYZ>& f_FChassis,
                                  IMessage<CFloatVectorXYZ>& f_FvRChassis,
                                  IMessage<CFloat>& f_m,
                                  IMessage<CFloat>& f_rWheelFront,
                                  IMessage<CFloat>& f_rWheelRear,
                                  IMessage<CFloatVectorXYZ>& f_angleRollPitchYaw )
{
    m_anhaltenState = 0;
    m_HystBrakeEngine = -2;
    /* Connect input with internal variables */
    i_accelerator.link( f_accelerator );
    i_nWheelFront.link( f_nWheelFront );
    i_nWheelRear.link( f_nWheelRear );
    i_clutch.link( f_clutch );
    i_gearStick.link( f_gearStick );
    i_brakepedal.link( f_brakepedal );
    i_parkingBrake.link( f_parkingBrake );
    i_FChassis.link( f_FChassis );
    i_FvRChassis.link( f_FvRChassis );
    i_VehicleMass.link( f_m );
    i_rWheelFront.link( f_rWheelFront );
    i_rWheelRear.link( f_rWheelRear );
    i_angleRollPitchYaw.link( f_angleRollPitchYaw );

    // input via internal modules
    i_MWheelFrontBrakeSystem.link( brakeSystem.o_MWheelFront );
    i_MWheelRearBrakeSystem.link( brakeSystem.o_MWheelRear );
    i_MdTransmission.link( transmission.o_MdTransmission );
    i_gearRatioTransmission.link( transmission.o_gearRatio );
    i_MMinEngine.link( motor.o_Mmin );
    i_MFrictionEngine.link( motor.o_MfrictionTorque );

    /* Initialization messages */
    initializationMessages();

    /* Initialization internal variables */

    /* Defines communication between objects */
    motor.init( i_accelerator,
                transmission.o_nTransmission,
                o_MtorqueRequest,
                o_MtorqueRequestEnable,
                o_sailing );

    transmission.init( motor.o_MengineTorque,
                       motor.o_MengineTorqueDesired,
                       i_nWheelRear,
                       i_clutch,
                       i_gearStick,
                       o_sailing );

    brakeSystem.init( i_brakepedal,
                      i_parkingBrake,
                      i_FChassis,
                      i_FvRChassis,
                      i_VehicleMass,
                      i_rWheelFront,
                      i_rWheelRear,
                      o_aBrakeRequest,
                      o_aBrakeRequestEnable,
                      o_pBrakeRequest,
                      o_pBrakeRequestEnable,
                      o_sailing );
}

/*------------------*/
/* private methods */
/*------------------*/
void CDriveTrainTwoWheeler::calc( CFloat f_dT, CFloat f_time )
{
    /* calculate power train components */
    transmission.process( f_dT, f_time );
    motor.process( f_dT, f_time );
    brakeSystem.process( f_dT, f_time );

    /* output */
    o_MWheelFront = 0;
    o_RvMWheelFront = -::sim::sig( i_nWheelFront ) * i_MWheelFrontBrakeSystem; //ToDo: not correct for hold forces n == 0

    o_MWheelRear = i_MdTransmission;
    o_RvMWheelRear = -::sim::sig( i_nWheelRear ) * i_MWheelRearBrakeSystem;


    /********************************************/
    /* TSK (Triebstrang Koordinator) simulation */
    /********************************************/
    long double l_Fsteigung = -9.81 * sin( i_angleRollPitchYaw.Y() ) * i_VehicleMass; // slope force
    long double l_Ratio = i_gearRatioTransmission;
    long double l_Mmin = i_MMinEngine;
    long double l_acc_wunschmoment = i_MFrictionEngine + ( l_Fsteigung - i_FvRChassis.X() + ( p_aTargetACC * i_VehicleMass ) ) * i_rWheelFront / l_Ratio;

    // example: ANB BREMSUNG
    if( p_aTargetPSSEnable == true )
    {
        o_aBrakeRequest = p_aTargetPSS;
        o_aBrakeRequestEnable = true;
    }
    else if( ( l_acc_wunschmoment < l_Mmin + m_HystBrakeEngine ) && p_aTargetACCEnable )
    {
        m_HystBrakeEngine = 30;
        o_aBrakeRequest = p_aTargetACC;
        o_aBrakeRequestEnable = true;
        o_MtorqueRequest = 0.0;
        o_MtorqueRequestEnable = false;
    }
    else if( ( l_acc_wunschmoment >= l_Mmin + m_HystBrakeEngine ) && p_aTargetACCEnable )
    {
        m_HystBrakeEngine = -2;
        o_aBrakeRequest = 0.0;
        o_aBrakeRequestEnable = false;
        o_MtorqueRequest = l_acc_wunschmoment;
        o_MtorqueRequestEnable = true;
    }
    else
    {
        m_HystBrakeEngine = -2;
        o_aBrakeRequest = 0.0;
        o_aBrakeRequestEnable = false;
        o_MtorqueRequest = 0.0;
        o_MtorqueRequestEnable = false;
    }

    switch( m_anhaltenState )
    {
        case 0: // Normalzustand
            o_holdTransition = false;
            o_holdConfirmation = false;
            if( p_holdRequestACC || p_holdRequestPSS )
            {
                m_anhaltenState = 10;
            }
            break;
        case 10: // Erste Stufe Halten // nur 1 Zyklus
            o_aBrakeRequest = 30;
            o_aBrakeRequestEnable = true;
            o_holdTransition = true;
            m_anhaltenState = 20;
            break;
        case 20: // Zweite Stufe Halten // nur 1 Zyklus
            o_holdConfirmation = true;
            m_anhaltenState = 30;
            break;
        case 30: // Halten Aktiv
            //brakeSystem.p_pBrakeRequestEnable.set( true );
            o_pBrakeRequestEnable = true;
            //brakeSystem.p_pBrakeRequest.set( p_pBrakeHoldPressure );
            o_pBrakeRequest = p_pBrakeHoldPressure;

            if( p_holdRelease || i_accelerator >= 0.1 || i_brakepedal >= 0.1 )
            {
                //brakeSystem.p_pBrakeRequestEnable.set( false );
                o_pBrakeRequestEnable = false;
                //brakeSystem.p_pBrakeRequest.set( 0 );
                o_pBrakeRequest = 0;
                m_anhaltenState = 40;
            }
            break;
        case 40: // Halten beenden // nur 1 Zyklus
            o_aBrakeRequest = 0;
            o_aBrakeRequestEnable = false;
            o_holdTransition = false;
            o_holdConfirmation = false;
            m_anhaltenState = 0;
            break;
        default:
            break;
    }
    // Prevent failure : FAULT_CIS_ESP_HOLD_PLAUS_FAIL
    if( p_holdConfirmationOverride )
    {
        o_holdConfirmation = true;
    }

    /********************************************/
    /* SAILING                                  */
    /********************************************/
    if( std::abs( motor.o_MengineTorque ) <= p_deltaMUnstressed )
    {
        o_unstressed = true;
    }
    else
    {
        o_unstressed = false;
    }
    if( o_unstressed == true && p_sailingRequest == true /*&& brakeSystem.o_pBrake <=0.001*/ )
    {
        m_HystSailing = m_HystSailing + f_dT;
    }
    if( o_unstressed == true && p_sailingRequest == true /*&& brakeSystem.o_pBrake <=0.001*/ && m_HystSailing > 2.0 )
    {
        o_sailing = true;
    }
    if( p_sailingRequest == false || motor.o_driverOverride )
    {
        o_sailing = false;
        m_HystSailing = 0.0;
    }


}

