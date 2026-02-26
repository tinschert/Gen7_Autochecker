/*******************************************************************************
 $Source: CDriveTrain.cpp $
 $Date: 2017/01/24 15:38:43CET $
 $Revision: 1.22 $

 author Robert Erhart, ett2si (18.11.2004 - 00:00:00)
 author (c) Copyright Robert Bosch GmbH 2004-2024. All rights reserved.
 *******************************************************************************/

#include "CDriveTrain.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CDriveTrain::CDriveTrain()
{
    /* Initialization messages */
    addMessageParameter( p_frontWheelDrive, true, CDriveTrainDoc::p_frontWheelDrive );
    addMessageParameter( p_rearWheelDrive, false, CDriveTrainDoc::p_rearWheelDrive );
    addMessageParameter( p_sailingRequest, false, CDriveTrainDoc::p_sailingRequest );
    addMessageParameter( p_deltaMUnstressed, 10, CDriveTrainDoc::p_deltaMUnstressed );
    /* TSK */
    addMessageParameter( p_holdConfirmationOverride, false, CDriveTrainDoc::p_holdConfirmationOverride );
    addMessageParameter( p_aTargetACCEnable, false, CDriveTrainDoc::p_aTargetACCEnable );
    addMessageParameter( p_aTargetACC, 0.0, CDriveTrainDoc::p_aTargetACC );
    addMessageParameter( p_aTargetPSSEnable, false, CDriveTrainDoc::p_aTargetPSSEnable );
    addMessageParameter( p_aTargetPSS, 0.0, CDriveTrainDoc::p_aTargetPSS );

    addMessageParameter( p_holdRequestPSS, false, CDriveTrainDoc::p_holdRequestPSS );
    addMessageParameter( p_holdRequestACC, false, CDriveTrainDoc::p_holdRequestACC );
    addMessageParameter( p_holdRelease, false, CDriveTrainDoc::p_holdRelease );
    addMessageParameter( p_pBrakeHoldPressure, 30000000, CDriveTrainDoc::p_pBrakeHoldPressure );

    addMessageOutput( o_MWheelRightFront, 0.0, CDriveTrainDoc::o_MWheelRightFront );
    addMessageOutput( o_MWheelLeftFront, 0.0, CDriveTrainDoc::o_MWheelLeftFront );
    addMessageOutput( o_MWheelRightRear, 0.0, CDriveTrainDoc::o_MWheelRightRear );
    addMessageOutput( o_MWheelLeftRear, 0.0, CDriveTrainDoc::o_MWheelLeftRear );
    addMessageOutput( o_RnMWheelLeftFront, 0.0, CDriveTrainDoc::o_RnMWheelLeftFront );
    addMessageOutput( o_RnMWheelRightFront, 0.0, CDriveTrainDoc::o_RnMWheelRightFront );
    addMessageOutput( o_RnMWheelLeftRear, 0.0, CDriveTrainDoc::o_RnMWheelLeftRear );
    addMessageOutput( o_RnMWheelRightRear, 0.0, CDriveTrainDoc::o_RnMWheelRightRear );

    addMessageOutput( o_sailing, false, CDriveTrainDoc::o_sailing );
    addMessageOutput( o_unstressed, true, CDriveTrainDoc::o_unstressed );

    addMessageOutput( o_holdConfirmation, false, CDriveTrainDoc::o_holdConfirmation );
    addMessageOutput( o_holdTransition, false, CDriveTrainDoc::o_holdTransition );
    addMessageOutput( o_aBrakeRequest, 0.0, CDriveTrainDoc::o_aBrakeRequest );
    addMessageOutput( o_aBrakeRequestEnable, false, CDriveTrainDoc::o_aBrakeRequestEnable );
    addMessageOutput( o_pBrakeRequest, 0.0, CDriveTrainDoc::o_pBrakeRequest );
    addMessageOutput( o_pBrakeRequestEnable, false, CDriveTrainDoc::o_pBrakeRequestEnable );
    addMessageOutput( o_MtorqueRequest, 0.0, CDriveTrainDoc::o_MtorqueRequest );
    addMessageOutput( o_MtorqueRequestEnable, false, CDriveTrainDoc::o_MtorqueRequestEnable );

    addMessageInput( i_accelerator, 0.0 );
    addMessageInput( i_nWheelRightFront, 0.0 );
    addMessageInput( i_nWheelLeftFront, 0.0 );
    addMessageInput( i_nWheelRightRear, 0.0 );
    addMessageInput( i_nWheelLeftRear, 0.0 );
    addMessageInput( i_clutch, 0.0 );
    addMessageInput( i_gearStick, 0 );
    addMessageInput( i_brakepedal, 0.0 );
    addMessageInput( i_parkingBrake, 0.0 );
    addMessageInput( i_FChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_FvRChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_VehicleMass, 0.0 );
    addMessageInput( i_rWheelRightFront, 0.0 );
    addMessageInput( i_rWheelLeftFront, 0.0 );
    addMessageInput( i_rWheelRightRear, 0.0 );
    addMessageInput( i_rWheelLeftRear, 0.0 );
    addMessageInput( i_angleRollPitchYaw, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );

    // input via internal modules
    addMessageInput( i_MWheelLeftFrontDifferentialGear, 0.0 );
    addMessageInput( i_MWheelLeftFrontBrakeSystem, 0.0 );
    addMessageInput( i_MWheelRightFrontDifferentialGear, 0.0 );
    addMessageInput( i_MWheelRightFrontBrakeSystem, 0.0 );
    addMessageInput( i_MWheelLeftRearDifferentialGear, 0.0 );
    addMessageInput( i_MWheelLeftRearBrakeSystem, 0.0 );
    addMessageInput( i_MWheelRightRearDifferentialGear, 0.0 );
    addMessageInput( i_MWheelRightRearBrakeSystem, 0.0 );
    addMessageInput( i_gearRatioTransmission, 0.0 );
    addMessageInput( i_gearRatioDifferential, 0.0 );
    addMessageInput( i_MMinEngine, 0.0 );
    addMessageInput( i_MFrictionEngine, 0.0 );

    m_stopState = 0;
    m_HystBrakeEngine = -2;
    m_HystSailing = 0;
}

