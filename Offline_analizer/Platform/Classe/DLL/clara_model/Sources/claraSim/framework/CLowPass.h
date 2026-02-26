/*!
********************************************************************************
@class CLowPass
@ingroup framework
@brief Low-pass filter 1nd Order

@author Robert Erhart, ett2si (22.10.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- transfer function of low-pass filter 1nd Order
-  H = c / ( 1 + a*s) = Output(s) / Input(s)
-  Laplace-transforming:
 -  L(y(t)/x(t)) = Output(s)/Input(s)
 -  a*y'(t) + y(t) =  c*x(t)
 -  y'(t) = (c*x(t) - y(t) ) / a
********************************************************************************

********************************************************************************
*/
#ifndef CLOWPASS_H
#define CLOWPASS_H

#include "CClass_ct.h"

class CLowPass : public CClass_ct<1>
{
public:
    /* constructor / destructor */
    CLowPass();
    virtual ~CLowPass();

    /*! setInit filter
        @param[in]  a  filter time constant init value
        @param[in]  v  amplification factor init value */
    void setInit( CFloat a, CFloat v );

    /*! init filter with setInit values
     * @param[in]  f_initState  initial state */
    void init( CFloat f_initState = 0.0 );

    /*! init filter
        @param[in]  a  filter time constant
        @param[in]  v  amplification factor
        @param[in]  f_initState  initial state  */
    void init( CFloat a, CFloat v, CFloat f_initState = 0.0 );

    /*! set filter parameter
        @param[in]  a  filter time constant
        @param[in]  v  amplification factor  */
    void setFilterParameter( CFloat a, CFloat v );

    /*! get low pass filtered value of x
        @param[in] x     input value
        @param[in] f_dT    delta time       */
    CFloat get( CFloat x, CFloat f_dT );

private:
    /* Input */
    CFloat m_x;

    /* filter coefficient */
    CFloat m_a;
    CFloat m_v;
    CFloat m_aInit;
    CFloat m_vInit;

    /* Implementation */
    CFloatVector& ddt( CFloatVector& state );

    /* Define State */
    enum { Y1, NumberOfStates };
};

#endif // CLOWPASS_H
