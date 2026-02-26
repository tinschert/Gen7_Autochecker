#ifndef CSUSPENSION_H
#define CSUSPENSION_H
/*!
********************************************************************************
@class CSuspension
@ingroup chassis
@brief simulation of a simple wheel suspension

@author Robert Erhart, ett2si (04.07.2005 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2005-2024. All rights reserved.
********************************************************************************
@remark
@f$ FSuspensionChassis = CSpring \times ( zMax - zSuspension ) - KDamper \times vZsuspension @f$
********************************************************************************
@param[in] i_vZsuspension        [m/s]  vertical velocity at suspension point
@param[in] i_zSuspension         [m]    vertical height at suspension point
********************************************************************************
@param[out] o_FSuspensionChassis [N]    vertical force at suspension point
@param[out] o_FSuspensionWheel   [N]    vertical force at wheel
********************************************************************************
@param[in,out] p_CSpring         [N/m]  spring constant
@param[in,out] p_KDamper         [Ns/m] damping constant
@param[in,out] p_zMax            [m]    maximum spring travel
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CSuspensionDoc
{
    const auto o_FSuspensionChassis = "[N] vertical force at suspension point";
    const auto o_FSuspensionWheel = "[N] vertical force at wheel";

    const auto p_CSpring = "[N/m] spring constant";
    const auto p_KDamper = "[Ns/m] damping constant";
    const auto p_zMax = "[m] maximum spring travel";
}

#include <claraSim/framework/CModule.h>

////*********************************
//// CSuspension
////*********************************
class CSuspension : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CSuspension();
    virtual ~CSuspension();

    //*******************************
    //classes
    //*******************************

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloat> o_FSuspensionChassis;
    CMessageOutput<CFloat> o_FSuspensionWheel;
    /* parameter */
    CMessageParameter<CFloat> p_CSpring;
    CMessageParameter<CFloat> p_KDamper;
    CMessageParameter<CFloat> p_zMax;
private:
    /* input */
    CMessageInput<CFloat> i_vZsuspension;
    CMessageInput<CFloat> i_zSuspension;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& vZsuspension,
               IMessage<CFloat>& zSuspension );
private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
};

#endif // CSUSPENSION_H
