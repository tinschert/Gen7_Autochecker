/**
 * @file      MathLibrary.h
 * @copyright 2023 Robert Bosch GmbH
 * @author    Robin Walter <robin.walter@de.bosch.com>
 * @date      25.07.2023
 * @brief     Contains definition of variables and functions used in the util_lib
 */

#pragma once
#ifndef MATH_LIBRARY_HPP
#define MATH_LIBRARY_HPP

#include "../../statistical_reflection_model/CRadarReflectionModel.h"
#include "SignalCalc.hpp"  // Contains the signal specific calculations for all sensors

const int max_loc = 1056;

using namespace SignalCalc;

namespace MathLibrary {

/**
 * @brief Contains the distances from the origin of the sensors coordinate system
 * to the different points on the visible sides of the target
*/
struct LPoint
{
  double X;
  double Y;
};

/**
 * @brief Contains the distances from the origin of the coordinate system to the 
 * center points of the sides of the rectangle around the target, as well as the 
 * corresponding corner points and the center of the reference side
*/
struct CoordinateSystem
{
  /// @brief Distance (in m) in x-direction from the ego to the target side
  double dx_rear, dx_front, dx_left, dx_right;
  /// @brief Distance (in m) in x-direction from the ego to the target edge point
  double dx_front_left, dx_front_right, dx_rear_left, dx_rear_right;
  /// @brief Distance (in m) in y-direction from the ego to the target side
  double dy_rear, dy_front, dy_left, dy_right;
  /// @brief Distance (in m) in y-direction from the ego to the target edge point
  double dy_front_left, dy_front_right, dy_rear_left, dy_rear_right;
  /// @brief Distance (in m) from the ego to the middle of the target reference side
  double dx_ref_point, dy_ref_point;
  /// @brief Distance (in m) from to ego to the edge of the target reference side. CARE: This is the view from the ego
  double dx_ref_left, dy_ref_left, dx_ref_right, dy_ref_right;
  /// @brief Heading angle of the target from the coordinate systems point of view
  double yaw_angle;
};

/**
 * @brief Contains the distances from the origin of the sensors coordinate system
 * to the different contour points on the visible sides of the target
*/
struct LocationContour
{
  /// @brief Distance (in m) in x-direction from the sensor to the target point
  double dx_left, dx_mid, dx_right, dx_far, dx_mid_of_tgt;
  /// @brief Distance (in m) in y-direction from the sensor to the target point
  double dy_left, dy_mid, dy_right, dy_far, dy_mid_of_tgt;
  /// @brief Total ammount of valid locations calculated
  int total_loc_count;
  /// @brief Calculated radar cross section
  double apparent_area, rcs;
  /// @brief Flag to indicate if the visible view on the object is L shaped
  int L_shape;
  /// @brief Integer defining which side of the target is the second side of the L Shape (not ref side). CARE: This is the actual side of the target, NOT view from ego
  ReferencePointPosition second_side_indicator;
  /// @brief Points (X/Y coordinates) of each sides starting point
  LPoint side_start_pt, Lshape_start_pt;
  /// @brief Points (X/Y coordinates) of each sides interval length
  LPoint interval_side, interval_Lshape;
};

/**
 * @brief Contains the distances from the origin of the sensors coordinate system
 * to the different points on the visible sides of the target
*/
struct LocationCloud
{
  /// @brief Longitudinal distance from the sensor to the target point (in m)
  double loc_dx;
  /// @brief Lateral distance from the sensor to the target point (in m)
  double loc_dy;
  /// @brief Radial distance from the sensor to the target point (in m)
  double radial_distance;
  /// @brief Relative radial velocity of the target point (in m/s)
  double radial_velocity;
  /// @brief Azimuth angle of the location (in rad)
  double azimuth_angle;
  /// @brief Elevation angle of the location (in rad)
  double elevation_angle;
  /// @brief Calculated radar cross section
  double radar_cross_section;
};


class TargetCalculation {
 public:
  TargetCalculation() {
    reference_point = ReferencePointPosition::UNKNOWN;
    visible_view = VisibleView::UNKNOWN;

    RCA.dx_rear = RCA.dx_front = RCA.dx_left = RCA.dx_right = RCA.dx_front_left =
        RCA.dx_front_right = RCA.dx_rear_left = RCA.dx_rear_right = 0;
    RCA.dy_rear = RCA.dy_front = RCA.dy_left = RCA.dy_right = RCA.dy_front_left =
        RCA.dy_front_right = RCA.dy_rear_left = RCA.dy_rear_right = 0;
    RCA.dx_ref_point = RCA.dy_ref_point = 0;
    RCA.yaw_angle = 0;

    Sensor_CS.dx_rear = Sensor_CS.dx_front = Sensor_CS.dx_left = Sensor_CS.dx_right = Sensor_CS.dx_front_left =
        Sensor_CS.dx_front_right = Sensor_CS.dx_rear_left = Sensor_CS.dx_rear_right = 0;
    Sensor_CS.dy_rear = Sensor_CS.dy_front = Sensor_CS.dy_left = Sensor_CS.dy_right = Sensor_CS.dy_front_left =
        Sensor_CS.dy_front_right = Sensor_CS.dy_rear_left = Sensor_CS.dy_rear_right = 0;
    Sensor_CS.dx_ref_point = Sensor_CS.dy_ref_point = 0;
    Sensor_CS.yaw_angle = 0;

    location_contour.dx_left = location_contour.dx_mid = location_contour.dx_right = location_contour.dx_far = location_contour.dx_mid_of_tgt = 0;
    location_contour.dy_left = location_contour.dy_mid = location_contour.dy_right = location_contour.dy_far = location_contour.dy_mid_of_tgt = 0;
    location_contour.rcs = location_contour.apparent_area =0;
    location_contour.total_loc_count = 0;
    location_contour.L_shape = 0;
    location_contour.second_side_indicator = ReferencePointPosition::UNKNOWN;
    location_contour.side_start_pt = location_contour.Lshape_start_pt = location_contour.interval_side = location_contour.interval_Lshape = {0.0, 0.0};

    for(int i = 0; i < max_loc; i++)
    {
      location_cloud[i].radial_distance = 0.0;
      location_cloud[i].radial_velocity = 0.0;
      location_cloud[i].azimuth_angle = 0.0;
      location_cloud[i].elevation_angle = 0.0;
      location_cloud[i].radar_cross_section = 0.0;
    }
  }
  /// @brief Calculated cloud of locations
  LocationCloud location_cloud[max_loc];

