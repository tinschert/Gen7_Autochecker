/*******************************************************************************
@author Markus Oenning, om72si (06.03.2007)
@author Andreas Brunner, bnr2lr (02.07.2019)
author (c) Copyright Robert Bosch GmbH 2007-2024. All rights reserved.
*******************************************************************************/

#include "CDriver.h"


/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CDriver::CDriver()
{
    m_roadNetwork_p = nullptr;
    m_x = 0.0, m_y = 0.0, m_z = 0.0, m_x_lateral = 0.0, m_y_lateral = 0, m_dx = 0.0, m_dy = 0.0, m_dz = 0.0;
    m_xTemp = 0.0, m_yTemp = 0.0, m_relativeDist = 0.0,  m_absolutePos = 0.0, m_dLateralOffset = 0.0, m_delta = 0.0;
    m_Kfeedback = 0.0, m_errorSignal = 0.0;
    m_integratedErrorSignal = 0.0;

    /* Initialization messages */
    addMessageParameter( p_vFactor, 0.5, CDriverDoc::p_vFactor );
    addMessageParameter( p_vOffset, 4.0, CDriverDoc::p_vOffset );
    addMessageParameter( p_angleFactor, 18.0, CDriverDoc::p_angleFactor );
    addMessageParameter( p_yawFactor, 30.0, CDriverDoc::p_yawFactor );
    addMessageParameter( p_angleSteeringWheelMax, 2 * M_PI, CDriverDoc::p_angleSteeringWheelMax );
    addMessageParameter( p_vDriver, 0, CDriverDoc::p_vDriver );
    addMessageParameter( p_Tintegration, 7.0, CDriverDoc::p_Tintegration );
    addMessageParameter( p_Kfeedback, 0.5, CDriverDoc::p_Kfeedback );
    addMessageParameter( p_brakepedalStandstill, 0.15, CDriverDoc::p_brakepedalStandstill );

    addMessageInput( i_velocity, 0 );
    addMessageInput( i_vChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_m, 0 );
    addMessageInput( i_rWheel, 0.33 );
    addMessageInput( i_Mmax, 1000.0 );
    addMessageInput( i_xyzWorld, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_angleRollPitchYaw, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_coursePosition, 0 );
    addMessageInput( i_lateralOffset, 0 );
    addMessageInput( i_targetLateralOffset, 0 );
    addMessageInput( i_lateralVelocity, 0 );
    addMessageInput( i_staticSimulation, false );
    addMessageInput( i_road, 0 );
    addMessageInput( i_lane, 0 );
    addMessageInput( i_angleSteeringWheel, 0 );
    addMessageInput( i_angleSteeringWheelAuto, true );
    addMessageInput( i_acceleratorAuto, false );
    addMessageInput( i_brakepedalAuto, false );

    addMessageOutput( o_angleSteeringWheel, 0.0, CDriverDoc::o_angleSteeringWheel );
    addMessageOutput( o_accelerator, 0.0, CDriverDoc::o_accelerator );
    addMessageOutput( o_brakepedal, 0.0, CDriverDoc::o_brakepedal );
    addMessageOutput( o_MDriverRequest, 0.0, CDriverDoc::o_MDriverRequest );
}

