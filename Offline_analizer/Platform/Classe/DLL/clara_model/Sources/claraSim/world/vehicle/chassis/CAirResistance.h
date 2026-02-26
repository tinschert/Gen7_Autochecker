#ifndef CAIRRESISTANCE_H
#define CAIRRESISTANCE_H
/*!
********************************************************************************
@class CAirResistance
@ingroup chassis
@brief calculation of air resistance

@author Robert Erhart, ett2si (12.10.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
********************************************************************************
@remark
only the air resistance in the longitudinal direction is calculated
@verbatim
F = 1/2 * p_dragCoefficient * p_crossSectionalArea * p_airDensity * i_velocity²
@endverbatim
********************************************************************************
@param[in] i_velocity                 [m/s]   car longitudinal velocity
********************************************************************************
@param[out] o_FairResistance          [N]     longitudinal air Resistance
********************************************************************************
@param[in,out] p_dragCoefficient      [Cw]    drag coefficient
@param[in,out] p_crossSectionalArea   [m²]    vehicle front cross section
@param[in,out] p_airDensity           [kg/m²] air density
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CAirResistanceDoc
{
    const auto o_FairResistance = "[N] longitudinal air Resistance";
    const auto p_dragCoefficient = "[Cw] drag coeffincen";
    const auto p_crossSectionalArea = "[m²] vehicle front cross section";
    const auto p_airDensity = "[kg/m²] air density";
}

#include <claraSim/framework/CModule.h>


////*********************************
//// CAirResistance
////*********************************
class CAirResistance : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CAirResistance();
    virtual ~CAirResistance();

    //*******************************
    //classes
    //*******************************
public:

    //*******************************
    //messages
    //*******************************
public:
    CMessageOutput<CFloat> o_FairResistance;
    /* parameter */
    CMessageParameter<CFloat> p_dragCoefficient;       // c_w value
    CMessageParameter<CFloat> p_crossSectionalArea;   // A
    CMessageParameter<CFloat> p_airDensity;           // rho
private:
    CMessageInput<CFloat> i_velocity;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& velocity );
private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
};

#endif // CAIRRESISTANCE_H
