#ifndef CArticulation_H
#define CArticulation_H

/*!
********************************************************************************
@class CArticulation
@ingroup chassis
@brief articulation model to interface two vehicle's articulation forces

@author Andreas Brunner, bnr2lr (29.05.2019)
@copyright (c) Robert Bosch GmbH 2019-2024. All rights reserved.
********************************************************************************
@remark
Coordinate transform between two vehicles.
Free axis of the articulation is z axis. For simplicity, the articulation is now
assumed to be placed on the x axis of both chassis.
@verbatim

               0-----------0
                     ^ x
                     |
                     |
             y <-----. Centre of Gravity (h = height over the street)
                     |
                     |
               o------------o
                     |
                     |
                     O
                     :\
                     : \
                     :  \
                     |phi|

@endverbatim
********************************************************************************
@param[in] i_angleRollPitchYawFirstVehicle   [rad]    (roll, pitch, yaw) angle vector of first vehicle (vs. world)
@param[in] i_angleRollPitchYawSecondVehicle  [rad]    (roll, pitch, yaw) angle vector of second vehicle (vs. world)
@param[in] i_xyzFirstVehicle                  [N]      force vector in first vehicle's coordinate system
@param[in] i_xyzSecondVehicle                 [N]      force vector in second vehicle's coordinate system
@param[in] i_xyzArticulationFirstVehicle      [m]      position of the articulation in first vehicle's coordinate system (currently only x value used!)
@param[in] i_xyzArticulationSecondVehicle     [m]      position of the articulation in second vehicle's coordinate system (currently only x value used!)
@param[in] i_detach                       [bool]   detach articulation (if true: output forces will be zero)
********************************************************************************
@param[in,out] p_Kacceleration            [N s²/m]  force feedback constant for articulation distance acceleration (2nd derivative)
@param[in,out] p_Kvelocity                [N s/m]    force feedback constant for articulation distance velocity (1st derivative)
@param[in,out] p_Kdistance                [N/m]      force feedback constant for articulation distance
@param[in,out] p_Kintegrated              [N m s]    force feedback constant for integrated articulation distance
********************************************************************************
@param[out] o_FxyzFirstVehicle                [N]      resulting force on first vehicle: vector in first vehicle's coordinate system
@param[out] o_FxyzSecondVehicle               [N]      resulting force on second vehicle: vector in second vehicle's coordinate system
********************************************************************************
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CArticulationDoc
{
    const auto o_FxyzFirstVehicle    = "[N]    resulting force on first vehicle: vector in first vehicle's coordinate system";
    const auto o_FxyzSecondVehicle   = "[N]    resulting force on second vehicle: vector in second vehicle's coordinate system";

    const auto p_Kacceleration       = "[N s²/m]  force feedback constant for articulation distance acceleration (2nd derivative)";
    const auto p_Kvelocity           = "[N s/m]    force feedback constant for articulation distance velocity (1st derivative)";
    const auto p_Kdistance           = "[N/m]      force feedback constant for articulation distance";
    const auto p_Kintegrated         = "[N m s]    force feedback constant for integrated articulation distance";
}

#include <claraSim/framework/CModule.h>

////*********************************
//// CArticulation
////*********************************
class CArticulation : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CArticulation();
    virtual ~CArticulation();

    //*******************************
    //classes
    //*******************************

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloatVectorXYZ> o_FxyzFirstVehicle;
    CMessageOutput<CFloatVectorXYZ> o_FxyzSecondVehicle;

    /* parameter */
    CMessageParameter<CFloatVector> p_Kacceleration;
    CMessageParameter<CFloatVector> p_Kvelocity;
    CMessageParameter<CFloatVector> p_Kdistance;
    CMessageParameter<CFloatVector> p_Kintegrated;

private:
    /* input */
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYawFirstVehicle;
    CMessageInput<CFloatVectorXYZ> i_angleRollPitchYawSecondVehicle;
    CMessageInput<CFloatVectorXYZ> i_xyzFirstVehicle;
    CMessageInput<CFloatVectorXYZ> i_xyzSecondVehicle;
    CMessageInput<CFloatVectorXYZ> i_xyzArticulationFirstVehicle;
    CMessageInput<CFloatVectorXYZ> i_xyzArticulationSecondVehicle;
    CMessageInput<CBool> i_detach;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloatVectorXYZ>& f_angleRollPitchYawFirstVehicle,
               IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSecondVehicle,
               IMessage<CFloatVectorXYZ>& f_xyzFirstVehicle,
               IMessage<CFloatVectorXYZ>& f_xyzSecondVehicle,
               IMessage<CFloatVectorXYZ>& f_xyzArticulationFirstVehicle,
               IMessage<CFloatVectorXYZ>& f_xyzArticulationSecondVehicle,
               IMessage<CBool>& f_detach );
private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
    CFloat m_dT0, m_dT1, m_dT2;

    CFloatVectorXYZ m_Fxyz, m_zeroVector;
    CFloatVectorXYZ m_angleRollPitchYawFirst, m_angleRollPitchYawSecond;
    CFloatVectorXYZ m_xyzArtFirst, m_xyzArtSecond, m_deltaxyzArt0, m_deltaxyzArt1,
                    m_deltaxyzVel0, m_deltaxyzVel1,
                    m_deltaxyzAcc0,
                    m_deltaxyzIntegrated;
};

#endif // CArticulation_H