  /**
   * @brief Calculates a rectangle around the target and based on this defines the middle of the side facing the ego (closest to the ego).
   * Also transforms the distances of all edges and sides of the target from the Rear Center Axle coordinate system to the Sensor Position Coordinate System (Sensor_CS)
   * @param height Height of the target
   * @param width Width of the target
   * @param length Length of the target
   * @param rca_dist_x Longitudinal distance from the ego rca ref point to the target ref point
   * @param rca_dist_y Lateral distance from the ego rca ref point to the target ref point
   * @param rca_heading_angle Heading angle of the target in relation to the ego rca
   * @param sensor_dist_x Longitudinal distance from the sensor ref point to the target ref point
   * @param sensor_dist_y Lateral distance from the sensor ref point to the target ref point
   * @param sensor_heading_angle Heading angle of the target in relation to the sensor
  */
  void calculate_ref_point(double, double, double, double, double, double, double, double, double);
  /**
   * @brief Calculates all the data based on the Aligned Camera Coordinate System (ACCS)
   * @param velocity_x Longitudinal relative velocity of the target
   * @param velocity_y Lateral relative velocity of the target
   * @param acceleration_x Longitudinal relative acceleration of the target
   * @param acceleration_y Lateral relative acceleration of the target
   * @param edge_left_old Left edge of the previous cycle
   * @param edge_right_old Right edge of the previous cycle
   * @param edge_mid_old Mid edge of the previous cycle
  */
  void calculate_ACCS(double, double, double, double, double, double, double);
  /**
   * @brief Calculates all the location data
   * @param nr_max_loc Maximum amount of locations that have to be calculated
   * @param location_distribution Flag to choose between different distribution algorithms for extra locations
   * @param radar_mode Movement mode of the sensor (0 = driving, 1 = parking)
   * @param object_type Defines the type of the object for which locations have to be calculated
   * @param mount_pos_z Vertical mounting position of the sensor
   * @param height Height of the target
   * @param vx Longitudinal velocity of the target
   * @param vy Lateral velocity of the target
  */
  void calculate_Locations(int, int, int, int, double, double, double, double);
  /**
   * @brief Calculates all the location data for RoadBarriers such as walls, guard rails etc
   * @param nr_max_loc Maximum amount of locations that have to be calculated
   * @param radar_mode Movement mode of the sensor (0 = driving, 1 = parking)
   * @param mount_pos_z Vertical mounting position of the sensor
   * @param height Height of the target
   * @param vx Longitudinal velocity of the target
   * @param vy Lateral velocity of the target
  */
  void calculate_RoadBarrier_Locations(int, int, double, double, double, double);

