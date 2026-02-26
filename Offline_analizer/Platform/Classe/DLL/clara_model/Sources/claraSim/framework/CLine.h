/*!
********************************************************************************
@class CLine
@ingroup framework
@brief

@author Robert Erhart, ett2si (03.07.2015)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- lane is horizontal projection of halfway line in x(s)-y(s) plane
- addition of elevator profile:  z(s)
********************************************************************************

********************************************************************************
*/
#ifndef CLine_H
#define CLine_H

#include <claraSim/framework/CSplineAkima.h>
#include <claraSim/framework/CClothoid.h>
#include <claraSim/framework/CTable.h>
#include <vector>

class CLine
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CLine();
    virtual ~CLine();
private:
    //CLine( const CLine& f_module ) ; //copy constructor

    //*******************************
    //classes
    //*******************************
public:
private:
    /* instances */
    CSplineAkima xSplineCoordinate;
    CSplineAkima ySplineCoordinate;
    CSplineAkima zSplineCoordinate;
    CIntVector typLeftBoundary;

    //*******************************
    // methods
    //*******************************
public:
    void init( CFloatVector& f_sVector_r, CFloatVector& f_xVector_r, CFloatVector& f_yVector_r, CFloatVector& f_zVector_r ); /* use only, if simulation is stopped */
    void init( CLine& f_firstLine, CLine& f_secondLine );
    void getXYZ( CFloat s, CFloat& x, CFloat& y, CFloat& z );
    void getXYZ( CFloat s, CFloat& x, CFloat& y, CFloat& z, CFloat& dx, CFloat& dy, CFloat& dz );
    void getXYZ( CFloat s, CFloat& x, CFloat& y, CFloat& z, CFloat& dx, CFloat& dy, CFloat& dz, CFloat& ddx, CFloat& ddy, CFloat& ddz );
    CInt getType( CFloat s ); //ToDo: Currently only 0 returned
    void findLinePositionInfo( CFloat f_x, CFloat f_y,
                               CFloat& f_sSpline, CFloat& f_distancePointSpline,
                               CFloat& f_xSpline, CFloat& f_ySpline, CFloat& f_zSpline,
                               CFloat& f_dxSpline, CFloat& f_dySpline, CFloat& f_dzSpline,
                               CInt&   f_index );

    void getXYZVector( CFloat f_stepSizeMax, CFloatVector& f_x, CFloatVector& f_y, CFloatVector& f_z );
    CFloat getLengthOfLine();
    CInt getNumberOfLineReferencePoints();

    CFloatVector* getXLineVector();
    CFloatVector* getYLineVector();
    CFloatVector* getZLineVector();
    CFloatVector* getSLineVector();
    CIntVector*   getTypLineVector();
private:
    void calc( CFloat f_dT, CFloat f_time ) {}; //not used in CLine; overload abstract method of class CClass

    //*******************************
    //variables
    //*******************************
private:
    CFloat m_errorTolerance;
    uint32_t m_indexSearch;
    CFloat m_lengthOfLine;
    CInt m_numberOfLineReferencePoints;
};

#endif // CLine_H