CDriver::~CDriver()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CDriver::init( IMessage<CFloat>& f_velocity,
                    IMessage<CFloatVectorXYZ>& f_vChassis,
                    IMessage<CFloat>& f_m,
                    IMessage<CFloat>& f_rWheel,
                    IMessage<CFloat>& f_Mmax,
                    IMessage<CFloatVectorXYZ>& f_xyzWorld,
                    IMessage<CFloatVectorXYZ>& f_angleRollPitchYaw,
                    IMessage<CFloat>& f_coursePosition,
                    IMessage<CInt>& f_road,
                    IMessage<CInt>& f_lane,
                    IMessage<CFloat>& f_lateralOffset,
                    IMessage<CFloat>& f_targetLateralOffset,
                    IMessage<CFloat>& f_lateralVelocity,
                    CRoadNetwork& f_roadNetwork_r,
                    IMessage<CBool>& f_staticSimulation,
                    IMessage<CFloat>& f_angleSteeringWheel,
                    IMessage<CBool>& f_angleSteeringWheelAuto,
                    IMessage<CBool>& f_acceleratorAuto,
                    IMessage<CBool>& f_brakepedalAuto )
{
    /* Connect input with internal variables */
    i_velocity.link( f_velocity );
    i_vChassis.link( f_vChassis );
    i_m.link( f_m );
    i_rWheel.link( f_rWheel );
    i_Mmax.link( f_Mmax );
    i_xyzWorld.link( f_xyzWorld );
    i_angleRollPitchYaw.link( f_angleRollPitchYaw );
    i_coursePosition.link( f_coursePosition );
    i_lateralOffset.link( f_lateralOffset );
    i_targetLateralOffset.link( f_targetLateralOffset );
    i_lateralVelocity.link( f_lateralVelocity );
    i_staticSimulation.link( f_staticSimulation );
    i_angleSteeringWheel.link( f_angleSteeringWheel );
    i_angleSteeringWheelAuto.link( f_angleSteeringWheelAuto );
    i_acceleratorAuto.link( f_acceleratorAuto );
    i_brakepedalAuto.link( f_brakepedalAuto );

    m_roadNetwork_p = &f_roadNetwork_r;

    i_road.link( f_road );
    i_lane.link( f_lane );


    /* Initialization messages */
    initializationMessages();

    /* Initialization of internal variables */
    m_y = i_lateralOffset;
    m_dy = i_lateralOffset;

    state[LATERALOFFSET] = i_lateralOffset;
    m_integratedErrorSignal = 0.0;
    m_errorSignal = 0.0;
}

/*------------------*/
/* private methods */
/*------------------*/
void CDriver::calcPre( CFloat f_dT, CFloat f_time )
{
    if( i_coursePosition >= m_roadNetwork_p->roads[i_road].o_lengthOfCourse.get() - 50 )
    {
        // no more steering
    }
    else
    {
        /**************************** Calculate future point *****************************
         * Future point is the position on the track the driver is aiming at.
         * Calculation is based on ego velocity, distance from course and yaw rate.
         *********************************************************************************/
        // m_relativeDist: distance of future point
        m_relativeDist  = i_velocity * p_vFactor + /*::sim::abs( m_delta ) * p_yawFactor +*/ p_vOffset;
        m_relativeDist  = ::sim::sig( i_vChassis.X() ) * m_relativeDist;
        // m_absolutePos: absolute 'future point' position on the track
        CFloat m_absolutePos =  i_coursePosition + m_relativeDist;

        // Get x,y,z positions (m_x etc.) of future point and distance relative to ego (m_dx etc.).
        m_roadNetwork_p->roads[i_road].lanes[i_lane].CourseLine.getXYZ( m_absolutePos,
                                                                        m_x, m_y, m_z,
                                                                        m_dx, m_dy, m_dz );
        // Get lateral positions of future point
        m_x_lateral = m_x -  state[LATERALOFFSET] * m_dy / sqrt( m_dx * m_dx + m_dy * m_dy );
        m_y_lateral = m_y +  state[LATERALOFFSET] * m_dx / sqrt( m_dx * m_dx + m_dy * m_dy );


        /***************************** Calculate delta angle *******************************
         * Calculate angle between ego direction of movement and future point.
         *********************************************************************************/
        m_xTemp = m_x_lateral - i_xyzWorld.X() ;
        m_yTemp = m_y_lateral - i_xyzWorld.Y() ;
        // avoid division by zero
        if( ::sim::abs( m_xTemp ) < 0.001 ) m_xTemp = ::sim::sig( m_xTemp ) * 0.001;
        // calculate delta angle
        m_delta = atan( m_yTemp / m_xTemp );
        // correct negative angle and
        if( m_xTemp < 0 ) m_delta += M_PI;

        if( i_vChassis.X() >= 0 )    // forward driving
        {
            m_delta = m_delta - i_angleRollPitchYaw.Z();
        }
        else    // reverse driving
        {
            m_delta = M_PI + i_angleRollPitchYaw.Z() - m_delta;
        }

        // bring m_delta to intervall [-pi, pi]
        m_delta = ::sim::fmod( m_delta, 2 * M_PI );
        if( ::sim::abs( m_delta ) > M_PI ) m_delta -= ::sim::sign_of( m_delta ) * 2 * M_PI;

        // calc steering angle
        //  - if <1/100 degrees: set zero (1/100 Grad Hysterese)
        //  - else: limit to allowed range
        if( i_angleSteeringWheelAuto )
        {
            o_angleSteeringWheel = ( ::sim::abs( m_delta ) < ( M_PI / 180 / 100 ) )
                                   ? 0
                                   : ::sim::limit( m_delta * p_angleFactor, -p_angleSteeringWheelMax, +p_angleSteeringWheelMax );
        }
        else
        {
            o_angleSteeringWheel.init( i_angleSteeringWheel );
        }

    }
}

