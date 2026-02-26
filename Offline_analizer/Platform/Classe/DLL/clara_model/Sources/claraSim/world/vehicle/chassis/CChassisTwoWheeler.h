#ifndef CChassisTwoWheeler_H
#define CChassisTwoWheeler_H

/*!
********************************************************************************
@class CChassisTwoWheeler
@ingroup chassis
@brief motorbike chassis with front wheel steering and vertical dynamic

@author Robert Erhart, ett2si (23.06.2005 - 00:00:00)
@author Andreas Brunner, bnr2lr (17.07.2019)
@copyright (c) Robert Bosch GmbH 2019-2024. All rights reserved.
********************************************************************************
@remark
Initialization of motorbike parameter
- motorbike definition
@verbatim
            front
               0
               ^ x
               |
               |
       y <-----. Center of Gravity (h = height over the street)
               |
               |
               0
             rear
@endverbatim
********************************************************************************
@param[in] i_wheelAngleFront    [rad]   steered wheel angle
@param[in] i_MWheelFront        [Nm]    drive (constructive) torque wheel -front
@param[in] i_MWheelRear         [Nm]    drive (constructive) torque wheel -rear
@param[in] i_RvMWheelFront      [Nm]    brake (destructive) torque wheel -front
@param[in] i_RvMWheelRear       [Nm]    brake (destructive) torque wheel -rear
@param[in] i_angleRollPitchYawSurface [rad] pitch angle vehicle coordinate system (positiv: right handed)
@param[in] i_setRollAngle       [rad]   roll angle vehicle coordinate system (positiv: right handed)
@param[in] i_FxyzArticulation   [N]     articulation x,y,z force vector (input from coupled chassis, in this chassis' coordinate system)
@param[in] i_staticSimulation   [bool]  switch between static and dynamic mode
********************************************************************************
@param[out] o_beta              [rad]   sideslip angle
@param[out] o_velocity          [m/s]   car velocity
@param[out] o_vChassis          [m/s]   car velocity vector car coordinate system
@param[out] o_yawRate           [rad/s] yaw velocity
@param[out] o_nWheelFront       [U/min] wheel rpm -front
@param[out] o_nWheelRear        [U/min] wheel rpm -rear
@param[out] o_camberAngle       [rad]   tire camber angle
********************************************************************************
- horizontal dynamic
@param[in,out] p_xWheelFront    [m]     x wheel suspension position front (vehicle coordinate system)
@param[in,out] p_yWheelFront    [m]     y wheel suspension position front (vehicle coordinate system)
@param[in,out] p_xWheelRear     [m]     x wheel suspension position rear (vehicle coordinate system)
@param[in,out] p_yWheelRear     [m]     y wheel suspension position rear (vehicle coordinate system)
@param[in,out] p_h                  [m]     centre-of-gravity height over street level
@param[in,out] p_m                  [kg]    vehicle mass
@param[in,out] p_myFront        [-]     fricton factor wheel-street -front
@param[in,out] p_myRear         [-]     fricton factor wheel-street -rear
-vertical dynamic
@param[in,out] p_Jroll              [kg m²] moment of inertia X-axis (roll)
@param[in,out] p_Jpitch             [kg m²] moment of inertia Y-axis (pitch)
@param[in,out] p_JRollPitchYaw      [kg m²] DUPLICATE: moment of inertia vector (X,Y,Z axis)
-configuration
@param[in,out] p_wheelAngleRear     [rad]   wheel angle rear (default: 0); simulate error
-articulation
@param[in,out] p_xyzArticulation    [m]     articulation x,y,z position vector (vehicle coordinate system)
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CChassisTwoWheelerDoc
{
    const auto o_beta               = "[rad] sideslip angle";
    const auto o_velocity           = "[m/s] car velocity";
    const auto o_vChassis           = "[m/s] car velocity vector car coordinate system";
    const auto o_yawRate            = "[rad/s] yaw velocity";
    const auto o_nWheelFront        = "[U/min] wheel rpm -front";
    const auto o_nWheelRear         = "[U/min] wheel rpm -rear";
    const auto o_camberAngle        = "[rad] tire camber angle";

    const auto p_xWheelFront    = "[m] x wheel suspension position front (vehicle coordinate system)";
    const auto p_yWheelFront    = "[m] y wheel suspension position front (vehicle coordinate system)";
    const auto p_xWheelRear     = "[m] x wheel suspension position rear (vehicle coordinate system)";
    const auto p_yWheelRear     = "[m] y wheel suspension position rear (vehicle coordinate system)";
    const auto p_h                  = "[m] centre-of-gravity height over street level";
    const auto p_m                  = "[kg] vehicle mass";
    const auto p_JRollPitchYaw      = "[kg m²] moment of inertia vector (X,Y,Z axis)";
    const auto p_myFront        = "[-] fricton factor wheel-street -front";
    const auto p_myRear         = "[-] fricton factor wheel-street -rear";
    const auto p_wheelAngleRear     = "[rad] wheel angle rear (default: 0); simulate error";
    const auto p_xyzArticulation    = "[m] articulation x,y,z position vector (vehicle coordinate system)";
}

#include <claraSim/framework/CModule.h>
#include "CAirResistance.h"
#include "CDynamic.h"
#include "CKinetics.h"
#include "CStaticTwoWheeler.h"
#include "CSuspension.h"
#include "CKineticsVertical.h"
#include "CWheel.h"

////*********************************
//// CChassisTwoWheeler
////*********************************
class CChassisTwoWheeler : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CChassisTwoWheeler();
    virtual ~CChassisTwoWheeler();

    //*******************************
    //classes
    //*******************************
public:
    CKinetics kineticsFront;
    CKinetics kineticsRear;
    CWheel wheelFront;
    CWheel wheelRear;
    CAirResistance airResistance;
    CStaticTwoWheeler staticTwoWheeler;
    CDynamic dynamic;
    CKineticsVertical kineticsVerticalFront;
    CKineticsVertical kineticsVerticalRear;
    CSuspension suspensionFront;
    CSuspension suspensionRear;

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloat> o_beta;
    CMessageOutput<CFloat> o_velocity;
    CMessageOutput<CFloatVectorXYZ> o_vChassis;
    CMessageOutput<CFloat> o_yawRate;
    CMessageOutput<CFloat> o_nWheelFront;
    CMessageOutput<CFloat> o_nWheelRear;
    CMessageOutput<CFloat> o_camberAngle;

    /* parameter */
    CMessageParameter<CFloat> p_xWheelFront;
    CMessageParameter<CFloat> p_yWheelFront;
    CMessageParameter<CFloat> p_xWheelRear;
    CMessageParameter<CFloat> p_yWheelRear;
    CMessageParameter<CFloat> p_h;
    CMessageParameter<CFloat> p_m;
    CMessageParameter<CFloat> p_myFront;
    CMessageParameter<CFloat> p_myRear;
    //vertical dynamic
    CMessageParameter<CFloatVectorXYZ> p_JRollPitchYaw;
    CMessageParameter<CFloat> p_wheelAngleRear;
    // articulation
    CMessageParameter<CFloatVectorXYZ> p_xyzArticulation;
