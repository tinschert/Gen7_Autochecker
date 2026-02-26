/*******************************************************************************
 $Source: CObstacleStatic.cpp $
 $Date: 2017/03/24 08:45:22CET $
 $Revision: 8.5 $

 @author Robert Erhart, ett2si (11.03.2016)
 @copyright (c) Robert Bosch GmbH 2016-2024. All rights reserved.
 *******************************************************************************/

#include "CObstacleStatic.h"
#include "CObstacles.h"  //get enum type

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CObstacleStatic::CObstacleStatic():
    m_roadNetwork_p( nullptr ),
    m_xLocalContour( 0.0, 4 ),
    m_yLocalContour( 0.0, 4 ),
    m_zLocalContour( 0.0, 4 ),
    m_xWorldContour( 0.0, 4 ),
    m_yWorldContour( 0.0, 4 ),
    m_zWorldContour( 0.0, 4 )
{
    /* Initialization messages */
    addMessageParameter( p_type, EObstacleTyp::DELINEATOR, CObstacleStaticDoc::p_type );
    addMessageParameter( p_depth, 0.2, CObstacleStaticDoc::p_depth );
    addMessageParameter( p_height, 1.0, CObstacleStaticDoc::p_height );
    addMessageParameter( p_width, 0.2, CObstacleStaticDoc::p_width );
    addMessageParameter( p_visibility, 1.0, CObstacleStaticDoc::p_visibility );
    addMessageParameter( p_road, -1LL, CObstacleStaticDoc::p_road );
    addMessageParameter( p_lane, 0LL, CObstacleStaticDoc::p_lane );
    addMessageParameter( p_coursePosition, 0, CObstacleStaticDoc::p_coursePosition );
    addMessageParameter( p_lateralOffset, 0, CObstacleStaticDoc::p_lateralOffset );

    addMessageOutput( o_x, 100.0 ); // (use o_xyzWorld; only needed for report visualisation)
    addMessageOutput( o_y, -15.0 ); // (use o_xyzWorld; only needed for report visualisation)
    addMessageOutput( o_z, 0.0 ); // (use o_xyzWorld; only needed for report visualisation)

    addMessageOutput( o_xyzWorld, CFloatVectorXYZ( 100.0, -15.0, 0.0 ), CObstacleStaticDoc::o_xyzWorld );
    addMessageOutput( o_coursePosition, 0.0, CObstacleStaticDoc::o_coursePosition );
    m_xLocalContour = { -p_depth / 2, -p_depth / 2, +p_depth / 2, +p_depth / 2 };
    addMessageOutput( o_xWorldContour, m_xLocalContour, CObstacleStaticDoc::o_xWorldContour );
    m_yLocalContour = { +p_width / 2, -p_width / 2, -p_width / 2, +p_width / 2 };
    addMessageOutput( o_yWorldContour, m_yLocalContour, CObstacleStaticDoc::o_yWorldContour );
    m_zLocalContour = { +p_height / 2, +p_height / 2, +p_height / 2, +p_height / 2 };
    addMessageOutput( o_zWorldContour, m_zLocalContour, CObstacleStaticDoc::o_zWorldContour );
    addMessageOutput( o_yawAngle, 0.0, CObstacleStaticDoc::o_yawAngle );
    addMessageOutput( o_rollAngle, 0.0, CObstacleStaticDoc::o_rollAngle );
    addMessageOutput( o_pitchAngle, 0.0, CObstacleStaticDoc::o_pitchAngle );
}

CObstacleStatic::~CObstacleStatic()
{
}

/*------------------*/
/* public methods  */
/*------------------*/
void CObstacleStatic::init( CRoadNetwork& f_roadNetwork_r )
{
    // define course for obstacle
    m_roadNetwork_p = &f_roadNetwork_r;

    /* link input messages */

    /* Initialization messages */
    initializationMessages();

    m_xLocalContour = { -p_depth / 2, -p_depth / 2, +p_depth / 2, +p_depth / 2 };
    m_yLocalContour = { +p_width / 2, -p_width / 2, -p_width / 2, +p_width / 2 };
    m_zLocalContour = { +p_height / 2, +p_height / 2, +p_height / 2, +p_height / 2 };

    // calc the output messages value
    if( p_road >= 0 )
    {
        SCoursePositionInfo l_positionInfo = m_roadNetwork_p->roads[p_road].lanes[p_lane].getCoursePositionInfo( p_coursePosition, p_lateralOffset );
        o_x.init( l_positionInfo.x );
        o_y.init( l_positionInfo.y );
        o_z.init( l_positionInfo.z );
        o_xyzWorld.init( {l_positionInfo.x, l_positionInfo.y, l_positionInfo.z} );
        o_coursePosition.init( p_coursePosition );
        o_yawAngle.init( l_positionInfo.gammaAngle );
        o_rollAngle.init( -l_positionInfo.crossfallAngleLocal );
        o_pitchAngle.init( -l_positionInfo.slopeAngleLocal );
    }

    //contour Points of obstacle
    for( auto index = 0 ; index < 4; index++ )
    {
        ::sim::coordinateRotation( o_rollAngle, o_pitchAngle, o_yawAngle,
                            m_xLocalContour[index], m_yLocalContour[index], m_zLocalContour[index],
                            m_xWorldContour[index], m_yWorldContour[index], m_zWorldContour[index] );
        m_xWorldContour[index] += o_xyzWorld[0];
        m_yWorldContour[index] += o_xyzWorld[1];
        m_zWorldContour[index] += o_xyzWorld[2];
    }
    o_xWorldContour.init( m_xWorldContour );
    o_yWorldContour.init( m_yWorldContour );
    o_zWorldContour.init( m_zWorldContour );
}

/*------------------*/
/* private methods */
/*------------------*/
void CObstacleStatic::calc( CFloat f_dT, CFloat f_time )
{
}

