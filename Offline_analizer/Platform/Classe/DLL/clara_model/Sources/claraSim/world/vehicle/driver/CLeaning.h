#ifndef _CLeaning_H_
#define _CLeaning_H_
/*!
********************************************************************************
@class CLeaning
@ingroup Leaning
@brief calculation of the leaning force actuated on the motorbike

@author Andreas Brunner, bnr2lr (18.07.2019)
@copyright (c) Robert Bosch GmbH 2019-2024. All rights reserved.
********************************************************************************
@f$
 F = c * (thetaTheo + theta + thetaBody)
 thetas = roll angles\\
 thetaTheo = arctan( v^2/(g R) )\\
 v: longitudinal velocity\\
 g: gravitational constant\\
 R: curve radius\\
 R = wheelbase / (steeringAngle * cos(casterAngle) )\\
@f$

********************************************************************************
@param[in] i_steeringAngle               [rad]   steering angle
@param[in] i_vChassis                    [m/s]   two wheeler velocity (vehicle coordinate system)
@param[in] i_angleRollPitchYaw          [rad]   course-induced (roll,pitch,yaw) angle vector of the two-wheeler
@param[in] i_xFront                      [m]     front wheel position
@param[in] i_xRear                       [m]     rear wheel position
@param[in] i_casterAngle                 [rad]   front wheel caster angle
********************************************************************************
@param[in,out] p_TLowPass                [s]     output force and angle low pass time constant
********************************************************************************
********************************************************************************
@param[out] o_rollAngle                  [rad]   optimal motorbike (chassis) roll angle
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CLeaningDoc
{
    const auto o_rollAngle   = "[rad]   optimal motorbike (chassis) roll angle";

    const auto p_TLowPass    = "[s]     output force and angle low pass time constant";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/framework/CLowPass.h>


////*********************************
//// CLeaning
////*********************************
class CLeaning : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CLeaning();
    virtual ~CLeaning();

    //*******************************
    //classes
    //*******************************
public:
private:
    CLowPass LowPassTheta;
    CLowPass LowPassDeltaTheta;

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloat> o_rollAngle;

    /* parameter */
    CMessageParameter<CFloat> p_TLowPass;
    CMessageParameter<CFloat> p_C_force;


private:
    CMessageInput<CFloat> i_steeringAngle;
    CMessageInput<CFloatVectorXYZ> i_vChassis;
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYaw;
    CMessageInput<CFloat> i_xFront;
    CMessageInput<CFloat> i_xRear;
    CMessageInput<CFloat> i_sideslipAngleFront;
    CMessageInput<CFloat> i_sideslipAngleRear;
    CMessageInput<CFloat> i_casterAngle;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_steeringAngle,
               IMessage<CFloatVectorXYZ>& f_vChassis,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYaw,
               IMessage<CFloat>& f_xFront,
               IMessage<CFloat>& f_xRear,
               IMessage<CFloat>& f_sideslipAngleFront,
               IMessage<CFloat>& f_sideslipAngleRear,
               IMessage<CFloat>& f_casterAngle );
private:
    void calc( CFloat f_dT, CFloat f_time );
    void calcPre( CFloat f_dT, CFloat f_time );
    void calcPost( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
private:
    CFloat m_theta, m_thetaLean, m_thetaTrack, m_thetaChassis;
};

#endif //_CLeaning_H_
