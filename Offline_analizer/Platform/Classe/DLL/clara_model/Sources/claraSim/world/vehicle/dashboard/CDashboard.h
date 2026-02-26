#ifndef CDASHBOARD_H
#define CDASHBOARD_H
/*!
********************************************************************************
@class CDashboard
@ingroup dashboard
@brief simulation of a dashboard of an vehicle

@author Robert Erhart, ett2si (27.06.2007)
@author Markus Oenning, om72si (review 21.07.2009)
@copyright (c) Robert Bosch GmbH 2007-2024. All rights reserved.
********************************************************************************
@remark

********************************************************************************
@param[in] i_aceleratorDriver           [0..1] driver's accelerator pedal state
@param[in] i_brakepedalDriver           [0..1] driver's brake pedal state
@param[in] i_angleSteeringWheelDriver   [rad]  driver's steering wheel angle
@param[in] i_angleSteeringWheel         [rad]  steering wheel angle
@param[in] i_nEngine                    [rpm]  current engine rpm
@param[in] i_velocityX                  [m/s]  current longitudinal vehicle velocity
********************************************************************************
@param[out] o_accelerator               [0..1] accelerator pedal state
@param[out] o_brakepedal                [0..1] brake pedal state
@param[out] o_angleSteeringWheel        [rad]  current steering wheel angle
@param[out] o_angleSteeringWheelTarget  [rad]  target steering wheel angle
@param[out] o_nEngine                   [rpm]  displayed engine rpm
@param[out] o_velocityDisplay           [m/s]  displayed vehicle velocity
********************************************************************************
- input elements with direct claraSim influence
@param[in,out] p_accelerator                [0..1]  accelerator pedal state (used by GUI)
@param[in,out] p_brakepedal                 [0..1]  brake pedal state (used by GUI)
@param[in,out] p_clutch                     [0..1]  clutch pedal for manual gear box
@param[in,out] p_parkingBrake               [0..1]  parking brake
@param[in,out] p_gearStick                  [-1..6] gear shift lever position
@param[in,out] p_angleSteeringWheelTarget   [rad]   target steering wheel angle (GUI)
@param[in,out] p_angleSteeringWheelAuto     [bool]  automatic steering control through driver: on/off
@param[in,out] p_acceleratorAuto            [bool]  automatic accelerator control through driver: on/off
@param[in,out] p_brakepedalAuto             [bool]  automatic brake control through driver: on/off
@param[in,out] p_angleSteeringWheelChangeRate [rad/s] steering wheel angular velocity (used when current and set value differ)
@param[in,out] p_acceleratorChangeRate      [1/s]   accelerator pedal change rate (used when current and set value differ)

- input elements (no function in claraSim, only message interface between restbus simulation, pythomation, and GUI)
@param[in,out] p_blinker                    [0..3]  0:=off 1:=Left 2:=Right 3:=Warn
@param[in,out] p_wiper                      [0,1]   0:=off 1:=on
@param[in,out] p_light                      [0..2]  0:=off 1:=low mode 2:=high mode
@param[in,out] p_kl15                       [bool]  KL15 info
@param[in,out] p_accMainSwitch              [bool]  ACC main switch
@param[in,out] p_accMainSwitchToggle        [bool]  ACC main button for 500 ms active. todo replace with message functionality
@param[in,out] p_accOff                     [bool]  ACC off button
@param[in,out] p_accMode                    [bool]  ACC mode switch
@param[in,out] p_accOnOff                   [bool]  ACC on / off switch
@param[in,out] p_accResume                  [bool]  ACC resume button
@param[in,out] p_accSet                     [bool]  ACC set button (e.g. setup ACC to current velocity)
@param[in,out] p_accTipUp                   [bool]  ACC set vSet higher
@param[in,out] p_accTipDown                 [bool]  ACC set vSet lower
@param[in,out] p_accTipUp2Step              [bool]  ACC set vSet higher second step
@param[in,out] p_accTipDown2Step            [bool]  ACC set vSet lower second step
@param[in,out] p_accSetPlusTime             [bool]  ACC tau gap set plus (set bigger time gap)
@param[in,out] p_accSetMinusTime            [bool]  ACC tau gap set minus (set bigger time gap)
@param[in,out] p_accLIM                     [bool]  ACCLim button
@param[in,out] p_accVSet                    [m/s]   ACC set velocity value input
@param[in,out] p_accTimeGap                 [s]     ACC set time gap value input
@param[in,out] p_accTargetObject            [bool]  ACC got target object (object valid)
@param[in,out] p_lrrStatusXcp               []      LRR status xcp : SysStates_SpecificState_ubonly message container for LRR STATUS
@param[in,out] p_lrrStatusPrj               [---]   LRR status depending on project
@param[in,out] p_lrrStatus1                 [---]   generic status depending on project
@param[in,out] p_lrrStatus2                 [---]   generic status depending on project
@param[in,out] p_lrrStatus3                 [---]   generic status depending on project
- configuration parameter
@param[in,out] p_velocityDisplayDelta       [m/s]   delta between car velocity and car velocity display
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CDashboardDoc
{
    const auto p_accelerator            = "[0..1] accelerator pedal state";
    const auto p_brakepedal             = "[0..1] brake pedal state";
    const auto p_clutch                 = "[0..1] clutch pedal for manual gear box";
    const auto p_parkingBrake           = "[0..1] parking brake";
    const auto p_gearStick              = "[-1..6] gear shift lever position";
    const auto p_angleSteeringWheelTarget = "[rad] target steering wheel angle (GUI)";
    const auto p_angleSteeringWheelAuto = "[bool] automatic steering control through driver: on/off";
    const auto p_acceleratorAuto        = "[bool] automatic accelerator control through driver: on/off";
    const auto p_brakepedalAuto         = "[bool] automatic brake control through driver: on/off";
    const auto p_angleSteeringWheelChangeRate = "[rad/s] steering wheel angular velocity (used when current and set value differ)";
    const auto p_acceleratorChangeRate = "[1/s] accelerator pedal change rate (used when current and set value differ)";

    const auto p_blinker                = "[0..3] 0:=off 1:=Left 2:=Right 3:=Warn";
    const auto p_wiper                  = "[0,1] 0:=off 1:=on";
    const auto p_light                  = "[0..2] 0:=off 1:=low mode 2:=high mode";
    const auto p_kl15                   = "[bool] KL15 info";
    const auto p_accMainSwitch          = "[bool] ACC main switch";
    const auto p_accMainSwitchToggle    = "[bool] ACC main button for 500 ms active. todo replace with message functionality";
    const auto p_accOff                 = "[bool] ACC off button";
    const auto p_accMode                = "[bool] ACC mode switch";
    const auto p_accOnOff               = "[bool] ACC on / off switch";
    const auto p_accResume              = "[bool] ACC resume button";
    const auto p_accSet                 = "[bool] ACC set button (e.g. setup ACC to current velocity)";
    const auto p_accTipUp               = "[bool] ACC set vSet higher";
    const auto p_accTipDown             = "[bool] ACC set vSet lower";
    const auto p_accTipUp2Step          = "[bool] ACC set vSet higher second step";
    const auto p_accTipDown2Step        = "[bool] ACC set vSet lower second step";
    const auto p_accSetPlusTime         = "[bool] ACC tau gap set plus (set bigger time gap)";
    const auto p_accSetMinusTime        = "[bool] ACC tau gap set minus (set bigger time gap)";
    const auto p_accLIM                 = "[bool] ACCLim button";
    const auto p_accVSet                = "[m/s] ACC set velocity value input";
    const auto p_accTimeGap             = "[s] ACC set time gap value input";
    const auto p_accTargetObject        = "[bool] ACC got target object (object valid)";
    const auto p_lrrStatusXcp           = "[] LRR status xcp : SysStates_SpecificState_ubonly message container for LRR STATUS";
    const auto p_lrrStatusPrj           = "[---] LRR status depending on project";
    const auto p_lrrStatus1             = "[---] generic status depending on project";
    const auto p_lrrStatus2             = "[---] generic status depending on project";
    const auto p_lrrStatus3             = "[---] generic status depending on project";
    const auto p_velocityDisplayDelta   = "[m/s] delta between car velocity and car velocity display";
    /* output */
    const auto o_accelerator              = "[0..1] accelerator pedal state";
    const auto o_brakepedal               = "[0..1] brake pedal state";
    const auto o_angleSteeringWheel       = "[rad] current angle steering wheel";
    const auto o_angleSteeringWheelTarget = "[rad] target angle steering wheel";
    const auto o_nEngine                  = "[rpm] displayed engine rpm";
    const auto o_velocityDisplay          = "[m/s] displayed vehicle velocity";
}

