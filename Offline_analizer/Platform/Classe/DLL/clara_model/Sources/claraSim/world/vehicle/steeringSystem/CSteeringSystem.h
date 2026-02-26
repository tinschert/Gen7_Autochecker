#ifndef _CSTEERINGSYSTEM_H_
#define _CSTEERINGSYSTEM_H_
/*!
********************************************************************************
@class CSteeringSystem
@ingroup steeringSystem
@brief calculation of the front and rear wheel angle from angle steering wheel

@author Robert Erhart, ett2si (13.04.2005 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2005-2024. All rights reserved.
********************************************************************************
@remark
- steering transmission
    + linear (change to table see todo) \n
@f$
a_o = a_i / i_s
@f$

- lateral actuator model (beta)
@dot
 digraph steeringModel
 {
     node [shape=box; fontsize=12;];
     edge [fontsize=10;];
     rankdir="LR";
     {
         node[shape=plaintext;style=invis];
         in -> 1 -> 2 ->3 ->4 -> 5 ->6 -> out [style=invis]
     }
     subgraph "cluster_input" {label = "Input"; M;};
     subgraph "cluster_kinetics" {label = "Kinetics"; steeringActuator;};
     M -> steeringActuator;
     steeringActuator -> sum [label="+"];
     sum [label="+";shape=circle];
     {rank=same; 2; sum; restoringTorque}
     subgraph "cluster_dynamic" {label = "Dynamic"; rotationEquation -> Integration1 -> Integration2; rotationEquation [label="1/J"];};
     sum -> rotationEquation;
     Integration2 -> steeringAngle
     restoringTorque -> sum [label="-"];
     {rank=same; 6; chassis-> steeringAngle [dir=back]};
     chassis -> restoringTorque [label="Wheel lateral force"];
     {rank=same; out; output;};
     steeringAngle -> output;
 }
@enddot

- steering actuator
    + PT1 Function over the nominal moment \n
@f$
  G(s) = K/(T*s +1)
@f$

- restoring torque
    + assumption: constant pneumatic trail \n
@f$
 M = F_l * n \\
 n = n_c + n_w \\
 F_l: lateralWheelForce \\
 n_c: constructiveTrail \\
 n_w: wheelTrail \\
@f$

********************************************************************************
@param[in] i_angleSteeringWheel          [rad]   steering wheel angle

@param[in] i_velocity                    [m/s]   car velocity (vehicle coordinate system)
@param[in] i_FLateralWheelLeftFront      [N]     constructive lateral force left front wheel (wheel coordinate system)
@param[in] i_RvFLateralWheelLeftFront    [N]     destructive lateral force left front wheel (wheel coordinate system)
@param[in] i_FLateralWheelRightFront     [N]     constructive lateral force right front wheel (wheel coordinate system)
@param[in] i_RvFLateralWheelRightFront   [N]     destructive lateral force right front wheel (wheel coordinate system)
********************************************************************************
@param[out] o_angleWheelFront            [rad]   front wheel angle (chassis axis)
@param[out] o_angleWheelRear             [rad]   rear wheel angle  (chassis axis)
@param[out] o_angleSteeringWheelVelocity [rad/s] angle steering wheel velocity
@param[out] o_angleSteeringWheel         [rad]   angle steering wheel
@param[out] o_MRestoring                 [Nm]    restoring torque front wheel
@param[out] o_MActuator                  [Nm]    actuator torque front wheel
********************************************************************************
@param[in,out] p_iSteeringTransmission   []      steering system ratio
@param[in,out] p_angleWheelFrontMax      [rad]   max. wheel angle front
@param[in,out] p_angleWheelFrontMin      [rad]   min. wheel angle front

@param[in,out] p_TSteeringActuator       [s]     PT1 time constant for steering actuator (new value only used after init)
@param[in,out] p_trail                   [m]     sum of pneumatic trail and constructive trail
@param[in,out] p_JInertiaTorque          [kgm²]  inertia torque of the steering system
@param[in,out] p_MActuatorRequest        [Nm]    requested current nominal torque for steering actuator
@param[in,out] p_MActuatorRequestEnable  [bool]  enable requested current nominal torque for steering actuator
********************************************************************************
@todo Currently, a constant transmission is used -> variable transmission over steering wheel angle?
@todo Different wheel angle left and right
@todo Steering wheel in dashboard not influenced by actuator
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CSteeringSystemDoc
{
    const auto o_angleWheelFront = "[rad] front wheel angle (chassis axis)";
    const auto o_angleWheelRear = "[rad] rear wheel angle (chassis axis)";
    const auto o_angleSteeringWheelVelocity = "[rad/s] angle steering wheel velocity";
    const auto o_angleSteeringWheel = "[rad] angle steering wheel";
    const auto o_MRestoring = "[Nm] restoring torque front wheel";
    const auto o_MActuator = "[Nm] actuator torque front wheel";
    const auto p_iSteeringTransmission = "steering system ratio";
    const auto p_angleWheelFrontMax = "[rad] max. wheel angle front";
    const auto p_angleWheelFrontMin = "[rad] min. wheel angle front";
    const auto p_TSteeringActuator = "[s] PT1 time constant for steering actuator";
    const auto p_trail = "[m] sum of pneumatic trail and constructive trail";
    const auto p_JInertiaTorque = "[kgm²] interia torque of the steering system";
    const auto p_MActuatorRequest = "[Nm] Requested current nominal torque for steering actuator";
    const auto p_MActuatorRequestEnable = "[bool] Enable requested current nominal torque for steering actuator";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/framework/CLowPass.h>

////*********************************
//// CSteeringSystem
////*********************************
class CSteeringSystem : public CModule<2>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CSteeringSystem();
    virtual ~CSteeringSystem();

    //*******************************
    //classes
    //*******************************
public:
    enum { RHORATE, RHO, NumberOfStates};
private:
    CLowPass LowPassActuator;

    //*******************************
    //messages
    //*******************************
public:
    CMessageOutput<CFloat> o_angleWheelFront;
    CMessageOutput<CFloat> o_angleWheelRear;
    CMessageOutput<CFloat> o_angleSteeringWheelVelocity;
    CMessageOutput<CFloat> o_angleSteeringWheel;
    CMessageOutput<CFloat> o_MRestoring;
    CMessageOutput<CFloat> o_MActuator;

    CMessageParameter<CFloat> p_iSteeringTransmission;
    CMessageParameter<CFloat> p_angleWheelFrontMax;
    CMessageParameter<CFloat> p_angleWheelFrontMin;
    CMessageParameter<CFloat> p_TSteeringActuator;
    CMessageParameter<CFloat> p_trail;
    CMessageParameter<CFloat> p_JInertiaTorque;
    CMessageParameter<CFloat> p_MActuatorRequest;
    CMessageParameter<CBool> p_MActuatorRequestEnable;

private:
    CMessageInput<CFloat> i_angleSteeringWheel;
    CMessageInput<CFloat> i_velocity;
    CMessageInput<CFloat> i_FLateralWheelLeftFront;
    CMessageInput<CFloat> i_RvFLateralWheelLeftFront;
    CMessageInput<CFloat> i_FLateralWheelRightFront;
    CMessageInput<CFloat> i_RvFLateralWheelRightFront;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_angleSteeringWheel,
               IMessage<CFloat>& f_velocity,
               IMessage<CFloat>& f_FLateralWheelLeftFront,
               IMessage<CFloat>& f_RvFLateralWheelLeftFront,
               IMessage<CFloat>& f_FLateralWheelRightFront,
               IMessage<CFloat>& f_RvFLateralWheelRightFront );
private:
    void calcPre( CFloat f_dT, CFloat f_time );
    CFloatVector& ddt( CFloatVector& state );
    void calcPost( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
private:
    CFloat m_angleSteeringWheel_K1;
    CFloat m_MSteering;
};

#endif //_CSTEERINGSYSTEM_H_
