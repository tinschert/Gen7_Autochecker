/**
 * @file        RoadObj.cpp
 * @copyright   2023 Robert Bosch GmbH
 * @author      Robin Walter <robin.walter@de.bosch.com>
 * @date        12.03.2024
 * @brief       Defines structures and classes for video cameras
 */

#ifndef VIDEO_HPP
#define VIDEO_HPP

#include "Sensor.hpp"

/**
 * @brief Contains the data needed to send a video object onto the bus. This data is in reference to both sensor and RCA, defined by each signal.
*/
struct Video_Object
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
  /// @brief Bounding box edge in sensor coordinate system
  double o_phi_top, o_phi_bottom, o_phi_left, o_phi_right, o_phi_mid;
  /// @brief Object normalised velocity (in 1/s)
  double o_norm_velocity_x, o_norm_velocity_y;
  /// @brief Object normalised acceleration (in 1/s2)
  double o_norm_acceleration_x;
  /// @brief Enumeration indicating the visible view on the target
  int o_visible_view;
  /// @brief Enumeration indicating the classified view on the target
  int o_classified_view;
  /// @brief Object movement probabilities (in %)
  int o_movement_prob_long, o_movement_prob_lat, o_movement_observed;
  /// @brief Status of objects lights
  int o_brake_light, o_turn_light;
  /// @brief Oncoming Flag (1 if the target is oncoming)
  int o_oncoming;
  /// @brief Acceleration type of the target
  int o_target_acc_type;
  /// @brief Reliability of the values
  int o_reliability;
  /// @brief Measurement source of the values
  int o_meas_source;
  /// @brief Video specfic object type
  int o_type;
  /// @brief Head orientation of the object in case of a pedestrian
  int o_head_orientation;

};

class Video : public Sensor{
 public:
  Video() {
    for(int i = 0; i < maximum_object_quantity; i++)
    {
      Obj[i].o_distance_x = 0.0;
      Obj[i].o_distance_y = 0.0;
      Obj[i].o_velocity_x = 0.0;
      Obj[i].o_velocity_y = 0.0;
      Obj[i].o_acceleration_x = 0.0;
      Obj[i].o_acceleration_y = 0.0;
      Obj[i].o_yaw_angle = 0.0;
      Obj[i].o_visible_view = 0;
      Obj[i].o_classified_view = 0;
      Obj[i].o_phi_top = 0.0;
      Obj[i].o_phi_bottom = 0.0;
      Obj[i].o_phi_left = 0.0;
      Obj[i].o_phi_right = 0.0;
      Obj[i].o_phi_mid = 0.0;
      Obj[i].o_norm_velocity_x = 0.0; 
      Obj[i].o_norm_velocity_y = 0.0;
      Obj[i].o_norm_acceleration_x = 0.0;
      Obj[i].o_movement_prob_long = 0; 
      Obj[i].o_movement_prob_lat = 0; 
      Obj[i].o_movement_observed = 0;
      Obj[i].o_brake_light = 0; 
      Obj[i].o_turn_light = 0;
      Obj[i].o_oncoming = 0;
      Obj[i].o_target_acc_type = 0;
      Obj[i].o_reliability = 0;
      Obj[i].o_meas_source = 0;
      Obj[i].o_type = 0;
      Obj[i].o_head_orientation = 0;
    }
  }
  
  /// @brief Array of object structure containing the data needed to send video objects onto the bus
  Video_Object Obj[maximum_object_quantity];

 protected:
};

#endif // VIDEO_HPP