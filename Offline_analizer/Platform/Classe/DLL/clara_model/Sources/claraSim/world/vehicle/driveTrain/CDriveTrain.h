#ifndef CDRIVETRAIN_H
#define CDRIVETRAIN_H
/*!
 ********************************************************************************
 @class CDriveTrain
 @ingroup driveTrain
 @brief power train model

 @author Robert Erhart, ett2si (18.11.2004 - 00:00:00)
 @copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
 ********************************************************************************
 @remark
 - Drivetrain
interface between chassis and drive train components
 - Drivetrain coordinator
longitudinal control simulation

Use acceleration target interfaces p_aTargetACC and p_aTargetPSS to request acceleration.
These overrule driver input, and PSS overrules ACC request.
*********************************************************************************
@param[in] i_accelerator            [%]    accelerator pedal
@param[in] i_nWheelRightFront       [rpm]  wheel rpm right-front
@param[in] i_nWheelLeftFront        [rpm]  wheel rpm left-front
@param[in] i_nWheelRightRear        [rpm]  wheel rpm right-rear
@param[in] i_nWheelLeftRear         [rpm]  wheel rpm left-rear
@param[in] i_clutch                 [%]    clutch pedal
@param[in] i_gearStick              [-1,6] gear shift lever position
@param[in] i_brakepedal             [%]    brake pedal
@param[in] i_parkingBrake           [%]    parking brake
@param[in] i_FChassis               [N]    constructive force (longitudinal only used)
@param[in] i_FvRChassis             [N]    destructive force (longitudinal only used)
@param[in] i_VehicleMass            [kg]   whole mass of the vehicle
@param[in] i_rWheelRightFront       [m]    radius of wheel right front
@param[in] i_rWheelLeftFront        [m]    radius of wheel left front
@param[in] i_rWheelRightRear        [m]    radius of wheel right rear
@param[in] i_rWheelLeftRear         [m]    radius of wheel left rear
@param[in] i_angleRollPitchYaw [rad]  rotation angle in world coordinates. use only to get pitch angle of vehicle (z,y',x'')
********************************************************************************
@param[out] o_MWheelLeftFront       [Nm]   torque wheel left-front
@param[out] o_MWheelRightFront      [Nm]   torque wheel right-front
@param[out] o_MWheelLeftRear        [Nm]   torque wheel left-rear
@param[out] o_MWheelRightRear       [Nm]   torque wheel right-rear
@param[out] o_RnMWheelLeftFront     [Nm]   destructive wheel left front torque (depending on rpm: max hold force / max dynamic force )
@param[out] o_RnMWheelRightFront    [Nm]   destructive wheel right front torque (depending on rpm: max hold force / max dynamic force )
@param[out] o_RnMWheelLeftRear      [Nm]   destructive wheel left rear torque (depending on rpm: max hold force / max dynamic force )
@param[out] o_RnMWheelRightRear     [Nm]   destructive wheel right rear torque (depending on rpm: max hold force / max dynamic force )

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
@param[in,out] p_aTargetPSS             [m/s²]   acceleration target request value input2 (PSS, overrules ACC input!)
@param[in,out] p_aTargetPSSEnable       [bool]   on/off acceleration target request input2 (PSS, overrules ACC input!)
@param[in,out] p_holdRequestACC         [bool]   auto hold request input1 (ACC)
@param[in,out] p_holdRequestPSS         [bool]   auto hold request input2 (PSS)
@param[in,out] p_holdRelease            [bool]   auto hold release
*********************************************************************************
@todo switch from rpm to 1/s
*********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CDriveTrainDoc
{
    /* parameter */
    const auto p_frontWheelDrive = "[bool] true: front wheel driven / false: non powered";
    const auto p_rearWheelDrive = "[bool] true: rear wheel driven / false: non powered";
    const auto p_sailingRequest = "[bool] request for sailing";
    const auto p_deltaMUnstressed = "[Nm] delta torque to determine a stress free drive train";
    const auto p_holdConfirmationOverride = "[bool] override hold o_holdConfirmation signal";
    const auto p_aTargetACC = "[m/s²] acceleration target request value input1 (ACC)";
    const auto p_aTargetACCEnable = "[bool] on/off acceleration target request input1 (ACC)";
    const auto p_aTargetPSS = "[m/s²] acceleration target request value input2 (PSS)";
    const auto p_aTargetPSSEnable = "[bool] on/off acceleration target request input2 (PSS, overrules ACC input!)";
    const auto p_holdRequestACC = "[bool] auto hold request input1 (ACC)";
    const auto p_holdRequestPSS = "[bool] auto hold request input2 (PSS, overrules ACC input!)";
    const auto p_holdRelease = "[bool] auto hold release";
    const auto p_pBrakeHoldPressure = "[Pa=N/m²] max. brake pressure for hold management, default 30000000";
    /* output */
    const auto o_MWheelLeftFront = "[Nm] torque wheel left-front";
    const auto o_MWheelRightFront = "[Nm] torque wheel right-front";
    const auto o_MWheelLeftRear = "[Nm] torque wheel left-rear";
    const auto o_MWheelRightRear = "[Nm] torque wheel right-rear";
    const auto o_RnMWheelLeftFront = "[Nm] destructive wheel left front torque (depending on rpm: max hold force / max dynamic force )";
    const auto o_RnMWheelRightFront = "[Nm] destructive wheel right front torque (depending on rpm: max hold force / max dynamic force )";
    const auto o_RnMWheelLeftRear = "[Nm] destructive wheel left rear torque (depending on rpm: max hold force / max dynamic force )";
    const auto o_RnMWheelRightRear = "[Nm] destructive wheel right rear torque (depending on rpm: max hold force / max dynamic force )";
    const auto o_sailing = "[bool] sailing activated/deactivated";
    const auto o_unstressed = "[bool] stress free drive drain";
    const auto o_holdTransition = "[bool] transition to auto hold";
    const auto o_holdConfirmation = "[bool] auto holt reached";
    const auto o_aBrakeRequest = "[m/s²] acceleration request to brake system";
    const auto o_aBrakeRequestEnable = "[bool] on/off acceleration request to brake system";
    const auto o_pBrakeRequest = "[Pa] brake pressure request";
    const auto o_pBrakeRequestEnable = "[bool] on/off brake pressure request";
    const auto o_MtorqueRequest = "[Nm] torques request to engine";
    const auto o_MtorqueRequestEnable = "[bool] on/off of torques request to engine";
}

