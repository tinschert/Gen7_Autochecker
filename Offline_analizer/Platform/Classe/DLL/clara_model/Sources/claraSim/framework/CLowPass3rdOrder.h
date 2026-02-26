/*!
********************************************************************************
@class CLowPass3ndOrder
@ingroup framework
@brief Low-pass filter 3nd Order

@author Robert Erhart, ett2si (20.10.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- transfer function of low-pass filter 3rd order
- H = v / ( 1 + a * s + b * s^2 + c * s^3 ) = Output(s) / Input(s)

- Laplace transforming:
   - L(y(t)/x(t)) = Output(s)/Input(s)
   - c * y'''(t) + b * y''(t) + a * y'(t) + y(t) = v * x(t)
   - y(t)   = y1(t)
   - y1'(t) = y2(t)
   - y2'(t) = y3(t)
   - y3'(t) = (v * x(t) - b * y''(t) - a * y'(t) - y(t)) / c
********************************************************************************

********************************************************************************
*/
#ifndef CLOWPASS3RDORDER_H
#define CLOWPASS3RDORDER_H

#include "CClass_ct.h"

class CLowPass3rdOrder : public CClass_ct<3>
{
public:
    /* constructor / destructor */
    CLowPass3rdOrder();
    virtual ~CLowPass3rdOrder();

    /*! setInit filter init values
            @param[in]  a  filter constant init
            @param[in]  b  filter constant init
            @param[in]  c  filter constant init
            @param[in]  v  amplification factor init  */
    void setInit( CFloat a, CFloat b, CFloat c, CFloat v );

    /*! init filter with init values
        @param[in]  f_initState  initial state  */
    void init( CFloat f_initState = 0.0 ) ;

    /*! init filter
        @param[in]  a  filter constant
        @param[in]  b  filter constant
        @param[in]  c  filter constant
        @param[in]  v  amplification factor
        @param[in]  f_initState  initial state  */
    void init( CFloat a, CFloat b, CFloat c, CFloat v, CFloat f_initState = 0.0 );

    /*! set filter parameter
        @param[in]  a  filter constant
        @param[in]  b  filter constant
        @param[in]  c  filter constant
        @param[in]  v  amplification factor  */
    void setFilterParameter( CFloat a, CFloat b, CFloat c, CFloat v );

    /*! get low pass filtered value of x
        @param[in] x     input value
        @param[in] f_dT    delta time       */
    CFloat get( CFloat x, CFloat f_dT );

private:
    /* filter coefficient */
    CFloat m_a;
    CFloat m_b;
    CFloat m_c;
    CFloat m_v;
    CFloat m_aInit;
    CFloat m_bInit;
    CFloat m_cInit;
    CFloat m_vInit;

    /* Input */
    CFloat m_x;

    /* Implementation */
    CFloatVector& ddt( CFloatVector& state );

    /* Define State */
    enum { Y1, Y2, Y3, NumberOfStates };
};

#endif // CLOWPASS2NDORDER_H
