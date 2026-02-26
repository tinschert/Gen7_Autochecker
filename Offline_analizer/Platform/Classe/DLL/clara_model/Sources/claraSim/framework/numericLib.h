#ifndef numericLib_H
#define numericLib_H

#include "CFloat.h"
#include "CBool.h"
#include "CInt.h"
#include "CFloatVector.h"
#include "CBoolVector.h"
#include "CIntVector.h"
#include "CMessage.h"
#include "CMessageInput.h"
#include "CMessageOutput.h"
#include "CMessageParameter.h"
#include <cmath>
#include <array>
#include <stdint.h>
#include <algorithm>

namespace sim
{
    using ::std::pow;
    using ::std::sqrt;
    using ::std::sin;
    using ::std::asin;
    using ::std::cos;
    using ::std::acos;
    using ::std::tan;
    using ::std::atan;
    using ::std::atan2;
    using ::std::abs;
    using ::std::log10;
    using ::std::floor;
    using ::std::fmod;

    //#define max(a,b) (((a) > (b)) ? (a) : (b))
    #undef max // or use #define NOMINMAX // the min max macro from include windows.h->windef.h lead to compile error, because #define don't use namespaces.
    inline CFloat max( CFloat f_a, CFloat f_b )
    {
        return ( ( f_a > f_b ) ? f_a : f_b );
    };
    inline CInt max( CInt f_a, CInt f_b )
    {
        return ( ( f_a > f_b ) ? f_a : f_b );
    };

    //#define min(a,b) ((a)<(b)?(a):(b))
    #undef min // or use #define NOMINMAX // the min max macro from include windows.h->windef.h lead to compile error, because #define don't use namespaces.
    inline CFloat min( CFloat f_a, CFloat f_b )
    {
        return ( f_a < f_b ? f_a : f_b );
    };
    inline CInt min( CInt f_a, CInt f_b )
    {
        return ( f_a < f_b ? f_a : f_b );
    };

    inline CFloat median( CFloat f_v1, CFloat f_v2, CFloat f_v3 )
    // poor man's median for three elements only
    {
        return ( ( f_v1 > f_v2 )  ? ( ( f_v3 > f_v1 ) ? f_v1 : ( ( f_v3 > f_v2 ) ? f_v3 : f_v2 ) )  : ( ( f_v3 > f_v2 ) ? f_v2 : ( ( f_v3 > f_v1 ) ? f_v3 : f_v1 ) ) );
    }

    inline CFloatVector median( CFloatVector f_v1, CFloatVector f_v2, CFloatVector f_v3 )
    // median for vectors (element-wise)
    {
        CFloatVector l_vec( 0., 3 );
        l_vec[0] = median( f_v1[0], f_v2[0], f_v3[0] );
        l_vec[1] = median( f_v1[1], f_v2[1], f_v3[1] );
        l_vec[2] = median( f_v1[2], f_v2[2], f_v3[2] );
        return l_vec;
    }

    //! Returns true, if value is in range [low, high].
    inline bool in_range( CFloat value, CFloat low, CFloat high )
    {
        return ( low <= value ) && ( value <= high );
    }
    //! Returns true, if value is in range [low, high].
    inline bool in_range( CInt value, CInt low, CInt high )
    {
        return ( low <= value ) && ( value <= high );
    }

    //! Returns the value of f_x, limited to the range [f_xmin, f_xmax].
    inline CFloat limit( CFloat f_x, CFloat f_xmin, CFloat f_xmax )
    {
        return ( ( f_x > f_xmax ) ? ( f_xmax ) : ( ( f_x < f_xmin ) ? ( f_xmin ) : ( f_x ) ) );
    };
    //! Vector version of 'limit'
    //! Limits each element of f_x to the range [f_xmin, f_xmax].
    inline CFloatVector limit( CFloatVector f_x, CFloat f_xmin, CFloat f_xmax )
    {
        CFloatVector l_vec( 0., 3 );
        l_vec[0] = limit( f_x[0], f_xmin, f_xmax );
        l_vec[1] = limit( f_x[1], f_xmin, f_xmax );
        l_vec[2] = limit( f_x[2], f_xmin, f_xmax );
        return l_vec;
    };
    inline CInt limit( CInt f_x, CInt f_xmin, CInt f_xmax )
    {
        return ( ( f_x > f_xmax ) ? ( f_xmax ) : ( ( f_x < f_xmin ) ? ( f_xmin ) : ( f_x ) ) );
    };

