#ifndef CStaticTwoWheeler_H
#define CStaticTwoWheeler_H
/*!
********************************************************************************
@class CStaticTwoWheeler
@ingroup chassis
@brief static model of a twowheeler

@author Robert Erhart, ett2si (20.12.2004 - 00:00:00)
@author Andreas Brunner, bnr2lr (24.05.2019)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
********************************************************************************
@remark
- twowheeler definition
@verbatim
            front
               0
               ^ x
               |
               |
       y <-----. Center of Gravity (h = height over the street)
               |
               |
               0
             rear
@endverbatim

- the influence of an moving Centre of Gravity at pitching and rolling is ignored
- only longitudinal component of air resistance is used
********************************************************************************
@param[in] i_FzFrontSuspension          [N]   vertical suspension force front
@param[in] i_FFrontWheelLateral         [N]   constructive lateral force wheel front
@param[in] i_RvFFrontWheelLateral       [N]   destructive  lateral force wheel front
@param[in] i_FFrontWheelLongitudinal    [N]   constructive longitudinal force wheel front
@param[in] i_RvFFrontWheelLongitudinal  [N]   destructive longitudinal force wheel front
@param[in] i_FzRearSuspension           [N]   vertical suspension force rear
@param[in] i_FRearWheelLateral          [N]   constructive lateral force wheel rear
@param[in] i_RvFRearWheelLateral        [N]   destructive lateral force wheel rear
@param[in] i_FRearWheelLongitudinal     [N]   constructive longitudinal force wheel rear
@param[in] i_RvFRearWheelLongitudinal   [N]   destructive longitudinal force wheel rear
@param[in] i_FairResistance                 [N]   air resistance force
@param[in] i_wheelAngleFront                [rad] steered wheel angle (front)
@param[in] i_wheelAngleRear                 [rad] steered wheel angle (rear)
@param[in] i_beta                           [rad] sideslip angle
@param[in] i_xWheelFront                [m]   x wheel suspension position front
@param[in] i_yWheelFront                [m]   y wheel suspension position front
@param[in] i_xWheelRear                 [m]   x wheel suspension position rear
@param[in] i_yWheelRear                 [m]   y wheel suspension position rear
@param[in] i_h                              [m]   centre of gravity height
@param[in] i_m                              [kg]  vehicle mass
@param[in] i_angleRollPitchYawSurface [rad] roll, pitch, yaw angle world -> vehicle coordinate system (positiv: right handed)
@param[in] i_angleRollPitchYawSuspension    [rad] roll, pitch, yaw angle
@param[in] i_FxyzArticulation               [m] articulation x,y,z force vector (input from connected chassis, other chassis coordinate system)
@param[in] i_xyzArticulation                [m] articulation x,y,z position vector(vehicle coordinate system)
********************************************************************************
@param[out] o_FChassis                      [N] constructive longitudinal force at the centre of gravity (vehicle coordinate-system)
@param[out] o_FvRChassis                    [N] destructive longitudinal force at the centre of gravity (vehicle coordinate-system)
@param[out] o_Fn                            [N] gravitational force at the centre of gravity
@param[out] o_MRollPitchYawChassis          [Nm] constructive yaw torque at the centre of gravity (positive: counterclockwise direction)
@param[out] o_MvRRollPitchYawChassis        [Nm] destructive yaw torque at the centre of gravity (positive: counterclockwise direction)
********************************************************************************
@param[in,out] p_g                         [m/s²] acceleration of free fall (gravity)
********************************************************************************
@todo rename wheel in suspension?
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CStaticTwoWheelerDoc
{
    const auto o_FChassis         = "[N] constructive longitudinal force at the centre of gravity (vehicle coordinate-system)";
    const auto o_FvRChassis       = "[N] destructive longitudinal force at the centre of gravity (vehicle coordinate-system)";
    const auto o_Fn               = "[N] gravitational force at the centre of gravity";
    const auto o_MRollPitchYawChassis  = "[Nm] constructive yaw torque at the centre of gravity (positive: counterclockwise direction)";
    const auto o_MvRRollPitchYawChassis = "[Nm] destructive yaw torque at the centre of gravity (positive: counterclockwise direction)";
    const auto p_g                = "[m/s²] acceleration of free fall (gravity)";
}

#include <claraSim/framework/CModule.h>

////*********************************
//// CStaticTwoWheeler
////*********************************
class CStaticTwoWheeler : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CStaticTwoWheeler();
    virtual ~CStaticTwoWheeler();

    //*******************************
    //classes
    //*******************************

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloatVectorXYZ> o_FChassis;
    CMessageOutput<CFloatVectorXYZ> o_FvRChassis;
    CMessageOutput<CFloat> o_Fn;
    CMessageOutput<CFloatVectorXYZ> o_MRollPitchYawChassis;
    CMessageOutput<CFloatVectorXYZ> o_MvRRollPitchYawChassis;
    CMessageOutput<CFloat> o_FzFront;
    CMessageOutput<CFloat> o_FzRear;
    /* parameter */
    CMessageParameter<CFloat> p_g;

