/*!
********************************************************************************
@class CTable
@ingroup framework
@brief 2D-characteristic curve

@author Robert Erhart, ett2si (26.10.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- Characteristic curve with
   - linear interpolation function: type=0
      -     x = x(n) + rho * (x(n+1) - x(n))
      -     rho = (x - x(n)) / (x(n+1) - x(n))
      -     y(x) = y(n) + rho*(y(n+1) - y(n) )
   - Spline interpolation: type=1
********************************************************************************
@param[in,out] x  [float]  x-values of table
@param[in,out] y  [float]  y-values of table
********************************************************************************
@todo Implementation of Spline interpolation
********************************************************************************
*/
#ifndef CTABLE_H
#define CTABLE_H

#include "CClass_ct.h"

class CTable// ToDo: public CClass
{
public:
    CTable();
    virtual ~CTable();

    /*! init table
        @param[in] size  [int]   number of columns
        @param[in] type   [0,1]   interpolation type  */
    void init( CInt size, CInt type );

    /*! init table
        @param[in] x     [vector] values
        @param[in] y     [vector] values
        @param[in] type   [0,1]    interpolation type  */
    void init( CFloatVector x, CFloatVector y, CInt type );

    /*! init table
        @param[in] size  [int]    number of columns
        @param[in] x     [array]  values
        @param[in] y     [array]  values
        @param[in] type   [0,1]    interpolation type  */
    void init( CInt size, CFloat* x, CFloat* y, CInt type );

    /*! get y[x]
        @param[in] x  [float]  value  */
    CFloat get( CFloat x );

    /*! set x values of the table
        @param[in] x  [vector] values   */
    void setX( CFloatVector x );

    /*! set y values of the table
        @param[in] y  [vector] values   */
    void setY( CFloatVector y );

    CFloatVector m_x;
    CFloatVector m_y;

private:
    /* decleration */
    CInt m_interpolationTyp;

    /* private methode */
    CFloat getLinear( CFloat );
};

#endif // CTABLE_H
