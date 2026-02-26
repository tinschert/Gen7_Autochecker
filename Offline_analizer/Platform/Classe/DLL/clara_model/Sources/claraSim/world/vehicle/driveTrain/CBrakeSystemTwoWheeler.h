#ifndef CBrakeSystemTwoWheeler_H
#define CBrakeSystemTwoWheeler_H
/*!
********************************************************************************
@class CBrakeSystemTwoWheeler
@ingroup driveTrain
@brief Brake system model for twowheeler

@author Robert Erhart, ett2si (23.11.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2019-2024. All rights reserved.
********************************************************************************
@remark
- lowPass P-T1 characteristic brake system
- calculate the maximal brake torque of each wheel
- stand still situation of the wheel is considered in the wheel model
- Always positive value. Direction of brake force is considered
   in the wheel model.
- dynamic friction torque for disc brake with brake caliper
- 100 ms dead time (if calculation time steps are 1 ms)
@verbatim
  M = 2 * µ * r * A * p
  with C = 2 * µ * r * A
  M = C * p
@endverbatim
********************************************************************************
@param[in] i_brakepedal          [%]       brake pedal
@param[in] i_parkingBrake        [%]       parking brake
@param[in] i_FChassis            [N]       constructive force (longitudinal only used)
@param[in] i_FvRChassis          [N]       destructive force (longitudinal only used)
@param[in] i_m                   [kg]      whole mass of the vehicle
@param[in] i_rWheelFront         [m]       radius of front wheel
@param[in] i_rWheelRear          [m]       radius of rear wheel
@param[in] i_aBrakeRequest       [m/s²]    brake acceleration request
@param[in] i_abrakeRequestEnable [bool]    brake acceleration release
@param[in] i_pBrakeRequest       [Pa=N/m²] brake pressure request
@param[in] i_pbrakeRequestEnable [bool]    brake pressure release
@param[in] i_sailingRequest      [bool]    sailing request from drive train
********************************************************************************
@param[out] o_MWheelFront        [Nm]      brake torque front wheel
@param[out] o_MWheelRear         [Nm]      brake torque rear wheel
@param[out] o_pBrake                 [Pa=N/m²] current brake pressure 1Pa = 1N/m^2 = 10^-5 bar
@param[out] o_pBrakeDriver           [Pa=N/m²] current brake pressure Driver 1Pa = 1N/m^2 = 10^-5 bar
@param[out] o_brakeLight             [bool]    brake light
@param[out] o_driverOverride         [bool]    driver brake pressure > brake pressure request
********************************************************************************
@param[in,out] p_CfrontWheel          [m³]     transformation constant brake wheels front C = 2 * µ * r * A
@param[in,out] p_CrearWheel           [m³]     transformation constant brake wheels rear C = 2 * µ * r * A
@param[in,out] p_MmaxParkingBrake     [Nm]     maximum torque parking brake
@param[in,out] p_pMaxBrake            [Pa]     maximum brake system pressure
@param[in,out] p_pBrakeGradientDriver [Pa/s]   driver brake gradient
@param[in,out] p_pBrakeRequest        [Pa]     brake pressure request
@param[in,out] p_pBrakeRequestEnable  [bool]   enable brake pressure request interface
@param[in,out] p_aBrakeRequest        [m/s²]   brake acceleration request
@param[in,out] p_aBrakeRequestEnable  [bool]   enable brake acceleration request interface
@param[in,out] p_MBrakeRequest        [Nm]     brake torque request
@param[in,out] p_MBrakeRequestEnable  [bool]   enable brake torque request interface
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CBrakeSystemTwoWheelerDoc
{
    const auto o_MWheelFront = "[Nm]  brake torque wheel -front";
    const auto o_MWheelRear = "[Nm]  brake torque wheel -rear";
    const auto o_pBrake = "[Pa=N/m²] current brake pressure 1Pa = 1N/m^2 = 10^-5 bar";
    const auto o_pBrakeDriver = "[Pa=N/m²] current brake pressure Driver 1Pa = 1N/m^2 = 10^-5 bar";
    const auto o_brakeLight = "[bool] brake light";
    const auto o_driverOverride = "[bool] driver brake pressure > brake pressure request";
    /* parameter */
    const auto p_CfrontWheel = "[m³] transformation constant brake wheels front C = 2 * µ * r * A";
    const auto p_CrearWheel = "[m³] transformation constant brake wheels rear C = 2 * µ * r * A";
    const auto p_MmaxParkingBrake = "[Nm] maximum torque parking brake";
    const auto p_pMaxBrake = "[Pa] maximum brake system pressure";
    const auto p_pBrakeGradientDriver = "[Pa/s] driver brake gradient";
    const auto p_pBrakeRequest = "[Pa] brake pressure request";
    const auto p_pBrakeRequestEnable = "[bool] enable brake pressure request interface";
    const auto p_aBrakeRequest = "[m/s²] brake acceleration request";
    const auto p_aBrakeRequestEnable = "[bool] enable brake acceleration request interface";
    const auto p_MBrakeRequest = "[Nm] brake torque request";
    const auto p_MBrakeRequestEnable = "[bool] enable brake torque request interface";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/framework/CLowPass.h>
