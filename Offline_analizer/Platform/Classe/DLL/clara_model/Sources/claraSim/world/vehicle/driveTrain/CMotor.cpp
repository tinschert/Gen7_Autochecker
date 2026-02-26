/*******************************************************************************
author Robert Erhart, ett2si (06.11.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004-2024. All rights reserved.
*******************************************************************************/

#include "CMotor.h"


/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CMotor::CMotor()
{
    /* Initialization low pass */
    lowPass.setInit( 0.5, 0.05, 1 );

    /* Initialization messages */
    addMessageInput( i_accelerator, 0.0 );
    addMessageInput( i_nTransmission, 0.0 );
    addMessageInput( i_MtorqueRequest, 0.0 );
    addMessageInput( i_MtorqueRequestEnable, false );
    addMessageInput( i_sailingRequest, false );

    addMessageParameter( p_nTargetIdleEngine, 600, CMotorDoc::p_nTargetIdleEngine );
    addMessageParameter( p_engineRunning, true, CMotorDoc::p_engineRunning );
    addMessageParameter( p_mdNorm, 600.0, CMotorDoc::p_mdNorm );
    addMessageParameter( p_MtorqueRequest, 0.0, CMotorDoc::p_MtorqueRequest );
    addMessageParameter( p_MtorqueRequestEnable, false, CMotorDoc::p_MtorqueRequestEnable );
    addMessageParameter( p_MengineDriverGradient, std::numeric_limits<CFloat>::max(), CMotorDoc::p_MengineDriverGradient );

    addMessageOutput( o_nEngine, 600.0, CMotorDoc::o_nEngine );
    addMessageOutput( o_MfrictionTorque, 0.0, CMotorDoc::o_MfrictionTorque );
    addMessageOutput( o_MengineIdleRequest, 0.0, CMotorDoc::o_MengineIdleRequest );
    addMessageOutput( o_MengineTorqueInd, 0.0, CMotorDoc::o_MengineTorqueInd );
    addMessageOutput( o_MengineTorque, 0.0, CMotorDoc::o_MengineTorque );
    addMessageOutput( o_MengineTorqueDesired, 0.0, CMotorDoc::o_MengineTorqueDesired );
    addMessageOutput( o_MengineTorqueDriver, 0.0, CMotorDoc::o_MengineTorqueDriver );
    addMessageOutput( o_Mmax, 1000.0, CMotorDoc::o_Mmax );
    addMessageOutput( o_Mmin, 0.0, CMotorDoc::o_Mmin );
    addMessageOutput( o_driverOverride, false, CMotorDoc::o_driverOverride );

    m_MdriverRequest = 0;
    m_torqueRequested = 0;
    m_MengineInterfaceRequest = 0;

}
CMotor::~CMotor()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CMotor::init( IMessage<CFloat>& f_accelerator,
                   IMessage<CFloat>& f_nTransmission,
                   IMessage<CFloat>& f_MtorqueRequest,
                   IMessage<CBool>&  f_MtorqueRequestEnable,
                   IMessage<CBool>&  f_sailingRequest )
{
    /* connect input with internal variables */
    i_accelerator.link( f_accelerator );
    i_nTransmission.link( f_nTransmission );
    i_MtorqueRequest.link( f_MtorqueRequest );
    i_MtorqueRequestEnable.link( f_MtorqueRequestEnable );

    i_sailingRequest.link( f_sailingRequest );

    /* Initialization messages */
    initializationMessages();

    // Initialization maxMdInd table */
    CFloat x1[] = {0, 400, 1000, 2000, 3000, 4000, 5000, 6000, 10000, 12000};
    CFloat y1[] = {0, 0.68, 0.82, 0.91,  0.94,  0.97,  1.00,  0.97,  0.82,  0};
    maxMdInd.init( 10, x1, y1, 0 );
    // Initialization MDrag table */
    CFloat y2[] = {0, 30, 35, 40,  45,  50,  55,  60,  65,  70};
    MDrag.init( 10, x1, y2, 0 );

    /* Re-Initialization depended messages */
    o_MfrictionTorque.init( MDrag.get( o_nEngine ) );
    o_MengineIdleRequest.init( nIdleController( p_nTargetIdleEngine, o_nEngine, o_MfrictionTorque ) );
    o_MengineTorqueInd.init( o_MengineIdleRequest );
    o_MengineTorque.init( o_MengineIdleRequest - o_MfrictionTorque );
    o_MengineTorqueDesired.init( o_MengineIdleRequest );

    /* init classes */
    lowPass.init( o_MengineTorqueInd );
    m_MdriverRequest = 0;
    m_torqueRequested = 0;
    m_MengineInterfaceRequest = 0;
}

