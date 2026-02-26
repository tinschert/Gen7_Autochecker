#ifndef CMOTOR_H
#define CMOTOR_H
/*!
********************************************************************************
@class CMotor
@ingroup driveTrain
@brief simulation of a motor

@author Robert Erhart, ett2si (06.11.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
********************************************************************************
@remark
- Interfaces of the motor:
    + 1) Inputs 'i_MtorqueRequest' and '...Enable', reflecting CDriveTrain messages'o_MTorqueRequest' and 'p_aTargetACC'
    + 2) Parameters 'p_MtorqueRequest' and '...Enable'. Maximum of 1) and 2) is used.
    + 3) Driver input 'i_accelerator'. A torque is calculated from gas pedal input. and maximum of 1), 2), and 3) is used.
-  P-T2 characteristic based on an table
    + 0.5  filter constant init
    + 0.05 filter constant init
    + 1    amplification factor
- engine diagram table
    + engine rpm        x = {0, 400, 1000, 2000, 3000, 4000, 5000, 6000, 10000, 12000}
    + normalized torque y = {0, 0.68, 0.82 , 0.91,  0.94,  0.97,  1.00,  0.97,  0.82,  0}
********************************************************************************
@param[in] i_accelerator           [%]    accelerator pedal
@param[in] i_nTransmission         [rpm]  transmission rpm
@param[in] i_MtorqueRequest        [Nm]   engine torque request
@param[in] i_MtorqueRequestEnable  [bool] enable engine torque request
@param[in] i_sailingRequest        [bool] sailing request from drive train
********************************************************************************
@param[out] o_nEngine              [rpm]  engine rpm (= transmission rpm)
@param[out] o_MfrictionTorque      [Nm]   engine friction torque
@param[out] o_MengineTorque        [Nm]   effective engine torque
@param[out] o_MengineTorqueInd     [Nm]   internal engine torque without friction torque
@param[out] o_MengineTorqueDesired [Nm]   desired engine torque
@param[out] o_MengineTorqueDriver  [Nm]   desired driver engine torque
@param[out] o_MengineIdleRequest   [Nm]   idle request engine torque
@param[out] o_Mmin                 [Nm]   minimum engine torque for this engine rpm
@param[out] o_Mmax                 [Nm]   maximum engine torque for this engine rpm
@param[out] o_driverOverride       [bool] true: driver request >= torque request
********************************************************************************
@param[in,out] p_nTargetIdleEngine     [rpm]  idle rpm engine
@param[in,out] p_engineRunning         [bool] engine running
@param[in,out] p_mdNorm                [Nm]   norming factor (max. engine torque) for torque engine diagram
@param[in,out] p_MtorqueRequest        [Nm]   torque request interface of the engine
@param[in,out] p_MtorqueRequestEnable  [bool] enable input from torque request interface
@param[in,out] p_MengineDriverGradient [Nm/s] driver torque gradient given by gas pedal
********************************************************************************
@todo add motor reaction delay (~100ms)
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CMotorDoc
{
    /* output */
    const auto o_nEngine                = "[rpm] engine rpm (= transmission rpm)";
    const auto o_MfrictionTorque        = "[Nm] engine friction torque";
    const auto o_MengineTorque          = "[Nm] effective engine torque";
    const auto o_MengineTorqueInd       = "[Nm] internal engine torque without friction torque";
    const auto o_MengineTorqueDesired   = "[Nm] desired engine torque";
    const auto o_MengineTorqueDriver    = "[Nm] desired driver engine torque";
    const auto o_MengineIdleRequest     = "[Nm] idle request engine torque";
    const auto o_Mmax                   = "[Nm] maximum engine torque for this engine rpm";
    const auto o_Mmin                   = "[Nm] minimum engine torque for this engine rpm";
    const auto o_driverOverride         = "[bool] true: driver request >= torque request";
    /* parameter */
    const auto p_nTargetIdleEngine      = "[rpm] idle rpm engine";
    const auto p_engineRunning          = "[bool] engine running";
    const auto p_mdNorm                 = "[Nm] norming factor (max. engine torque) for torque engine diagram";
    const auto p_MtorqueRequest         = "[Nm] torque request interface of the engine";
    const auto p_MtorqueRequestEnable   = "[bool] enable input from torque request interface";
    const auto p_MengineDriverGradient  = "[Nm/s] maximum driver torque gradient allowed through gas pedal";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/framework/CLowPass2ndOrder.h>
#include <claraSim/framework/CTable.h>

////*********************************
//// CMotor
////*********************************
class CMotor : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CMotor();
    virtual ~CMotor();

    //*******************************
    //classes
    //*******************************
public:
    CLowPass2ndOrder lowPass;
    CTable maxMdInd;
    CTable MDrag;

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloat> o_nEngine;
    CMessageOutput<CFloat> o_MfrictionTorque;
    CMessageOutput<CFloat> o_MengineTorque;
    CMessageOutput<CFloat> o_MengineTorqueInd;
    CMessageOutput<CFloat> o_MengineTorqueDesired;
    CMessageOutput<CFloat> o_MengineTorqueDriver;
    CMessageOutput<CFloat> o_MengineIdleRequest;
    CMessageOutput<CFloat> o_Mmax;
    CMessageOutput<CFloat> o_Mmin;
    CMessageOutput<CBool>  o_driverOverride;
    /* parameter */
    CMessageParameter<CFloat> p_nTargetIdleEngine;
    CMessageParameter<CBool>  p_engineRunning;
    CMessageParameter<CFloat> p_mdNorm;
    CMessageParameter<CFloat> p_MtorqueRequest;
    CMessageParameter<CBool>  p_MtorqueRequestEnable;
    CMessageParameter<CFloat> p_MengineDriverGradient;
private:
    /* input */
    CMessageInput<CFloat> i_accelerator;
    CMessageInput<CFloat> i_nTransmission;
    CMessageInput<CFloat> i_MtorqueRequest;
    CMessageInput<CBool>  i_MtorqueRequestEnable;
    CMessageInput<CBool>  i_sailingRequest;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_accelerator,
               IMessage<CFloat>& f_nTransmission,
               IMessage<CFloat>& f_MtorqueRequest,
               IMessage<CBool>& f_MtorqueRequestEnable,
               IMessage<CBool>& f_sailingRequest );
private:
    void calc( CFloat f_dT, CFloat f_time );
    CFloat nIdleController( CFloat f_nTargetIdleEngine, CFloat f_nEngine, CFloat f_MfrictionTorque );

    //*******************************
    //variables
    //*******************************
public:
private:
    CFloat m_MdriverRequest;            // local variable for storing the driver requested torque (from i_accelerator)
    CFloat m_MengineInterfaceRequest;   // local variable for storing the maximum value of the torque interfaces (i_MtorqueRequest and p_MtorqueRequest)
    CBool m_torqueRequested;
};

#endif // CMOTOR_H