#include <claraSim/framework/CModule.h>


////*********************************
//// CDashboard
////*********************************
class CDashboard: public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CDashboard();
    virtual ~CDashboard();

    //*******************************
    //classes
    //*******************************
public:

    //*******************************
    //messages
    //*******************************
public:
    CMessageParameter<CFloat> p_accelerator;
    CMessageParameter<CFloat> p_brakepedal;
    CMessageParameter<CFloat> p_clutch;
    CMessageParameter<CFloat> p_parkingBrake;
    CMessageParameter<CInt>   p_gearStick;
    CMessageParameter<CBool>  p_angleSteeringWheelAuto;
    CMessageParameter<CBool>  p_acceleratorAuto;
    CMessageParameter<CBool>  p_brakepedalAuto;
    CMessageParameter<CFloat> p_angleSteeringWheelTarget;
    CMessageParameter<CFloat> p_angleSteeringWheelChangeRate;
    CMessageParameter<CFloat> p_acceleratorChangeRate;

    CMessageParameter<CInt> p_blinker;
    CMessageParameter<CInt> p_wiper;
    CMessageParameter<CInt> p_light;
    CMessageParameter<CBool> p_kl15;
    CMessageParameter<CBool> p_accMainSwitch;
    CMessageParameter<CBool> p_accMainSwitchToggle;
    CMessageParameter<CBool> p_accOff;
    CMessageParameter<CBool> p_accMode;
    CMessageParameter<CBool> p_accOnOff;
    CMessageParameter<CBool> p_accResume;
    CMessageParameter<CBool> p_accSet;
    CMessageParameter<CBool> p_accTipUp;
    CMessageParameter<CBool> p_accTipDown;
    CMessageParameter<CBool> p_accTipUp2Step;
    CMessageParameter<CBool> p_accTipDown2Step;
    CMessageParameter<CBool> p_accSetPlusTime;
    CMessageParameter<CBool> p_accSetMinusTime;
    CMessageParameter<CBool> p_accLIM;
    CMessageParameter<CFloat> p_accVSet;
    CMessageParameter<CFloat> p_accTimeGap;
    CMessageParameter<CBool> p_accTargetObject;
    CMessageParameter<CFloat> p_lrrStatusXcp;
    CMessageParameter<CFloat> p_lrrStatusPrj;
    CMessageParameter<CFloat> p_lrrStatus1;
    CMessageParameter<CFloat> p_lrrStatus2;
    CMessageParameter<CFloat> p_lrrStatus3;
    CMessageParameter<CFloat> p_velocityDisplayDelta;
    /* output */
    CMessageOutput<CFloat> o_accelerator;
    CMessageOutput<CFloat> o_brakepedal;
    CMessageOutput<CFloat> o_angleSteeringWheel;
    CMessageOutput<CFloat> o_angleSteeringWheelTarget;
    CMessageOutput<CFloat> o_nEngine;
    CMessageOutput<CFloat> o_velocityDisplay;

private:
    /* input */
    CMessageInput<CFloat> i_acceleratorDriver;
    CMessageInput<CFloat> i_brakepedalDriver;
    CMessageInput<CFloat> i_angleSteeringWheelDriver;
    CMessageInput<CFloat> i_angleSteeringWheel;
    CMessageInput<CFloat> i_nEngine;
    CMessageInput<CFloatVectorXYZ> i_vChassis;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_acceleratorDriver,
               IMessage<CFloat>& f_brakepedalDriver,
               IMessage<CFloat>& f_angleSteeringWheelDriver,
               IMessage<CFloat>& f_angleSteeringWheel,
               IMessage<CFloat>& f_nEngine,
               IMessage<CFloatVectorXYZ>& f_vChassis );
    void setVehicleParameter();
private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
    bool k1_accMainSwitchToggle;
    CFloat m_time;
    // accelerator and steering wheel angle helper variables:
    CFloat m_accel, m_SW;
    CFloat m_deltaAccel, m_deltaSW;
    CFloat m_maxChangeAccel, m_maxChangeSW;
};

#endif // CDASHBOARD_H
