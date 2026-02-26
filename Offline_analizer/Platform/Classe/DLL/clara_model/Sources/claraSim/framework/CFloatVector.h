/*!
********************************************************************************
@class CFloatVector
@ingroup framework
@brief Defines a vector class of type CFloat

@author Robert Erhart, ett2si (18.10.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- typedef of STL class valarray
- specialized CFloatVectorXYZ for 3D coordinates and angles
********************************************************************************
*/
#ifndef CFLOATVECTOR_H
#define CFLOATVECTOR_H

#include <cmath>
#include "CFloat.h"
#include <valarray>
#include <initializer_list>

using CFloatVector = ::std::valarray<CFloat>;

#ifdef __linux__
template<class _Clos, typename _Tp>
class _Expr;

template<typename _Tp1, typename _Tp2>
class _ValArray;

template<class _Oper, template<class, class> class _Meta, class _Dom>
struct _UnClos;

template<class _Op>
struct _UnaryOp
{
    typedef typename ::std::__fun<_Op, CFloat>::result_type __rt;
    typedef _Expr<_UnClos<_Op, _ValArray, CFloat>, __rt> _Rt;
};

#endif

class CFloatVectorXYZ : public CFloatVector
{
public:
    CFloatVectorXYZ() : CFloatVector( 0.0, 3 ) {};

    CFloatVectorXYZ( CFloat x, CFloat y, CFloat z ) : CFloatVector( {x, y, z} ) {};

    ///  Construct an array with an initializer_list of values.
    CFloatVectorXYZ( ::std::initializer_list<CFloat> list ) : CFloatVector( list ) {};

    ///  Construct an array with @a n elements.
    //explicit CFloatVectorXYZ(size_t n) : CFloatVector(n) {};

    ///  Construct an array with @a n elements initialized to @a t.
    //CFloatVectorXYZ(const CFloat& array, size_t n) : CFloatVector(array, n) {};

    ///  Construct an array initialized to the first @a n elements of @a t.
    //CFloatVectorXYZ(const CFloat* __restrict__ array, size_t n) : CFloatVector(array, n) {};

    ///  Copy and Move constructor.
    CFloatVectorXYZ( const CFloatVectorXYZ& array ) = default;
    CFloatVectorXYZ( const valarray& array ) : CFloatVector( array ) {};
    CFloatVectorXYZ( valarray&& value ): CFloatVector( value ) {};
    // valarray calc expressions (floatvectorxyz = a1+a2+a3)

#ifdef __linux__
    template<class _Dom>
    CFloatVectorXYZ( const ::std::_Expr<_Dom, CFloat>& __e ): CFloatVector( __e ) {};
#endif
    //cast operator
    // operator ::std::valarray<CFloat>&()
    // {
    //     return *this;
    // };

    //Operator overload
#ifdef __linux__
    using CFloatVector::operator=; //operator= not automatically derived
#endif
    CFloatVectorXYZ& operator=( const CFloatVectorXYZ& ) = default;

    // template<typename T0>
    // inline CFloatVectorXYZ& operator=(const T0 & rhs)
    // {
    //     CFloatVector::operator=(rhs);
    //     return *this;
    // };

    virtual ~CFloatVectorXYZ() {};

    // Getter methods
    CFloat X()
    {
        return ( *this )[0];
    };

    CFloat Y()
    {
        return ( *this )[1];
    };

    CFloat Z()
    {
        return ( *this )[2];
    };

    //! Returns the radius (Euclidean norm)
    CFloat Radius()
    {
        // TODO: Euclidean norm also defined in CClass_ct.h for CFloatVector.
        //      Can this be defined more elegantly?
        return ::std::sqrt( ( *this )[0] * ( *this )[0] + ( *this )[1] * ( *this )[1] + ( *this )[2] * ( *this )[2] );
    };

    CFloat AbsoluteValue()
    {
        return ( *this ).Radius();
    };

    CFloat Azimuth()
    {
        // arctan( Y / X )
        return ::std::atan2( ( *this )[1], ( *this )[0] );
    };

    //! Calculate inclination angle = arccos( Z / radius )
    CFloat InclinationAngle()
    {
        return ::std::acos( ( *this )[2] / ( *this ).Radius() );
    };

    //! Return elevation angle = pi/2 - inclination angle
    CFloat ElevationAngle()
    {
        return M_PI / 2. - ( *this ).InclinationAngle();
    };

    //! Returns spherical coordinates in ISO notation: (radius, inclination, azimuth)
    CFloatVector SphericalCoordinates()
    {
        return CFloatVector( { ( *this ).Radius(), ( *this ).InclinationAngle(), ( *this ).Azimuth() } );
    };


    // Setter methods
    CFloat X( CFloat x )
    {
        ( *this )[0] = x;
        return ( *this )[0];
    };

    CFloat Y( CFloat y )
    {
        ( *this )[1] = y;
        return ( *this )[1];
    };

    CFloat Z( CFloat z )
    {
        ( *this )[2] = z;
        return ( *this )[2];
    };

    CFloatVectorXYZ& XYZ( CFloat x, CFloat y, CFloat z )
    {
        *this = {x, y, z};
        return *this;
    };


};

#endif // CFLOATVECTOR_H
