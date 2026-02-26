#ifndef CKINETICS_H
#define CKINETICS_H
/*!
********************************************************************************
@class CKinetics
@ingroup chassis
@brief simulation of two track car kinetics

@author Robert Erhart, ett2si (12.10.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
********************************************************************************
@remark

********************************************************************************
@param[in] i_vVehicle         [m/s]   (vector) X,Y,Z velocities at the centre of gravity (vehicle coordinate system)
@param[in] i_rateRollPitchYaw [rad/s] (vector) roll rate, pitch rate, yaw rate
@param[in] i_wheelAngle       [rad]   steered wheel angle
@param[in] i_x                [m]     longitudinal wheel position
@param[in] i_y                [m]     lateral wheel position
********************************************************************************
@param[out] o_alpha     [rad]   tire slip angle
@param[out] o_vXwheel   [m/s]   longitudinal wheel velocity (wheel coordinate-system)
@param[out] o_vYwheel   [m/s]   lateral wheel velocity (wheel coordinate-system)
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CKineticsDoc
{
    const auto o_alpha = "[rad] tire slip angle";
    const auto o_vXwheel = "[m/s] longitudinal wheel velocity (wheel coordinate-system)";
    const auto o_vYwheel = "[m/s] lateral wheel velocity (wheel coordinate-system)";
}

#include <claraSim/framework/CModule.h>

////*********************************
//// CKinetics
////*********************************
class CKinetics : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CKinetics();
    virtual ~CKinetics();

    //*******************************
    //classes
    //*******************************

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloat> o_alpha;
    CMessageOutput<CFloat> o_vXwheel;
    CMessageOutput<CFloat> o_vYwheel;
private:
    /* input */
    CMessageInput<CFloatVectorXYZ> i_vVehicle;
    CMessageInput<CFloatVectorXYZ> i_rateRollPitchYaw;
    CMessageInput<CFloat> i_wheelAngle;
    CMessageInput<CFloat> i_x;
    CMessageInput<CFloat> i_y;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloatVectorXYZ>& f_vVehicle,
               IMessage<CFloatVectorXYZ>& f_rateRollPitchYaw,
               IMessage<CFloat>& f_wheelAngle,
               IMessage<CFloat>& f_x,
               IMessage<CFloat>& f_y );
private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
    CFloat m_vX;
    CFloat m_vY;
};

#endif // CKINETICS_H