    inline CFloat normalizeAnglePosNegPI( CFloat f_angle )
    {
        /* Mathematical source for the inclined reader (German, 07.05.2020):
        http://www.hinterseher.de/Diplomarbeit/TrigonometrischeFunktionen.html#Winkel%20modulo%20[-Pi,%20Pi]
        NOTE: "f_angle + M_PI" is calculated to compare in the next step l_angle
                against zero instead of "plus/minus PI" as stated in the above
                resource. This calculation needs to be considered by
                - in case of positive l_angle: reverting the rotation backwards (" - M_PI")
                - in case of negative l_angle: finishing the full convolution of two pi (" + M_PI")
                The algorithm is very elegant, but hard to understand when reading for the
                first time, so I decided to describe it.
        */
        CFloat l_angle = ::std::fmod( f_angle + M_PI, 2 * M_PI );
        return l_angle >= 0 ? ( l_angle - M_PI ) : ( l_angle + M_PI );
    }

    inline CFloat normalizeAngleTwoPI( CFloat f_angle )
    {
        CFloat l_angle = ::std::fmod( f_angle, 2 * M_PI );
        return l_angle >= 0 ? ( l_angle ) : ( l_angle + 2 * M_PI );
    }

    /* @brief The coordinateRotation() function transforms coordinates from the origin
    *      coordinate system into a new target coordinate system, based on the three
    *      rotation input angles.
    *
    *  As an example:
    *
    *   - use 'coordinateRotation(rollAngle, pitchAngle, yawAngle, ...)'
    *     to transform from vehicle to world coordinates.
    *
    *   - use 'coordinateRotationInv(rollAngle, pitchAngle, yawAngle, ...)'
    *     to transform from world to vehicle coordinates.
    *
    *  Rotations about a non-fixed (=previously rotated) axis are denoted by primes (e.g. y').
    *
    *  @input f_roll  The rotation angle in [rad] that needs to be performed around the x''-axis.
    *  @input f_pitch The rotation angle in [rad] that needs to be performed around the y_-axis.
    *  @input f_yaw   The rotation angle in [rad] that needs to be performed around the z-axis.
    *  @input f_x*_in The x-position in the "origin" coordinate system
    *  @input f_y*_in The y-position in the "origin" coordinate system
    *  @input f_z*_in The z-position in the "origin" coordinate system
    *  @input/output f_x*_out The x-position in the "target" coordinate system.
    *  @input/output f_y*_out The y-position in the "target" coordinate system.
    *  @input/output f_z*_out The z-position in the "target" coordinate system.
    *
    * */

    inline void coordinateRotation( const auto& f_roll, const auto& f_pitch, const auto& f_yaw,
                                    auto f_xEgo_in, auto f_yEgo_in, auto f_zEgo_in,
                                    auto& f_xWorld_out, auto& f_yWorld_out, auto& f_zWorld_out )
    /* Coordinate transformation in x,y',z'' order according to DIN ISO 8855.
    * Use this method to transform a vector from local (ego) to global (world) coordinates.
    * This convention uses Tait–Bryan angles (= Cardan angles = roll, pitch, yaw), which are NOT
    * standard Euler angles */
    {
        // transformation to prime coordinate system
        auto f_xPrime = f_xEgo_in;
        auto f_yPrime = f_yEgo_in * ::std::cos( f_roll ) - f_zEgo_in * ::std::sin( f_roll );
        auto f_zPrime = f_yEgo_in * ::std::sin( f_roll ) + f_zEgo_in * ::std::cos( f_roll );

        // transformation to double prime coordinate system
        auto f_xDbPrime =   f_xPrime * ::std::cos( f_pitch ) + f_zPrime * ::std::sin( f_pitch );
        auto f_yDbPrime =   f_yPrime;
        auto f_zDbPrime = - f_xPrime * ::std::sin( f_pitch ) + f_zPrime * ::std::cos( f_pitch );

        // transformation to output coordinate system
        f_xWorld_out = f_xDbPrime * std::cos( f_yaw ) - f_yDbPrime * std::sin( f_yaw );
        f_yWorld_out = f_xDbPrime * std::sin( f_yaw ) + f_yDbPrime * std::cos( f_yaw );
        f_zWorld_out = f_zDbPrime;
    }


