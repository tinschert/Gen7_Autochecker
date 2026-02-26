#ifndef CDriveTrainTwoWheeler_H
#define CDriveTrainTwoWheeler_H
/*!
 ********************************************************************************
 @class CDriveTrainTwoWheeler
 @ingroup driveTrain
 @brief motorbike power train model

 @author Robert Erhart, ett2si (18.11.2004 - 00:00:00)
 @copyright (c) Robert Bosch GmbH 2019-2024. All rights reserved.
 ********************************************************************************
 @remark
 - Drivetrain
interface between chassis and drive train components
 - Drivetrain coordinator
longitudinal control simulation
*********************************************************************************
@param[in] i_accelerator            [%]    accelerator pedal
@param[in] i_nWheelFront            [rpm]  wheel rpm ront
@param[in] i_nWheelRear             [rpm]  wheel rpm rear
@param[in] i_clutch                 [%]    clutch pedal
@param[in] i_gearStick              [-1,6] gear shift lever position
@param[in] i_brakepedal             [%]    brake pedal
@param[in] i_parkingBrake           [%]    parking brake
@param[in] i_FChassis               [N]    constructive force (longitudinal only used)
@param[in] i_FvRChassis             [N]    destructive force (longitudinal only used)
@param[in] i_VehicleMass            [kg]   whole mass of the vehicle
@param[in] i_rWheelFront            [m]    radius of front wheel
@param[in] i_rWheelRear             [m]    radius of rear wheel
@param[in] i_angleRollPitchYaw [rad]  pitch angle of vehicle
********************************************************************************
@param[out] o_MWheelFront           [Nm]   torque wheel front
@param[out] o_MWheelRear            [Nm]   torque wheel rear
@param[out] o_RvMWheelFront         [Nm]   destructive front wheel torque (depending on rpm: max hold force / max dynamic force )
@param[out] o_RvMWheelRear          [Nm]   destructive rear wheel torque (depending on rpm: max hold force / max dynamic force )
@param[out] o_brakeLight            [bool] activate brake light

- drivetrain coordinator
@param[out] o_holdConfirmation      [bool] auto holt reached
@param[out] o_holdTransition        [bool] transition to auto hold
@param[out] o_aBrakeRequest         [m/s²] acceleration request to brake system
@param[out] o_aBrakeRequestEnable   [bool] on/off acceleration request to brake system
@param[out] o_pBrakeRequest         [Pa]   brake pressure request
@param[out] o_pBrakeRequestEnable   [bool] on/off brake pressure request
@param[out] o_MtorqueRequest        [Nm]   torques request to engine
@param[out] o_MtorqueRequestEnable  [bool] on/off of torques request to engine
@param[out] o_sailing               [bool] sailing activated/deactivated
@param[out] o_unstressed            [bool] stress free drive drain
*********************************************************************************
- Configuration
@param[in,out] p_frontWheelDrive        [bool]   true: front wheel driven / false: non powered
@param[in,out] p_rearWheelDrive         [bool]   true: rear wheel driven / false: non powered
@param[in,out] p_pBrakeHoldPressure     [Pa=N/m²] max. brake pressure for hold management, default 30000000

- Drivetrain coordinator
@param[in,out] p_sailingRequest         [bool]   request for sailing
@param[in,out] p_deltaMUnstressed       [Nm]     delta torque to determine a stress free drive train
@param[in,out] p_holdConfirmationOverride [bool] override hold o_holdConfirmation signal
@param[in,out] p_aTargetACC             [m/s²]   acceleration target request value input1 (ACC)
@param[in,out] p_aTargetACCEnable       [bool]   on/off acceleration target request input1 (ACC)
@param[in,out] p_aTargetPSS             [m/s²]   acceleration target request value input2 (PSS)
@param[in,out] p_aTargetPSSEnable       [bool]   on/off acceleration target request input2 (PSS)
@param[in,out] p_holdRequestACC         [bool]   auto hold request input1 (ACC)
@param[in,out] p_holdRequestPSS         [bool]   auto hold request input2 (PSS)
@param[in,out] p_holdRelease            [bool]   auto hold release
*********************************************************************************
@todo switch from rpm to 1/s
*********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CDriveTrainTwoWheelerDoc
{
    /* parameter */
    const auto p_frontWheelDrive    = "[bool] true: front wheel driven / false: non powered";
    const auto p_rearWheelDrive     = "[bool] true: rear wheel driven / false: non powered";
    const auto p_pBrakeHoldPressure = "[Pa=N/m²] max. brake pressure for hold management, default 30000000";
    const auto p_sailingRequest     = "[bool] request for sailing";
    const auto p_deltaMUnstressed   = "[Nm] delta torque to determine a stress free drive train";
    const auto p_holdConfirmationOverride = "[bool] override hold o_holdConfirmation signal";
    const auto p_aTargetACC         = "[m/s²] acceleration target request value input1 (ACC)";
    const auto p_aTargetACCEnable   = "[bool] on/off acceleration target request input1 (ACC)";
    const auto p_aTargetPSS         = "[m/s²] acceleration target request value input2 (PSS)";
    const auto p_aTargetPSSEnable   = "[bool] on/off acceleration target request input2 (PSS)";
    const auto p_holdRequestACC     = "[bool] auto hold request input1 (ACC)";
    const auto p_holdRequestPSS     = "[bool] auto hold request input2 (PSS)";
    const auto p_holdRelease        = "[bool] auto hold release";
    /* output */
    const auto o_MWheelFront        = "[Nm] torque front wheel";
    const auto o_MWheelRear         = "[Nm] torque rear wheel";
    const auto o_RvMWheelFront      = "[Nm] destructive front wheel torque (depending on rpm: max hold force / max dynamic force )";
    const auto o_RvMWheelRear       = "[Nm] destructive rear wheel torque (depending on rpm: max hold force / max dynamic force )";
    const auto o_sailing            = "[bool] sailing activated/deactivated";
    const auto o_unstressed         = "[bool] stress free drive drain";
    const auto o_holdTransition     = "[bool] transition to auto hold";
    const auto o_holdConfirmation   = "[bool] auto holt reached";
    const auto o_aBrakeRequest      = "[m/s²] acceleration request to brake system";
    const auto o_aBrakeRequestEnable = "[bool] on/off acceleration request to brake system";
    const auto o_pBrakeRequest      = "[Pa] brake pressure request";
    const auto o_pBrakeRequestEnable = "[bool] on/off brake pressure request";
    const auto o_MtorqueRequest     = "[Nm] torques request to engine";
    const auto o_MtorqueRequestEnable = "[bool] on/off of torques request to engine";
}