  /// @return Gives back the reference point of the target. Unitless.
  ReferencePointPosition get_reference_point();
  /// @return Gives back the visible view on the target. Unitless.
  VisibleView get_visible_view();
  /// @return Gives back the coordinate system with the center in the Rear Center Axle. This is the ground truth coordinate system. In m.
  CoordinateSystem get_RCA();
  /// @return Gives back the coordinate system with the center in the Sensor Position. In m.
  CoordinateSystem get_Sensor_CS();
  /// @return Gives back the Locations in x- and y-distances of the different contour points on the visible sides of the target. In m.
  LocationContour get_location_contour();
  /// @return Gives back the normalized longitudinal velocity of the target (vx/dx). In 1/s.
  double get_norm_vel_x();
  /// @return Gives back the normalized lateral velocity of the target (vy/dx). In 1/s.
  double get_norm_vel_y();
  /// @return Gives back the normalized longitudinal acceleration of the target (ax/dx). In 1/s^2.
  double get_norm_accel_x();
  /// @return Gives back the normalized lateral acceleration of the target (ay/dx). In 1/s^2.
  double get_norm_accel_y();
  /// @return Gives back the normalized lateral velocity of the targets edge (vy/dx_edge). In 1/s.
  double get_norm_vel_y_edge_left(), get_norm_vel_y_edge_right();
  /// @return Gives back the edge as tan(viewing_angle). Unitless.
  double get_edge_left(), get_edge_right(), get_edge_mid(), get_edge_top(), get_edge_bottom();

 protected:
  /// @brief Nearest Side of the target.
  ReferencePointPosition reference_point;
  /// @brief View on the target. Defines if Classic, Side or LShape.
  VisibleView visible_view;
  /// @brief Coordinate system with the center in the Rear Center Axle. This is the ground truth coordinate system.
  CoordinateSystem RCA;
  /// @brief Coordinate system with the center in the Sensor Position defined by the offsets
  CoordinateSystem Sensor_CS;
  /// @brief Calculated contour of the object containing the data of the basic locations
  LocationContour location_contour;
  /// @brief Reflection Model for distributing extra locations on a statistical basis
  CRadarReflectionModel CReflectionModel;
  /// @brief Target declaration. In m.
  double target_height, target_width, target_length;
  /// @brief Normalized longitudinal velocity of the target (vx/dx)
  double norm_vel_x;
  /// @brief Normalized lateral velocity of the target (vx/dx)
  double norm_vel_y;
  /// @brief Normalized longitudinal acceleration of the target (ax/dx)
  double norm_accel_x;
  /// @brief Normalized lateral acceleration of the target (ax/dx)
  double norm_accel_y;
  /// @brief Edges of the target as tan(viewing_angle)
  double edge_left, edge_right, edge_mid, edge_top, edge_bottom;
  /// @brief Edges of the target as tan(viewing_angle)
  double norm_vel_y_edge_left, norm_vel_y_edge_right;

  /// @brief Calculates the LShape of the target for the given reference point.
  void calculate_Location_LShape();
  /**
   * @brief Calculates the height of the location based on the object type.
   * @param radar_mode 
   * @param object_type Defines the type of the object for which locations have to be calculated.
   * @param tgt_height 
   * @param sensor_mount_pos_z 
   * @return Returns the height of the location (in m).
  */
  double calculate_dz(int,int,double,double);
};
}  // namespace MathLibrary

#endif  // MATH_LIBRARY_HPP
