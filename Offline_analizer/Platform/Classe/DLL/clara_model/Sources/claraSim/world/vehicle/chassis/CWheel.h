#ifndef CWHEEL_H
#define CWHEEL_H
/*!
********************************************************************************
@class CWheel
@ingroup chassis
@brief Simulation of simple wheel model

@author Robert Erhart, ett2si (12.10.2004 - 00:00:00)
@author Andreas Brunner, bnr2lr (2020)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
********************************************************************************
@remark
- Reverse, longitudinal force: rolling resistance:
    + @f$ F_rr = p_rollResistCoefficent * i_Fz @f$
- Reverse, lateral force (type 1): segmented linear model (default; currently implemented and used)
    + @f$ RvFLateral = p_C * i_alpha @f$
- Reverse, lateral force (type 2): Pacejka model (currently NOT used):
    + @f$ RvFLateral = A * sin( B * atan(C*alpha) ) @f$
    + @f$ A = my * Fvertical @f$

- Circle of Forces (Kammscher Kreis)
     + superposition of lateral and longitudinal force
     + @f$ F^2 = Flateral^2 + Flongitudinal^2 @f$
     + theorem of intersecting lines
********************************************************************************
@param[in] i_alpha            [rad]   tire slip angle
@param[in] i_camberAngle      [rad]   tire camber angle
@param[in] i_Fvertical        [N]     vertical force at wheel
@param[in] i_MWheel           [Nm]    drive torque
@param[in] i_RvMWheel         [Nm]    brake torque
@param[in] i_vXwheel          [m/s]   longitudinal wheel velocity (wheel axis system)
@param[in] i_vYwheel          [m/s]   lateral wheel velocity (wheel axis system)
@param[in] i_my               [ ]     street coefficient of friction (limits maximum vertical force)
********************************************************************************
@param[out] o_FrollResistance [N]     longitudinal rolling resistance
@param[out] o_FLongitudinal   [N]     constructive longitudinal force wheel (wheel coordinate-system)
@param[out] o_RvFLongitudinal [N]     destructive longitudinal force wheel (wheel coordinate-system)
@param[out] o_FLateral        [N]     constructive lateral force wheel (wheel coordinate-system)
@param[out] o_RvFLateral      [N]     destructive lateral force wheel (wheel coordinate-system)
@param[out] o_FmaxWheel       [N]     max force wheel
@param[out] o_nWheel          [rpm]   wheel rpm
@param[out] o_omega           [rad/s] rotating velocity
@param[out] o_wheelPlsCnt     [0,255] wheel pulse counter (0..255)
********************************************************************************
@param[in,out] p_rollResistCoefficent [m²]   rolling coefficient
@param[in,out] p_rWheel               [m]     wheel radius
@param[in,out] p_B                    [-]     factor for Pacejka model
@param[in,out] p_C                    [N/rad] cornering stiffness
@param[in,out] p_camberCoefficient    [rad]   coefficient between camber force, load, and camber angle
@param[in,out] p_wheelPlsTeeth        [1-n]   number of teeth of wheel pulse counter
@param[in,out] p_wheelPlsRangeMax     [n]     max of wheel pulse counter
@param[in,out] p_wheelPlsRangeMin     [n]     min of wheel pulse counter
@param[in,out] p_omegaAcceleration    [m/s^2] delta omega acceleration
********************************************************************************
@todo Numeric problem lateral force at low speed -> 0; Change model to Ackermann angle
@todo Implement lateral force (type 2): Pacejka model
@todo Make sideslip calculation load-dependent
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CWheelDoc
{
    const auto o_FrollResistance    = "[N] longitudinal rolling resistance";
    const auto o_FLongitudinal      = "[N] constructive longitudinal force wheel (wheel coordinate-system)";
    const auto o_RvFLongitudinal    = "[N] destructive longitudinal force wheel (wheel coordinate-system)";
    const auto o_FLateral           = "[N] constructive lateral force wheel (wheel coordinate-system)";
    const auto o_RvFLateral         = "[N] destructive lateral force wheel (wheel coordinate-system)";
    const auto o_FmaxWheel          = "[N] max force wheel (wheel coordinate-system)";
    const auto o_nWheel             = "[rpm] wheel rpm";
    const auto o_omega              = "[rad/s] rotating velocity";
    const auto o_wheelPlsCnt        = "[n] wheel pulse counter (0..255)";
    const auto p_rollResistCoefficent = "[Cw] drag coefficient";
    const auto p_rWheel             = "[m] wheel radius";
    const auto p_B                  = "[-] factor for Pacejka model";
    const auto p_C                  = "[N/rad] cornering stiffness";
    const auto p_camberCoefficient  = "[rad] coefficient between camber force, load, and camber angle";
    const auto p_wheelPlsTeeth      = "[1-n] number of teeth of wheel pulse counter";
    const auto p_wheelPlsRangeMax   = "[n] max of wheel pulse counter";
    const auto p_wheelPlsRangeMin   = "[n] min of wheel pulse counter";
    const auto p_omegaAcceleration  = "[m/s^2] delta omega acceleration";
}

#include <claraSim/framework/CModule.h>

////*********************************
//// CWheel
////*********************************
class CWheel : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CWheel();
    virtual ~CWheel();

    //*******************************
    // classes
    //*******************************

    //*******************************
    // messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloat> o_FrollResistance;
    CMessageOutput<CFloat> o_FLongitudinal;
    CMessageOutput<CFloat> o_RvFLongitudinal;
    CMessageOutput<CFloat> o_FLateral;
    CMessageOutput<CFloat> o_RvFLateral;
    CMessageOutput<CFloat> o_FmaxWheel;
    CMessageOutput<CFloat> o_nWheel;
    CMessageOutput<CFloat> o_omega;
    CMessageOutput<CInt> o_wheelPlsCnt;
    /* parameter */
    CMessageParameter<CFloat> p_rollResistCoefficent;
    CMessageParameter<CFloat> p_rWheel;
    CMessageParameter<CFloat> p_B;
    CMessageParameter<CFloat> p_C;
    CMessageParameter<CFloat> p_camberCoefficient;
    CMessageParameter<CInt> p_wheelPlsTeeth;
    CMessageParameter<CInt> p_wheelPlsRangeMax;
    CMessageParameter<CInt> p_wheelPlsRangeMin;
    CMessageParameter<CFloat> p_omegaAcceleration;
private:
    /* input */
    CMessageInput<CFloat> i_alpha;
    CMessageInput<CFloat> i_camberAngle;
    CMessageInput<CFloat> i_Fvertical;
    CMessageInput<CFloat> i_MWheel;
    CMessageInput<CFloat> i_RvMWheel;
    CMessageInput<CFloat> i_vXwheel;
    CMessageInput<CFloat> i_vYwheel;
    CMessageInput<CFloat> i_my;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_alpha,
               IMessage<CFloat>& f_camberAngle,
               IMessage<CFloat>& f_Fvertical,
               IMessage<CFloat>& f_MWheel,
               IMessage<CFloat>& f_RvMWheel,
               IMessage<CFloat>& f_vXwheel,
               IMessage<CFloat>& f_vYwheel,
               IMessage<CFloat>& f_my );
private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
    CFloat m_Fcombined;
    CFloat m_Fsideslip, m_Fcamber;
    CFloat m_wheelPlsCnt;
    CFloat m_deltaOmega;
    CFloat m_velocity;
};

#endif // CWHEEL_H
