/**
 * @file        RoadObj.cpp
 * @copyright   2023 Robert Bosch GmbH
 * @author      Robin Walter <robin.walter@de.bosch.com>
 * @date        12.03.2024
 * @brief       Calculates object and location data for multiple sensors
 */

#include "Sensor.hpp"
#include <cmath>

void Sensor::calculate_validity_flag(int simulator, int obj_id, double sensor_dx, double sensor_dy)
{
    switch (simulator)
    {
    case 1: // Classe mode
        if(sensor_dx > 0.0 
            && atan2(sensor_dy, sensor_dx) < Sensor_Def.i_fov 
            && atan2(sensor_dy, sensor_dx) > -Sensor_Def.i_fov
            && Input_Obj[obj_id].i_obj_sim_on == 1
            && Sensor_Def.i_sensor_sim_on == 1)
        {   // +- FOV && Sensor is being used on this obj -> valid target
            Input_Obj[obj_id].o_validity_flag = 1;
            Input_Obj[obj_id].o_empty_flag = 0;
        }
        else if(Sensor_Def.i_validity_sending_flag == 0)
        {   // only valid target sending off -> dummy target
            Input_Obj[obj_id].o_validity_flag = 1;
            Input_Obj[obj_id].o_empty_flag = 1;
        }
        else
        {   // only valid target sending on -> empty target
            Input_Obj[obj_id].o_validity_flag = 0;
            Input_Obj[obj_id].o_empty_flag = 1;
        }
        break;

    case 2: // CarMaker mode
        if(obj_id < Sensor_Def.o_valid_obj_count
            && Sensor_Def.i_sensor_sim_on == 1)
        {   // valid target
            Input_Obj[obj_id].o_validity_flag = 1;
            Input_Obj[obj_id].o_empty_flag = 0;
        }
        else if(Sensor_Def.i_validity_sending_flag == 0)
        {   // only valid target sending off -> dummy target
            Input_Obj[obj_id].o_validity_flag = 1;
            Input_Obj[obj_id].o_empty_flag = 1;
        }
        else
        {   // only valid target sending on -> empty target
            Input_Obj[obj_id].o_validity_flag = 0;
            Input_Obj[obj_id].o_empty_flag = 1;
        }
        break;
    
    default:
        break;
    }
}

/**
 *  Setter
 */
void Sensor::set_sensor_values(double mount_dx,double mount_dy,double mount_dz,double mount_yaw,double fov_angle,int validity_sending_active,int sensor_sim_active,int obj_count)
{
    Sensor_Def.i_mount_pos_x = mount_dx;
    Sensor_Def.i_mount_pos_y = mount_dy;
    Sensor_Def.i_mount_pos_z = mount_dz;
    Sensor_Def.i_mount_pos_yaw = mount_yaw;
    Sensor_Def.i_fov = fov_angle;
    Sensor_Def.i_validity_sending_flag = validity_sending_active;
    Sensor_Def.i_sensor_sim_on = sensor_sim_active;
    Sensor_Def.o_valid_obj_count = obj_count;
}
void Sensor::set_object_values(int obj_id,int sim_on,int sensor_mode,double dx,double dy,double vx,double vy,double ax,double ay,double yaw_angle,double width,double length, double height, int type, double rcs, double snr, double signal_strength)
{
    Input_Obj[obj_id].i_obj_sim_on = sim_on;
    Input_Obj[obj_id].i_obj_sensor_mode = sensor_mode;
    Input_Obj[obj_id].i_distance_x = dx;
    Input_Obj[obj_id].i_distance_y = dy;
    Input_Obj[obj_id].i_velocity_x = vx;
    Input_Obj[obj_id].i_velocity_y = vy;
    Input_Obj[obj_id].i_acceleration_x = ax;
    Input_Obj[obj_id].i_acceleration_y = ay;
    Input_Obj[obj_id].i_yaw_angle = yaw_angle;
    Input_Obj[obj_id].i_width = width;
    Input_Obj[obj_id].i_length = length;
    Input_Obj[obj_id].i_height = height;
    Input_Obj[obj_id].i_type = type;
    Input_Obj[obj_id].i_radar_cross_section = rcs;
    Input_Obj[obj_id].i_signal_noise_ratio = snr;
    Input_Obj[obj_id].i_signal_strength = signal_strength;
}
void Sensor::set_sensor_valid_obj_count(int obj_count)
{
    Sensor_Def.o_valid_obj_count = obj_count;
}

