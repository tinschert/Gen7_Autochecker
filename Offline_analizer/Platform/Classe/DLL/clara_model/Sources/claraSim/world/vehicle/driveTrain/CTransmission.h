#ifndef CTRANSMISSION_H
#define CTRANSMISSION_H
/*!
********************************************************************************
@class CTransmission
@ingroup driveTrain
@brief simulation of an automatic, semiAutomatic and manual gear box

@author Robert Erhart, ett2si (10.11.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
Default values (could be overridden in your project specific CSimModel class
- shifting characteristic
    + lowPass2ndOrder define the p-T2 characteristic for shifting with
      filter constant a = 0.5;  b = 0.125 and amplification factor v = 1

- shift up characteristic in automatic and semiAutomatic mode
    + torque Request x = { 0, 50, 100, 200, 400, 500, 600, 700 }
    + engine rpm     y = { 1800, 2000, 3500, 4000, 5000, 6000, 6000, 6000 }
    + shiftUpTable.init( 8, x, y, 0 );
- shift down characteristic in automatic and semiAutomatic mode
    + torque Request x = { 0, 50, 100, 200, 400, 500, 600, 700 }
    + engine rpm     y = { 1800, 2000, 3500, 4000, 5000, 6000, 6000, 6000 }
    + shiftDownTable.init( 8, x, y, 0 );
********************************************************************************
@param[in] i_MdEngine           [Nm]    torque engine
@param[in] i_MdEngineRequest    [Nm]    requested moment for engine
@param[in] i_nDifferentialGear  [rpm]   rpm differential gear
@param[in] i_clutch             [%]     clutch pedal (not used)
@param[in] i_gearStick          [-1..6] gear shift lever position
@param[in] i_sailingRequest     [bool]  sailing request from drive train
********************************************************************************
@param[out] o_nTransmission     [rpm]   rpm transmission
@param[out] o_MdTransmission    [Nm]    torque transmission
@param[out] o_gearRatio         [ ]     current gear ratio
@param[out] o_gearPosition      [-1..6] current gear
@param[out] o_gearPositionTarget[-1..6] target gear
@param[out] o_gearStick         [ ]     current gear stick position
@param[out] o_shifting          [bool]  true: shifting in progress
********************************************************************************
@param[in,out] p_nMaxEngineShift       [rpm]   maximum allowed rpm after shifting
@param[in,out] p_nMinEngineShift       [rpm]   minimum allowed rpm after shifting
@param[in,out] p_transmissionMode      [enum]  automatic = 0, semiAutomatic = 1, manual = 2
@param[in,out] p_gearRatioXGearLever   [-1..n] x-axis (gear lever) for gearRatio table
@param[in,out] p_gearRatioYRatio       [ratio] y-axis (gear ration) for gearRatio table
@param[in,out] p_gearPositionTargetMin [1..n]  minimal target gear position; only for automatic gearbox
********************************************************************************
@todo clutch 100%: transmission moment of inertia + friction of transmission
@todo parameter for shift up and down table; paramter for lowPass2ndOrder
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CTransmissionDoc
{
    const auto o_nTransmission = "[rpm] rpm transmission";
    const auto o_MdTransmission = "[Nm] torque transmission";
    const auto o_gearRatio = "[ ] current gear ratio";
    const auto o_gearPosition = "[-1..6] current gear";
    const auto o_gearPositionTarget = "[-1..6] target gear";
    const auto o_gearStick = "[ ] current gear stick position";
    const auto o_shifting = "[bool] true: shifting in progress";
    const auto p_nMaxEngineShift = "[rpm] maximum allowed rpm after shifting";
    const auto p_nMinEngineShift = "[rpm] minimum allowed rpm after shifting";
    const auto p_transmissionMode = "[enum] automatic = 0, semiAutomatic = 1, manual = 2";
    const auto p_gearRatioXGearLever = "[-1..n] x-axis (gear lever) for gearRatio table";
    const auto p_gearRatioYRatio = "[ratio] y-axis (gear ration) for gearRatio table";
    const auto p_gearPositionTargetMin = "[1..6] minimal target gear position; only for automatic gearbox";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/framework/CLowPass2ndOrder.h>
#include <claraSim/framework/CTable.h>

enum EtransmissionTyp {automatic = 0, semiAutomatic = 1, manual = 2};

////*********************************
//// CTransmission
////*********************************
class CTransmission : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CTransmission();
    virtual ~CTransmission();

    //*******************************
    //classes
    //*******************************
public:
    CTable gearRatioTable;
    CTable shiftUpTable;
    CTable shiftDownTable;
    CLowPass2ndOrder lowPass2ndOrder;

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloat> o_nTransmission;
    CMessageOutput<CFloat> o_MdTransmission;
    CMessageOutput<CFloat> o_gearRatio;
    CMessageOutput<CInt> o_gearPosition;
    CMessageOutput<CInt> o_gearPositionTarget;
    CMessageOutput<CInt> o_gearStick;
    CMessageOutput<CBool> o_shifting;
    /* parameter */
    CMessageParameter<CFloat> p_nMaxEngineShift;
    CMessageParameter<CFloat> p_nMinEngineShift;
    CMessageParameter<CInt> p_transmissionMode;
    CMessageParameter<CFloatVector> p_gearRatioXGearLever;
    CMessageParameter<CFloatVector> p_gearRatioYRatio;
    CMessageParameter<CInt> p_gearPositionTargetMin;
private:
    /* input */
    CMessageInput<CFloat> i_MdEngine;
    CMessageInput<CFloat> i_MdEngineRequest;
    CMessageInput<CFloat> i_nDifferentialGear;
    CMessageInput<CFloat> i_clutch;
    CMessageInput<CInt> i_gearStick;
    CMessageInput<CBool>  i_sailingRequest;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_MdEngine,
               IMessage<CFloat>& f_MdEngineRequest,
               IMessage<CFloat>& f_nDifferentialGear,
               IMessage<CFloat>& f_clutch,
               IMessage<CInt>&   f_gearStick,
               IMessage<CBool>&  f_sailingRequest );
private:
    void calc( CFloat f_dT, CFloat f_time );
    void calcGearStep();

    //*******************************
    //variables
    //*******************************
public:
private:
    CFloat m_gearRatioInternal;
    CFloat m_gearPositionInternal;
};

#endif // CTRANSMISSION_H
