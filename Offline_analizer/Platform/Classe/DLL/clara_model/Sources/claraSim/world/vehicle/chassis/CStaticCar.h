#ifndef CStaticCar_H
#define CStaticCar_H
/*!
********************************************************************************
@class CStaticCar
@ingroup chassis
@brief static model of a two track vehicle

@author Robert Erhart, ett2si (20.12.2004 - 00:00:00)
@author Andreas Brunner, bnr2lr (24.05.2019)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
********************************************************************************
@remark
- car definition:
@verbatim
              leftFront    rightFront
                 0-----------0
                       ^ x
                       |
                       |
               y <-----. Centre of Gravity (h = height over the street)
                       |
                       |
                 o------------o
              leftRear     rightRear
@endverbatim

- the influence of an moving Centre of Gravity at pitching and rolling is ignored
- only longitudinal component of air resistance is used
********************************************************************************
@param[in] i_FzLeftFrontSuspension          [N]   vertical suspension force left-front
@param[in] i_FLeftFrontWheelLateral         [N]   constructive lateral force wheel left-front
@param[in] i_RvFLeftFrontWheelLateral       [N]   destructive  lateral force wheel left-front
@param[in] i_FLeftFrontWheelLongitudinal    [N]   constructive longitudinal force wheel left-front
@param[in] i_RvFLeftFrontWheelLongitudinal  [N]   destructive longitudinal force wheel left-front
@param[in] i_FzRightFrontSuspension         [N]   vertical suspension force right-front
@param[in] i_FRightFrontWheelLateral        [N]   constructive lateral force wheel right-front
@param[in] i_RvFRightFrontWheelLateral      [N]   destructive lateral force wheel right-front
@param[in] i_FRightFrontWheelLongitudinal   [N]   constructive longitudinal force wheel right-front
@param[in] i_RvFRightFrontWheelLongitudinal [N]   destructive longitudinal force wheel right-front
@param[in] i_FzLeftRearSuspension           [N]   vertical suspension force left-rear
@param[in] i_FLeftRearWheelLateral          [N]   constructive lateral force wheel left-rear
@param[in] i_RvFLeftRearWheelLateral        [N]   destructive lateral force wheel left-rear
@param[in] i_FLeftRearWheelLongitudinal     [N]   constructive longitudinal force wheel left-rear
@param[in] i_RvFLeftRearWheelLongitudinal   [N]   destructive longitudinal force wheel left-rear
@param[in] i_FzRightRearSuspension          [N]   vertical suspension force right-rear
@param[in] i_FRightRearWheelLateral         [N]   constructive lateral force wheel right-rear
@param[in] i_RvFRightRearWheelLateral       [N]   destructive lateral force wheel right-rear
@param[in] i_FRightRearWheelLongitudinal    [N]   constructive longitudinal force wheel right-rear
@param[in] i_RvFRightRearWheelLongitudinal  [N]   destructive longitudinal force wheel right-rear
@param[in] i_FairResistance                 [N]   air resistance force
@param[in] i_wheelAngleFront                [rad] steered wheel angle (front)
@param[in] i_wheelAngleRear                 [rad] steered wheel angle (rear)
@param[in] i_beta                           [rad] sideslip angle
@param[in] i_xWheelLeftFront                [m]   x wheel suspension position left-front
@param[in] i_yWheelLeftFront                [m]   y wheel suspension position left-front
@param[in] i_xWheelRightFront               [m]   x wheel suspension position right-front
@param[in] i_yWheelRightFront               [m]   y wheel suspension position right-front
@param[in] i_xWheelLeftRear                 [m]   x wheel suspension position left-rear
@param[in] i_yWheelLeftRear                 [m]   y wheel suspension position left-rear
@param[in] i_xWheelRightRear                [m]   x wheel suspension position right-rear
@param[in] i_yWheelRightRear                [m]   y wheel suspension position right-rear
@param[in] i_h                              [m]   centre of gravity height
@param[in] i_m                              [kg]  vehicle mass
@param[in] i_angleRollPitchYawSurface       [rad] roll, pitch, yaw angle of road surface (world coordinate system)
@param[in] i_angleRollPitchYawSuspension    [rad] roll, pitch, yaw angle of chassis <-> road surface
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
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CStaticCarDoc
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
//// CStaticCar
////*********************************
class CStaticCar : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CStaticCar();
    virtual ~CStaticCar();

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
    CMessageOutput<CFloat> o_FzLeftFront;
    CMessageOutput<CFloat> o_FzRightFront;
    CMessageOutput<CFloat> o_FzLeftRear;
    CMessageOutput<CFloat> o_FzRightRear;
    /* parameter */
    CMessageParameter<CFloat> p_g;