#include <claraSim/framework/CModule.h>

#include "CMotor.h"
#include "CTransmission.h"
#include "CDifferentialGear.h"
#include "CBrakeSystem.h"

////*********************************
//// CTransmission
////*********************************
class CDriveTrain: public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CDriveTrain();
    virtual ~CDriveTrain();

    //*******************************
    //classes
    //*******************************
public:
    CMotor motor;
    CTransmission transmission;
    CDifferentialGear differentialGear;
    CBrakeSystem brakeSystem;

    //*******************************
    //messages
    //*******************************
public:
    /* parameter */
    CMessageParameter<CBool> p_frontWheelDrive;
    CMessageParameter<CBool> p_rearWheelDrive;
    CMessageParameter<CFloat> p_pBrakeHoldPressure;
    /* TSK */
    CMessageParameter<CBool>    p_sailingRequest;
    CMessageParameter<CFloat>   p_deltaMUnstressed;
    CMessageParameter<CBool>    p_holdConfirmationOverride;
    CMessageParameter<CFloat>   p_aTargetACC;
    CMessageParameter<CBool>    p_aTargetACCEnable;
    CMessageParameter<CFloat>   p_aTargetPSS;
    CMessageParameter<CBool>    p_aTargetPSSEnable;
    CMessageParameter<CBool>    p_holdRequestACC;
    CMessageParameter<CBool>    p_holdRequestPSS;
    CMessageParameter<CBool>    p_holdRelease;
    /* output */
    CMessageOutput<CFloat> o_MWheelLeftFront;
    CMessageOutput<CFloat> o_MWheelRightFront;
    CMessageOutput<CFloat> o_MWheelLeftRear;
    CMessageOutput<CFloat> o_MWheelRightRear;
    CMessageOutput<CFloat> o_RnMWheelLeftFront;
    CMessageOutput<CFloat> o_RnMWheelRightFront;
    CMessageOutput<CFloat> o_RnMWheelLeftRear;
    CMessageOutput<CFloat> o_RnMWheelRightRear;
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
    CMessageInput<CFloat> i_nWheelRightFront;
    CMessageInput<CFloat> i_nWheelLeftFront;
    CMessageInput<CFloat> i_nWheelRightRear;
    CMessageInput<CFloat> i_nWheelLeftRear;
    CMessageInput<CFloat> i_clutch;
    CMessageInput<CInt> i_gearStick;
    CMessageInput<CFloat> i_brakepedal;
    CMessageInput<CFloat> i_parkingBrake;
    CMessageInput<CFloatVectorXYZ> i_FChassis;
    CMessageInput<CFloatVectorXYZ> i_FvRChassis;
    CMessageInput<CFloat> i_VehicleMass;
    CMessageInput<CFloat> i_rWheelRightFront;
    CMessageInput<CFloat> i_rWheelLeftFront;
    CMessageInput<CFloat> i_rWheelRightRear;
    CMessageInput<CFloat> i_rWheelLeftRear;
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYaw;

    // input via internal modules (documentation only here)
    CMessageInput<CFloat> i_MWheelLeftFrontDifferentialGear;  // [Nm] torque wheel left-front ; differentialGear.o_MWheelLeftFront.get()
    CMessageInput<CFloat> i_MWheelLeftFrontBrakeSystem;       // [Nm] torque wheel left-front ; brakeSystem.o_MWheelLeftFront.get()
    CMessageInput<CFloat> i_MWheelRightFrontDifferentialGear; // [Nm] torque wheel right-front ; differentialGear.o_MWheelRightFront.get()
    CMessageInput<CFloat> i_MWheelRightFrontBrakeSystem;      // [Nm] torque wheel right-front ; brakeSystem.o_MWheelRightFront.get()
    CMessageInput<CFloat> i_MWheelLeftRearDifferentialGear;   // [Nm] torque wheel left-rear ; differentialGear.o_MWheelLeftRear.get()
    CMessageInput<CFloat> i_MWheelLeftRearBrakeSystem;        // [Nm] torque wheel left-rear ; brakeSystem.o_MWheelLeftRear.get()
    CMessageInput<CFloat> i_MWheelRightRearDifferentialGear;  // [Nm] torque wheel right-rear ; differentialGear.o_MWheelRightRear.get()
    CMessageInput<CFloat> i_MWheelRightRearBrakeSystem;       // [Nm] torque wheel right-rear ; brakeSystem.o_MWheelRightRear.get()
    CMessageInput<CFloat> i_gearRatioTransmission;            // [ ] current gear ratio ; transmission.o_gearRatio.get()
    CMessageInput<CFloat> i_gearRatioDifferential;            // [-] current differential ratio ; differentialGear.o_differentialGearRatio.get()
    CMessageInput<CFloat> i_MMinEngine;                       // [Nm] minimum engine torque for this engine rpm ; motor.o_Mmin.get()
    CMessageInput<CFloat> i_MFrictionEngine;                  // [Nm] friction torque ; motor.o_MfrictionTorque.get()

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_accelerator,
               IMessage<CFloat>& f_nWheelRightFront,
               IMessage<CFloat>& f_nWheelLeftFront,
               IMessage<CFloat>& f_nWheelRightRear,
               IMessage<CFloat>& f_nWheelLeftRear,
               IMessage<CFloat>& f_clutch,
               IMessage<CInt>& f_gearStick,
               IMessage<CFloat>& f_brakepedal,
               IMessage<CFloat>& f_parkingBrake,
               IMessage<CFloatVectorXYZ>& i_FChassis,
               IMessage<CFloatVectorXYZ>& i_FvRChassis,
               IMessage<CFloat>& f_m,
               IMessage<CFloat>& f_rWheelLeftFront,
               IMessage<CFloat>& f_rWheelRightFront,
               IMessage<CFloat>& f_rWheelLeftRear,
               IMessage<CFloat>& f_rWheelRightRear,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYaw );
private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
    int m_stopState;
    long double m_HystBrakeEngine;
    long double m_HystSailing;
};

#endif // CDRIVETRAIN_H
