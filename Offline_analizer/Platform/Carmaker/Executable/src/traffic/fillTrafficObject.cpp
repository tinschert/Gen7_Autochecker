/*
 * FILE:            fillTrafficObject.cpp
 * SW-COMPONENT:    fillTrafficObject
 * DESCRIPTION:     Source file for the fillTrafficObject component
 * COPYRIGHT:       © 2024 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#define _USE_MATH_DEFINES
 
#include "fillTrafficObject.h"
#include "trafficDVAs.h"
#include <chrono>
#include <cmath>
#include <DataDict.h>
#include <DirectVarAccess.h>
#include <string>
#include "SimCore.h"
#include <Log.h>
#include <Car/Car.h>

extern RbTraffic g_rbTraffic;

typedef enum tDVAWriteAccess {
    UAQ_SET = 0,
    DVA_WRITE
};

typedef enum tDVACtrl {
    DVA_CTRL_RELEASED = 0,
    DVA_CTRL_LOCKED
};

typedef enum tIndLightStatus {
    IND_LI_OFF = 0,
    IND_LI_LEFT,
    IND_LI_RIGHT,
    IND_LI_HAZARD
};

typedef enum tHeadLightStatus {
    HEAD_LI_OFF = 0,
    HEAD_LI_ON
};

struct{
    double x; // m
    double y; // m
}g_prev_target_coord[MAX_NUMBER_OF_TRAFFIC_OBJ];

uint64_t prev_t_stamp_us{0};

// check if two values are not equal. True if they are not equal, otherwise false.
bool is_neq(double value1, double value2)
{
    return std::abs(value1 - value2) > 0.001;
}

// sets a dict entry if a value was updated
void set_value_if_updated(tDDictEntry *handle_to_set, const char * DVA_to_set, double value_to_set, bool update_value, tDVAWriteAccess write_access, tDVACtrl DVA_ctrl_status)
{
    if (handle_to_set != nullptr && update_value)
    {
        if(write_access == UAQ_SET)
        {
            handle_to_set->SetFunc(value_to_set, handle_to_set->Var);
        }
        else if(write_access == DVA_WRITE)
        {
            if(DVA_to_set != nullptr)
            {
                if(DVA_ctrl_status == DVA_CTRL_RELEASED)
                {
                    DVA_WriteRequest(DVA_to_set, OWMode_Abs, 1, 0, 1, value_to_set, nullptr);
                }
                else if(DVA_ctrl_status == DVA_CTRL_LOCKED)
                {
                    DVA_WriteRequest(DVA_to_set, OWMode_Abs, -1, 0, 1, value_to_set, nullptr);
                }
            }
        }
    }
}

double ConfineEgoAngle_in_rad(double angle_in_rad)
{
    double cAngle{0.0};
    
    // limit angle withween [0..360]°
    cAngle = angle_in_rad - (double)((long)(angle_in_rad / (2*M_PI))) * 2*M_PI;
    // left side [0..+180]°, right side: [0..-180]°
    cAngle = (cAngle > M_PI) ? (-2*M_PI + cAngle) : ((cAngle < -M_PI) ? (2*M_PI + cAngle) : cAngle);
    
    return cAngle;
}

double ConfineTrgt2EgoAngle_in_rad(double trgt_y, double ego_y, double angle_in_rad)
{
    double cAngle{0.0};
    
    // modified absolute value
    cAngle = (angle_in_rad < 0) ? (M_PI + angle_in_rad) : angle_in_rad;
    // sign of angle
    cAngle = ((trgt_y - ego_y) < 0) ? (-cAngle) : (cAngle);
    
    return cAngle;
}

double GetEgoTrgtDist_in_m(double trgt_x_in_m, double trgt_y_in_m, double ego_x_in_m, double ego_y_in_m)
{
    return std::sqrt(std::pow(trgt_x_in_m - ego_x_in_m, 2) + std::pow(trgt_y_in_m - ego_y_in_m, 2));
}

double GetDy_in_m(double trgt_x_in_m, double trgt_y_in_m, double ego_x_in_m, double ego_y_in_m, double ego_yaw_angle_in_rad)
{
    double dy;
    double ego_to_trgt_dist_in_m;

    dy = 0;
    ego_to_trgt_dist_in_m = GetEgoTrgtDist_in_m(trgt_x_in_m, trgt_y_in_m, ego_x_in_m, ego_y_in_m);

    if(ego_to_trgt_dist_in_m != 0)
    {
        dy = std::sin(ConfineTrgt2EgoAngle_in_rad(trgt_y_in_m, ego_y_in_m, std::acos((trgt_x_in_m - ego_x_in_m) / ego_to_trgt_dist_in_m)) - ConfineEgoAngle_in_rad(ego_yaw_angle_in_rad)) * ego_to_trgt_dist_in_m;
    }

    return dy;
}

double GetDx_in_m(double trgt_x_in_m, double trgt_y_in_m, double ego_x_in_m, double ego_y_in_m, double ego_yaw_angle_in_rad)
{
    double dx;
    double ego_to_trgt_dist_in_m;

    dx = 0;
    ego_to_trgt_dist_in_m = GetEgoTrgtDist_in_m(trgt_x_in_m, trgt_y_in_m, ego_x_in_m, ego_y_in_m);

    if(ego_to_trgt_dist_in_m != 0)
    {
        dx = std::cos(ConfineTrgt2EgoAngle_in_rad(trgt_y_in_m, ego_y_in_m, std::acos((trgt_x_in_m - ego_x_in_m) / ego_to_trgt_dist_in_m)) - ConfineEgoAngle_in_rad(ego_yaw_angle_in_rad)) * ego_to_trgt_dist_in_m;
    }

    return dx;
}

double GetVx_in_mps(double trgt_x_in_m, double& prev_trgt_x_in_m, double dt_in_s)
{
    double vx{0.0};
    vx = (trgt_x_in_m - prev_trgt_x_in_m) / dt_in_s;
    prev_trgt_x_in_m = trgt_x_in_m;
    return vx;
}

double GetVy_in_mps(double trgt_y_in_m, double& prev_trgt_y_in_m, double dt_in_s)
{
    double vy{0.0};
    vy = (trgt_y_in_m - prev_trgt_y_in_m) / dt_in_s;
    prev_trgt_y_in_m = trgt_y_in_m;
    return vy;
}

// value conversion from RB DVA to CarMaker DVA
int GetIndicatorLightStatus(int ind_light)
{
    int liSts;

    switch (ind_light)
    {
        case IND_LI_LEFT:
            liSts = 1;
            break;
        case IND_LI_RIGHT:
            liSts = -1;
            break;
        default:
            liSts = 0;
            break;
    }

    return liSts;
}

// value conversion from RB DVA to CarMaker DVA
int GetHazardLightStatus(int ind_light)
{
    int liSts;

    switch (ind_light)
    {
        case IND_LI_HAZARD:
            liSts = 1;
            break;
        default:
            liSts = 0;
            break;
    }
    
    return liSts;
}

// value conversion from RB DVA to CarMaker DVA
int GetLowBeamStatus(int headlight)
{
    int liSts;

    switch (headlight)
    {
        case HEAD_LI_OFF:
            liSts = 0;
            break;
        case HEAD_LI_ON:
            liSts = 2;
            break;
        default:
            liSts = 0;
            break;
    }
    
    return liSts;
}

// value conversion from RB DVA to CarMaker DVA
int GetHighBeamStatus(int headlight)
{
    int liSts;

    switch (headlight)
    {
        case HEAD_LI_OFF:
            liSts = 0;
            break;
        case HEAD_LI_ON:
            liSts = 1;
            break;
        default:
            liSts = 0;
            break;
    }
    
    return liSts;
}

int fillTrafficObject()
{
    if(RB_Traffic_IsActive() == INT_ST_ON)
    {
        g_rbTraffic.prev_t_stamp_s = g_rbTraffic.t_stamp_s;
        g_rbTraffic.t_stamp_s = TimeGlobal;

    if (SimCore.State != SCState_Simulate)
    {
        g_rbTraffic.n_objs = 0;
        return 0;
    }

    g_rbTraffic.n_objs = Traffic_GetNObj();
    for (int i = 0; i < MAX_NUMBER_OF_TRAFFIC_OBJ && i < Traffic_GetNObj(); i++)
    {
        // get traffic obj by index
        tTrafficObj *obj = Traffic_GetByTrfId(i);

        if (obj == nullptr)
        {
            continue;
        }

        /// 1) Variables that we read from carmaker and are forwarded to the "RB" traffic structure 
        std::string object_name = obj->Cfg.Name;
        
        // std::string traffic_lat_man_idx = "Traffic." + object_name + ".Lat.ManIdx";
        // tDDictEntry *const h_lat_man_idx = DDictGetEntry(traffic_lat_man_idx.c_str());

        // if (h_lat_man_idx != nullptr)
        // {
        //     g_rbTraffic.trafficObjects[i].lat_man_idx = h_lat_man_idx->GetFunc(h_lat_man_idx->Var);
        // }

        // std::string traffic_long_man_idx = "Traffic." + object_name + ".Long.ManIdx";
        // tDDictEntry *const h_long_man_idx = DDictGetEntry(traffic_long_man_idx.c_str());

        // if(h_long_man_idx != nullptr)
        // {
        //     g_rbTraffic.trafficObjects[i].long_man_idx = h_long_man_idx->GetFunc(h_long_man_idx->Var);
        // }
        
        g_rbTraffic.trafficObjects[i].obj_id = obj->Cfg.ObjId;

        /// 2) Variables that are modifiable from external
        // 2.1) check if the values were updated by the user by comparing with the stored value from the last cycle
        bool lat_step_idx_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].lat_step_idx, g_rbTraffic.trafficObjects[i].lat_step_idx_last_cycle);
        bool long_step_idx_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].long_step_idx, g_rbTraffic.trafficObjects[i].long_step_idx_last_cycle);
        bool long_vel_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].long_vel, g_rbTraffic.trafficObjects[i].long_vel_last_cycle);
        bool s_road_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].s_road, g_rbTraffic.trafficObjects[i].s_road_last_cycle);
        bool t_road_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].t_road, g_rbTraffic.trafficObjects[i].t_road_last_cycle);
        
        bool dr_z_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].dr_z, g_rbTraffic.trafficObjects[i].dr_z_last_cycle);
        bool dt_x_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].dt_x, g_rbTraffic.trafficObjects[i].dt_x_last_cycle);
        bool dt_y_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].dt_y, g_rbTraffic.trafficObjects[i].dt_y_last_cycle);
        bool dt_z_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].dt_z, g_rbTraffic.trafficObjects[i].dt_z_last_cycle);

        bool steer_ang_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].steer_ang, g_rbTraffic.trafficObjects[i].steer_ang_last_cycle);
        
        bool ind_light_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].ind_light, g_rbTraffic.trafficObjects[i].ind_light_last_cycle);
        bool low_beam_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].low_beam, g_rbTraffic.trafficObjects[i].low_beam_last_cycle);
        bool high_beam_updated_by_user = is_neq(g_rbTraffic.trafficObjects[i].high_beam, g_rbTraffic.trafficObjects[i].high_beam_last_cycle);

        // 2.2) get handles of dict entries
        std::string traffic_obj_lat_step_idx = "Traffic." + object_name + ".Lat.StepIdx";
        std::string traffic_obj_long_step_idx = "Traffic." + object_name + ".Long.StepIdx";
        std::string traffic_obj_long_vel = "Traffic." + object_name + ".LongVel";
        std::string traffic_obj_s_road = "Traffic." + object_name + ".sRoad";
        std::string traffic_obj_t_road = "Traffic." + object_name + ".tRoad";
        
        std::string traffic_obj_r_z = "Traffic." + object_name + ".rz";
        std::string traffic_obj_t_x = "Traffic." + object_name + ".tx";
        std::string traffic_obj_t_y = "Traffic." + object_name + ".ty";
        std::string traffic_obj_t_z = "Traffic." + object_name + ".tz";

        std::string traffic_obj_steer_ang = "Traffic." + object_name + ".SteerAng";

        std::string traffic_obj_ind_light = "Traffic." + object_name + ".Lights.Indicator";
        std::string traffic_obj_hazard_light = "Traffic." + object_name + ".Lights.Hazard";
        std::string traffic_obj_low_beam = "Traffic." + object_name + ".Lights.MainLight";
        std::string traffic_obj_high_beam = "Traffic." + object_name + ".Lights.HighBeam";
        
        tDDictEntry *const handle_lat_step_idx = DDictGetEntry(traffic_obj_lat_step_idx.c_str());
        tDDictEntry *const handle_long_step_idx = DDictGetEntry(traffic_obj_long_step_idx.c_str());
        tDDictEntry *const handle_long_vel = DDictGetEntry(traffic_obj_long_vel.c_str());
        tDDictEntry *const handle_s_road = DDictGetEntry(traffic_obj_s_road.c_str());
        tDDictEntry *const handle_t_road = DDictGetEntry(traffic_obj_t_road.c_str());
        
        tDDictEntry *const handle_r_z = DDictGetEntry(traffic_obj_r_z.c_str());
        tDDictEntry *const handle_t_x = DDictGetEntry(traffic_obj_t_x.c_str());
        tDDictEntry *const handle_t_y = DDictGetEntry(traffic_obj_t_y.c_str());
        tDDictEntry *const handle_t_z = DDictGetEntry(traffic_obj_t_z.c_str());
        
        tDDictEntry *const handle_steer_ang = DDictGetEntry(traffic_obj_steer_ang.c_str());

        tDDictEntry *const handle_ind_light = DDictGetEntry(traffic_obj_ind_light.c_str());
        tDDictEntry *const handle_hazard_light = DDictGetEntry(traffic_obj_hazard_light.c_str());
        tDDictEntry *const handle_low_beam = DDictGetEntry(traffic_obj_low_beam.c_str());
        tDDictEntry *const handle_high_beam = DDictGetEntry(traffic_obj_high_beam.c_str());

        // 2.3.1) If the user has updated the value, take this value (value_to_set / 2nd argument, i.e. value in global structure) and set it in the traffic structure (handle)
        // set_value_if_updated(handle, value_to_set, updated)
        set_value_if_updated(handle_lat_step_idx, NULL, g_rbTraffic.trafficObjects[i].lat_step_idx, lat_step_idx_updated_by_user, UAQ_SET, DVA_CTRL_RELEASED);
        set_value_if_updated(handle_long_step_idx, NULL, g_rbTraffic.trafficObjects[i].long_step_idx, long_step_idx_updated_by_user, UAQ_SET, DVA_CTRL_RELEASED);
        set_value_if_updated(handle_long_vel, NULL, g_rbTraffic.trafficObjects[i].long_vel, long_vel_updated_by_user, UAQ_SET, DVA_CTRL_RELEASED);
        set_value_if_updated(handle_s_road, NULL, g_rbTraffic.trafficObjects[i].s_road, s_road_updated_by_user, UAQ_SET, DVA_CTRL_RELEASED);
        set_value_if_updated(handle_t_road, NULL, g_rbTraffic.trafficObjects[i].t_road, t_road_updated_by_user, UAQ_SET, DVA_CTRL_RELEASED);
        set_value_if_updated(handle_steer_ang, NULL, g_rbTraffic.trafficObjects[i].steer_ang, steer_ang_updated_by_user, UAQ_SET, DVA_CTRL_RELEASED);
        set_value_if_updated(handle_ind_light, traffic_obj_ind_light.c_str(), GetIndicatorLightStatus(g_rbTraffic.trafficObjects[i].ind_light), ind_light_updated_by_user, DVA_WRITE, DVA_CTRL_LOCKED);
        set_value_if_updated(handle_hazard_light, traffic_obj_hazard_light.c_str(), GetHazardLightStatus(g_rbTraffic.trafficObjects[i].ind_light), ind_light_updated_by_user, DVA_WRITE, DVA_CTRL_LOCKED);
        set_value_if_updated(handle_low_beam, traffic_obj_low_beam.c_str(), GetLowBeamStatus(g_rbTraffic.trafficObjects[i].low_beam), low_beam_updated_by_user, DVA_WRITE, DVA_CTRL_LOCKED);
        set_value_if_updated(handle_high_beam, traffic_obj_high_beam.c_str(), GetHighBeamStatus(g_rbTraffic.trafficObjects[i].high_beam), high_beam_updated_by_user, DVA_WRITE, DVA_CTRL_LOCKED);
        
        // 2.3.2) If the user has update the value, take this value, do conversion, and set in traffic structure.
        set_value_if_updated(handle_r_z, NULL, g_rbTraffic.trafficObjects[i].dr_z + Car.Fr1.r_zyx[2], dr_z_updated_by_user, UAQ_SET, DVA_CTRL_RELEASED);
        set_value_if_updated(handle_t_x, NULL, g_rbTraffic.trafficObjects[i].dt_x + Car.Fr1.t_0[0], dt_x_updated_by_user, UAQ_SET, DVA_CTRL_RELEASED);
        set_value_if_updated(handle_t_y, NULL, g_rbTraffic.trafficObjects[i].dt_y + Car.Fr1.t_0[1], dt_y_updated_by_user, UAQ_SET, DVA_CTRL_RELEASED);
        set_value_if_updated(handle_t_z, NULL, g_rbTraffic.trafficObjects[i].dt_z + Car.Fr1.t_0[2], dt_z_updated_by_user, UAQ_SET, DVA_CTRL_RELEASED);

        // 2.4.1) Take over the traffic structure value to the rb structure value. Needed for use case where value shall be read.
        // also store value in last cycle variable in order that check if a value was updated by user works.
        if(handle_lat_step_idx != nullptr)
        {
            g_rbTraffic.trafficObjects[i].lat_step_idx = handle_lat_step_idx->GetFunc(handle_lat_step_idx->Var);
            g_rbTraffic.trafficObjects[i].lat_step_idx_last_cycle = handle_lat_step_idx->GetFunc(handle_lat_step_idx->Var);
        }
        if(handle_long_step_idx != nullptr)
        {
            g_rbTraffic.trafficObjects[i].long_step_idx = handle_long_step_idx->GetFunc(handle_long_step_idx->Var);
            g_rbTraffic.trafficObjects[i].long_step_idx_last_cycle = handle_long_step_idx->GetFunc(handle_long_step_idx->Var);
        }

        g_rbTraffic.trafficObjects[i].long_vel = obj->LongVel;
        g_rbTraffic.trafficObjects[i].long_vel_last_cycle = obj->LongVel;

        g_rbTraffic.trafficObjects[i].s_road = obj->sRoad;
        g_rbTraffic.trafficObjects[i].s_road_last_cycle = obj->sRoad;

        g_rbTraffic.trafficObjects[i].t_road = obj->tRoad;
        g_rbTraffic.trafficObjects[i].t_road_last_cycle = obj->tRoad;

        if(handle_steer_ang != nullptr)
        {
            g_rbTraffic.trafficObjects[i].steer_ang = handle_steer_ang->GetFunc(handle_steer_ang->Var);
            g_rbTraffic.trafficObjects[i].steer_ang_last_cycle = g_rbTraffic.trafficObjects[i].steer_ang;
        }

        // note: no feedback is needed from original DVAs, because DVA_WRITE is applied at value set
        g_rbTraffic.trafficObjects[i].ind_light_last_cycle = g_rbTraffic.trafficObjects[i].ind_light;
        g_rbTraffic.trafficObjects[i].low_beam_last_cycle = g_rbTraffic.trafficObjects[i].low_beam;
        g_rbTraffic.trafficObjects[i].high_beam_last_cycle = g_rbTraffic.trafficObjects[i].high_beam;

        //g_rbTraffic.trafficObjects[i].lat_vel = obj->LatVel;
        g_rbTraffic.trafficObjects[i].lat_a = obj->a_1[1];
        
        // 2.4.2) Take over the traffic structure value to the rb structure values. 
        // For these values it was defined with the HIL colleagues that we take the delta values and do the calculation here.
        g_rbTraffic.trafficObjects[i].dr_z = (obj->r_zyx[2] - Car.Fr1.r_zyx[2]);
        g_rbTraffic.trafficObjects[i].dr_z_last_cycle = g_rbTraffic.trafficObjects[i].dr_z;

        g_rbTraffic.trafficObjects[i].dt_x = (obj->t_0[0] - Car.Fr1.t_0[0]);
        g_rbTraffic.trafficObjects[i].dt_x_last_cycle = g_rbTraffic.trafficObjects[i].dt_x;

        g_rbTraffic.trafficObjects[i].dt_y = (obj->t_0[1] - Car.Fr1.t_0[1]);
        g_rbTraffic.trafficObjects[i].dt_y_last_cycle = g_rbTraffic.trafficObjects[i].dt_y;

        g_rbTraffic.trafficObjects[i].dt_z = (obj->t_0[2] - Car.Fr1.t_0[2]);
        g_rbTraffic.trafficObjects[i].dt_z_last_cycle = g_rbTraffic.trafficObjects[i].dt_z;

            g_rbTraffic.trafficObjects[i].rel_dx = GetDx_in_m(obj->t_0[0], obj->t_0[1], Car.Fr1.t_0[0], Car.Fr1.t_0[1], Car.Yaw);
            g_rbTraffic.trafficObjects[i].rel_dy = GetDy_in_m(obj->t_0[0], obj->t_0[1], Car.Fr1.t_0[0], Car.Fr1.t_0[1], Car.Yaw);
            g_rbTraffic.trafficObjects[i].rel_vx = GetVx_in_mps(g_rbTraffic.trafficObjects[i].rel_dx, g_prev_target_coord[i].x, (g_rbTraffic.t_stamp_s - g_rbTraffic.prev_t_stamp_s));
            g_rbTraffic.trafficObjects[i].rel_vy = GetVy_in_mps(g_rbTraffic.trafficObjects[i].rel_dy, g_prev_target_coord[i].y, (g_rbTraffic.t_stamp_s - g_rbTraffic.prev_t_stamp_s));
        }
    }

    return 0;
}