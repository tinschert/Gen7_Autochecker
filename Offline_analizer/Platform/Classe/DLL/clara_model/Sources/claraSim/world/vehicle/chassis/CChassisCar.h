#ifndef CChassisCar_H
#define CChassisCar_H

/*!
********************************************************************************
@class CChassisCar
@ingroup chassis
@brief unibody chassis with front wheel steering and vertical dynamic

@author Robert Erhart, ett2si (23.06.2005 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2005-2024. All rights reserved.
********************************************************************************
@remark
Initialization of car parameters.

Architecturally, CChassisCar defines the car geometry and its movement.
It contains components for kinetics, dynamics, static, air resistance, suspension, and wheels.

Mechanically, the simulation corresponds to a unibody model (unity of frame/chassis + body).
Movement of the body is mediated via suspension from the wheel forces.

- Car definition:
@verbatim
            leftFront    rightFront
               0-----------0
                     ^ x
                     |
                     |
             y <-----. Centre of Gravity (h = height over the street)
                     |
                     |
               o------------o
          leftRear     rightRear
@endverbatim
********************************************************************************
@param[in] i_wheelAngleFront    [rad]   steered wheel angle
@param[in] i_MWheelLeftFront    [Nm]    drive (constructive) torque wheel left-front
@param[in] i_MWheelRightFront   [Nm]    drive (constructive) torque wheel right-front
@param[in] i_MWheelLeftRear     [Nm]    drive (constructive) torque wheel left-rear
@param[in] i_MWheelRightRear    [Nm]    drive (constructive) torque wheel right-rear
@param[in] i_RvMWheelLeftFront  [Nm]    brake (destructive) torque wheel left-front
@param[in] i_RvMWheelRightFront [Nm]    brake (destructive) torque wheel right-front
@param[in] i_RvMWheelLeftRear   [Nm]    brake (destructive) torque wheel left-rear
@param[in] i_RvMWheelRightRear  [Nm]    brake (destructive) torque wheel right-rear
@param[in] i_angleRollPitchYawSurface [rad] rotation angles of the road surface
@param[in] i_rollAngle          [rad]   roll angle vehicle coordinate system (positiv: right handed)
@param[in] i_FxyzArticulation   [N]     articulation x,y,z force vector (input from coupled chassis, in this chassis' coordinate system)
@param[in] i_staticSimulation   [bool]  switch between static and dynamic mode
********************************************************************************
@param[out] o_beta              [rad]   sideslip angle
@param[out] o_velocity          [m/s]   car absolute velocity
@param[out] o_vChassis          [m/s]   car velocity vector car coordinate system
@param[out] o_yawRate           [rad/s] yaw velocity
@param[out] o_nWheelRightFront  [U/min] wheel rpm right-front
@param[out] o_nWheelLeftFront   [U/min] wheel rpm left-front
@param[out] o_nWheelRightRear   [U/min] wheel rpm right-rear
@param[out] o_nWheelLeftRear    [U/min] wheel rpm left-rear
********************************************************************************
- horizontal dynamic
@param[in,out] p_xWheelLeftFront    [m]     x wheel suspension position left-front (vehicle coordinate system)
@param[in,out] p_yWheelLeftFront    [m]     y wheel suspension position left-front (vehicle coordinate system)
@param[in,out] p_xWheelRightFront   [m]     x wheel suspension position right-front (vehicle coordinate system)
@param[in,out] p_yWheelRightFront   [m]     y wheel suspension position right-front (vehicle coordinate system)
@param[in,out] p_xWheelLeftRear     [m]     x wheel suspension position left-rear (vehicle coordinate system)
@param[in,out] p_yWheelLeftRear     [m]     y wheel suspension position left-rear (vehicle coordinate system)
@param[in,out] p_xWheelRightRear    [m]     x wheel suspension position right-rear (vehicle coordinate system)
@param[in,out] p_yWheelRightRear    [m]     y wheel suspension position right-rear (vehicle coordinate system)
@param[in,out] p_h                  [m]     centre-of-gravity height over street level
@param[in,out] p_m                  [kg]    vehicle mass
@param[in,out] p_myLeftFront        [-]     fricton factor wheel-street left-front
@param[in,out] p_myRightFront       [-]     fricton factor wheel-street right-front
@param[in,out] p_myLeftRear         [-]     fricton factor wheel-street left-rear
@param[in,out] p_myRightRear        [-]     fricton factor wheel-street right-rear
-vertical dynamic
@param[in,out] p_JRollPitchYaw      [kg m²] moment of inertia vector (X,Y,Z axis) , zeros are not permitted
-configuration
@param[in,out] p_wheelAngleRear     [rad]   wheel angle rear (default: 0); simulate error
-articulation
@param[in,out] p_xyzArticulation    [m]     articulation x,y,z position vector (vehicle coordinate system)
-dummy only relevant for two wheeler
@param[in,out] p_setRollAngle       [m]     don't change p_setRollAngle.setInit(0.0);
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CChassisCarDoc
{
    const auto o_beta               = "[rad] sideslip angle";
    const auto o_velocity           = "[m/s] car absolute velocity";
    const auto o_vChassis           = "[m/s] car velocity vector car coordinate system";
    const auto o_yawRate            = "[rad/s] yaw velocity";
    const auto o_nWheelRightFront   = "[U/min] wheel rpm right-front";
    const auto o_nWheelLeftFront    = "[U/min] wheel rpm left-front";
    const auto o_nWheelRightRear    = "[U/min] wheel rpm right-rear";
    const auto o_nWheelLeftRear     = "[U/min] wheel rpm left-rear";

    const auto p_xWheelLeftFront    = "[m] x wheel suspension position left-front (vehicle coordinate system)";
    const auto p_yWheelLeftFront    = "[m] y wheel suspension position left-front (vehicle coordinate system)";
    const auto p_xWheelRightFront   = "[m] x wheel suspension position right-front (vehicle coordinate system)";
    const auto p_yWheelRightFront   = "[m] y wheel suspension position right-front (vehicle coordinate system)";
    const auto p_xWheelLeftRear     = "[m] x wheel suspension position left-rear (vehicle coordinate system)";
    const auto p_yWheelLeftRear     = "[m] y wheel suspension position left-rear (vehicle coordinate system)";
    const auto p_xWheelRightRear    = "[m] x wheel suspension position right-rear (vehicle coordinate system)";
    const auto p_yWheelRightRear    = "[m] y wheel suspension position right-rear (vehicle coordinate system)";
    const auto p_h                  = "[m] centre-of-gravity height over street level";
    const auto p_m                  = "[kg] vehicle mass";
    const auto p_JRollPitchYaw      = "[kg m²] moment of inertia vector (X,Y,Z axis)";
    const auto p_myLeftFront        = "[-] fricton factor wheel-street left-front";
    const auto p_myRightFront       = "[-] fricton factor wheel-street right-front";
    const auto p_myLeftRear         = "[-] fricton factor wheel-street left-rear";
    const auto p_myRightRear        = "[-] fricton factor wheel-street right-rear";
    const auto p_wheelAngleRear     = "[rad] wheel angle rear (default: 0); simulate error";
    const auto p_xyzArticulation    = "[m] articulation x,y,z position vector (vehicle coordinate system)";
}

#include <claraSim/framework/CModule.h>
#include "CAirResistance.h"
#include "CDynamic.h"
#include "CKinetics.h"
#include "CStaticCar.h"
#include "CSuspension.h"
#include "CKineticsVertical.h"
#include "CWheel.h"

////*********************************
//// CChassisCar
////*********************************
class CChassisCar : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CChassisCar();
    virtual ~CChassisCar();

    //*******************************
    //classes
    //*******************************
public:
    CKinetics kineticsLeftFront;
    CKinetics kineticsRightFront;
    CKinetics kineticsLeftRear;
    CKinetics kineticsRightRear;
    CWheel wheelLeftFront;
    CWheel wheelRightFront;
    CWheel wheelLeftRear;
    CWheel wheelRightRear;
    CAirResistance airResistance;
    CStaticCar staticCar;
    CDynamic dynamic;
    //vertical dynamic
    CKineticsVertical kineticsVerticalLeftFront;
    CKineticsVertical kineticsVerticalRightFront;
    CKineticsVertical kineticsVerticalLeftRear;
    CKineticsVertical kineticsVerticalRightRear;
    CSuspension suspensionLeftFront;
    CSuspension suspensionRightFront;
    CSuspension suspensionLeftRear;
    CSuspension suspensionRightRear;

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloat> o_beta;
    CMessageOutput<CFloat> o_velocity;
    CMessageOutput<CFloatVectorXYZ> o_vChassis;
    CMessageOutput<CFloat> o_yawRate;
    CMessageOutput<CFloat> o_nWheelRightFront;
    CMessageOutput<CFloat> o_nWheelLeftFront;
    CMessageOutput<CFloat> o_nWheelRightRear;
    CMessageOutput<CFloat> o_nWheelLeftRear;

    CMessageOutput<CFloat> o_zero; // helper dummy CMessageOutput for syntax compatibility

    /* parameter */
    CMessageParameter<CFloat> p_xWheelLeftFront;
    CMessageParameter<CFloat> p_yWheelLeftFront;
    CMessageParameter<CFloat> p_xWheelRightFront;
    CMessageParameter<CFloat> p_yWheelRightFront;
    CMessageParameter<CFloat> p_xWheelLeftRear;
    CMessageParameter<CFloat> p_yWheelLeftRear;
    CMessageParameter<CFloat> p_xWheelRightRear;
    CMessageParameter<CFloat> p_yWheelRightRear;
    CMessageParameter<CFloat> p_h;
    CMessageParameter<CFloat> p_m;
    CMessageParameter<CFloat> p_myLeftFront;
    CMessageParameter<CFloat> p_myRightFront;
    CMessageParameter<CFloat> p_myLeftRear;
    CMessageParameter<CFloat> p_myRightRear;
    CMessageParameter<CFloatVectorXYZ> p_JRollPitchYaw;
    CMessageParameter<CFloat> p_wheelAngleRear;
    // articulation
    CMessageParameter<CFloatVectorXYZ> p_xyzArticulation;
    CMessageParameter<CFloat> p_setRollAngle;
