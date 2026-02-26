/*!
********************************************************************************
@class CClothoid
@ingroup framework
@brief

@author Robert Erhart, ett2si (19.02.2007)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark

********************************************************************************

********************************************************************************
*/
#ifndef CKLOTHOIDE_H
#define CKLOTHOIDE_H

#include "CClass_ct.h"
#include "CFloatVector.h"

class CClothoid : public CClass_ct<4>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CClothoid();
    virtual ~CClothoid();

    //*******************************
    //classes
    //*******************************
public:
private:
    enum { X, Y, S, ALPHA, NumberOfStates};
    //*******************************
    // methods
    //*******************************
public:
    /*! init filter
        @param[in]  s1 Bogenlänge Startpunkt
        @param[in]  s2 Bogenlänge Endpunkt
        @param[in]  k1 Bahnkrümmung Startpunkt
        @param[in]  k2 Bahnkrümmung Endpunkt
        @param[in]  a1 Tangentenwinkel Startpunkt
        @param[in]  x1 x Startpunkt
        @param[in]  y1 y Startpunkt
     */
    void init( CFloat s1, CFloat s2, CFloat k1, CFloat k2, CFloat a1, CFloat x1, CFloat y1 );

    /*! init filter
        @param[in]  s Bogenlänge
        @param[in]  k1 Bahnkrümmung Startpunkt
        @param[in]  dk Bahnkrümmungsänderung über Strecke
        @param[in]  a1 Tangentenwinkel Startpunkt
        @param[in]  x1 x Startpunkt
        @param[in]  y1 y Startpunkt
     */
    void init( CFloat s, CFloat k1, CFloat dk, CFloat a1, CFloat x1, CFloat y1 );

    /*! get x y with stepSize
        @param[in]   stepSize  step size
        @param[out]  s Bogenlänge
        @param[out]  x
        @param[out]  y
     */
    void getXY( CFloat stepSize, CFloat& s, CFloat& x, CFloat& y );

    /*! get x y s vector with stepSize
        @param[in]   stepSize  step size
        @param[out]  s vector Bogenlänge
        @param[out]  x vector x
        @param[out]  y vector y
     */
    void getXY( CFloat stepSize, CFloatVector& s, CFloatVector& x, CFloatVector& y, CFloatVector& alpha );

private:
    CFloatVector& ddt( CFloatVector& state );

    //*******************************
    //variables
    //*******************************
private:
    CFloat m_s1, m_s2, m_k1, m_a1, m_x1, m_y1, m_stepSize, m_dk;
};

#endif // CKLOTHOIDE_H
