/*
 * FILE:            trafficDVAs.h
 * SW-COMPONENT:    trafficDVAs
 * DESCRIPTION:     Header file for the trafficDVAs component
 * COPYRIGHT:       © 2023 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */


#ifndef TRAFFIC_DVAS_H_
#define TRAFFIC_DVAS_H_

#include <Config.h>
#include <array>
#include "Traffic.h"
#include "common/commonDefinitions.h"

constexpr unsigned int MAX_NUMBER_OF_TRAFFIC_OBJ = Config::Radar::MAX_RADAR_OBJECTS;

struct RbTrafficObject
{  
    int lat_man_idx{0};

    int lat_step_idx{0};
    int lat_step_idx_last_cycle{0};

    double lat_vel{0.0};
    double lat_a{0.0};

    // int long_man_idx{0};

    int long_step_idx{0};
    int long_step_idx_last_cycle{0};

    double long_vel{0.0};
    double long_vel_last_cycle{0.0};
    
    int obj_id{0};

    double s_road{0.0};
    double s_road_last_cycle{0.0};

    double t_road{0.0};
    double t_road_last_cycle{0.0};

    double dr_z{0.0};
    double dr_z_last_cycle{0.0};    
    double dt_x{0.0};
    double dt_x_last_cycle{0.0};
    double dt_y{0.0};
    double dt_y_last_cycle{0.0};
    double dt_z{0.0};
    double dt_z_last_cycle{0.0};

    // data relative to ego (read-only)
    double rel_dx{0.0};
    double rel_dy{0.0};
    double rel_vx{0.0};
    double rel_vy{0.0};

    double steer_ang{0.0};
    double steer_ang_last_cycle{0.0};

    int ind_light{0};
    int ind_light_last_cycle{0};
    int low_beam{0};
    int low_beam_last_cycle{0};
    int high_beam{0};
    int high_beam_last_cycle{0};

    int dil_status{0};
};

struct RbTraffic
{
    int n_objs{0};
    double t_stamp_s{0.0};
    double prev_t_stamp_s{0.0};
    std::array<RbTrafficObject, MAX_NUMBER_OF_TRAFFIC_OBJ> trafficObjects{};
};

int RB_Traffic_IsActive();
int RB_Traffic_DeclQuants();

#endif /* TRAFFIC_DVAS_H_ */