/**
 *  Getter
 */
double Sensor::get_sensor_mount_pos_x()
{
    return Sensor_Def.i_mount_pos_x;
}
double Sensor::get_sensor_mount_pos_y()
{
    return Sensor_Def.i_mount_pos_y;
}
double Sensor::get_sensor_mount_pos_z()
{
    return Sensor_Def.i_mount_pos_z;
}
double Sensor::get_sensor_mount_pos_yaw()
{
    return Sensor_Def.i_mount_pos_yaw;
}
double Sensor::get_sensor_fov()
{
    return Sensor_Def.i_fov;
}
int Sensor::get_sensor_validity_sending_flag()
{
    return Sensor_Def.i_validity_sending_flag;
}
int Sensor::get_sensor_sim_on()
{
    return Sensor_Def.i_sensor_sim_on;
}
int Sensor::get_sensor_valid_obj_count()
{
    return Sensor_Def.o_valid_obj_count;
}

int Sensor::get_in_obj_sim_on(int obj_id)
{
    return Input_Obj[obj_id].i_obj_sim_on;
}
int Sensor::get_in_obj_sensor_mode(int obj_id)
{
    return Input_Obj[obj_id].i_obj_sensor_mode;
}
double Sensor::get_in_obj_distance_x(int obj_id)
{
    return Input_Obj[obj_id].i_distance_x;
}
double Sensor::get_in_obj_distance_y(int obj_id)
{
    return Input_Obj[obj_id].i_distance_y;
}
double Sensor::get_in_obj_velocity_x(int obj_id)
{
    return Input_Obj[obj_id].i_velocity_x;
}
double Sensor::get_in_obj_velocity_y(int obj_id)
{
    return Input_Obj[obj_id].i_velocity_y;
}
double Sensor::get_in_obj_acceleration_x(int obj_id)
{
    return Input_Obj[obj_id].i_acceleration_x;
}
double Sensor::get_in_obj_acceleration_y(int obj_id)
{
    return Input_Obj[obj_id].i_acceleration_y;
}
double Sensor::get_in_obj_yaw_angle(int obj_id)
{
    return Input_Obj[obj_id].i_yaw_angle;
}
double Sensor::get_in_obj_width(int obj_id)
{
    return Input_Obj[obj_id].i_width;
} 
double Sensor::get_in_obj_length(int obj_id)
{
    return Input_Obj[obj_id].i_length;
} 
double Sensor::get_in_obj_height(int obj_id)
{
    return Input_Obj[obj_id].i_height;
}
int Sensor::get_in_obj_type(int obj_id)
{
    return Input_Obj[obj_id].i_type;
}
double Sensor::get_in_obj_rcs(int obj_id)
{
    return Input_Obj[obj_id].i_radar_cross_section;
}
double Sensor::get_in_obj_snr(int obj_id)
{
    return Input_Obj[obj_id].i_signal_noise_ratio;
}
double Sensor::get_in_obj_signal_strength(int obj_id)
{
    return Input_Obj[obj_id].i_signal_strength;
}
double Sensor::get_in_obj_fov_distance_x(int obj_id)
{
    return Input_Obj[obj_id].fov_distance_x;
}
double Sensor::get_in_obj_fov_distance_y(int obj_id)
{
    return Input_Obj[obj_id].fov_distance_y;
}
int Sensor::get_in_obj_validity_flag(int obj_id)
{
    return Input_Obj[obj_id].o_validity_flag;
}
int Sensor::get_in_obj_empty_flag(int obj_id)
{
    return Input_Obj[obj_id].o_empty_flag;
}

Sensor_Definitions Sensor::get_sensor_def()
{
    return Sensor_Def;
}
Input_Object Sensor::get_input_obj(int obj_id)
{
    return Input_Obj[obj_id];
}