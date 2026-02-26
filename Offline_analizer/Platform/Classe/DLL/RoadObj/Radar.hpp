/**
 * @file        Radar.hpp
 * @copyright   2023 Robert Bosch GmbH
 * @author      Robin Walter <robin.walter@de.bosch.com>
 * @date        12.03.2024
 * @brief       Defines structures and classes for radars
 */

#ifndef RADAR_HPP
#define RADAR_HPP

#include "Sensor.hpp"

/**
 * @brief Contains the data needed to send a radar location onto the bus. This data is in reference to the sensor position.
*/
struct Radar_Definitions
{
  /// @brief hil_ctrl::radar_xx_loc_sim - Flag to activate calculations of location data for this sensor
  int i_loc_sim;
  /// @brief target_radar_xx_sim::locdata.location_model - Flag to choose which sensor model to use -> 0 = 1objXloc, 1 = Star, 2 = Clara
  int i_loc_model;
  /// @brief hil_ctrl::location_distribution_model - Flag to choose the distribution model to use -> 0 = Even, 1 = CMP, 2 = Statistical
  int i_loc_distribution_model;
  /// @brief hil_ctrl::clara_model_max_loc_nr_per_obj - Maximum number of locations to be generated per object
  int i_max_nr_of_loc;
  /// @brief hil_ctrl::clara_model_loc_separation_angle - Separation angle between generated locations
  double i_loc_separation_angle;
  /// @brief Indicates the generation of the radar which influences the data being calculated
  int i_radar_generation;
  /// @brief Number of valid locations
  int o_valid_loc_count;
};

/**
 * @brief Contains the data needed to send a radar location onto the bus. This data is in reference to the sensor position.
*/
struct Radar_Location
{
  /// @brief Location radial distance in m. Represented in conical coordinate system. Same as ISO 23150:2021(E): Position radial distance (A.4.16)
  double o_radial_distance;
  /// @brief Location radial relative velocity in m/s. ISO 23150:2021(E): Relative velocity {radial distance} (A.4.18)
  double o_radial_velocity;
  /// @brief Location elevation angle. Represented in conical coordinate system. Same as ISO 23150:2021(E): Position elevation (A.4.16)
  double o_elevation;
  /// @brief Location azimuth angle. Represented in conical coordinate system. Deviation from ISO 23150:2021(E): Position azimuth (A.4.16)
  double o_azimuth;
  /// @brief Radar Cross Section (RCS) estimation ISO 23150:2021(E): Radar cross section (A.4.5)
  double o_radar_cross_section;
  /// @brief Received Signal Strength Indication (RSSI).
  double o_rssi;
  /// @brief Signal to Noise Ratio (SNR). 
  double o_snr;
};

/**
 * @brief Contains the data needed to send a radar object onto the bus. This data is in reference to the RCA position.
*/
struct Radar_Object
{
  /// @brief Object distance in longitudinal direction (in m)
  double o_distance_x;
  /// @brief Object distance in lateral direction (in m)
  double o_distance_y;
  /// @brief Object velocity in longitudinal direction (in m/s)
  double o_velocity_x;
  /// @brief Object velocity in lateral direction (in m/s)
  double o_velocity_y;
  /// @brief Object acceleration in longitudinal direction (in m/s2)
  double o_acceleration_x;
  /// @brief Object acceleration in lateral direction (in m/s2)
  double o_acceleration_y;
  /// @brief Object heading angle (in rad)
  double o_yaw_angle;
  /// @brief Enumeration to indicate which side of the target is the calculated reference point
  int o_reference_point;
  /// @brief Probability that the target is moving according to the radar gen 5
  int o_ra5_prob_moving;
  /// @brief Probability that the target is stationary according to the radar gen 5
  int o_ra5_prob_stationary;
  /// @brief Probability that the target is no obstacle according to the radar gen 5
  int o_ra5_prob_non_obst;
  /// @brief Probability that the target is a truck according to the radar gen 5
  int o_ra5_prob_truck;
  /// @brief Probability that the target is a car according to the radar gen 5
  int o_ra5_prob_car;
  /// @brief Probability that the target is a 2 wheeler according to the radar gen 5
  int o_ra5_prob_2wheeler;
  /// @brief Probability that the target is a pedestrian according to the radar gen 5
  int o_ra5_prob_pedestrian;
  /// @brief Radar Cross Section (RCS) estimation ISO 23150:2021(E): Radar cross section (A.4.5) according to the radar gen 6
  double o_ra6_radar_cross_section;
  /// @brief Object type definition according to the radar gen 6
  int o_ra6_obj_type;
  /// @brief Moving status definition according to the radar gen 6
  int o_ra6_moving_status;
};

