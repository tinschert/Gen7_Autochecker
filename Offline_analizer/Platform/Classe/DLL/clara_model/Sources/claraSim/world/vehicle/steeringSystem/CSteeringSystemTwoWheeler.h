#ifndef _CSteeringSystemTwoWheeler_H_
#define _CSteeringSystemTwoWheeler_H_
/*!
********************************************************************************
@class CSteeringSystemTwoWheeler
@ingroup steeringSystem
@brief calculation of the front and rear wheel angle from angle steering wheel

@author Robert Erhart, ett2si (13.04.2005 - 00:00:00)
@author Andreas Brunner, bnr2lr (26.07.2019)
@copyright (c) Robert Bosch GmbH 2019-2024. All rights reserved.
********************************************************************************
@remark
- steering transmission = 1
- no actuator (as in car)
- restoring torque from wheel trail not considered (compare car steering model with actuation)

********************************************************************************
@param[in] i_angleSteeringWheel          [rad]   steering wheel angle
********************************************************************************
@param[out] o_angleWheelFront            [rad]   front wheel angle (chassis axis)
@param[out] o_angleWheelRear             [rad]   rear wheel angle  (chassis axis)
@param[out] o_angleSteeringWheelVelocity [rad/s] angle steering wheel velocity
********************************************************************************
@param[in,out] p_angleWheelFrontMax      [rad]   max. wheel angle front
@param[in,out] p_angleWheelFrontMin      [rad]   min. wheel angle front
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CSteeringSystemTwoWheelerDoc
{
    const auto o_angleWheelFront = "[rad] front wheel angle (chassis axis)";
    const auto o_angleWheelRear = "[rad] rear wheel angle (chassis axis)";
    const auto o_angleSteeringWheelVelocity = "[rad/s] angle steering wheel velocity";
    const auto o_angleSteeringWheel = "[rad] current angle steering wheel";

    const auto p_angleWheelFrontMax = "[rad] max. wheel angle front";
    const auto p_angleWheelFrontMin = "[rad] min. wheel angle front";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/framework/CLowPass.h>

////*********************************
//// CSteeringSystemTwoWheeler
////*********************************
class CSteeringSystemTwoWheeler : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CSteeringSystemTwoWheeler();
    virtual ~CSteeringSystemTwoWheeler();

    //*******************************
    //classes
    //*******************************
public:
private:
    //*******************************
    //messages
    //*******************************
public:
    CMessageOutput<CFloat> o_angleWheelFront;
    CMessageOutput<CFloat> o_angleWheelRear;
    CMessageOutput<CFloat> o_angleSteeringWheelVelocity;
    CMessageOutput<CFloat> o_angleSteeringWheel;

    CMessageParameter<CFloat> p_angleWheelFrontMax;
    CMessageParameter<CFloat> p_angleWheelFrontMin;
private:
    CMessageInput<CFloat> i_angleSteeringWheel;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_angleSteeringWheel );
private:
    void calc( CFloat f_dT, CFloat f_time );
    //*******************************
    //variables
    //*******************************
private:
    CFloat m_angleSteeringWheel_K1;
};

#endif //_CSteeringSystemTwoWheeler_H_