private:
    /* input */
    CMessageInput<CFloat> i_FzLeftFrontSuspension;
    CMessageInput<CFloat> i_FLeftFrontWheelLateral;
    CMessageInput<CFloat> i_RvFLeftFrontWheelLateral;
    CMessageInput<CFloat> i_FLeftFrontWheelLongitudinal;
    CMessageInput<CFloat> i_RvFLeftFrontWheelLongitudinal;
    CMessageInput<CFloat> i_FzRightFrontSuspension;
    CMessageInput<CFloat> i_FRightFrontWheelLateral;
    CMessageInput<CFloat> i_RvFRightFrontWheelLateral;
    CMessageInput<CFloat> i_FRightFrontWheelLongitudinal;
    CMessageInput<CFloat> i_RvFRightFrontWheelLongitudinal;
    CMessageInput<CFloat> i_FzLeftRearSuspension;
    CMessageInput<CFloat> i_FLeftRearWheelLateral;
    CMessageInput<CFloat> i_RvFLeftRearWheelLateral;
    CMessageInput<CFloat> i_FLeftRearWheelLongitudinal;
    CMessageInput<CFloat> i_RvFLeftRearWheelLongitudinal;
    CMessageInput<CFloat> i_FzRightRearSuspension;
    CMessageInput<CFloat> i_FRightRearWheelLateral;
    CMessageInput<CFloat> i_RvFRightRearWheelLateral;
    CMessageInput<CFloat> i_FRightRearWheelLongitudinal;
    CMessageInput<CFloat> i_RvFRightRearWheelLongitudinal;
    CMessageInput<CFloat> i_FairResistance;
    CMessageInput<CFloat> i_wheelAngleFront;
    CMessageInput<CFloat> i_wheelAngleRear;
    CMessageInput<CFloat> i_beta;
    CMessageInput<CFloat> i_xWheelLeftFront;
    CMessageInput<CFloat> i_yWheelLeftFront;
    CMessageInput<CFloat> i_xWheelRightFront;
    CMessageInput<CFloat> i_yWheelRightFront;
    CMessageInput<CFloat> i_xWheelLeftRear;
    CMessageInput<CFloat> i_yWheelLeftRear;
    CMessageInput<CFloat> i_xWheelRightRear;
    CMessageInput<CFloat> i_yWheelRightRear;
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
    void init( IMessage<CFloat>& f_FzLeftFrontSuspension,
               IMessage<CFloat>& f_FLeftFrontWheelLateral,
               IMessage<CFloat>& f_RvFLeftFrontWheelLateral,
               IMessage<CFloat>& f_FLeftFrontWheelLongitudinal,
               IMessage<CFloat>& f_RvFLeftFrontWheelLongitudinal,
               IMessage<CFloat>& f_FzRightFrontSuspension,
               IMessage<CFloat>& f_FRightFrontWheelLateral,
               IMessage<CFloat>& f_RvFRightFrontWheelLateral,
               IMessage<CFloat>& f_FRightFrontWheelLongitudinal,
               IMessage<CFloat>& f_RvFRightFrontWheelLongitudinal,
               IMessage<CFloat>& f_FzLeftRearSuspension,
               IMessage<CFloat>& f_FLeftRearWheelLateral,
               IMessage<CFloat>& f_RvFLeftRearWheelLateral,
               IMessage<CFloat>& f_FLeftRearWheelLongitudinal,
               IMessage<CFloat>& f_RvFLeftRearWheelLongitudinal,
               IMessage<CFloat>& f_FzRightRearSuspension,
               IMessage<CFloat>& f_FRightRearWheelLateral,
               IMessage<CFloat>& f_RvFRightRearWheelLateral,
               IMessage<CFloat>& f_FRightRearWheelLongitudinal,
               IMessage<CFloat>& f_RvFRightRearWheelLongitudinal,
               IMessage<CFloat>& f_FairResistance,
               IMessage<CFloat>& f_wheelAngleFront,
               IMessage<CFloat>& f_wheelAngleRear,
               IMessage<CFloat>& f_beta,
               IMessage<CFloat>& f_xWheelLeftFront,
               IMessage<CFloat>& f_yWheelLeftFront,
               IMessage<CFloat>& f_xWheelRightFront,
               IMessage<CFloat>& f_yWheelRightFront,
               IMessage<CFloat>& f_xWheelLeftRear,
               IMessage<CFloat>& f_yWheelLeftRear,
               IMessage<CFloat>& f_xWheelRightRear,
               IMessage<CFloat>& f_yWheelRightRear,
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
    CFloat m_FxLeftFront, m_FxRightFront, m_FxLeftRear, m_FxRightRear;
    CFloat m_FyLeftFront, m_FyRightFront, m_FyLeftRear, m_FyRightRear;
    CFloat m_RvFxLeftFront, m_RvFxRightFront, m_RvFxLeftRear, m_RvFxRightRear, m_RvFyLeftFront;
    CFloat m_RvFyRightFront, m_RvFyLeftRear, m_RvFyRightRear;
    CFloat m_Fz, m_FxMass, m_FyMass;
    CFloat m_tau;
    CFloatVectorXYZ m_pLF, m_pLR, m_pRF, m_pRR;
    CFloatVectorXYZ m_fLF, m_fLR, m_fRF, m_fRR, m_fCoG;           // force vectors: constructive
    CFloatVectorXYZ m_RvfLF, m_RvfLR, m_RvfRF, m_RvfRR, m_RvfCoG; // force vectors: destructive
    CFloatVectorXYZ m_crossProductLF, m_crossProductLR, m_crossProductRF, m_crossProductRR, m_crossProductArticulation;
};
#endif // CStaticCar_H