#include <claraSim/framework/CModule.h>

#include "CMotor.h"
#include "CTransmission.h"
#include "CBrakeSystemTwoWheeler.h"

////*********************************
//// CTransmission
////*********************************
class CDriveTrainTwoWheeler: public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CDriveTrainTwoWheeler();
    virtual ~CDriveTrainTwoWheeler();

    //*******************************
    //classes
    //*******************************
public:
    CMotor motor;
    CTransmission transmission;
    CBrakeSystemTwoWheeler brakeSystem;

    //*******************************
    //messages
    //*******************************
public:
    /* parameter */
    CMessageParameter<CBool> p_frontWheelDrive;
    CMessageParameter<CBool> p_rearWheelDrive;
    CMessageParameter<CFloat> p_pBrakeHoldPressure;
    /* TSK */
    CMessageParameter<CBool> p_sailingRequest;
    CMessageParameter<CFloat> p_deltaMUnstressed;
    CMessageParameter<CBool> p_holdConfirmationOverride;
    CMessageParameter<CFloat> p_aTargetACC;
    CMessageParameter<CBool> p_aTargetACCEnable;
    CMessageParameter<CFloat> p_aTargetPSS;
    CMessageParameter<CBool> p_aTargetPSSEnable;
    CMessageParameter<CBool> p_holdRequestACC;
    CMessageParameter<CBool> p_holdRequestPSS;
    CMessageParameter<CBool> p_holdRelease;
    /* output */
    CMessageOutput<CFloat> o_MWheelFront;
    CMessageOutput<CFloat> o_MWheelRear;
    CMessageOutput<CFloat> o_RvMWheelFront;
    CMessageOutput<CFloat> o_RvMWheelRear;
    CMessageOutput<CBool> o_sailing;
    CMessageOutput<CBool> o_unstressed;
    /* drivetrain coordinator */
    CMessageOutput<CBool> o_holdConfirmation;
    CMessageOutput<CBool> o_holdTransition;
    CMessageOutput<CFloat> o_aBrakeRequest;
    CMessageOutput<CBool> o_aBrakeRequestEnable;
    CMessageOutput<CFloat> o_pBrakeRequest;
    CMessageOutput<CBool> o_pBrakeRequestEnable;
    CMessageOutput<CFloat> o_MtorqueRequest;
    CMessageOutput<CBool> o_MtorqueRequestEnable;
private:
    /* input */
    CMessageInput<CFloat> i_accelerator;
    CMessageInput<CFloat> i_nWheelFront;
    CMessageInput<CFloat> i_nWheelRear;
    CMessageInput<CFloat> i_clutch;
    CMessageInput<CInt> i_gearStick;
    CMessageInput<CFloat> i_brakepedal;
    CMessageInput<CFloat> i_parkingBrake;
    CMessageInput<CFloatVectorXYZ> i_FChassis;
    CMessageInput<CFloatVectorXYZ> i_FvRChassis;
    CMessageInput<CFloat> i_VehicleMass;
    CMessageInput<CFloat> i_rWheelFront;
    CMessageInput<CFloat> i_rWheelRear;
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYaw;

    // input via internal modules (documentation only here)
    CMessageInput<CFloat> i_MWheelFrontBrakeSystem;       // [Nm] torque wheel left-front ; brakeSystem.o_MWheelFront.get()
    CMessageInput<CFloat> i_MWheelRearBrakeSystem;        // [Nm] torque wheel left-rear ; brakeSystem.o_MWheelRear.get()
    CMessageInput<CFloat> i_MdTransmission;               // [Nm] torque transmission ; transmission.o_MdTransmission.get();
    CMessageInput<CFloat> i_gearRatioTransmission;        // [ ] current gear ratio ; transmission.o_gearRatio.get()
    CMessageInput<CFloat> i_MMinEngine;                   // [Nm] minimum engine torque for this engine rpm ; motor.o_Mmin.get()
    CMessageInput<CFloat> i_MFrictionEngine;              // [Nm] friction torque ; motor.o_MfrictionTorque.get()

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_accelerator,
               IMessage<CFloat>& f_nWheelFront,
               IMessage<CFloat>& f_nWheelRear,
               IMessage<CFloat>& f_clutch,
               IMessage<CInt>& f_gearStick,
               IMessage<CFloat>& f_brakepedal,
               IMessage<CFloat>& f_parkingBrake,
               IMessage<CFloatVectorXYZ>& i_FChassis,
               IMessage<CFloatVectorXYZ>& i_FvRChassis,
               IMessage<CFloat>& f_m,
               IMessage<CFloat>& f_rWheelFront,
               IMessage<CFloat>& f_rWheelRear,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYaw );
private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
    int m_anhaltenState;
    long double m_HystBrakeEngine;
    long double m_HystSailing;
};

#endif // CDriveTrainTwoWheeler_H
