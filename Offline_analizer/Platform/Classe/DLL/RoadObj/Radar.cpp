/**
 * @file        Radar.hpp
 * @copyright   2023 Robert Bosch GmbH
 * @author      Robin Walter <robin.walter@de.bosch.com>
 * @date        12.03.2024
 * @brief       Defines functions for radars
 */

#include "Radar.hpp"

void Radar::set_radar_values(int loc_model,int loc_distribution_model,int loc_sim,int max_nr_of_loc,double loc_separation_angle,int radar_generation)
{
    Radar_Def.i_loc_model = loc_model;
    Radar_Def.i_loc_distribution_model = loc_distribution_model;
    Radar_Def.i_loc_sim = loc_sim;
    Radar_Def.i_max_nr_of_loc = max_nr_of_loc;
    Radar_Def.i_loc_separation_angle = loc_separation_angle;
    Radar_Def.i_radar_generation = radar_generation;
}
void Radar::set_radar_loc_count(int loc_count)
{
    Radar_Def.o_valid_loc_count = loc_count;
}
void Radar::set_radar_loc_values(int loc_id, double radial_distance, double radial_velocity, double elevation, double azimuth, double radar_cross_section, double rssi, double snr)
{
      Loc[loc_id].o_radial_distance = radial_distance;
      Loc[loc_id].o_radial_velocity = radial_velocity;
      Loc[loc_id].o_elevation = elevation;
      Loc[loc_id].o_azimuth = azimuth;
      Loc[loc_id].o_radar_cross_section = radar_cross_section;
      Loc[loc_id].o_rssi = rssi;
      Loc[loc_id].o_snr = snr;
}

/**
 * Definition Getters
 */
int Radar::get_radar_valid_loc_count()
{
    return Radar_Def.o_valid_loc_count;
}
int Radar::get_radar_loc_sim()
{
    return Radar_Def.i_loc_sim;
}
int Radar::get_radar_loc_model()
{
    return Radar_Def.i_loc_model;
}
int Radar::get_radar_loc_distribution_model()
{
    return Radar_Def.i_loc_distribution_model;
}
int Radar::get_radar_max_nr_of_loc()
{
    return Radar_Def.i_max_nr_of_loc;
}
double Radar::get_radar_loc_separation_angle()
{
    return Radar_Def.i_loc_separation_angle;
}
int Radar::get_radar_generation()
{
    return Radar_Def.i_radar_generation;
}