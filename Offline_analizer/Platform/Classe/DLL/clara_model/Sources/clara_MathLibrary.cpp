/**
 * @file        MathLibrary.cpp
 * @copyright   2023 Robert Bosch GmbH
 * @author      Robin Walter <robin.walter@de.bosch.com>
 * @date        25.07.2023
 * @brief       Contains calculations for the distance of the target
 */

#include "clara_MathLibrary.hpp"
#include <cmath>

using namespace std;
using namespace MathLibrary;

/**
 * Calculation functions. Inputs are expected to be:
 * Ego - Rear Center Axle
 * Target - Middle of the geometry
*/
void TargetCalculation::calculate_contour(double height, double width, double length, double dist_x, double dist_y, double heading_angle)
{
    /**
     * Calculate a rectangle around the target and therefor the distances of all 4 edges + middle of sides
     * Ego: Center of Gravity
    */
    CS.dx_front = dist_x + ((length/2) * cos(heading_angle));
    CS.dx_rear = dist_x + ((length/2) * cos(heading_angle - M_PI));
    CS.dx_left = dist_x + ((width/2) * cos(heading_angle + (M_PI/2)));
    CS.dx_right = dist_x + ((width/2) * cos(heading_angle - (M_PI/2)));

    CS.dy_front = dist_y + ((length/2) * sin(heading_angle));
    CS.dy_rear = dist_y + ((length/2) * sin(heading_angle - M_PI));
    CS.dy_left = dist_y + ((width/2) * sin(heading_angle + (M_PI/2)));
    CS.dy_right = dist_y + ((width/2) * sin(heading_angle - (M_PI/2)));

    // Calculation of the corner points
    CS.dx_front_left = CS.dx_rear + (sqrt(pow(length,2) + pow(width/2,2)) * cos(heading_angle + atan((width/2) / length)));
    CS.dx_front_right = CS.dx_rear + (sqrt(pow(length,2) + pow(width/2,2)) * cos(heading_angle - atan((width/2) / length)));
    CS.dx_rear_left = CS.dx_rear + ((width/2) * cos(heading_angle + 1.5708));
    CS.dx_rear_right = CS.dx_rear + ((width/2) * cos(heading_angle - 1.5708));

    CS.dy_front_left = CS.dy_rear + (sqrt(pow(length,2) + pow(width/2,2)) * sin(heading_angle + atan((width/2) / length)));
    CS.dy_front_right = CS.dy_rear + (sqrt(pow(length,2) + pow(width/2,2)) * sin(heading_angle - atan((width/2) / length)));
    CS.dy_rear_left = CS.dy_rear + ((width/2) * sin(heading_angle + 1.5708));
    CS.dy_rear_right = CS.dy_rear + ((width/2) * sin(heading_angle - 1.5708));
}

int TargetCalculation::map_type(int type) {
  // enum EobstacleTyp {INVISIBLE, POINT, CAR, MOTORBIKE, TRUCK, BUS, BICYCLE, PEDESTRIAN, DELINEATOR, UNKNOWN_CLASS};
  switch (type) {
    case 3:
      return 3; // Bike
    case 4:
      return 7; // Pedestrian
    case 5:
      return 4; // Truck
    case 6:
      return 2; // Car
    default:
      return 9; // Unknown
  }
}
    
/**
 * Getter
*/
CoordinateSystem TargetCalculation::get_CS(){
        return CS;
}
