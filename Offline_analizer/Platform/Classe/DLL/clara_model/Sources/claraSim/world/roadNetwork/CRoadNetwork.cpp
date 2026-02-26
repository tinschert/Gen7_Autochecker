/*******************************************************************************
@author Robert Erhart, ett2si (03.07.2015)
@copyright (c) Robert Bosch GmbH 2015-2024. All rights reserved.
*******************************************************************************/

#include "CRoadNetwork.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CRoadNetwork::CRoadNetwork( CInt numberOfRoads, CInt numberOfLanes ):
    roads( numberOfRoads, &numberOfLanes )

{
    addMessageOutput( o_NumberOfRoads, static_cast<uint32_t>( numberOfRoads ), CRoadNetworkDoc::o_NumberOfRoads );
    addMessageOutput( o_NumberOfLanes, static_cast<uint32_t>( numberOfLanes ), CRoadNetworkDoc::o_NumberOfLanes );

    addMessageParameter( p_mapOrientation, 0., CRoadNetworkDoc::p_mapOrientation );
    addMessageParameter( p_gnssLatitude, 0., CRoadNetworkDoc::p_gnssLatitude );
    addMessageParameter( p_gnssLongitude, 0., CRoadNetworkDoc::p_gnssLongitude );

    for( unsigned int index = 1; index < roads.size(); index++ )
    {
        roads[index].p_clothoidLine.setInit( {500.0, 0.0, 0.0} );
        roads[index].p_gradientLine.setInit( {100.0, 0.0, 0.0} );
        roads[index].p_crossfallLine.setInit( {100.0, 0.0, 0.0} );
        roads[index].p_lanes.setInit( {1.0, 0., 50.0, 2.0, 2.0} );
        roads[index].p_roadBoundary.setInit( { 50.0, 0.0, 50.0, 0.0, 0.12, 1.0, 0.12 } );
        roads[index].p_startPoint.setInit( {200.0, -100.0, 0.0, M_PI_2} );
    }
}

CRoadNetwork::~CRoadNetwork()
{}

/*------------------*/
/* public methods   */
/*------------------*/
void CRoadNetwork::init()         // use only, if simulation is stopped
{
    initializationMessages();

    for( unsigned int index = 0; index < roads.size(); index++ )
    {
        roads[index].initStartPoints(); // copy 'startPoint' and 'startPointRelative' init values first

        // get relative startPoint parameters
        CInt l_roadIndex    = ( int ) roads[index].p_startPointRelative[0];
        CInt l_laneIndex    = ( int ) roads[index].p_startPointRelative[1];
        CFloat l_s          = roads[index].p_startPointRelative[2];

        // If a valid 'p_startPointRelative' was defined, we translate the definition into
        // an absolute 'p_startPoint'.
        // Remark: Only refer to roads with LOWER index in 'p_startPointRelative' to get well-defined behaviour!
        if( l_roadIndex >= index )
        {
            std::cerr << "<CRoadNetwork::init> Invalid p_startPointRelative defined. Recursion broken by too high road index." << std::endl;
            roads[index].init();
            continue; // skip relative start point initialization
        }

        if( l_roadIndex >= 0 )
        {
            // TODO: safety checks of p_startPointRelative indices (values) + error output
            if( l_s < 0 ) // negative values are interpreted as 'lane end'
            {
                l_s = roads[l_roadIndex].lanes[l_laneIndex].o_lengthOfCourse;
            }
            SCoursePositionInfo l_pos = roads[l_roadIndex].lanes[l_laneIndex].getCoursePositionInfo( l_s, 0.0 );
            roads[index].p_startPoint.init( {l_pos.x, l_pos.y, l_pos.z, l_pos.gammaAngle} );
        }

        roads[index].init(); // initialize the road completely
    }

    updateConversionFactors();


}


CFloat CRoadNetwork::getLatitude( CFloat f_x, CFloat f_y )
{
    // Rotate x and y coordinates of ego/object according to map orientation...
    CFloat l_lat = sin( p_mapOrientation ) * f_x + cos( p_mapOrientation ) * f_y; // 'l_y' points in lateral direction (positive: North)
    // ... and add map offsets from roadNetwork
    return p_gnssLatitude + l_lat / m_metersPerDegreeLatitude;
}


CFloat CRoadNetwork::getLongitude( CFloat f_x, CFloat f_y )
{
    // Rotate x and y coordinates of ego/object according to map orientation...
    CFloat l_lon = cos( p_mapOrientation ) * f_x - sin( p_mapOrientation ) * f_y; // 'l_x' points in longitudinal direction (positive: East)
    // ... and add map offsets from roadNetwork
    return p_gnssLongitude + l_lon / m_meterPerDegreeLongitude;
}


/*------------------*/
/* private methods  */
/*------------------*/
void CRoadNetwork::calc( CFloat f_dT, CFloat f_time )
{

    /* calculate roads */
    roads.process( f_dT, f_time );


}

void CRoadNetwork::updateConversionFactors()
{
    // Calculate conversion factors (meters <-> degrees).
    // References for this approximation:
    //  - https://en.wikipedia.org/wiki/Geographic_coordinate_system#Length_of_a_degree
    //  - https://gis.stackexchange.com/questions/75528/understanding-terms-in-length-of-degree-formula
    m_metersPerDegreeLatitude = 111132.92
                                - 559.82   * cos( ::sim::to_radians( 2 * p_gnssLatitude ) )
                                + 1.175  * cos( ::sim::to_radians( 4 * p_gnssLatitude ) )
                                - 0.0023 * cos( ::sim::to_radians( 6 * p_gnssLatitude ) );
    m_meterPerDegreeLongitude = 111412.84   * cos( ::sim::to_radians( p_gnssLatitude ) )
                                - 93.5    * cos( ::sim::to_radians( 3 * p_gnssLatitude ) )
                                + 0.118  * cos( ::sim::to_radians( 5 * p_gnssLatitude ) );
    // print("m/degLat: ", m_metersPerDegreeLatitude, ", m/degLon: ", m_metersPerDegreeLatitude);

    // Calculate conversion factors (meters <-> degrees).
    // References for this approximation:
    //  - https://en.wikipedia.org/wiki/Geographic_coordinate_system#Length_of_a_degree
    //  - https://gis.stackexchange.com/questions/75528/understanding-terms-in-length-of-degree-formula
    m_metersPerDegreeLatitude = 111132.92
                                - 559.82   * cos( ::sim::to_radians( 2 * p_gnssLatitude ) )
                                + 1.175  * cos( ::sim::to_radians( 4 * p_gnssLatitude ) )
                                - 0.0023 * cos( ::sim::to_radians( 6 * p_gnssLatitude ) );
    m_meterPerDegreeLongitude = 111412.84   * cos( ::sim::to_radians( p_gnssLatitude ) )
                                - 93.5    * cos( ::sim::to_radians( 3 * p_gnssLatitude ) )
                                + 0.118  * cos( ::sim::to_radians( 5 * p_gnssLatitude ) );
    // print("m/degLat: ", m_metersPerDegreeLatitude, ", m/degLon: ", m_metersPerDegreeLatitude);
}
