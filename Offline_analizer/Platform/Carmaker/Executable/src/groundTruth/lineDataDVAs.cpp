/*
 * FILE:            lineDataDVAs.cpp
 * SW-COMPONENT:    lineDataDVAs
 * DESCRIPTION:     Source file for the lineDataDVAs component
 * COPYRIGHT:       © 2023 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#include "lineDataDVAs.h"
#include <string>

std::string sensor_name_to_find = "Line";

RbGroundTruthSensor g_groundTruthSensor;

int RB_Line_IsActive()
{
    return (GroundTruthSensor_FindIndexForName(sensor_name_to_find.c_str()) != -1) ? (INT_ST_ON) : (INT_ST_OFF);
}

int RB_GT_Line_DeclQuants()
{
#if defined(RB_INT_VARIANT_HANDLING_ON)
    if(RB_Line_IsActive() == INT_ST_ON)
#endif
    {
        std::string base_name = "RB.GroundTruth.Line";

        std::string n_lines = base_name + ".nLines";
        DDefInt(NULL, n_lines.c_str(), "", &g_groundTruthSensor.n_lines,  DVA_None);

        for (int i = 0; i < MAX_LINES_PER_SENSOR; i++)
        {
            std::string line_n_points = base_name + ".object" + std::to_string(i) + ".Line.nPoints";
            std::string line_type = base_name + ".object" + std::to_string(i) + ".Line.Type";
            std::string line_width = base_name + ".object" + std::to_string(i) + ".Line.Width";
            
            DDefInt(NULL, line_n_points.c_str(), "", &g_groundTruthSensor.lines[i].line_n_points,  DVA_None);
            DDefInt(NULL, line_type.c_str(), "", &g_groundTruthSensor.lines[i].line_type,  DVA_None);
            DDefDouble(NULL, line_width.c_str(), "", &g_groundTruthSensor.lines[i].line_width,  DVA_None);


            for (int j = 0; j < MAX_NUMBER_OF_POINTS; j++)
            {
                std::string line_points_x = base_name + ".object" + std::to_string(i) + ".Line.Point" + std::to_string(j) + ".x";
                std::string line_points_y = base_name + ".object" + std::to_string(i) + ".Line.Point" + std::to_string(j) + ".y";

                DDefDouble(NULL, line_points_x.c_str(), "", &g_groundTruthSensor.lines[i].line_points[j][0], DVA_None);
                DDefDouble(NULL, line_points_y.c_str(), "", &g_groundTruthSensor.lines[i].line_points[j][1], DVA_None);
            }        
        }
    }
    
    return 0;
}
