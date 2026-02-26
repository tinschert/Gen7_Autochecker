/*!
********************************************************************************
@class CLowPass2ndOrder
@ingroup framework
@brief Low-pass filter 2nd Order

@author Robert Erhart, ett2si (20.10.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- transfer function of low-pass filter 2nd Order
- H = c / ( 1 + a*s + b * s^2) = Output(s) / Input(s)
   - with a = 2d0/w0, b=1/w0^2
   - good value for d0 = 1/2*sqrt(2)
- Laplace-transforming:
   - L(y(t)/x(t)) = Output(s)/Input(s)
   - b*y''(t) + a*y'(t) + y(t) =  c*x(t)
   - y(t) = y1(t)
   - y1'(t) = y2(t)
   - y2'(t) = (c*x(t) - a*y2(t) - y1(t) ) / b
********************************************************************************

********************************************************************************
*/
#ifndef CLOWPASS2NDORDER_H
#define CLOWPASS2NDORDER_H

#include "CClass_ct.h"

class CLowPass2ndOrder : public CClass_ct<2>
{
public:
    /* constructor / destructor */
    CLowPass2ndOrder();
    virtual ~CLowPass2ndOrder();

    /*! setInit filter init values
            @param[in]  a  filter constant init
            @param[in]  b  filter constant init
            @param[in]  v  amplification factor init  */
    void setInit( CFloat a, CFloat b, CFloat v );

    /*! init filter with init values
        @param[in]  f_initState  initial state  */
    void init( CFloat f_initState = 0.0 ) ;

    /*! init filter
        @param[in]  a  filter constant
        @param[in]  b  filter constant
        @param[in]  v  amplification factor
        @param[in]  f_initState  initial state  */
    void init( CFloat a, CFloat b, CFloat v, CFloat f_initState = 0.0 );

    /*! set filter parameter
        @param[in]  a  filter constant
        @param[in]  b  filter constant
        @param[in]  v  amplification factor  */
    void setFilterParameter( CFloat a, CFloat b, CFloat v );

    /*! get low pass filtered value of x
        @param[in] x     input value
        @param[in] f_dT    delta time       */
    CFloat get( CFloat x, CFloat f_dT );

private:
    /* filter coefficient */
    CFloat m_a;
    CFloat m_b;
    CFloat m_v;
    CFloat m_aInit;
    CFloat m_bInit;
    CFloat m_vInit;

    /* Input */
    CFloat m_x;

    /* Implementation */
    CFloatVector& ddt( CFloatVector& state );

    /* Define State */
    enum { Y1, Y2, NumberOfStates };
};

#endif // CLOWPASS2NDORDER_H
