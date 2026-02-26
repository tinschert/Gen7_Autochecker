/*
 * FILE:            lineDataDVAs.h
 * SW-COMPONENT:    lineDataDVAs
 * DESCRIPTION:     Header file for the lineDataDVAs component
 * COPYRIGHT:       © 2023 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */


#ifndef LINE_DATA_DVAS_H_
#define LINE_DATA_DVAS_H_

extern "C" {
    #include "DataDict.h"
}

#include <array>
#include "Vehicle/Sensor_GroundTruth.h"
#include "common/commonDefinitions.h"

constexpr unsigned int MAX_LINES_PER_SENSOR = 6U;
constexpr unsigned int MAX_NUMBER_OF_POINTS = 10U;

struct RbGroundTruthLine
{ 
    int line_n_points{0};

    double line_width{0.0};
    int line_type{0};  

    // for each point in the list, there is an x, and y coordinate
    std::array<std::array<double, 2>, MAX_NUMBER_OF_POINTS> line_points{};
};

struct RbGroundTruthSensor
{
    int n_lines{0};
    std::array<RbGroundTruthLine, MAX_LINES_PER_SENSOR> lines;
};

int RB_Line_IsActive();
int RB_GT_Line_DeclQuants();

#endif /* TRAFFIC_SIGN_DVAS_H_ */