/*------------------*/
/* private methods */
/*------------------*/
void CMotor::calc( CFloat f_dT, CFloat f_time )
{
    if( p_engineRunning )
    {
        /* nEngine */
        o_nEngine = i_nTransmission;

        /* MfrictionTorque */
        o_MfrictionTorque = MDrag.get( o_nEngine );

        /* nIdleController */
        o_MengineIdleRequest = nIdleController( p_nTargetIdleEngine, o_nEngine, o_MfrictionTorque );

        /* torque min */
        o_Mmin = -o_MfrictionTorque + o_MengineIdleRequest;

        /* torque max */
        o_Mmax = maxMdInd.get( o_nEngine ) * p_mdNorm;

        // Now, compare torque interface requests (p_MtorqueRequest, i_MtorqueRequest) and driver request (i_accelerator).
        // 1) Get maximum torque from torque interfaces.
        // 2) Calculate driver torque request from accelerator pedal.
        // 3) Use maximum of 1) and 2), and fill output messages.

        /* 1) MengineInterfaceRequest */
        if( p_MtorqueRequestEnable and i_MtorqueRequestEnable and !i_sailingRequest )
        {
            m_MengineInterfaceRequest = ::sim::max( p_MtorqueRequest, i_MtorqueRequest );
            m_torqueRequested = true;
        }
        else if( p_MtorqueRequestEnable and !i_sailingRequest )
        {
            m_MengineInterfaceRequest = p_MtorqueRequest;
            m_torqueRequested = true;
        }
        else if( i_MtorqueRequestEnable and !i_sailingRequest )
        {
            m_MengineInterfaceRequest = i_MtorqueRequest;
            m_torqueRequested = true;
        }
        else
        {
            m_MengineInterfaceRequest = 0.0;
            m_torqueRequested = false;
        }
        m_MengineInterfaceRequest = ::sim::min( m_MengineInterfaceRequest, o_Mmax );


        // print("m_MengineInterfaceRequest: ",m_MengineInterfaceRequest);


        // 2) MengineDriverRequest
        //
        // Update m_MdriverRequest, but limit change rate to p_MengineDriverGradient
        CFloat l_MdriverRequest     = ::sim::min( p_mdNorm * ( 1.0 - ::sim::pow( 1.0 - i_accelerator, 2 ) ), o_Mmax );
        CFloat l_MdriverMaxDelta    = ::sim::abs( p_MengineDriverGradient * f_dT );

        m_MdriverRequest = ::sim::limit( l_MdriverRequest,  m_MdriverRequest - l_MdriverMaxDelta, m_MdriverRequest + l_MdriverMaxDelta );

        // 3) MengineTorqueDesired output
        //
        // Set to maximum of
        // - idle torque (o_MengineIdleRequest)
        // - driver request (m_MdriverRequest)
        // - interface request (m_MengineInterfaceRequest)

        // Driver vs. idle torque
        o_MengineTorqueDesired = ::sim::max( o_MengineIdleRequest, m_MdriverRequest );

        // ... vs. interface torque request
        if( m_torqueRequested )
        {
            o_MengineTorqueDesired = ::sim::max( o_MengineTorqueDesired, m_MengineInterfaceRequest );

            if( ( m_MdriverRequest > m_MengineInterfaceRequest ) && ( m_MdriverRequest >= 0.01 ) )
            {
                o_driverOverride = true;
            }
            else
            {
                o_driverOverride = false;
            }
        }
        else    // m_torqueRequested == false
        {
            o_driverOverride = ( m_MdriverRequest >= 0.01 ) ? true : false;
        }

        /* current MengineTorque */
        o_MengineTorqueInd = ::sim::min( o_MengineTorqueDesired, o_Mmax );
        o_MengineTorqueInd = lowPass.get( o_MengineTorqueInd, f_dT );

        o_MengineTorque = o_MengineTorqueInd - o_MfrictionTorque;
        o_MengineTorqueDriver = m_MdriverRequest;
    }
    else // p_engineRunning == false
    {
        o_nEngine = i_nTransmission;
        o_MfrictionTorque = MDrag.get( o_nEngine );
        o_MengineTorque = -o_MfrictionTorque;
        o_MengineTorqueInd = 0;
        o_MengineTorqueDesired = 0;
        o_Mmax = 0;
        o_driverOverride = false;
    }
}

CFloat CMotor::nIdleController( CFloat f_nTargetIdleEngine, CFloat f_nEngine, CFloat f_MfrictionTorque )
{
    return ::sim::limit( 0.5 * ( f_nTargetIdleEngine - f_nEngine ), 0.0, f_MfrictionTorque + 50 );
}

