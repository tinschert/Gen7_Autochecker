/*
 * FILE:            fillLineData.cpp
 * SW-COMPONENT:    fillLineData
 * DESCRIPTION:     Source file for the fillLineData component
 * COPYRIGHT:       © 2023 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#include <string>
#include "fillLineData.h"
#include "lineDataDVAs.h"
#include "SimCore.h"

extern RbGroundTruthSensor g_groundTruthSensor;
extern std::string sensor_name_to_find;

int fillGroundTruthLineData()
{
    if(RB_Line_IsActive() == INT_ST_ON)
    {
        if (SimCore.State != SCState_Simulate)
        {
            g_groundTruthSensor.n_lines = 0;
            return 0;
        }

        int sensorId = GroundTruthSensor_FindIndexForName(sensor_name_to_find.c_str());

        const tGroundTruthSensor *const gt_sensor = GroundTruthSensor_GetByIndex(sensorId);

        if (gt_sensor == nullptr)
        {
            return 0;
        }

        for (int i = 0; i < MAX_LINES_PER_SENSOR && i < gt_sensor->nGTObjects_Lines; i++)
        {
            const auto *const line = gt_sensor->GTObj[i].data.line;
            
            if(!line)
            {
                continue;
            }
            
            g_groundTruthSensor.lines[i].line_n_points = line->nPoints;
            g_groundTruthSensor.lines[i].line_width = line->width;
            g_groundTruthSensor.lines[i].line_type = line->lineType;

            for (int j = 0; j < MAX_NUMBER_OF_POINTS && j < line->nPoints; j++)
            {
                g_groundTruthSensor.lines[i].line_points[j][0] = line->points[j][0];
                g_groundTruthSensor.lines[i].line_points[j][1] = line->points[j][1];
            }
        }

        g_groundTruthSensor.n_lines = gt_sensor->nGTObjects_Lines;
    }

    return 0;
}