    inline void coordinateRotationInv( const auto& f_roll, const auto& f_pitch, const auto& f_yaw,
                                    auto f_xWorld_in, auto f_yWorld_in, auto f_zWorld_in,
                                    auto& f_xEgo_out, auto& f_yEgo_out, auto& f_zEgo_out )
    /* INVERSE coordinate transformation in z,y',x'' order according to DIN ISO 8855.
    * Use this method to transform a vector from global (world) to local (ego) coordinates.
    * This convention uses Tait–Bryan angles (= Cardan angles = roll, pitch, yaw), which are NOT
    * standard Euler angles */
    {
        // transformation to prime coordinate system
        auto f_xPrime =   f_xWorld_in * ::std::cos( f_yaw ) + f_yWorld_in * ::std::sin( f_yaw ) ;
        auto f_yPrime = - f_xWorld_in * ::std::sin( f_yaw ) + f_yWorld_in * ::std::cos( f_yaw ) ;
        auto f_zPrime =   f_zWorld_in;

        // transformation to double prime coordinate system
        auto f_xDbPrime = f_xPrime * ::std::cos( f_pitch ) - f_zPrime * ::std::sin( f_pitch );
        auto f_yDbPrime = f_yPrime;
        auto f_zDbPrime = f_xPrime * ::std::sin( f_pitch ) + f_zPrime * ::std::cos( f_pitch );

        // transformation to output coordinate system
        f_xEgo_out =   f_xDbPrime;
        f_yEgo_out =   f_yDbPrime * ::std::cos( f_roll ) + f_zDbPrime * ::std::sin( f_roll );
        f_zEgo_out = - f_yDbPrime * ::std::sin( f_roll ) + f_zDbPrime * ::std::cos( f_roll );
    }


    inline void coordinateRotation( const CFloatVector& f_Alphas, CFloatVector& f_Input, CFloatVector& f_Output )
    /* Coordinate rotation in vector notation */
    {
        coordinateRotation( f_Alphas[0], f_Alphas[1], f_Alphas[2],
                            f_Input[0], f_Input[1], f_Input[2],
                            f_Output[0], f_Output[1], f_Output[2] );
    }


    inline void coordinateRotation( const CFloatVector& f_Alphas,
                                    auto f_xInput, auto f_yInput, auto f_zInput,
                                    auto& f_xOutput, auto& f_yOutput, auto& f_zOutput )
    /* Coordinate rotation in semi-vector notation */
    {
        coordinateRotation( f_Alphas[0], f_Alphas[1], f_Alphas[2],
                            f_xInput, f_yInput, f_zInput,
                            f_xOutput, f_yOutput, f_zOutput );
    }


    inline void coordinateRotationInv( const CFloatVector& f_Alphas, CFloatVector& f_Input, CFloatVector& f_Output )
    /* Inverse coordinate rotation in vector notation */
    {
        coordinateRotationInv( f_Alphas[0], f_Alphas[1], f_Alphas[2],
                            f_Input[0], f_Input[1], f_Input[2],
                            f_Output[0], f_Output[1], f_Output[2] );
    }