private:
    /* Input */
    CMessageInput<CFloat> i_wheelAngleFront;
    CMessageInput<CFloat> i_MWheelLeftFront;
    CMessageInput<CFloat> i_MWheelRightFront;
    CMessageInput<CFloat> i_MWheelLeftRear;
    CMessageInput<CFloat> i_MWheelRightRear;
    CMessageInput<CFloat> i_RvMWheelLeftFront;
    CMessageInput<CFloat> i_RvMWheelRightFront;
    CMessageInput<CFloat> i_RvMWheelLeftRear;
    CMessageInput<CFloat> i_RvMWheelRightRear;
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYawSurface;
    CMessageInput<CFloatVectorXYZ> i_FxyzArticulation;
    CMessageInput<CBool> i_staticSimulation;

    // input via internal modules (documentation only here)
    CMessageInput<CFloat> i_beta;                   // [rad] sideslip angle ; dynamic.o_beta
    CMessageInput<CFloat> i_velocity;               // [m/s] velocity of vehicle ; dynamic.o_velocity
    CMessageInput<CFloatVectorXYZ> i_vChassis;      // [m/s] velocity vector car coordinate-system ; dynamic.o_vChassis
    CMessageInput<CFloatVectorXYZ> i_rateRollPitchYawChassis;// [rad/s] (vector) roll, pitch, and yaw rate at the centre of gravity (chassis coordinate system) ; dynamic.o_rateRollPitchYawChassis;
    CMessageInput<CFloat> i_nWheelRightFront;       // [rpm] wheel rpm wheelRightFront ; o_nWheel
    CMessageInput<CFloat> i_nWheelLeftFront;        // [rpm] wheel rpm wheelLeftFront ; o_nWheel
    CMessageInput<CFloat> i_nWheelRightRear;        // [rpm] wheel rpm wheelRightRear ; o_nWheel
    CMessageInput<CFloat> i_nWheelLeftRear;         // [rpm] wheel rpm wheelLeftRear ; o_nWheel

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_wheelAngleFront,
               IMessage<CFloat>& f_MWheelLeftFront,
               IMessage<CFloat>& f_RvMWheelLeftFront,
               IMessage<CFloat>& f_MWheelRightFront,
               IMessage<CFloat>& f_RvMWheelRightFront,
               IMessage<CFloat>& f_MWheelLeftRear,
               IMessage<CFloat>& f_RvMWheelLeftRear,
               IMessage<CFloat>& f_MWheelRightRear,
               IMessage<CFloat>& f_RvMWheelRightRear,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSurface,
               IMessage<CFloatVectorXYZ>& f_FxyzArticulation,
               IMessage<CBool>& f_staticSimulation );

    /* Calculate suspension steady state by integrating the model for some time.
       Init values of suspension position and forces are updated using the final values.
       A logical use would be to parametrize and initialize the model as follows:
           Vehicle.p_whatever.setInit( 42 );
           Vehicle.init();
           Vehicle.process(0, 0);
           Vehicle.chassis.calcSuspensionSteadyState();
           (then start your simulation)
    */
    void calcSuspensionSteadyState( CFloat f_integrationTime = 3. );

private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
};

#endif // CChassisCar_H
