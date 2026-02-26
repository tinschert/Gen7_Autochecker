#ifndef CRoadNetwork_H
#define CRoadNetwork_H
/*!
********************************************************************************
@class CRoadNetwork
@ingroup roadNetwork
@brief container CModuleVector for the roads

@author Robert Erhart, ett2si (03.07.2015)
@copyright (c) Robert Bosch GmbH 2015-2024. All rights reserved.
********************************************************************************
@remark
- road is horizontal projection of halfway line in x(s)-y(s) plane and addition of elevator profile z(s)
********************************************************************************
@param[out] o_NumberOfRoads  [-]  max. number of roads
@param[out] o_NumberOfLanes  [-]  max. number of lanes per road
@param[in,out] p_mapOrientation [rad]   map orientation: 0 = x direction towards East, PI/2 = x direction towards North, ...
@param[in,out] p_gnssLatitude   [deg]   GNSS latitude at coordinate origin in degrees; zero = Equator, positive for northern hemisphere, negative for southern hemisphere. E.g. 43.040833 = 43°2’27” N
@param[in,out] p_gnssLongitude  [deg]   GNSS longitude at coordinate origin in degrees; zero = Prime Meridian, positive for eastern hemisphere, negative for western hemisphere. E.g. 43.040833 = 43°2’27 E
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CRoadNetworkDoc
{
    const auto o_NumberOfRoads  = "max. number of roads";
    const auto o_NumberOfLanes  = "max. number of lanes per road";
    const auto p_mapOrientation = "(radians) map orientation: 0 = x direction towards East, PI/2 = x direction towards North, ...";
    const auto p_gnssLatitude   = "(degrees) GNSS latitude at coordinate origin in degrees; zero = Equator, positive for northern hemisphere, negative for southern hemisphere. E.g. 43.040833 = 43°2’27” N";
    const auto p_gnssLongitude  = "(degrees) GNSS longitude at coordinate origin in degrees; zero = Prime Meridian, positive for eastern hemisphere, negative for western hemisphere. E.g. 43.040833 = 43°2’27” E";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/framework/CModuleVector.h>

#include "CRoad.h"

class CRoadNetwork : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CRoadNetwork( CInt numberOfRoads, CInt numberOfLanes );
    virtual ~CRoadNetwork();

    //*******************************
    //classes
    //*******************************
public:
    CModuleVector<CRoad> roads;

    //*******************************
    //messages
    //*******************************
public:
    CMessageOutput<CInt> o_NumberOfRoads;
    CMessageOutput<CInt> o_NumberOfLanes;
    CMessageParameter<CFloat> p_mapOrientation;
    CMessageParameter<CFloat> p_gnssLatitude;
    CMessageParameter<CFloat> p_gnssLongitude;

    //*******************************
    // methods
    //*******************************
public:
    void init(); // calc course; /* use only, if simulation is stopped */

    //! Get GNSS latitude [degrees] of a position [m] in the simulated world.
    //! Uses offset and orientation of the map defined by p_mapOrientation, p_gnssLatitude, and p_gnssLongitude.
    //! Convention: Positive for northern hemisphere, negative for southern hemisphere.
    //! TODO: Calculation parameters are updated in 'init' only. Use 'setInit' of p_gnssLatitude etc. only for manipulation!
    //! @param[in] f_x [CFloat] x coordinate of world position queried
    //! @param[in] f_y [CFloat] y coordinate of world position queried
    CFloat getLatitude( CFloat f_x, CFloat f_y );

    //! Get GNSS longitude [degrees] of a position [m] in the simulated world.
    //! Uses offset and orientation of the map defined by p_mapOrientation, p_gnssLatitude, and p_gnssLongitude.
    //! Convention: Positive for eastern hemisphere, negative for western hemisphere.
    //! TODO: Calculation parameters are updated in 'init' only. Use 'setInit' of p_gnssLatitude etc. only for manipulation!
    //! @param[in] f_x [CFloat] x coordinate of world position queried
    //! @param[in] f_y [CFloat] y coordinate of world position queried

    CFloat getLongitude( CFloat f_x, CFloat f_y );

private:
    void calc( CFloat f_dT, CFloat f_time );
    void updateConversionFactors();
    //********************************
    // variables
    //********************************
private:
    CFloat m_metersPerDegreeLatitude = 1.; // non-zero inizialization to avoid division by zero. Will be updated in 'updateConversionFactors'.
    CFloat m_meterPerDegreeLongitude = 1.; // non-zero inizialization to avoid division by zero. Will be updated in 'updateConversionFactors'.
};

#endif // CRoadNetwork_H
