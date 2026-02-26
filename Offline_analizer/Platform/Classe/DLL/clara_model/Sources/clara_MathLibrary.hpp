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

namespace MathLibrary {
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
};


class TargetCalculation {
 public:
  TargetCalculation() {
    CS.dx_rear = CS.dx_front = CS.dx_left = CS.dx_right = CS.dx_front_left =
        CS.dx_front_right = CS.dx_rear_left = CS.dx_rear_right = 0;
    CS.dy_rear = CS.dy_front = CS.dy_left = CS.dy_right = CS.dy_front_left =
        CS.dy_front_right = CS.dy_rear_left = CS.dy_rear_right = 0;
    CS.dx_ref_point = CS.dy_ref_point = 0;
  }

  /**
   * @brief Calculates a rectangle around the target and based on this defines the middle of the side facing the ego (closest to the ego).
   * Also transforms the distances of all edges and sides of the target from the Rear Center Axle coordinate system to the Sensor Position Coordinate System (Sensor_CS)
   * @param height Height of the target
   * @param width Width of the target
   * @param length Length of the target
   * @param heading_angle Heading angle of the target in relation to the ego
   * @param dx Longitudinal distance from the ego ref point to the target ref point
   * @param dy Lateral distance from the ego ref point to the target ref point
   * @param vx Longitudinal relative velocity of the target
   * @param vy Lateral relative velocity of the target
   * @param mount_pos_dx Mounting position in longitudinal direction of the sensor in reference to the ego rear center axle
   * @param mount_pos_dy Mounting position in lateral direction of the sensor in reference to the ego rear center axle
   * @param mount_pos_yaw Mounting position in lateral direction of the sensor in reference to the ego rear center axle
   * @param ego_current_ref_point Defines the reference point (center of coordinates) on the ego vehicle in which the data is given
   * @param tgt_current_ref_point Defines the reference point on the target in which the data is given
  */
  void calculate_contour(double, double, double, double, double, double);

  /**
   * @brief Converts our Classe type enum to the expected Clara type enum
   * @param type Classe type
  */
  int map_type(int);

  /// @return Gives back the coordinate system with the center in the Rear Center Axle. This is the ground truth coordinate system. In m.
  CoordinateSystem get_CS();

 protected:
  /// @brief Coordinate system with the center in the Rear Center Axle. This is the ground truth coordinate system.
  CoordinateSystem CS;
};
}  // namespace MathLibrary

#endif  // MATH_LIBRARY_HPP