private:
    /* Input */
    CMessageInput<CFloat> i_wheelAngleFront;
    CMessageInput<CFloat> i_MWheelFront;
    CMessageInput<CFloat> i_MWheelRear;
    CMessageInput<CFloat> i_RvMWheelFront;
    CMessageInput<CFloat> i_RvMWheelRear;
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYawSurface;
    CMessageInput<CFloat> i_setRollAngle;
    CMessageInput<CFloatVectorXYZ> i_FxyzArticulation;
    CMessageInput<CBool> i_staticSimulation;

    // input via internal modules (documentation only here)
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYawSuspension; // [rad] (roll,pitch,yaw) angle vector of the chassis ; dynamic.o_angleRollPitchYawSuspension
    CMessageInput<CFloat> i_beta;                   // [rad] sideslip angle ; dynamic.o_beta
    CMessageInput<CFloat> i_velocity;               // [m/s] velocity of vehicle ; dynamic.o_velocity
    CMessageInput<CFloatVectorXYZ> i_vChassis;      // [m/s] velocity vector car coordinate-system ; dynamic.o_vChassis
    CMessageInput<CFloatVectorXYZ> i_rateRollPitchYawChassis;    // [rad/s] (vector) roll, pitch, and yaw rate at the centre of gravity (chassis coordinate system) ; dynamic.o_rateRollPitchYawChassis;
    CMessageInput<CFloat> i_nWheelFront;       // [rpm] wheel rpm wheelFront ; o_nWheel
    CMessageInput<CFloat> i_nWheelRear;        // [rpm] wheel rpm wheelRear ; o_nWheel

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_wheelAngleFront,
               IMessage<CFloat>& f_MWheelFront,
               IMessage<CFloat>& f_RvMWheelFront,
               IMessage<CFloat>& f_MWheelRear,
               IMessage<CFloat>& f_RvMWheelRear,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSurface,
               IMessage<CFloat>& f_setRollAngle,
               IMessage<CFloatVectorXYZ>& f_FxyzArticulation,
               IMessage<CBool>& f_staticSimulation );
private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
};

#endif // CChassisTwoWheeler_H
