/*!
********************************************************************************
@class CViewSegment
@ingroup framework
@brief view segment for sensor models

@author Robert Erhart, ett2si (11.07.2016)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@verbatim
Geometry of the view segment:

          a_1   a_2
           v     v
                      . <- alpha == zero line (dots)
            \   (C)   .
vis.rng. -> (B)xxx\   .
              \xxxx|  .
               \xxx\  .
                \xxx| .
                 \xx\ .
                  \xx|.
                   \x\.
                    \x|
                     (A) <- sensor position

a_1 = "alphaLeft"
a_2 = "alphaLeft" - "openingAngle"
vis.rng. = "visibilityRange"
x = points within field of view
(A), (B), (C) = corner points of rectangle that defines view segment
(A) = sensor position

@remark
currently only the x-y projection of point and contour is used
********************************************************************************
*/
#ifndef CViewSegment_H
#define CViewSegment_H

#include "CClass_ct.h"

////*********************************
//// CViewSegment
////*********************************
class CViewSegment
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    /*!
     * Constructor
     */
    CViewSegment();
    virtual ~CViewSegment();
public:
    //CViewSegment( const CViewSegment& obj );

    //*******************************
    // methods
    //*******************************
public:
    /*!
     * define a view segment and update its parameters
     *
     *     Input parameters:
     * @param[in] f_alphaLeft       [CFloat]   left boundary angle of the segment
     * @param[in] f_openingAngle    [CFloat]   opening angle (span) of the segment
     * @param[in] f_visibilityRange [CFloat]   range of vision of the segment
     * @param[in] f_rollAngle       [CFloat]   sensor orientation roll angle
     * @param[in] f_pitchAngle      [CFloat]   sensor orientation pitch angle
     * @param[in] f_yawAngle        [CFloat]   sensor orientation yaw angle
     * @param[in] f_x               [CFloat]   x-coordinate of Point A of the triangle
     * @param[in] f_y               [CFloat]   y-coordinate of Point A of the triangle
     * @param[in] f_z               [CFloat]   z-coordinate of Point A of the triangle
     * -----------
     *     Output parameters:
     * @param[out] f_Ax_r           [CFloat]   x-coordinate of Point A of the triangle
     * @param[out] f_Ay_r           [CFloat]   y-coordinate of Point A of the triangle
     * @param[out] f_Az_r           [CFloat]   z-coordinate of Point A of the triangle
     * @param[out] f_Bx_r           [CFloat]   x-coordinate of Point B of the triangle
     * @param[out] f_By_r           [CFloat]   y-coordinate of Point B of the triangle
     * @param[out] f_Bz_r           [CFloat]   z-coordinate of Point B of the triangle
     * @param[out] f_Cx_r           [CFloat]   x-coordinate of Point C of the triangle
     * @param[out] f_Cy_r           [CFloat]   y-coordinate of Point C of the triangle
     * @param[out] f_Cz_r           [CFloat]   z-coordinate of Point C of the triangle
     */
    void init( CFloat f_alphaLeft, CFloat f_openingAngle, CFloat f_visibilityRange,
               CFloat f_rollAngle, CFloat f_pitchAngle, CFloat f_yawAngle,
               CFloat f_x, CFloat f_y, CFloat f_z,
               CFloat& f_Ax_r, CFloat& f_Ay_r, CFloat& f_Az_r,
               CFloat& f_Bx_r, CFloat& f_By_r, CFloat& f_Bz_r,
               CFloat& f_Cx_r, CFloat& f_Cy_r, CFloat& f_Cz_r
             );

    /*!
     * check if point P is inside the triangle spanned by the view segment
     * @param[in] f_x [CFloat] x-coordinate of Point P
     * @param[in] f_y [CFloat] y-coordinate of Point P
     * @param[in] f_z [CFloat] z-coordinate of Point P
     * @return distance from point A
     */
    CFloat checkInRange( const CFloat f_x, const CFloat f_y, const CFloat f_z );

    /*!
     * check if contour has an intersection with triangle spanned by the view segment
     * @param[in] f_x [CFloatVector] x-coordinate vector of contour corner points
     * @param[in] f_y [CFloatVector] y-coordinate vector of contour corner points
     * @param[in] f_z [CFloatVector] z-coordinate vector of contour corner points
     * @return nearest distance from point A
     */
    CFloat checkInRange( const CFloatVector& f_x, const CFloatVector& f_y, const CFloatVector& f_z );

    /*!
     * check if contour has an intersection with triangle spanned by the view segment
     * @param[in] f_boundryLine [-1, 0, 1] check with segment line 1: left line, 0: range line , -1 right line
     * @param[in] f_x1 [CFloat] x-coordinate P1 of line
     * @param[in] f_y1 [CFloat] y-coordinate P1 of line
     * @param[in] f_x2 [CFloat] x-coordinate P2 of line
     * @param[in] f_y2 [CFloat] y-coordinate P2 of line
     * @param[out] f_sLine [CFloat] z-coordinate vector of contour
     * @return intersection found
     */
    CBool findIntersectionWithLine( CInt f_boundryLine, CFloat f_x1, CFloat f_y1, CFloat f_x2, CFloat f_y2, CFloat& f_sLine );
private:
    //*******************************
    //variables
    //*******************************
private:
    enum {x, y, z};
    CFloatVector m_A, m_B, m_C, m_AB, m_AC;
    CFloat m_divTerm;
};

#endif // CViewSegment_H
