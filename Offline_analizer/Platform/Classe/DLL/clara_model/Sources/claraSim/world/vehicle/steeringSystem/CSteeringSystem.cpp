/*******************************************************************************
author Robert Erhart, ett2si (13.04.2005 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2005-2024. All rights reserved.
*******************************************************************************/

#include "CSteeringSystem.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CSteeringSystem::CSteeringSystem(): CModule<NumberOfStates>(),
    m_angleSteeringWheel_K1( 0 ),
    m_MSteering( 0 )
{
    /* Initialization messages */
    addMessageParameter( p_iSteeringTransmission, 14.0, CSteeringSystemDoc::p_iSteeringTransmission );
    addMessageParameter( p_angleWheelFrontMax, 0.698, CSteeringSystemDoc::p_angleWheelFrontMax );  //~40°
    addMessageParameter( p_angleWheelFrontMin, -0.698, CSteeringSystemDoc::p_angleWheelFrontMin );  //~40°
    addMessageParameter( p_TSteeringActuator, 0.17, CSteeringSystemDoc::p_TSteeringActuator );  //0.17
    addMessageParameter( p_trail, 0.053, CSteeringSystemDoc::p_trail );
    addMessageParameter( p_JInertiaTorque, 4.8, CSteeringSystemDoc::p_JInertiaTorque );  //0.048 kgm² orginal value from Thomas Eigel "Integrierte Längs- und Querführung.." 2010
    addMessageParameter( p_MActuatorRequest, 0.0, CSteeringSystemDoc::p_MActuatorRequest );
    addMessageParameter( p_MActuatorRequestEnable, false, CSteeringSystemDoc::p_MActuatorRequestEnable );

    addMessageOutput( o_angleWheelFront, 0.0, CSteeringSystemDoc::o_angleWheelFront );
    addMessageOutput( o_angleWheelRear, 0.0, CSteeringSystemDoc::o_angleWheelRear );
    addMessageOutput( o_angleSteeringWheelVelocity, 0.0, CSteeringSystemDoc::o_angleSteeringWheelVelocity );
    addMessageOutput( o_angleSteeringWheel, 0.0, CSteeringSystemDoc::o_angleSteeringWheel );
    addMessageOutput( o_MRestoring, 0.0, CSteeringSystemDoc::o_MRestoring );
    addMessageOutput( o_MActuator, 0.0, CSteeringSystemDoc::o_MActuator );

    addMessageInput( i_angleSteeringWheel, 0.0 );
    addMessageInput( i_velocity, 0.0 );
    addMessageInput( i_FLateralWheelLeftFront, 0.0 );
    addMessageInput( i_RvFLateralWheelLeftFront, 0.0 );
    addMessageInput( i_FLateralWheelRightFront, 0.0 );
    addMessageInput( i_RvFLateralWheelRightFront, 0.0 );
}

CSteeringSystem::~CSteeringSystem()
{}

/*------------------*/
/* public methods   */
/*------------------*/
void CSteeringSystem::init( IMessage<CFloat>& f_angleSteeringWheel,
                            IMessage<CFloat>& f_velocity,
                            IMessage<CFloat>& f_FLateralWheelLeftFront,
                            IMessage<CFloat>& f_RvFLateralWheelLeftFront,
                            IMessage<CFloat>& f_FLateralWheelRightFront,
                            IMessage<CFloat>& f_RvFLateralWheelRightFront )
{
    /* init of internal variables */
    m_angleSteeringWheel_K1 = 0.0;

    /* Connect input with internal variables */
    i_angleSteeringWheel.link( f_angleSteeringWheel );
    i_velocity.link( f_velocity );
    i_FLateralWheelLeftFront.link( f_FLateralWheelLeftFront );
    i_RvFLateralWheelLeftFront.link( f_RvFLateralWheelLeftFront );
    i_FLateralWheelRightFront.link( f_FLateralWheelRightFront );
    i_RvFLateralWheelRightFront.link( f_RvFLateralWheelRightFront );

    /* Initialization messages */
    initializationMessages();

    // init filter a filter time constant; v amplification factor; f_initState
    LowPassActuator.init( p_TSteeringActuator, 1.0, 0.0 );
}

/*------------------*/
/* private methods  */
/*------------------*/
void CSteeringSystem::calcPre( CFloat f_dT, CFloat f_time )
{
    // calculate front wheel angle
    o_angleWheelFront = i_angleSteeringWheel / p_iSteeringTransmission;

    // calculate rear wheel angle
    o_angleWheelRear = 0.0;

    o_angleSteeringWheelVelocity = ( i_angleSteeringWheel - m_angleSteeringWheel_K1 ) / f_dT;
    m_angleSteeringWheel_K1 = i_angleSteeringWheel;

    // restoring torque
    CFloat l_Fy = 0.0;
    if( ::sim::abs( i_velocity ) > 0.01 )
    {
        l_Fy = i_FLateralWheelLeftFront + i_RvFLateralWheelLeftFront + i_FLateralWheelRightFront + i_RvFLateralWheelRightFront;
    }
    o_MRestoring = l_Fy * p_trail;

    // actuator output torque
    if( p_MActuatorRequestEnable )
    {
        o_MActuator = LowPassActuator.get( p_MActuatorRequest, f_dT ) * p_iSteeringTransmission;
    }
    else
    {
        //when activating steering actuator start with current torque and current wheel angle front
        LowPassActuator.get( 0, f_dT ); //o_MActuator override in calcPost
        ddtState[RHORATE] = 0.0;
        state[RHORATE] = 0.0;
        ddtState[RHO] = 0.0;
        state[RHO] = o_angleWheelFront;
    }

    //todo superposition of driver steering torque
    m_MSteering = o_MActuator - o_MRestoring;

}

CFloatVector& CSteeringSystem::ddt( CFloatVector& state )
{
    /* Start    "equation of state */
    ddtState[RHORATE] = m_MSteering / p_JInertiaTorque ;
    ddtState[RHO] = state[RHORATE];
    /* End      "equation of state */
    return ddtState;
}

void CSteeringSystem::calcPost( CFloat f_dT, CFloat f_time )
{
    if( p_MActuatorRequestEnable )
    {
        o_angleWheelFront = ::sim::limit( state[RHO], p_angleWheelFrontMin, p_angleWheelFrontMax );

        if( state[RHO] > p_angleWheelFrontMax or state[RHO] < p_angleWheelFrontMin )
        {
            ddtState[RHORATE] = 0.0;
            state[RHORATE] = 0.0;
            ddtState[RHO] = 0.0;
            state[RHO] = o_angleWheelFront;
        }
        o_angleSteeringWheel = o_angleWheelFront * p_iSteeringTransmission;
    }
    else
    {
        o_MActuator = 0.0;
        o_angleSteeringWheel = i_angleSteeringWheel; // just a back loop from dashboard
        o_angleWheelFront = ::sim::limit( o_angleWheelFront, p_angleWheelFrontMin, p_angleWheelFrontMax );
    }
}