class Radar : public Sensor{
 public:
  Radar() {
    Radar_Def.i_loc_model = 0;
    Radar_Def.i_loc_sim = 0;
    Radar_Def.i_max_nr_of_loc = 0;
    Radar_Def.i_loc_separation_angle = 0.0;
    Radar_Def.i_radar_generation = 0;
    Radar_Def.o_valid_loc_count = 0;

    for(int i = 0; i < maximum_location_quantity; i++)
    {
      Loc[i].o_radial_distance = 0.0;
      Loc[i].o_radial_velocity = 0.0;
      Loc[i].o_elevation = 0.0;
      Loc[i].o_azimuth = 0.0;
      Loc[i].o_radar_cross_section = 0.0;
      Loc[i].o_snr = 0.0;
      Loc[i].o_rssi = 0.0;
    }

    for(int i = 0; i < maximum_object_quantity; i++)
    {
      Obj[i].o_distance_x = 0.0;
      Obj[i].o_distance_y = 0.0;
      Obj[i].o_velocity_x = 0.0;
      Obj[i].o_velocity_y = 0.0;
      Obj[i].o_acceleration_x = 0.0;
      Obj[i].o_acceleration_y = 0.0;
      Obj[i].o_yaw_angle = 0.0;
      Obj[i].o_reference_point = 0;
      Obj[i].o_ra5_prob_moving = 0;
      Obj[i].o_ra5_prob_stationary = 0;
      Obj[i].o_ra5_prob_non_obst = 0;
      Obj[i].o_ra5_prob_truck = 0;
      Obj[i].o_ra5_prob_car = 0;
      Obj[i].o_ra5_prob_2wheeler = 0;
      Obj[i].o_ra5_prob_pedestrian = 0;
      Obj[i].o_ra6_radar_cross_section = 0.0;
      Obj[i].o_ra6_obj_type = 0;
      Obj[i].o_ra6_moving_status = 0;
    }
  }

  /// @brief Array of object structure containing the data needed to send radar locations onto the bus
  Radar_Location Loc[maximum_location_quantity];
  /// @brief Array of object structure containing the data needed to send radar objects onto the bus
  Radar_Object Obj[maximum_object_quantity];

  /**
   * @brief Sets the superior sensor values
   * @param loc_model Flag to choose which sensor model to use -> 0 = 1objXloc, 1 = Star, 2 = Clara
   * @param loc_distribution_model Flag to choose the distribution model to use -> 0 = Even, 1 = CMP, 2 = Statistical
   * @param loc_sim Flag to activate calculations of location data for this sensor
   * @param max_nr_of_loc Maximum number of locations to be generated per object
   * @param loc_separation_angle Separation angle between generated locations
   * @param radar_generation Indicates the generation of the radar which influences the data being calculated
  */
  void set_radar_values(int,int,int,int,double,int);
  /// @brief Sets the number of calculated valid locations
  void set_radar_loc_count(int);
  /**
   * @brief Sets the values of a location with the given ID
   * @param loc_id ID of the location
   * @param radial_distance Location radial distance in m. Represented in conical coordinate system. Same as ISO 23150:2021(E): Position radial distance (A.4.16)
   * @param radial_velocity Location radial relative velocity in m/s. ISO 23150:2021(E): Relative velocity {radial distance} (A.4.18)
   * @param elevation Location elevation angle. Represented in conical coordinate system. Same as ISO 23150:2021(E): Position elevation (A.4.16)
   * @param azimuth Location azimuth angle. Represented in conical coordinate system. Deviation from ISO 23150:2021(E): Position azimuth (A.4.16)
   * @param radar_cross_section Radar Cross Section (RCS) of the location estimation ISO 23150:2021(E): Radar cross section (A.4.5)
   * @param rssi Received Signal Strength Indication (RSSI). This signal is not exactly ISO 23150:2021(E): Signal to noise ratio - detection level (A.4.7), but SNR can be calculated from this signal.
   * @param snr Signal to Noise Ratio
  */
  void set_radar_loc_values(int,double,double,double,double,double,double,double);

  /// @return Returns the number of calculated valid locations
  int get_radar_valid_loc_count();
  /// @return Returns the flag to activate calculations of location data for this sensor
  int get_radar_loc_sim();
  /// @return Returns the flag to choose which radar model to use -> 0 = 1objXloc, 1 = Star, 2 = Clara
  int get_radar_loc_model();
  /// @return Returns flag to choose the distribution model -> 0 = Even, 1 = CMP, 2 = Statistical
  int get_radar_loc_distribution_model();
  /// @return Returns the maximum number of locations generated per object
  int get_radar_max_nr_of_loc();
  /// @return Returns the separation angle between generated locations
  double get_radar_loc_separation_angle();
  /// @return Returns the generation of the radar
  int get_radar_generation();

 protected:
  /// @brief Array of object structure containing the data needed to send radar locations onto the bus
  Radar_Definitions Radar_Def;
};

#endif // RADAR_HPP