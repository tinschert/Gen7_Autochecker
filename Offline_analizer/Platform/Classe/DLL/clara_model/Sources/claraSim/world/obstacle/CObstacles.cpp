/*******************************************************************************
@author Robert Erhart, ett2si (19.02.2016)
@copyright (c) Robert Bosch GmbH 2016-2024. All rights reserved.
*******************************************************************************/

#include "CObstacles.h"


//*********************************
// constructor/destructor/copy/move
//*********************************
CObstacles::CObstacles( CInt numberOfObstaclesDynamic, CInt numberOfObstaclesStatic ):
    ObstacleDynamic( numberOfObstaclesDynamic ),
    ObstacleStatic( numberOfObstaclesStatic )
{
    addMessageOutput( o_numberOfObstaclesDynamic, static_cast<uint32_t>( numberOfObstaclesDynamic ), CObstacleDoc::o_numberOfObstaclesDynamic );
    addMessageOutput( o_numberOfObstaclesStatic, static_cast<uint32_t>( numberOfObstaclesStatic ), CObstacleDoc::o_numberOfObstaclesStatic );

    if( numberOfObstaclesDynamic > 0 )
    {
        ObstacleDynamic[0].p_type.setInit( EObstacleTyp::CAR );
        ObstacleDynamic[0].o_coursePosition.setInit( 20 );
    }
}

CObstacles::~CObstacles()
{}


//*******************************
// methods
//*******************************
void CObstacles::init( CRoadNetwork& f_roadNetwork_r,
                       IMessage<CBool>& f_staticSimulation )
{
    for( size_t l_index = 0; l_index < ObstacleDynamic.size(); ++l_index )
    {
        ObstacleDynamic[l_index].init( f_roadNetwork_r, f_staticSimulation );
    }

    //set roadBoundary
    CInt l_indexStaticObstacle = o_numberOfObstaclesStatic - 1;
    for( size_t l_indexRoad = 0; l_indexRoad < static_cast<size_t>( f_roadNetwork_r.o_NumberOfRoads ) and l_indexStaticObstacle > 10; ++l_indexRoad )
    {
        long double l_lengthOfRoad = f_roadNetwork_r.roads[l_indexRoad].o_lengthOfCourse.get();
        long double l_coursePositionSum = 0;
        for( size_t l_indexRoadBoundary = 0; l_indexRoadBoundary < f_roadNetwork_r.roads[l_indexRoad].p_roadBoundary.size(); l_indexRoadBoundary += 7 )
        {
            //  roadBoundary
            //  [ lengthRoadSegment, type, distance, side, p_depth, p_height, p_width]
            //                                              [m]    length road segment
            //                                              [enum] type
            //                                              [m]    distance between boundaries
            //                                              [enum] side 0:no 1:left, 2:right,  3:both
            //                                              [m]    depth of the obstacle
            //                                              [m]    height of the obstacle
            //                                              [m]    width of the obstacle
            CFloat l_lengthRoadSegment = f_roadNetwork_r.roads[l_indexRoad].p_roadBoundary[l_indexRoadBoundary] + l_coursePositionSum;
            CInt l_typ = static_cast<CInt>( f_roadNetwork_r.roads[l_indexRoad].p_roadBoundary[l_indexRoadBoundary + 1] );
            CFloat l_distance = f_roadNetwork_r.roads[l_indexRoad].p_roadBoundary[l_indexRoadBoundary + 2];
            CInt l_side = static_cast<CInt>( f_roadNetwork_r.roads[l_indexRoad].p_roadBoundary[l_indexRoadBoundary + 3] );
            CFloat l_depth = f_roadNetwork_r.roads[l_indexRoad].p_roadBoundary[l_indexRoadBoundary + 4];
            CFloat l_height = f_roadNetwork_r.roads[l_indexRoad].p_roadBoundary[l_indexRoadBoundary + 5];
            CFloat l_width = f_roadNetwork_r.roads[l_indexRoad].p_roadBoundary[l_indexRoadBoundary + 6];
            for( ; l_indexStaticObstacle > 10 and l_coursePositionSum < l_lengthOfRoad and l_coursePositionSum < l_lengthRoadSegment; l_coursePositionSum += l_distance )
            {
                if( ( l_side & 0x1 ) > 0 )
                {
                    //left
                    CInt l_indexLane = f_roadNetwork_r.roads[l_indexRoad].o_indexOfLeftmostLane.get();
                    long double l_lateralOffset = f_roadNetwork_r.roads[l_indexRoad].lanes[l_indexLane].getTrackWidth( l_coursePositionSum ) / 2 + 0.5;
                    ObstacleStatic[l_indexStaticObstacle].p_type.setInit( l_typ );
                    ObstacleStatic[l_indexStaticObstacle].p_depth.setInit( l_depth );
                    ObstacleStatic[l_indexStaticObstacle].p_height.setInit( l_height );
                    ObstacleStatic[l_indexStaticObstacle].p_width.setInit( l_width );
                    ObstacleStatic[l_indexStaticObstacle].p_road.setInit( l_indexRoad );
                    ObstacleStatic[l_indexStaticObstacle].p_lane.setInit( l_indexLane );
                    ObstacleStatic[l_indexStaticObstacle].p_coursePosition.setInit( l_coursePositionSum );
                    ObstacleStatic[l_indexStaticObstacle].p_lateralOffset.setInit( l_lateralOffset );
                    l_indexStaticObstacle--;
                }
                if( ( l_side & 0x2 ) > 0 )
                {
                    //right
                    CInt l_indexLane = f_roadNetwork_r.roads[l_indexRoad].o_indexOfRightmostLane.get();
                    long double l_lateralOffset = - f_roadNetwork_r.roads[l_indexRoad].lanes[l_indexLane].getTrackWidth( l_coursePositionSum ) / 2 - 0.5;
                    ObstacleStatic[l_indexStaticObstacle].p_type.setInit( l_typ );
                    ObstacleStatic[l_indexStaticObstacle].p_depth.setInit( l_depth );
                    ObstacleStatic[l_indexStaticObstacle].p_height.setInit( l_height );
                    ObstacleStatic[l_indexStaticObstacle].p_width.setInit( l_width );
                    ObstacleStatic[l_indexStaticObstacle].p_road.setInit( l_indexRoad );
                    ObstacleStatic[l_indexStaticObstacle].p_lane.setInit( l_indexLane );
                    ObstacleStatic[l_indexStaticObstacle].p_coursePosition.setInit( l_coursePositionSum );
                    ObstacleStatic[l_indexStaticObstacle].p_lateralOffset.setInit( l_lateralOffset );
                    l_indexStaticObstacle--;
                }
            }
        }
    }

    for( size_t l_index = 0; l_index < ObstacleStatic.size(); ++l_index )
    {
        ObstacleStatic[l_index].init( f_roadNetwork_r );
    }
}

void CObstacles::calc( CFloat f_dT, CFloat f_time )
{
    for( size_t l_index = 0; l_index < ObstacleDynamic.size(); ++l_index )
    {
        ObstacleDynamic[l_index].process( f_dT, f_time );
    }
    //ObstacleStatic nothing to do
}
