/*!
********************************************************************************
@class CSplineAkima
@ingroup framework
@brief akima spline interpolation

@author Robert Erhart, ett2si (13.02.2007)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- Akima Spline: Reference "A New Method of Interpolation and Smooth Curve Fitting Based on Local Procedures" J.ACM, vol17, 1970
- Notation from Wikipedia: https://de.wikipedia.org/wiki/Akima-Interpolation

The idea and notation used in this class is the following:

This polynomial is used for interpolation between these points and yields a continuous function y(x), with
continuous first derivative y'(x), but not necessarily continuous second derivative y''(x).
One big advantage is its simple calculation, which is based on points with maximum distance two positions
from the current one.

The interpolation on interval [x_i , x_i+1] is given by the cubic polynomial
    p_i(x) = a_i + b_i (x - x_i) + c_i (x - x_i)^2 + d_i (x - x_i)^3

with
    p_i (x_i) = y_i
    p_i (x_i+1) = y_i+1

If the slope t_i = p'_i(x_i) is known, coefficients a_i, ..., d_i are given by Hermite interpolation:
    a_i = y_i
    b_i = t_i
    c_i = [ 3 (y_i+1 - y_i)/(x_i+1-x*i) - t_i+1 - 2 t_i] / [x_i+1 - x_i]
    d_i = [t_i+1 + t_i - 2 (y_i+1 - y_i)(x_i+1 - x_i)] / [x_i-1 - x_i]^2

Key to Akima interpolation is the slope t_i, extracted from the support points by this formula:
    m_i = (y_i+1 - y_i) / (x_i+1 - x_i)                    <--- = dy / dx
    t_i = [ abs(m_i+1 - m_i) m_i-1 + abs(m_i-1 - m_i-2) m_i ] / [ abs(m_i+1 - m_i) + abs(m_i-1 - m_i-2) ]

********************************************************************************
@param[in,out] x  [float]  x-values of table
@param[in,out] y  [float]  y-values of table
********************************************************************************
@todo implementation of the spline interpolation
@todo delete dynamic arrays
@todo acceleration of find index (remember for each object m_index)
********************************************************************************/

#ifndef CSPLINEAKIMA_H_
#define CSPLINEAKIMA_H_

#include <iostream>
#include "CClass_ct.h" //cmath

class CSplineAkima
{
public:
    CSplineAkima();
    virtual ~CSplineAkima();

    //! Initialize Spline interpolation object
    //! @param[in] x_array      [long double array] support points x values
    //! @param[in] y_array      [long double array] support points y values
    //! @param[in] size_array   [size_t]     size of the support point arrays
    //! @param[in] periodic     [bool]              is the curve periodic, i.e. value and slope of x_0 == of x_end
    int init( const long double x_array[], const long double y_array[], size_t size_array, bool periodic );

    //! Evaluate interpolation value at input point
    //! @param[in]  x       [long double] input value
    //! @param[out] p(x)    [long double] interpolation at point x
    long double Eval( long double x ) const;

    //! Evaluate interpolation value and first derivative at input point
    //! @param[in]  x       [long double]       input value
    //! @param[in]  y       [long double ref.]  reference to write p(x) to
    //! @param[in]  dy      [long double ref]   referenct to write first derivative to = dp(x)/dx
    void EvalDeriv1( long double x, long double& y, long double& dy ) const;

    //! Evaluate interpolation value, first, and second derivative at input point
    //! @param[in]  x       [long double]       input value
    //! @param[in]  y       [long double ref.]  reference to write p(x) to
    //! @param[in]  dy      [long double ref]   referenct to write first derivative to = dp(x)/dx
    //! @param[in]  ddy     [long double ref]   referenct to write second derivative to = d^2 p(x)/ dx^2
    void EvalDeriv2( long double x, long double& y, long double& dy, long double& ddy ) const;

    //! Return support point x_i
    //! @param[in] index    [size_t] query index
    long double getX( size_t index ) const;

    //! Return support point value y_i
    //! @param[in] index    [size_t] query index
    long double getY( size_t index ) const;

    //! Return support point x vector (= m_x)
    CFloatVector& getXVector();

    //! Return support point y vector (= m_a)
    CFloatVector& getYVector();

    //! Return support point vector length (= m_size)
    CInt NumberOfElements() const;

private:
    /* variables */
    size_t m_size;              // number of support points

    // The following CFloatVector quantities hold the piecewise coefficients of p_i
    CFloatVector m_gradient;    // m_i = delta y_i / delta x_i
    CFloatVector m_x;           // x_i points; set by input array x
    CFloatVector m_a;           // y_i = p(x_i) = a_i values; set by input array y
    CFloatVector m_b;           // b_i coefficients (first order)
    CFloatVector m_c;           // c_i coefficients (second order)
    CFloatVector m_d;           // d_i coefficients (third order)

    /* methods */

    //! Find index of interval [x_i, x_i+1] that x lies in.
    //! @param[in]  x [long double] value for interval index search
   size_t findInterval( long double x ) const;
};

#endif /*CSPLINEAKIMA_H_*/