CDriveTrain::~CDriveTrain()
{
}

/*------------------*/
/* public methods  */
/*------------------*/
void CDriveTrain::init( IMessage<CFloat>& f_accelerator,
                        IMessage<CFloat>& f_nWheelRightFront,
                        IMessage<CFloat>& f_nWheelLeftFront,
                        IMessage<CFloat>& f_nWheelRightRear,
                        IMessage<CFloat>& f_nWheelLeftRear,
                        IMessage<CFloat>& f_clutch,
                        IMessage<CInt>& f_gearStick,
                        IMessage<CFloat>& f_brakepedal,
                        IMessage<CFloat>& f_parkingBrake,
                        IMessage<CFloatVectorXYZ>& f_FChassis,
                        IMessage<CFloatVectorXYZ>& f_FvRChassis,
                        IMessage<CFloat>& f_m,
                        IMessage<CFloat>& f_rWheelLeftFront,
                        IMessage<CFloat>& f_rWheelRightFront,
                        IMessage<CFloat>& f_rWheelLeftRear,
                        IMessage<CFloat>& f_rWheelRightRear,
                        IMessage<CFloatVectorXYZ>& f_angleRollPitchYaw )
{
    m_stopState = 0;
    m_HystBrakeEngine = -2;
    /* Connect input with internal variables */
    i_accelerator.link( f_accelerator );
    i_nWheelRightFront.link( f_nWheelRightFront );
    i_nWheelLeftFront.link( f_nWheelLeftFront );
    i_nWheelRightRear.link( f_nWheelRightRear );
    i_nWheelLeftRear.link( f_nWheelLeftRear );
    i_clutch.link( f_clutch );
    i_gearStick.link( f_gearStick );
    i_brakepedal.link( f_brakepedal );
    i_parkingBrake.link( f_parkingBrake );
    i_FChassis.link( f_FChassis );
    i_FvRChassis.link( f_FvRChassis );
    i_VehicleMass.link( f_m );
    i_rWheelLeftFront.link( f_rWheelLeftFront );
    i_rWheelRightFront.link( f_rWheelRightFront );
    i_rWheelLeftRear.link( f_rWheelLeftRear );
    i_rWheelRightRear.link( f_rWheelRightRear );
    i_angleRollPitchYaw.link( i_angleRollPitchYaw );

    // input via internal modules
    i_MWheelLeftFrontDifferentialGear.link( differentialGear.o_MWheelLeftFront );
    i_MWheelLeftFrontBrakeSystem.link( brakeSystem.o_MWheelLeftFront );
    i_MWheelRightFrontDifferentialGear.link( differentialGear.o_MWheelRightFront );
    i_MWheelRightFrontBrakeSystem.link( brakeSystem.o_MWheelRightFront );
    i_MWheelLeftRearDifferentialGear.link( differentialGear.o_MWheelLeftRear );
    i_MWheelLeftRearBrakeSystem.link( brakeSystem.o_MWheelLeftRear );
    i_MWheelRightRearDifferentialGear.link( differentialGear.o_MWheelRightRear );
    i_MWheelRightRearBrakeSystem.link( brakeSystem.o_MWheelRightRear );
    i_gearRatioTransmission.link( transmission.o_gearRatio );
    i_gearRatioDifferential.link( differentialGear.o_differentialGearRatio );
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
                       differentialGear.o_nDifferentialGear,
                       i_clutch,
                       i_gearStick,
                       o_sailing );

    differentialGear.init( i_nWheelRightFront,
                           i_nWheelLeftFront,
                           i_nWheelRightRear,
                           i_nWheelLeftRear,
                           transmission.o_MdTransmission,
                           p_frontWheelDrive,
                           p_rearWheelDrive );

    brakeSystem.init( i_brakepedal,
                      i_parkingBrake,
                      i_FChassis,
                      i_FvRChassis,
                      i_VehicleMass,
                      i_rWheelLeftFront,
                      i_rWheelRightFront,
                      i_rWheelLeftRear,
                      i_rWheelRightRear,
                      o_aBrakeRequest,
                      o_aBrakeRequestEnable,
                      o_pBrakeRequest,
                      o_pBrakeRequestEnable,
                      o_sailing );
}