#include <claraSim/framework/CFifo.h>


////*********************************
//// CBrakeSystemTwoWheeler
////*********************************

class CBrakeSystemTwoWheeler : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CBrakeSystemTwoWheeler();
    virtual ~CBrakeSystemTwoWheeler();

    //*******************************
    //classes
    //*******************************
public:
    CLowPass lowPass; //CLowPass2ndOrder lowPass2ndOrder;
private:
    CFifo<CFloat> DeadTime;

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloat> o_MWheelFront;
    CMessageOutput<CFloat> o_MWheelRear;
    CMessageOutput<CFloat> o_pBrake;
    CMessageOutput<CFloat> o_pBrakeDriver;
    CMessageOutput<CBool> o_brakeLight;
    CMessageOutput<CBool> o_driverOverride;
    /* parameter */
    CMessageParameter<CFloat> p_CfrontWheel;
    CMessageParameter<CFloat> p_CrearWheel;
    CMessageParameter<CFloat> p_MmaxParkingBrake;
    CMessageParameter<CFloat> p_pMaxBrake;
    CMessageParameter<CFloat> p_pBrakeRequest;
    CMessageParameter<CBool> p_pBrakeRequestEnable;
    CMessageParameter<CFloat> p_aBrakeRequest;
    CMessageParameter<CBool> p_aBrakeRequestEnable;
    CMessageParameter<CFloat> p_MBrakeRequest;
    CMessageParameter<CBool> p_MBrakeRequestEnable;
    CMessageParameter<CFloat> p_pBrakeGradientDriver;
private:
    /* input */
    CMessageInput<CFloat> i_brakepedal;
    CMessageInput<CFloat> i_parkingBrake;
    CMessageInput<CFloatVectorXYZ> i_FChassis;
    CMessageInput<CFloatVectorXYZ> i_FvRChassis;
    CMessageInput<CFloat> i_m;
    CMessageInput<CFloat> i_rWheelFront;
    CMessageInput<CFloat> i_rWheelRear;
    CMessageInput<CFloat> i_aBrakeRequest;
    CMessageInput<CBool>  i_aBrakeRequestEnable;
    CMessageInput<CFloat> i_pBrakeRequest;
    CMessageInput<CBool>  i_pBrakeRequestEnable;
    CMessageInput<CBool>  i_sailingRequest;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_brakepedal,
               IMessage<CFloat>& f_parkingBrake,
               IMessage<CFloatVectorXYZ>& f_FChassis,
               IMessage<CFloatVectorXYZ>& f_FvRChassis,
               IMessage<CFloat>& f_m,
               IMessage<CFloat>& f_rWheelFront,
               IMessage<CFloat>& f_rWheelRear,
               IMessage<CFloat>& f_aBrakeRequest,
               IMessage<CBool>&  f_aBrakeRequestEnable,
               IMessage<CFloat>& f_pBrakeRequest,
               IMessage<CBool>&  f_pBrakeRequestEnable,
               IMessage<CBool>&  f_sailingRequest );

private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
    CFloat m_pBrakeFront;
    CFloat m_pBrakeRear;
    CFloat m_MparkingBrake;
};

#endif // CBrakeSystemTwoWheeler_H
