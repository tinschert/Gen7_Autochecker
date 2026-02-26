/*
 * FILE:            objectDataDVAs.h
 * SW-COMPONENT:    objectDataDVAs
 * DESCRIPTION:     Header file for the objectDataDVAs component
 * COPYRIGHT:       © 2017 - 2023 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#ifndef OBJECT_DATA_H_
#define OBJECT_DATA_H_

#include <Config.h>

#include "DataDict.h"

typedef enum {
    RT_DRIVING = 0,
    RT_PARKING = 1
} eRType;

typedef struct tObject
{
    // Object CarMaker ID
    int	objId {0};
    
    int	radar_type {0};

    // Object Data
    double dxN {0.0};
    double dyN {0.0};
    double dzN {0.0};
    double vxN {0.0};  
    double vyN {0.0};
    double axN {0.0};
    double ayN {0.0};
    double dLengthN {0.0};
    double dWidthN {0.0};
    double alpPiYawAngleN {0.0};
    unsigned char classification {0U};

    // Radar Object Data
    int	inLineOfSight {0};
    double rcsN {0.0};
    double snrN {0.0};
    double signalStrengthN {0.0};

}tObject;

typedef struct tSensorData
{
    double mountPosX {0.0};
    double mountPosY {0.0};
    double mountPosZ {0.0};

	unsigned int object_count;
	tObject objects[Config::Radar::MAX_RADAR_OBJECTS];
}tSensorData;

typedef struct tRbRadarData
{
	unsigned int radar_type_req[Config::Radar::TOTAL_RADAR_COUNT];
    tSensorData radarSensorData[Config::Radar::TOTAL_RADAR_COUNT];
}tRbRadarData;

#endif /* OBJECT_DATA_H_ */