private:
    /* input */
    CMessageInput<CFloat> i_FzFrontSuspension;
    CMessageInput<CFloat> i_FFrontWheelLateral;
    CMessageInput<CFloat> i_RvFFrontWheelLateral;
    CMessageInput<CFloat> i_FFrontWheelLongitudinal;
    CMessageInput<CFloat> i_RvFFrontWheelLongitudinal;
    CMessageInput<CFloat> i_FzRearSuspension;
    CMessageInput<CFloat> i_FRearWheelLateral;
    CMessageInput<CFloat> i_RvFRearWheelLateral;
    CMessageInput<CFloat> i_FRearWheelLongitudinal;
    CMessageInput<CFloat> i_RvFRearWheelLongitudinal;
    CMessageInput<CFloat> i_FairResistance;
    CMessageInput<CFloat> i_wheelAngleFront;
    CMessageInput<CFloat> i_wheelAngleRear;
    CMessageInput<CFloat> i_beta;
    CMessageInput<CFloat> i_xWheelFront;
    CMessageInput<CFloat> i_yWheelFront;
    CMessageInput<CFloat> i_xWheelRear;
    CMessageInput<CFloat> i_yWheelRear;
    CMessageInput<CFloat> i_h;
    CMessageInput<CFloat> i_m;
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYawSurface;
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYawSuspension;
    CMessageInput<CFloatVectorXYZ> i_FxyzArticulation;
    CMessageInput<CFloatVectorXYZ> i_xyzArticulation;

    //*******************************
    // methods
    //*******************************


public:
    void init( IMessage<CFloat>& f_FzFrontSuspension,
               IMessage<CFloat>& f_FFrontWheelLateral,
               IMessage<CFloat>& f_RvFFrontWheelLateral,
               IMessage<CFloat>& f_FFrontWheelLongitudinal,
               IMessage<CFloat>& f_RvFFrontWheelLongitudinal,
               IMessage<CFloat>& f_FzRearSuspension,
               IMessage<CFloat>& f_FRearWheelLateral,
               IMessage<CFloat>& f_RvFRearWheelLateral,
               IMessage<CFloat>& f_FRearWheelLongitudinal,
               IMessage<CFloat>& f_RvFRearWheelLongitudinal,
               IMessage<CFloat>& f_FairResistance,
               IMessage<CFloat>& f_wheelAngleFront,
               IMessage<CFloat>& f_wheelAngleRear,
               IMessage<CFloat>& f_beta,
               IMessage<CFloat>& f_xWheelFront,
               IMessage<CFloat>& f_yWheelFront,
               IMessage<CFloat>& f_xWheelRear,
               IMessage<CFloat>& f_yWheelRear,
               IMessage<CFloat>& f_h,
               IMessage<CFloat>& f_m,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSurface,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSuspension,
               IMessage<CFloatVectorXYZ>& f_FxyzArticulation,
               IMessage<CFloatVectorXYZ>& f_xyzArticulation );
private:
    void calc( CFloat f_dT, CFloat f_time );
    inline void transformWheelForce( CFloat& f_Fx, CFloat& f_Fy, CFloat f_FWheelLongitudinal, CFloat f_FWheelLateral, CFloat f_wheelAngle );

    //*******************************
    //variables
    //*******************************
public:
private:
    CFloat m_FxFront, m_FxRear;
    CFloat m_FyFront, m_FyRear;
    CFloat m_RvFxFront, m_RvFxRear;
    CFloat m_RvFyFront, m_RvFyRear;
    CFloat m_Fz, m_FxMass, m_FyMass;
    CFloat m_tau;
    CFloatVectorXYZ m_pF, m_pR;
    CFloatVectorXYZ m_fF, m_fR, m_fCoG;           // force vectors: constructive
    CFloatVectorXYZ m_RvfF, m_RvfR, m_RvfCoG; // force vectors: destructive
    CFloatVectorXYZ m_crossProductF, m_crossProductR, m_crossProductArticulation;
};
#endif // CStaticTwoWheeler_H
