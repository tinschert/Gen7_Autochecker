#ifndef CDYNAMIC_H
#define CDYNAMIC_H
/*!
********************************************************************************
@class CDynamic
@ingroup chassis
@brief simulation of horizontal and vertical car dynamic (equation of state)

@author Robert Erhart, ett2si (12.10.2004 - 00:00:00)
@author Andreas Brunner, bnr2lr (27.05.2019)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
********************************************************************************
@remark
- for more information see diploma thesis of Robert Erhart
    + (1) Fx = -m v (beta_ddt + yawRate) sin(beta) + m v_ddt cos(beta)
    + (2) Fy = m v (beta_ddt + yawRate) cos(beta) + m v_ddt sin(beta)
    + (3) Msp = J yawRate_ddt

- after a transformation you get the typical equation:
    + yawRate_ddt  = M_sp / J
    + velocity_ddt = ( F_x * cos(beta_s) + F_y * sin(beta_s) ) / m
    + beta_ddt     = -yawRate_s + (-F_x * sin(beta_s) + F_y * cos(beta_s)) / (m * velocity_s)

- for numerical simulation is the following equation better:
    + target: transform beta and velocity to velocityX and velocityY
      vX = v cos(beta) =>
      (4) vX_ddt = v_ddt cos(beta) - v sin(beta) beta_ddt

- vY = v sin(beta) =>
    + (5) vY_ddt = v_ddt sin(beta) + v cos(beta) beta_ddt

- you get:
    + (4) and (1):\n
      vX_ddt = Fx/m + yawRate * vY

    + (5) and (2):\n
      vY_ddt = Fy/m - yawRate * vX

- (3):
    + yawRate = Msp / J
********************************************************************************
@param[in] i_FChassis              [N]     longitudinal force at the centre of gravity (vehicle coordinate system)
@param[in] i_FvRChassis            [N]     destructive longitudinal force at the centre of gravity (vehicle coordinate system)
@param[in] i_MRollPitchYawChassis  [Nm]    torque at the centre of gravity
@param[in] i_MvRRollPitchYawChassis[Nm]    destructive torque at the centre of gravity (positive: counterclockwise) (vehicle coordinate system)
@param[in] i_m                     [kg]    vehicle mass
@param[in] i_JRollPitchYawChassis  [kg m²] moment of inertia X,Y,Z-axis (roll, pitch, yaw)
@param[in] i_setRollAngle          [rad]   externally set (forced) roll angle
@param[in] i_staticSimulation      [bool]
********************************************************************************
@param[out] o_zChassis               [m]     centre of gravity height
@param[out] o_velocity               [m/s]   total velocity at the centre of gravity (chassis coordinate system)
@param[out] o_acceleration           [m/s²]  total acceleration at the centre of gravity (chassis coordinate system)";
@param[out] o_beta                   [rad]   sideslip angle at the centre of gravity (chassis coordinate system)
@param[out] o_vChassis               [m/s]   X,Y,Z velocities at the centre of gravity (chassis coordinate system)
@param[out] o_aChassis               [m/s²]  X,Y,Z acceleration at the centre of gravity (chassis coordinate system)
@param[out] o_rateRollPitchYawChassis[rad/s] roll, pitch, and yaw rate at the centre of gravity (chassis coordinate system)
@param[out] o_angleRollPitchYawSuspension["[rad] (roll, pitch, yaw=0) angles of the chassis (street x-y plane coordinate system)"
********************************************************************************
@param[in,out] p_overrideDynamic  [bool]  override horizontal dynamic and use p_velocityXStatic
@param[in,out] p_velocityXStatic  [m/s]   longitudinal car velocity, if p_overrideDynamic = True
@param[in,out] p_forceRollAngle   [bool]  force roll angle to externally given i_setRollAngle, only relevant for two wheeler
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CDynamicDoc
{
    const auto o_zChassis         = "[m]   centre of gravity height";
    const auto o_velocity         = "[m/s] total velocity at the centre of gravity (chassis coordinate system)";
    const auto o_acceleration     = "[m/s²] total acceleration at the centre of gravity (chassis coordinate system)";
    const auto o_vChassis         = "[m/s] (vector) X,Y,Z velocities at the centre of gravity (chassis coordinate system)";
    const auto o_aChassis         = "[m/s²] (vector) X,Y,Z acceleration at the centre of gravity (chassis coordinate system)";
    const auto o_rateRollPitchYawChassis = "[rad/s] (vector) roll, pitch, and yaw rate at the centre of gravity (chassis coordinate system)";
    const auto o_beta             = "[rad] sideslip angle at the centre of gravity (chassis coordinate system)";
    const auto o_angleRollPitchYawSuspension = "[rad] (roll, pitch, yaw=0) angles of the chassis (street x-y plane coordinate system)";
    const auto p_overrideDynamic  = "[bool] override horizontal dynamic and use p_velocityXStatic";
    const auto p_velocityXStatic  = "[m/s] longitudinal car velocity, if p_overrideDynamic = True";
    const auto p_forceRollAngle   = "[bool] force roll angle to externally given i_setRollAngle";
}

#include <claraSim/framework/CModule.h>

////*********************************
//// CDynamic
////*********************************
class CDynamic : public CModule<9>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CDynamic();
    virtual ~CDynamic();

    //*******************************
    //classes
    //*******************************
public:
    enum { VELOCITYx, VELOCITYy, VELOCITYz, YAWRATE, ROLLRATE, PITCHRATE,
           PITCHANGLE, ROLLANGLE, ZChassis, NumberOfStates
         };

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloatVectorXYZ> o_aChassis;
    CMessageOutput<CFloatVectorXYZ> o_vChassis;  // state output
    CMessageOutput<CFloat> o_beta;
    CMessageOutput<CFloat> o_velocity;
    CMessageOutput<CFloat> o_acceleration;
    CMessageOutput<CFloat> o_zChassis;   // state output
    CMessageOutput<CFloatVectorXYZ> o_rateRollPitchYawChassis;
    CMessageOutput<CFloatVectorXYZ> o_angleRollPitchYawSuspension; // (roll, pitch, 0) state output
    /* parameter */
    CMessageParameter<CBool> p_overrideDynamic;
    CMessageParameter<CFloat> p_velocityXStatic;
    CMessageParameter<CBool> p_forceRollAngle;
