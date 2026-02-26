#ifndef CObstacles_H
#define CObstacles_H
/*!
********************************************************************************
@class CObstacles
@ingroup obstacle
@brief container class for dynamic and static obstacles

@author Robert Erhart, ett2si (19.02.2016)
@copyright (c) Robert Bosch GmbH 2016-2024. All rights reserved.
********************************************************************************
@remark
- calculate the boundary objects of a road
- instantiate, initialize and process the static (CObstacleStatic) and dynamic (CObstacleDynamic) obstacles.
********************************************************************************
@param[out] o_numberOfObstaclesDynamic [0..n] maximum number of available dynamic obstacles
@param[out] o_numberOfObstaclesStatic  [0..n] maximum number of available static obstacles
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CObstacleDoc
{
    const auto o_numberOfObstaclesDynamic = "[0..n] maximum number of available dynamic obstacles";
    const auto o_numberOfObstaclesStatic = "[0..n] maximum number of available static obstacles";
}

#include <claraSim/framework/CModule.h>
#include <claraSim/framework/CModuleVector.h>

#include "CObstacleDynamic.h"
#include "CObstacleStatic.h"

namespace EObstacleTyp
{
    enum EObstacleTyp {INVISIBLE, POINT, CAR, MOTORBIKE, TRUCK, BUS, BICYCLE, PEDESTRIAN, DELINEATOR, UNKNOWN_CLASS};
}

class CObstacles : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CObstacles( CInt numberOfObstaclesDynamic, CInt numberOfObstaclesStatic );
    virtual ~CObstacles();


    //*******************************
    // classes
    //*******************************
public:
    CModuleVector<CObstacleDynamic> ObstacleDynamic;
    CModuleVector<CObstacleStatic> ObstacleStatic;


    //*******************************
    //messages
    //*******************************
public:
    CMessageOutput<CInt> o_numberOfObstaclesDynamic;
    CMessageOutput<CInt> o_numberOfObstaclesStatic;


    //*******************************
    // methods
    //*******************************
public:
    void init( CRoadNetwork& f_roadNetwork_r,
               IMessage<CBool>& f_staticSimulation );
private:
    void calc( CFloat f_dT, CFloat f_time );


    //*******************************
    //variables
    //*******************************
};

#endif // CObstacles_H
