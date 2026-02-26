#ifndef CKineticsVertical_H
#define CKineticsVertical_H
/*!
********************************************************************************
@class CKineticsVertical
@ingroup chassis
@brief vertical car kinetics

@author Robert Erhart, ett2si (04.07.2005 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2005-2024. All rights reserved.
********************************************************************************
@remark
- restriction: suspension point is in the area of x-y axis and centre-of-gravity
********************************************************************************
@param[in] i_angleRollPitchYaw  [rad]       roll, pitch and yaw angle
@param[in] i_rateRollPitchYaw   [rad/s]     roll, pitch and yaw angular velocity
@param[in] i_zChassis           [m]         centre-of-gravity height
@param[in] f_vChassis          [m/s]        centre-of-gravity velocity (only Z used)
@param[in] i_x                  [m]         x suspension position
@param[in] i_y                  [m]         y suspension position
********************************************************************************
@param[out] o_vZsuspension      [m/s]       vertical velocity at suspension point
@param[out] o_zSuspension       [m]         vertical height at suspension point
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CKineticsVerticalDoc
{
    const auto o_vZsuspension = "[m/s] vertical velocity at suspension point";
    const auto o_zSuspension = "[m] vertical height at suspension point";
}

#include <claraSim/framework/CModule.h>

////*********************************
//// CKineticsVertical
////*********************************
class CKineticsVertical : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CKineticsVertical();
    virtual ~CKineticsVertical();

    //*******************************
    //classes
    //*******************************

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloat> o_vZsuspension;
    CMessageOutput<CFloat> o_zSuspension;
private:
    /* input */
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYawSuspension;
    CMessageInput<CFloatVectorXYZ> i_rateRollPitchYawChassis;
    CMessageInput<CFloat> i_zChassis;
    CMessageInput<CFloatVectorXYZ> i_vChassis;
    CMessageInput<CFloat> i_x;
    CMessageInput<CFloat> i_y;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSuspension,
               IMessage<CFloatVectorXYZ>& f_rateRollPitchYawChassis,
               IMessage<CFloat>& f_zChassis,
               IMessage<CFloatVectorXYZ>& f_vChassis,
               IMessage<CFloat>& f_x,
               IMessage<CFloat>& f_y );
private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
};

#endif // CKineticsVertical_H
