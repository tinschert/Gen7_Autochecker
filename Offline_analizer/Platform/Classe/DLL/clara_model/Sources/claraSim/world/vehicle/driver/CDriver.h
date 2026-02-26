#ifndef _CDRIVER_H_
#define _CDRIVER_H_
/*!
********************************************************************************
@class CDriver
@ingroup driver
@brief driver model

@author Markus Oenning, om72si (06.03.2007)
@author Andreas Brunner, bnr2lr (02.07.2019)
@copyright (c) Robert Bosch GmbH 2007-2024. All rights reserved.
********************************************************************************
@remark
********************************************************************************
@param[in] i_velocity               [m/s]  velocity ego vehicle
@param[in] i_velocityX              [m/s]  velocity ego vehicle x-value
@param[in] i_velocityY              [m/s]  velocity ego vehicle y-value
@param[in] i_m                      [kg]   vehicle mass
@param[in] i_rWheel                 [m]    wheel radius
@param[in] i_Mmax                   [Nm]   max torque
@param[in] i_xyzWorld               [m]    world xyz-position ego vehicle
@param[in] i_angleRollPitchYaw      [rad]  rotation ego vehicle (world coordinate) (only yaw needed)
@param[in] i_road                   [-]    road
@param[in] i_lane                   [-]    lane
@param[in] i_coursePosition         [m]    current course position of ego vehicle
@param[in] i_lateralOffset          [m]    lateral offset of course line
@param[in] i_targetLateralOffset    [m]    target lateral offset from course line
@param[in] i_lateralVelocity        [m/s]  lateral velocity for lane change
@param[in] i_angleSteeringWheel     [rad]  steering wheel angle
@param[in] i_angleSteeringWheelAuto [bool] automatic steering control through driver: on/off
@param[in] i_acceleratorAuto        [bool] automatic gas pedal control through driver: on/off
@param[in] i_brakepedalAuto         [bool] automatic brake pedal control through driver: on/off
@param[in] roadNetwork              [-]    reference to roadNetwork
********************************************************************************
@param[out] o_angleSteeringWheel [rad]   steering wheel angle
@param[out] o_accelerator        [0..1]  accelerator pedal state
@param[out] o_brakepedal         [0..1]  brake pedal state
@param[out] o_MDriverRequest     [Nm]    torque request driver
********************************************************************************
@param[in,out] p_vFactor         [1/s]   velocity factor for transforming ego velocity to predictive distance
@param[in,out] p_vOffset         [m]     offset for transforming ego velocity to predictive distance
@param[in,out] p_yawFactor       [m/rad] yaw angle factor for transforming ego velocity to predictive distance
@param[in,out] p_angleFactor     []      factor course relative angle and angle steering wheel
@param[in,out] p_angleSteeringWheelMax [rad] max steering wheel angle
@param[in,out] p_vDriver         [m/s]   target velocity for driver
@param[in,out] p_Tintegration    [s]     feedback integration time constant
@param[in,out] p_Kfeedback       [s]     feedback constant
@param[in,out] p_brakepedalStandstill [] standstill value of the brakepdal (used if p_vDriver == 0)
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CDriverDoc
{
    const auto o_angleSteeringWheel = "[rad]  steering wheel angle";
    const auto o_accelerator        = "[0..1] accelerator pedal state";
    const auto o_brakepedal         = "[0..1] brake pedal state";
    const auto o_MDriverRequest     = "[N/m] torque request driver";

    const auto p_vFactor            = "[1/s] velocity factor for transforming ego velocity to predictive distance";
    const auto p_vOffset            = "[m] offset for transforming ego velocity to predictive distance";
    const auto p_yawFactor          = "[m/rad] yaw angle factor for transforming ego velocity to predictive distance";
    const auto p_angleFactor        = "[] factor course relative angle and angle steering wheel";
    const auto p_angleSteeringWheelMax = "[rad] max steering wheel angle";
    const auto p_vDriver            = "[m/s] target velocity for driver";
    const auto p_Tintegration       = "[s] feedback integration time constant";
    const auto p_Kfeedback          = "[s] feedback constant";
    const auto p_brakepedalStandstill = "[] standstill value of the brakepdal (used if p_vDriver == 0)";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/world/roadNetwork/CRoadNetwork.h>

class CDriver : public CModule<2>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CDriver();
    virtual ~CDriver();
private:
    CDriver( const CDriver& obj ) = delete;

    //*******************************
    //classes
    //*******************************
private:
    CRoadNetwork* m_roadNetwork_p;

    //*******************************
    //messages
    //*******************************
public:
    CMessageOutput<CFloat> o_angleSteeringWheel;
    CMessageOutput<CFloat> o_accelerator;
    CMessageOutput<CFloat> o_brakepedal;
    CMessageOutput<CFloat> o_MDriverRequest;

    CMessageParameter<CFloat> p_vFactor;
    CMessageParameter<CFloat> p_vOffset;
    CMessageParameter<CFloat> p_yawFactor;
    CMessageParameter<CFloat> p_angleFactor;
    CMessageParameter<CFloat> p_angleSteeringWheelMax;
    CMessageParameter<CFloat> p_vDriver;
    CMessageParameter<CFloat> p_Tintegration;
    CMessageParameter<CFloat> p_Kfeedback;
    CMessageParameter<CFloat> p_brakepedalStandstill;

private:
    CMessageInput<CFloat> i_velocity;
    CMessageInput<CFloatVectorXYZ> i_vChassis;
    CMessageInput<CFloat> i_m;
    CMessageInput<CFloat> i_rWheel;
    CMessageInput<CFloat> i_Mmax;
    CMessageInput<CFloatVectorXYZ> i_xyzWorld;
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYaw;
    CMessageInput<CFloat> i_coursePosition; // meters from beginning of course to point on course
    CMessageInput<CInt> i_road;
    CMessageInput<CInt> i_lane;
    CMessageInput<CFloat> i_lateralOffset;
    CMessageInput<CFloat> i_targetLateralOffset;
    CMessageInput<CFloat> i_lateralVelocity;
    CMessageInput<CBool> i_staticSimulation;
    CMessageInput<CFloat> i_angleSteeringWheel;
    CMessageInput<CBool> i_angleSteeringWheelAuto;                // [bool]  switch steering wheel angle between simulated driver or manual input
    CMessageInput<CBool> i_acceleratorAuto;
    CMessageInput<CBool> i_brakepedalAuto;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_velocity,
               IMessage<CFloatVectorXYZ>& f_vChassis,
               IMessage<CFloat>& f_m,
               IMessage<CFloat>& f_rWheel,
               IMessage<CFloat>& f_Mmax,
               IMessage<CFloatVectorXYZ>& f_xyzWorld,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYaw,
               IMessage<CFloat>& f_coursePosition,
               IMessage<CInt>& f_road,
               IMessage<CInt>& f_lane,
               IMessage<CFloat>& f_lateralOffset,
               IMessage<CFloat>& f_targetLateralOffset,
               IMessage<CFloat>& f_lateralVelocity,
               CRoadNetwork& f_roadNetwork_r,
               IMessage<CBool>& f_staticSimulation,
               IMessage<CFloat>& f_angleSteeringWheel,
               IMessage<CBool>& f_angleSteeringWheelAuto,
               IMessage<CBool>& f_acceleratorAuto,
               IMessage<CBool>& f_brakepedalAuto );
private:
    void calcPre( CFloat f_dT, CFloat f_time );
    CFloatVector& ddt( CFloatVector& state );
    void calcPost( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
private:
    enum { input, LATERALOFFSET, NumberOfStates };

    /* internal variable */
    // future point on course
    CFloat m_x, m_y, m_z;           // x,y,z-values of point on course
    CFloat m_x_lateral, m_y_lateral;// x,y-values of point on course
    CFloat m_dx, m_dy, m_dz;        // dx,dy,dz-value of point on course

    CFloat m_xTemp, m_yTemp;
    CFloat m_relativeDist, m_absolutePos;
    CFloat m_dLateralOffset;        // deviation from lateral offset target
    CFloat m_delta;                 // angle between vehicle direction of movement and future point

    // Control element. Input = delta v , Outputs = accelerator pedal, brake pedal
    CFloat m_Kfeedback; // helper variable for feedback constant conversion
    // p_Tintegration and p_Kfeedback are public

    CFloat m_errorSignal;           // error signal used for speed control: deviation between setpoint and current value
    CFloat m_integratedErrorSignal; // summed up error signal
};

#endif //_CDRIVER_H_
