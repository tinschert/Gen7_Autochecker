/*
 * FILE:            trafficDVAs.cpp
 * SW-COMPONENT:    trafficDVAs
 * DESCRIPTION:     Source file for the trafficDVAs component
 * COPYRIGHT:       © 2024 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */


#include "trafficDVAs.h"
#include <string>
#include "DataDict.h"
#include "common/objectData.h"

RbTraffic g_rbTraffic;

int RB_Traffic_IsActive()
{
    return (Traffic_GetNObj() != 0) ? (INT_ST_ON) : (INT_ST_OFF);
}

int RB_Traffic_DeclQuants()
{
#if defined(RB_INT_VARIANT_HANDLING_ON)
    if(RB_Traffic_IsActive() == INT_ST_ON)
#endif
    {
        std::string base_name = "RB.TrafficObj";
        
        std::string n_objs = base_name + ".nObjs";
        DDefInt(NULL, n_objs.c_str(), "-", &g_rbTraffic.n_objs, DVA_None);

        for (int i = 0; i < MAX_NUMBER_OF_TRAFFIC_OBJ; i++)
        {
            // std::string traffic_obj_lat_man_idx = base_name + ".object" + std::to_string(i) + ".Lat.ManIdx";
            std::string traffic_obj_lat_step_idx = base_name + ".object" + std::to_string(i) + ".Lat.StepIdx";
            //std::string traffic_obj_lat_vel = base_name + ".object" + std::to_string(i) + ".LatVel";
            std::string traffic_obj_lat_a = base_name + ".object" + std::to_string(i) + ".LatAcc";

            // std::string traffic_obj_long_man_idx = base_name + ".object" + std::to_string(i) + ".Long.ManIdx";
            std::string traffic_obj_long_step_idx = base_name + ".object" + std::to_string(i) + ".Long.StepIdx";
            std::string traffic_obj_long_vel = base_name + ".object" + std::to_string(i) + ".LongVel";
        
            std::string traffic_obj_obj_id = base_name + ".object" + std::to_string(i) + ".ObjId";

            std::string traffic_obj_s_road = base_name + ".object" + std::to_string(i) + ".sRoad";
            std::string traffic_obj_t_road = base_name + ".object" + std::to_string(i) + ".tRoad";
            
            std::string traffic_obj_dr_z = base_name + ".object" + std::to_string(i) + ".drz";
            std::string traffic_obj_dt_x = base_name + ".object" + std::to_string(i) + ".dtx";
            std::string traffic_obj_dt_y = base_name + ".object" + std::to_string(i) + ".dty";
            std::string traffic_obj_dt_z = base_name + ".object" + std::to_string(i) + ".dtz";

            std::string traffic_obj_rel_dx = base_name + ".object" + std::to_string(i) + ".rel_dx";
            std::string traffic_obj_rel_dy = base_name + ".object" + std::to_string(i) + ".rel_dy";
            std::string traffic_obj_rel_vx = base_name + ".object" + std::to_string(i) + ".rel_vx";
            std::string traffic_obj_rel_vy = base_name + ".object" + std::to_string(i) + ".rel_vy";

            std::string traffic_obj_steer_ang = base_name + ".object" + std::to_string(i) + ".SteerAng";

            std::string traffic_obj_ind_light = base_name + ".object" + std::to_string(i) + ".IndLight";
            std::string traffic_obj_low_beam = base_name + ".object" + std::to_string(i) + ".LowBeam";
            std::string traffic_obj_high_beam = base_name + ".object" + std::to_string(i) + ".HighBeam";

            std::string traffic_obj_dil_status = base_name + ".object" + std::to_string(i) + ".DILStatus";

            // Build the DVAs
            // DDefInt(NULL, traffic_obj_lat_man_idx.c_str(), "-", &g_rbTraffic.trafficObjects[i].lat_man_idx, DVA_None);
            DDefInt(NULL, traffic_obj_lat_step_idx.c_str(), "-", &g_rbTraffic.trafficObjects[i].lat_step_idx, DVA_IO_Out);
            //DDefDouble(NULL, traffic_obj_lat_vel.c_str(), "m/s", &g_rbTraffic.trafficObjects[i].lat_vel, DVA_None);
            DDefDouble(NULL, traffic_obj_lat_a.c_str(), "m/s2", &g_rbTraffic.trafficObjects[i].lat_a, DVA_IO_Out);

            // DDefInt(NULL, traffic_obj_long_man_idx.c_str(), "-", &g_rbTraffic.trafficObjects[i].long_man_idx, DVA_None);
            DDefInt(NULL, traffic_obj_long_step_idx.c_str(), "-", &g_rbTraffic.trafficObjects[i].long_step_idx, DVA_IO_Out);
            DDefDouble(NULL, traffic_obj_long_vel.c_str(), "m/s", &g_rbTraffic.trafficObjects[i].long_vel, DVA_IO_Out);
        
            DDefInt(NULL, traffic_obj_obj_id.c_str(), "-", &g_rbTraffic.trafficObjects[i].obj_id, DVA_None);

            DDefDouble(NULL, traffic_obj_s_road.c_str(), "m", &g_rbTraffic.trafficObjects[i].s_road, DVA_IO_Out);
            DDefDouble(NULL, traffic_obj_t_road.c_str(), "m", &g_rbTraffic.trafficObjects[i].t_road, DVA_IO_Out);

            DDefDouble(NULL, traffic_obj_dr_z.c_str(), "rad", &g_rbTraffic.trafficObjects[i].dr_z, DVA_IO_Out);
            DDefDouble(NULL, traffic_obj_dt_x.c_str(), "m", &g_rbTraffic.trafficObjects[i].dt_x, DVA_IO_Out);
            DDefDouble(NULL, traffic_obj_dt_y.c_str(), "m", &g_rbTraffic.trafficObjects[i].dt_y, DVA_IO_Out);
            DDefDouble(NULL, traffic_obj_dt_z.c_str(), "m", &g_rbTraffic.trafficObjects[i].dt_z, DVA_IO_Out);

            DDefDouble(NULL, traffic_obj_rel_dx.c_str(), "m", &g_rbTraffic.trafficObjects[i].rel_dx, DVA_None);
            DDefDouble(NULL, traffic_obj_rel_dy.c_str(), "m", &g_rbTraffic.trafficObjects[i].rel_dy, DVA_None);
            DDefDouble(NULL, traffic_obj_rel_vx.c_str(), "m/s", &g_rbTraffic.trafficObjects[i].rel_vx, DVA_None);
            DDefDouble(NULL, traffic_obj_rel_vy.c_str(), "m/s", &g_rbTraffic.trafficObjects[i].rel_vy, DVA_None);

            DDefDouble(NULL, traffic_obj_steer_ang.c_str(), "rad", &g_rbTraffic.trafficObjects[i].steer_ang, DVA_IO_Out);

            DDefInt(NULL, traffic_obj_ind_light.c_str(), "-", &g_rbTraffic.trafficObjects[i].ind_light, DVA_IO_Out);
            DDefInt(NULL, traffic_obj_low_beam.c_str(), "-", &g_rbTraffic.trafficObjects[i].low_beam, DVA_IO_Out);
            DDefInt(NULL, traffic_obj_high_beam.c_str(), "-", &g_rbTraffic.trafficObjects[i].high_beam, DVA_IO_Out);

            DDefInt(NULL, traffic_obj_dil_status.c_str(), "on/off", &g_rbTraffic.trafficObjects[i].dil_status, DVA_IO_Out);
        }
    }

    return 0;
}