    inline void coordinateRotationInv( const CFloatVector& f_Alphas,
                                    auto f_xInput, auto f_yInput, auto f_zInput,
                                    auto& f_xOutput, auto& f_yOutput, auto& f_zOutput )
    /* Inverse coordinate rotation in semi-vector notation */
    {
        coordinateRotationInv( f_Alphas[0], f_Alphas[1], f_Alphas[2],
                            f_xInput, f_yInput, f_zInput,
                            f_xOutput, f_yOutput, f_zOutput );
    }


    /* vector operations */

    inline CFloat vectorNorm( CFloatVector& a )
    /* Euclidean norm of a vector */
    {
        CFloat sum = 0;
        for( unsigned int i = 0; i < a.size(); i++ )
            sum += std::pow( a[i], 2 );
        return ::std::sqrt( sum );
    }

    /* Euclidean norm squared of a vector */
    inline CFloat vectorNormSquared(CFloatVector a)
    /* Euclidean norm squared of a vector */
    {
        CFloat sum = 0;
        for (unsigned int i = 0; i < a.size(); i++)
            sum += ::std::pow(a[i], 2);
        return sum;
    }

    inline CFloatVectorXYZ& crossProduct( CFloatVectorXYZ& out, CFloatVectorXYZ& a, CFloatVectorXYZ& b )
    /* cross product of two 3x1 vectors */
    {
        out[0] = a[1] * b[2] - a[2] * b[1];
        out[1] = a[2] * b[0] - a[0] * b[2];
        out[2] = a[0] * b[1] - a[1] * b[0];
        return out;
    }

    // inline CFloatVector crossProduct( CFloatVectorXYZ& a, CFloatVectorXYZ& b )
    // //malloc/new possible -> dynamic memory -> not allowed in the real time context
    // /* cross product of two 3x1 vectors */
    // {
    //     CFloatVector m_cProduct( 0.0, 3 );
    //     m_cProduct[0] = a[1] * b[2] - a[2] * b[1];
    //     m_cProduct[1] = a[2] * b[0] - a[0] * b[2];
    //     m_cProduct[2] = a[0] * b[1] - a[1] * b[0];
    //     return m_cProduct;
    // }

    inline CFloat dotProduct(CFloatVector a, CFloatVector b)
    /* dot product of two vectors */
    {
        CFloat sum = 0;
        for (unsigned int i = 0; i < a.size(); i++)
            sum += a[i] * b[i];
        return sum;
    }

    template<class T> CInt sign_of( T X )
    {
        // #define sign_of(X) ( X>0 ? 1 : (X<0 ? -1 : 0) )
        return ( X>0 ? 1 : (X<0 ? -1 : 0) );
    }
    template<class T> CInt sig( T X )
    {
        //#define sig(X) ( X>=0 ? 1 : -1 )
        return ( X>=0 ? 1 : -1 );
    }

    inline CFloat to_radians( CFloat degrees )
    {
        return ( degrees * M_PI / 180. );
    };
    inline CFloatVector to_radians( CFloatVector degrees )
    {
        return ( degrees * CFloatVector( M_PI, degrees.size() ) / CFloatVector( 180., degrees.size() ) );
    };

    inline CFloat to_degrees( CFloat radians )
    {
        return ( radians * 180. / M_PI );
    };
    inline CFloatVector to_degrees( CFloatVector radians )
    {
        return ( radians * CFloatVector( 180., radians.size() ) / CFloatVector( M_PI, radians.size() ) );
    };

    /*!
    * Returns num evenly spaced samples, calculated over the interval [start, stop].
    * Analogous to Python's numpy.linspace function.
    */
    inline CFloatVector linspace( CFloat start, CFloat stop, CInt num )
    {
        CFloatVector line( 0., ( int ) num );
        CFloat delta = ( stop - start ) / ( ( CFloat )num - 1. );
        for( int i = 0; i < num; ++i )
        {
            line[i] = start + ( i * delta );
        }
        return line;
    };
}

#ifndef M_PI
    #define M_PI    3.14159265358979323846
#endif

#endif //numericLib_H