/*------------------*/
/* private methods */
/*------------------*/
void CDriveTrain::calc( CFloat f_dT, CFloat f_time )
{
    /* calculate power train components */
    differentialGear.process( f_dT, f_time );
    transmission.process( f_dT, f_time );
    motor.process( f_dT, f_time );
    brakeSystem.process( f_dT, f_time );

    /* output */
    o_MWheelLeftFront = i_MWheelLeftFrontDifferentialGear;
    o_RnMWheelLeftFront = -::sim::sig( i_nWheelLeftFront ) * i_MWheelLeftFrontBrakeSystem; //ToDo: not correct for hold forces n == 0

    o_MWheelRightFront = i_MWheelRightFrontDifferentialGear;
    o_RnMWheelRightFront = -::sim::sig( i_nWheelRightFront ) * i_MWheelRightFrontBrakeSystem;

    o_MWheelLeftRear = i_MWheelLeftRearDifferentialGear;
    o_RnMWheelLeftRear = -::sim::sig( i_nWheelLeftRear ) * i_MWheelLeftRearBrakeSystem;

    o_MWheelRightRear = i_MWheelRightRearDifferentialGear;
    o_RnMWheelRightRear = -::sim::sig( i_nWheelRightRear ) * i_MWheelRightRearBrakeSystem;


    /**********************************************************************/
    /* Drive Train Coordinator / TSK (Triebstrang Koordinator) simulation */
    /**********************************************************************/
    long double l_Fslope = -9.81 * sin( i_angleRollPitchYaw.Y() ) * i_VehicleMass; // slope force
    long double l_Ratio = i_gearRatioTransmission * i_gearRatioDifferential; // transmission ratio
    long double l_Mmin = i_MMinEngine;
    long double l_MAccTarget = i_MFrictionEngine + ( l_Fslope - i_FvRChassis.X() + ( p_aTargetACC * i_VehicleMass ) ) * i_rWheelLeftFront / l_Ratio; // ACC-Wunschmoment

    if( p_aTargetPSSEnable == true )
    {
        o_aBrakeRequest = p_aTargetPSS;
        o_aBrakeRequestEnable = true;
    }
    else if( ( l_MAccTarget < l_Mmin + m_HystBrakeEngine ) && p_aTargetACCEnable )
    {
        m_HystBrakeEngine = 30;
        o_aBrakeRequest = p_aTargetACC;
        o_aBrakeRequestEnable = true;
        o_MtorqueRequest = 0.0;
        o_MtorqueRequestEnable = false;
    }
    else if( ( l_MAccTarget >= l_Mmin + m_HystBrakeEngine ) && p_aTargetACCEnable )
    {
        m_HystBrakeEngine = -2;
        o_aBrakeRequest = 0.0;
        o_aBrakeRequestEnable = false;
        o_MtorqueRequest = l_MAccTarget;
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

    switch( m_stopState )
    {
        case 0: // Default state (Normalzustand)
            o_holdTransition = false;
            o_holdConfirmation = false;
            if( p_holdRequestACC || p_holdRequestPSS )
            {
                m_stopState = 10;
            }
            break;
        case 10: // First stage: single cycle only (Erste Stufe Halten // nur 1 Zyklus)
            o_aBrakeRequest = 30;
            o_aBrakeRequestEnable = true;
            o_holdTransition = true;
            m_stopState = 20;
            break;
        case 20: // Second stage: single cycle only (Zweite Stufe Halten // nur 1 Zyklus)
            o_holdConfirmation = true;
            m_stopState = 30;
            break;
        case 30: // Stopping active (Halten Aktiv)
            o_pBrakeRequestEnable = true;
            o_pBrakeRequest = p_pBrakeHoldPressure;

            if( p_holdRelease || i_accelerator >= 0.1 || i_brakepedal >= 0.1 )
            {
                o_pBrakeRequestEnable = false;
                o_pBrakeRequest = 0;
                m_stopState = 40;
            }
            break;
        case 40: // Exit stopping state: single cycle only (Halten beenden // nur 1 Zyklus)
            o_aBrakeRequest = 0;
            o_aBrakeRequestEnable = false;
            o_holdTransition = false;
            o_holdConfirmation = false;
            m_stopState = 0;
            break;
        default:
            break;
    }

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