CFloatVector& CDriver::ddt( CFloatVector& state )
{
    if( i_staticSimulation == false )
    {
        /* Move to target lateral value with lateral velocity.
         * Note that i_lateralVelocity (=vehicle.p_lateralVelocity) is an interface
         *  to be filled externally, it is not set inside claraSim.  */

        m_dLateralOffset = i_targetLateralOffset - state[LATERALOFFSET];
        if( ::sim::abs( m_dLateralOffset ) > 0.001 )
        {
            ddtState[LATERALOFFSET] = ::sim::sign_of( m_dLateralOffset ) * i_lateralVelocity;
            //o_yVelocity = i_lateralVelocity;
        }
        else
        {
            ddtState[LATERALOFFSET] = 0;
            //o_yVelocity = 0;
            state[LATERALOFFSET] = i_targetLateralOffset;
        }
    }
    else    // static simulation
    {
        ddtState[input] = 0;
        ddtState[LATERALOFFSET] = 0;
    }

    return ddtState;
}

void CDriver::calcPost( CFloat f_dT, CFloat f_time )
{
    if( i_staticSimulation == false )
    {
        ///////////////////////////////////////////////////////////////////////
        // calculate feedback signal output: o_MDriverRequest
        ///////////////////////////////////////////////////////////////////////

        if( i_acceleratorAuto == true || i_brakepedalAuto == true ) // driver active
        {
            // unit conversion: p_Kfeedback [acceleration] --> m_Kfeedback [torque]
            m_Kfeedback         = i_m * i_rWheel * p_Kfeedback;
            m_errorSignal       = p_vDriver - i_velocity;
            o_MDriverRequest    = m_Kfeedback * ( m_errorSignal + m_integratedErrorSignal );
            // update error integral
            m_integratedErrorSignal += m_errorSignal * f_dT / p_Tintegration;
            m_integratedErrorSignal = ::sim::limit( m_integratedErrorSignal, -i_Mmax / m_Kfeedback, +i_Mmax / m_Kfeedback );
        }
        else // driver NOT active: reset error integral, set outputs to zero
        {
            o_MDriverRequest = 0.0;
            o_accelerator = 0.0;
            o_brakepedal = 0.0;
            m_integratedErrorSignal = 0.0;  // inactive driver -> feedback loop not closed -> don't accumulate error integral
        }

        ///////////////////////////////////////////////////////////////////////
        // transform o_MDriverRequest to accelerator and brakepedal output
        ///////////////////////////////////////////////////////////////////////

        // Discriminate braking / acceleration
        if( o_MDriverRequest < 0.0 ) // brake
        {
            o_accelerator = 0.0;
            // Brake torque is proportional to brake pressure. Brake pressure is proportional to i_brakepedal^2.
            // --> o_brakepedal ~ sqrt( Mbrake )
            o_brakepedal  = ::sim::sqrt( ::sim::limit( -o_MDriverRequest / i_Mmax, 0.0, 1.0 ) );
            // TODO: normalize torque to maximum !brake! force, not engine Mmax
        }
        else // accelerate
        {
            o_MDriverRequest = ::sim::limit( o_MDriverRequest, 0.0, i_Mmax );
            o_accelerator = 1 - ::sim::sqrt( 1 - o_MDriverRequest / i_Mmax );
            o_brakepedal = 0.0;
        }

        // If target velocity is zero:
        // Map near-zero velocity and low brakepedal value to "standstill regime"
        if( p_vDriver == 0.0 && i_brakepedalAuto == true && i_velocity <= 0.3 ) // TODO: Switch from fixed 0.3 to dependency on cycle time and control parameter
        {
            o_MDriverRequest = 0.0;
            o_accelerator = 0.0;
            o_brakepedal = p_brakepedalStandstill;
            // TODO: Driver is not controlling gear. We're not switching to gear zero in standstill.
            //       So, idle acceleration is still present (but overcompensated by brakepedal action)
        }
    }
}