private:
    /* input */
    CMessageInput<CFloatVectorXYZ> i_FChassis;
    CMessageInput<CFloatVectorXYZ> i_FvRChassis;
    CMessageInput<CFloatVectorXYZ> i_MRollPitchYawChassis;
    CMessageInput<CFloatVectorXYZ> i_MvRRollPitchYawChassis;
    CMessageInput<CFloat> i_m;
    CMessageInput<CFloatVectorXYZ> i_JRollPitchYawChassis;
    CMessageInput<CFloat> i_setRollAngle;
    CMessageInput<CBool> i_staticSimulation;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloatVectorXYZ>& f_FChassis,
               IMessage<CFloatVectorXYZ>& f_FvRChassis,
               IMessage<CFloatVectorXYZ>& f_MRollPitchYawChassis,
               IMessage<CFloatVectorXYZ>& f_MvRRollPitchYawChassis,
               IMessage<CFloat>& f_m,
               IMessage<CFloatVectorXYZ>& f_JRollPitchYawChassis,
               IMessage<CFloat>& f_setRollAngle,
               IMessage<CBool>& f_staticSimulation );
private:
    void calcPre( CFloat f_dT, CFloat f_time );
    CFloatVector& ddt( CFloatVector& state );
    void calcPost( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
    CFloatVectorXYZ m_F;
    CBool  m_FxDestructive, m_FyDestructive, m_FzDestructive;
    CFloatVectorXYZ m_M;
    CBool  m_MyawDestructive, m_MrollDestructive, m_MpitchDestructive;
    CFloat m_VELOCITYxK1, m_VELOCITYyK1;
    CFloat m_YAWRATEK1;
    CFloat m_rollAngleK1;
};

#endif //_CDYNAMIC_H_
