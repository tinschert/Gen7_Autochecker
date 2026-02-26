/**
 * @file        MathLibrary.cpp
 * @copyright   2023 Robert Bosch GmbH
 * @author      Robin Walter <robin.walter@de.bosch.com>
 * @date        25.07.2023
 * @brief       Contains calculations for the distance of the target
 */

#include "MathLibrary.hpp"
#include <iostream>
#include <cmath>
#include <limits>
#include <random>

using namespace std;
using namespace MathLibrary;

/**
 * Calculation functions. Inputs are expected to be:
 * Ego - Rear Center Axle and Sensor Position
 * Target - Middle of the geometry
 * Calculated positions on the target: Front (f), Rear (r), Left (l), Right (r), Front Left (fl), Front Right (fr), Rear Left (rl), Rear Right (rr)
 *          3D view                       Top view
 *        |---------|                  rl    r    rr
 *       /         /|                   x----x----x
 *      /         / x height            |         | length
 *     /         /  |                   |         |
 *    |---------| x |                 l x         x r
 *    |         |  /                    |         |
 *    x    x    x / length              |         |
 *    |         |/                      x----x----x
 *    |---------|                      fr    f    fl
 *       width                             width
*/
void TargetCalculation::calculate_ref_point(double height, double width, double length, double rca_dist_x, double rca_dist_y, double rca_heading_angle,
                                        double sensor_dist_x, double sensor_dist_y, double sensor_heading_angle)
{
    /**
     * Read the dimensions of the target
     * The length must not be 0, otherwise it would be divided by 0 in further calculations
    */
    target_height = height;
    target_width = width;
    if(length == 0.0){
        target_length = 0.1;
    }else{
        target_length = length;
    }
    
    RCA.yaw_angle = rca_heading_angle;
    Sensor_CS.yaw_angle = sensor_heading_angle;

    // Precompute common values
    double half_length = target_length / 2;
    double half_width = target_width / 2;
    double length_width_sqrt = sqrt(pow(target_length, 2) + pow(half_width, 2));

    /**
     * Calculate a rectangle around the target and therefor the distances of all 4 edges + middle of sides
     * Ego: Rear Center Axle
    */
    // Calculation of the centers of the individual sides -> Basically forming a rectangle around the target
    RCA.dx_front = rca_dist_x + (half_length * cos(rca_heading_angle));
    RCA.dx_rear = rca_dist_x + (half_length * cos(rca_heading_angle - M_PI));
    RCA.dx_left = rca_dist_x + (half_width * cos(rca_heading_angle + M_PI_2));
    RCA.dx_right = rca_dist_x + (half_width * cos(rca_heading_angle - M_PI_2));

    RCA.dy_front = rca_dist_y + (half_length * sin(rca_heading_angle));
    RCA.dy_rear = rca_dist_y + (half_length * sin(rca_heading_angle - M_PI));
    RCA.dy_left = rca_dist_y + (half_width * sin(rca_heading_angle + M_PI_2));
    RCA.dy_right = rca_dist_y + (half_width * sin(rca_heading_angle - M_PI_2));

    // Calculation of the corner points
    //RCA.dx_front_left = RCA.dx_rear + (length_width_sqrt * cos(rca_heading_angle + atan(half_width / length)));
    //RCA.dx_front_right = RCA.dx_rear + (length_width_sqrt * cos(rca_heading_angle - atan(half_width / length)));
    //RCA.dx_rear_left = RCA.dx_rear + (half_width * cos(rca_heading_angle + M_PI_2));
    //RCA.dx_rear_right = RCA.dx_rear + (half_width * cos(rca_heading_angle - M_PI_2));

    //RCA.dy_front_left = RCA.dy_rear + (length_width_sqrt * sin(rca_heading_angle + atan(half_width / length)));
    //RCA.dy_front_right = RCA.dy_rear + (length_width_sqrt * sin(rca_heading_angle - atan(half_width / length)));
    //RCA.dy_rear_left = RCA.dy_rear + (half_width * sin(rca_heading_angle + M_PI_2));
    //RCA.dy_rear_right = RCA.dy_rear + (half_width * sin(rca_heading_angle - M_PI_2));

    /**
     * Calculate a rectangle around the target and therefor the distances of all 4 edges + middle of sides
     * Ego: Sensor Position
    */
    Sensor_CS.dx_front = sensor_dist_x + (half_length * cos(sensor_heading_angle));
    Sensor_CS.dx_rear = sensor_dist_x + (half_length * cos(sensor_heading_angle - M_PI));
    Sensor_CS.dx_left = sensor_dist_x + (half_width * cos(sensor_heading_angle + M_PI_2));
    Sensor_CS.dx_right = sensor_dist_x + (half_width * cos(sensor_heading_angle - M_PI_2));

    Sensor_CS.dy_front = sensor_dist_y + (half_length * sin(sensor_heading_angle));
    Sensor_CS.dy_rear = sensor_dist_y + (half_length * sin(sensor_heading_angle - M_PI));
    Sensor_CS.dy_left = sensor_dist_y + (half_width * sin(sensor_heading_angle + M_PI_2));
    Sensor_CS.dy_right = sensor_dist_y + (half_width * sin(sensor_heading_angle - M_PI_2));

    // Calculation of the corner points
    Sensor_CS.dx_front_left = Sensor_CS.dx_rear + (length_width_sqrt * cos(sensor_heading_angle + atan(half_width / target_length)));
    Sensor_CS.dx_front_right = Sensor_CS.dx_rear + (length_width_sqrt * cos(sensor_heading_angle - atan(half_width / target_length)));
    Sensor_CS.dx_rear_left = Sensor_CS.dx_rear + (half_width * cos(sensor_heading_angle + M_PI_2));
    Sensor_CS.dx_rear_right = Sensor_CS.dx_rear + (half_width * cos(sensor_heading_angle - M_PI_2));

    Sensor_CS.dy_front_left = Sensor_CS.dy_rear + (length_width_sqrt * sin(sensor_heading_angle + atan(half_width / target_length)));
    Sensor_CS.dy_front_right = Sensor_CS.dy_rear + (length_width_sqrt * sin(sensor_heading_angle - atan(half_width / target_length)));
    Sensor_CS.dy_rear_left = Sensor_CS.dy_rear + (half_width * sin(sensor_heading_angle + M_PI_2));
    Sensor_CS.dy_rear_right = Sensor_CS.dy_rear + (half_width * sin(sensor_heading_angle - M_PI_2));

    /**
     * Save mit of the target into Location structure
     */
    location_contour.dx_mid_of_tgt = sensor_dist_x;
    location_contour.dy_mid_of_tgt = sensor_dist_y;

    /**
     * Calculate Reference Point
     * Step 1: Find the nearest side depending on the Sensor Coordinate System since this is what the real sensor would see
     * BUT the values of the distances are based on RCA!
     * Step 2: Define Reference Point
     * Step 2.1: In case front or rear are defined as reference point we need to calculate the angle 
     * in which the front is facing the sensor, since those are not as long as the sides and by this the sides 
     * could be the actual reference points even if the smallest Element is front or rear.
     * If the angle is between 90° +-55° take the front, if the angle is outside of this range take one of the sides.
     * In the example pictured below the smallestIndex would maybe indicate the front as reference side, but by checking the 
     * angle it gets changed to the left side of the target. This works analogue in case reference side is the rear of the target.
     * 
     *                 |--------|
     *    vector_front |   <-   |
     *                /|--------|
     *               /
     *              /
     *             / Sensor_CS.dx_front + Sensor_CS.dy_front
     *            /
     *           v
     *         |---|
     *         |   |
     *         |   |
     *         |---|
     *          EGO
     * 
     * vector_front = Front of the target calculated as a vector
     * Sensor_CS.dx_front / Sensor_CS.dy_front = Thought line from the sensor position to the center of the front
     */
    double distance[4];
    distance[0] = sqrt(pow(Sensor_CS.dx_front,2) + pow(Sensor_CS.dy_front,2));
    distance[1] = sqrt(pow(Sensor_CS.dx_rear,2) + pow(Sensor_CS.dy_rear,2));
    distance[2] = sqrt(pow(Sensor_CS.dx_left,2) + pow(Sensor_CS.dy_left,2));
    distance[3] = sqrt(pow(Sensor_CS.dx_right,2) + pow(Sensor_CS.dy_right,2));

    //Find smallest element
    double smallestElement = std::numeric_limits<double>::max();
    int indexSmallestElement;
    for(int i = 0; i < 4; i++)
    {
        if(distance[i] < smallestElement || i == 0){
            smallestElement = distance[i];
            indexSmallestElement = i;
        }
    }
    indexSmallestElement = indexSmallestElement + 1;

    //Define Reference Point
    if(indexSmallestElement == 1)
    {   // Nearest side is front
        // Calculate the vector of the front of the target
        double vector_front_x = Sensor_CS.dx_front_left - Sensor_CS.dx_front_right;
        double vector_front_y = Sensor_CS.dy_front_left - Sensor_CS.dy_front_right;

        // Calculate the dot product of the line from sensor to front and the line of the front of the target. If the dot product is 0, then the two vectors are perpendicular to each other
        // dot_prod = x1 * x2 + y1 * y2
        double dot_prod = vector_front_x * Sensor_CS.dx_front + vector_front_y * Sensor_CS.dy_front;

        // Calculate the angle between the two vectors and transform into degree
        // arccos ( dot_prod / multiplied amounts of the two vectors )
        double angle_deg = acos(dot_prod / (sqrt(pow(vector_front_x,2) + pow(vector_front_y,2)) * sqrt(pow(Sensor_CS.dx_front,2) + pow(Sensor_CS.dy_front,2)))) * 180 / M_PI;

        if(angle_deg > 145.0)
        {
            reference_point = ReferencePointPosition::LEFT;
        }
        else if(angle_deg < 35.0)
        {
            reference_point = ReferencePointPosition::RIGHT;
        }
        else
        {
            reference_point = ReferencePointPosition::FRONT;
        }
    }
    else if(indexSmallestElement == 2)
    {   // Nearest side is rear
        // Calculate the vector of the rear of the target
        double vector_rear_x = Sensor_CS.dx_rear_left - Sensor_CS.dx_rear_right;
        double vector_rear_y = Sensor_CS.dy_rear_left - Sensor_CS.dy_rear_right;

        // Calculate the dot product of the line from sensor to rear and the line of the rear of the target. If the dot product is 0, then the two vectors are perpendicular to each other
        // dot_prod = x1 * x2 + y1 * y2
        double dot_prod = vector_rear_x * Sensor_CS.dx_rear + vector_rear_y * Sensor_CS.dy_rear;

        // Calculate the angle between the two vectors and transform into degree
        // arccos ( dot_prod / multiplied amounts of the two vectors )
        double angle_deg = acos(dot_prod / (sqrt(pow(vector_rear_x,2) + pow(vector_rear_y,2)) * sqrt(pow(Sensor_CS.dx_rear,2) + pow(Sensor_CS.dy_rear,2)))) * 180 / M_PI;

        if(angle_deg > 145.0)
        {
            reference_point = ReferencePointPosition::LEFT;
        }
        else if(angle_deg < 35.0)
        {
            reference_point = ReferencePointPosition::RIGHT;
        }
        else
        {
            reference_point = ReferencePointPosition::REAR;
        }
    }
    else if(indexSmallestElement == 3)
    {   // Nearest side is left
        reference_point = ReferencePointPosition::LEFT;
    }
    else if(indexSmallestElement == 4)
    {   // Nearest side is right
        reference_point = ReferencePointPosition::RIGHT;
    }

    /**
     * Fill in data of the reference point according to the defined Reference point
    */
    switch (reference_point)
    {
        case ReferencePointPosition::FRONT:
            RCA.dx_ref_point = RCA.dx_front;
            RCA.dy_ref_point = RCA.dy_front;
            Sensor_CS.dx_ref_point = Sensor_CS.dx_front;
            Sensor_CS.dy_ref_point = Sensor_CS.dy_front;
            
            //If we see the front of the target, its left side is on our right
            RCA.dx_ref_left = RCA.dx_front_right;
            RCA.dy_ref_left = RCA.dy_front_right;
            RCA.dx_ref_right = RCA.dx_front_left;
            RCA.dy_ref_right = RCA.dy_front_left;
            Sensor_CS.dx_ref_left = Sensor_CS.dx_front_right;
            Sensor_CS.dy_ref_left = Sensor_CS.dy_front_right;
            Sensor_CS.dx_ref_right = Sensor_CS.dx_front_left;
            Sensor_CS.dy_ref_right = Sensor_CS.dy_front_left;
            break;
        
        case ReferencePointPosition::REAR:
            RCA.dx_ref_point = RCA.dx_rear;
            RCA.dy_ref_point = RCA.dy_rear;
            Sensor_CS.dx_ref_point = Sensor_CS.dx_rear;
            Sensor_CS.dy_ref_point = Sensor_CS.dy_rear;

            //If we see the rear of the target, its left side is on our left
            RCA.dx_ref_left = RCA.dx_rear_left;
            RCA.dy_ref_left = RCA.dy_rear_left;
            RCA.dx_ref_right = RCA.dx_rear_right;
            RCA.dy_ref_right = RCA.dy_rear_right;
            Sensor_CS.dx_ref_left = Sensor_CS.dx_rear_left;
            Sensor_CS.dy_ref_left = Sensor_CS.dy_rear_left;
            Sensor_CS.dx_ref_right = Sensor_CS.dx_rear_right;
            Sensor_CS.dy_ref_right = Sensor_CS.dy_rear_right;
            break;
        
        case ReferencePointPosition::LEFT:
            RCA.dx_ref_point = RCA.dx_left;
            RCA.dy_ref_point = RCA.dy_left;
            Sensor_CS.dx_ref_point = Sensor_CS.dx_left;
            Sensor_CS.dy_ref_point = Sensor_CS.dy_left;

            //If we see the left of the target, its front side is on our left
            RCA.dx_ref_left = RCA.dx_front_left;
            RCA.dy_ref_left = RCA.dy_front_left;
            RCA.dx_ref_right = RCA.dx_rear_left;
            RCA.dy_ref_right = RCA.dy_rear_left;
            Sensor_CS.dx_ref_left = Sensor_CS.dx_front_left;
            Sensor_CS.dy_ref_left = Sensor_CS.dy_front_left;
            Sensor_CS.dx_ref_right = Sensor_CS.dx_rear_left;
            Sensor_CS.dy_ref_right = Sensor_CS.dy_rear_left;
            break;
        
        case ReferencePointPosition::RIGHT:
            RCA.dx_ref_point = RCA.dx_right;
            RCA.dy_ref_point = RCA.dy_right;
            Sensor_CS.dx_ref_point = Sensor_CS.dx_right;
            Sensor_CS.dy_ref_point = Sensor_CS.dy_right;
            
            //If we see the right of the target, its rear side is on our left
            RCA.dx_ref_left = RCA.dx_rear_right;
            RCA.dy_ref_left = RCA.dy_rear_right;
            RCA.dx_ref_right = RCA.dx_front_right;
            RCA.dy_ref_right = RCA.dy_front_right;
            Sensor_CS.dx_ref_left = Sensor_CS.dx_rear_right;
            Sensor_CS.dy_ref_left = Sensor_CS.dy_rear_right;
            Sensor_CS.dx_ref_right = Sensor_CS.dx_front_right;
            Sensor_CS.dy_ref_right = Sensor_CS.dy_front_right;
            break;
        
        default:
            break;
    }
}

void TargetCalculation::calculate_Locations(int nr_max_loc, int location_distribution, int radar_mode, int object_type, double mount_pos_z, double height, double vx, double vy)
{
    // Calculate the detected shape of the target
    TargetCalculation::calculate_Location_LShape();
    
    // Fill in Locations of reference side
    location_contour.dx_mid = Sensor_CS.dx_ref_point;
    location_contour.dy_mid = Sensor_CS.dy_ref_point;
    location_contour.dx_left = Sensor_CS.dx_ref_left;
    location_contour.dy_left = Sensor_CS.dy_ref_left;
    location_contour.dx_right = Sensor_CS.dx_ref_right;
    location_contour.dy_right = Sensor_CS.dy_ref_right;
    
    /**
     * Find points in between the contour points
     * For no LShape the locations are filled from both edges onwards
     * For LShape the locations are filled from the 2 points of the main side with the middle point going to the far edge
    */
    LPoint side_diff_pt = {0.0, 0.0}, Lshape_diff_pt = {0.0, 0.0};
    
    if(nr_max_loc > 3 && location_distribution != 2)
    {   // Only calculate interval step length if it is needed later on (more than 3 locations AND not statistical distribution)
        if(location_contour.L_shape == 1)
        {   // LShape

            switch (reference_point)
            {
            case ReferencePointPosition::FRONT:
                if(location_contour.second_side_indicator == ReferencePointPosition::LEFT)
                { // Far edge is from ego perspective visible on the right of the reference side, so visible line is between right and far
                    location_contour.side_start_pt.X = location_contour.dx_right;
                    location_contour.side_start_pt.Y = location_contour.dy_right;
                    side_diff_pt.X = location_contour.dx_left - location_contour.dx_right;
                    side_diff_pt.Y = location_contour.dy_left - location_contour.dy_right;

                    location_contour.Lshape_start_pt.X = location_contour.dx_right;
                    location_contour.Lshape_start_pt.Y = location_contour.dy_right;
                    Lshape_diff_pt.X = location_contour.dx_far - location_contour.dx_right;
                    Lshape_diff_pt.Y = location_contour.dy_far - location_contour.dy_right;
                }
                else if(location_contour.second_side_indicator == ReferencePointPosition::RIGHT)
                { // Far edge is from ego perspective visible on the left of the reference side, so visible line is between left and far
                    location_contour.side_start_pt.X = location_contour.dx_left;
                    location_contour.side_start_pt.Y = location_contour.dy_left;
                    side_diff_pt.X = location_contour.dx_right - location_contour.dx_left;
                    side_diff_pt.Y = location_contour.dy_right - location_contour.dy_left;

                    location_contour.Lshape_start_pt.X = location_contour.dx_left;
                    location_contour.Lshape_start_pt.Y = location_contour.dy_left;
                    Lshape_diff_pt.X = location_contour.dx_far - location_contour.dx_left;
                    Lshape_diff_pt.Y = location_contour.dy_far - location_contour.dy_left;
                }
                break;
            case ReferencePointPosition::REAR:
                if(location_contour.second_side_indicator == ReferencePointPosition::LEFT)
                { // Far edge is from ego perspective visible on the left of the reference side, so visible line is between left and far
                    location_contour.side_start_pt.X = location_contour.dx_left;
                    location_contour.side_start_pt.Y = location_contour.dy_left;
                    side_diff_pt.X = location_contour.dx_right - location_contour.dx_left;
                    side_diff_pt.Y = location_contour.dy_right - location_contour.dy_left;

                    location_contour.Lshape_start_pt.X = location_contour.dx_left;
                    location_contour.Lshape_start_pt.Y = location_contour.dy_left;
                    Lshape_diff_pt.X = location_contour.dx_far - location_contour.dx_left;
                    Lshape_diff_pt.Y = location_contour.dy_far - location_contour.dy_left;
                }
                else if(location_contour.second_side_indicator == ReferencePointPosition::RIGHT)
                { // Far edge is from ego perspective visible on the right of the reference side, so visible line is between right and far
                    location_contour.side_start_pt.X = location_contour.dx_right;
                    location_contour.side_start_pt.Y = location_contour.dy_right;
                    side_diff_pt.X = location_contour.dx_left - location_contour.dx_right;
                    side_diff_pt.Y = location_contour.dy_left - location_contour.dy_right;

                    location_contour.Lshape_start_pt.X = location_contour.dx_right;
                    location_contour.Lshape_start_pt.Y = location_contour.dy_right;
                    Lshape_diff_pt.X = location_contour.dx_far - location_contour.dx_right;
                    Lshape_diff_pt.Y = location_contour.dy_far - location_contour.dy_right;
                }
                break;
            case ReferencePointPosition::LEFT:
                if(location_contour.second_side_indicator == ReferencePointPosition::FRONT)
                { // Far edge is from ego perspective visible on the left of the reference side, so visible line is between left and far
                    location_contour.side_start_pt.X = location_contour.dx_left;
                    location_contour.side_start_pt.Y = location_contour.dy_left;
                    side_diff_pt.X = location_contour.dx_right - location_contour.dx_left;
                    side_diff_pt.Y = location_contour.dy_right - location_contour.dy_left;

                    location_contour.Lshape_start_pt.X = location_contour.dx_left;
                    location_contour.Lshape_start_pt.Y = location_contour.dy_left;
                    Lshape_diff_pt.X = location_contour.dx_far - location_contour.dx_left;
                    Lshape_diff_pt.Y = location_contour.dy_far - location_contour.dy_left;
                }
                else if(location_contour.second_side_indicator == ReferencePointPosition::REAR)
                { // Far edge is from ego perspective visible on the right of the reference side, so visible line is between right and far
                    location_contour.side_start_pt.X = location_contour.dx_right;
                    location_contour.side_start_pt.Y = location_contour.dy_right;
                    side_diff_pt.X = location_contour.dx_left - location_contour.dx_right;
                    side_diff_pt.Y = location_contour.dy_left - location_contour.dy_right;

                    location_contour.Lshape_start_pt.X = location_contour.dx_right;
                    location_contour.Lshape_start_pt.Y = location_contour.dy_right;
                    Lshape_diff_pt.X = location_contour.dx_far - location_contour.dx_right;
                    Lshape_diff_pt.Y = location_contour.dy_far - location_contour.dy_right;
                }
                break;
            case ReferencePointPosition::RIGHT:
                if(location_contour.second_side_indicator == ReferencePointPosition::REAR)
                { // Far edge is from ego perspective visible on the left of the reference side, so visible line is between left and far
                    location_contour.side_start_pt.X = location_contour.dx_left;
                    location_contour.side_start_pt.Y = location_contour.dy_left;
                    side_diff_pt.X = location_contour.dx_right - location_contour.dx_left;
                    side_diff_pt.Y = location_contour.dy_right - location_contour.dy_left;

                    location_contour.Lshape_start_pt.X = location_contour.dx_left;
                    location_contour.Lshape_start_pt.Y = location_contour.dy_left;
                    Lshape_diff_pt.X = location_contour.dx_far - location_contour.dx_left;
                    Lshape_diff_pt.Y = location_contour.dy_far - location_contour.dy_left;
                }
                else if(location_contour.second_side_indicator == ReferencePointPosition::FRONT)
                { // Far edge is from ego perspective visible on the right of the reference side, so visible line is between right and far
                    location_contour.side_start_pt.X = location_contour.dx_right;
                    location_contour.side_start_pt.Y = location_contour.dy_right;
                    side_diff_pt.X = location_contour.dx_left - location_contour.dx_right;
                    side_diff_pt.Y = location_contour.dy_left - location_contour.dy_right;

                    location_contour.Lshape_start_pt.X = location_contour.dx_right;
                    location_contour.Lshape_start_pt.Y = location_contour.dy_right;
                    Lshape_diff_pt.X = location_contour.dx_far - location_contour.dx_right;
                    Lshape_diff_pt.Y = location_contour.dy_far - location_contour.dy_right;
                }
                break;
            
            default:
                break;
            }
        }
        else
        { // far edge is not visible
            location_contour.side_start_pt.X = location_contour.dx_mid;
            location_contour.side_start_pt.Y = location_contour.dy_mid;
            side_diff_pt.X = location_contour.dx_left - location_contour.dx_mid;
            side_diff_pt.Y = location_contour.dy_left - location_contour.dy_mid;

            location_contour.Lshape_start_pt.X = location_contour.dx_mid;
            location_contour.Lshape_start_pt.Y = location_contour.dy_mid;
            Lshape_diff_pt.X = location_contour.dx_right - location_contour.dx_mid;
            Lshape_diff_pt.Y = location_contour.dy_right - location_contour.dy_mid;
        }

        // Calculate the number of extra locations for each side
        double pt_space = ((nr_max_loc-2) * 0.5);
        if(pt_space == 0)
        {
            pt_space = 1;
        }

        switch (location_distribution)
        { // Distribution of locations... 0 = even on the sides, 1 = crowded on middle point, 2 = statistical reflection
        case 0: // Calculate the intervals on each side, distributing the points to be 50/50
            location_contour.interval_side.X = side_diff_pt.X / pt_space;
            location_contour.interval_side.Y = side_diff_pt.Y / pt_space;
            location_contour.interval_Lshape.X = Lshape_diff_pt.X / pt_space;
            location_contour.interval_Lshape.Y = Lshape_diff_pt.Y / pt_space;
            break;

        case 1: // Calculate the intervals on each side, distributing the points to be crowded on the middle point of the seen surface
        case 2: // Statistical Reflection Model - use crowded distribution for now since reflection distribution is only available for cars
            location_contour.interval_side.X = side_diff_pt.X / pow(pt_space+1,2);
            location_contour.interval_side.Y = side_diff_pt.Y / pow(pt_space+1,2);
            location_contour.interval_Lshape.X = Lshape_diff_pt.X / pow(pt_space+1,2);
            location_contour.interval_Lshape.Y = Lshape_diff_pt.Y / pow(pt_space+1,2);
            break;
        
        default:
            break;
        }
    }
    
    /**
     * Fill the Location Cloud up to given maximum number of location or max_loc from array definition
    */
    int Lshape_counter = 0, side_counter = 0, stat_ref_counter = 0;
    double dx_temp = 0.0, dy_temp = 0.0, dz_temp = 0.0;
    double z_x = 0.0, z_y = 0.0;
    location_contour.total_loc_count = 0;
    // Local variables needed for statistical reflection model
    double aspect_angle = normAnglePosNegPI(Sensor_CS.yaw_angle);
    ::std::vector<vrmReflection> vrmLocs(nr_max_loc);

    for(int i = 0; i < nr_max_loc && i < max_loc; i++)
    {
        // Calculate the 2D position of the location (X and Y coordinates)
        switch (i)
        {
        case 0:
            dx_temp = location_contour.dx_mid_of_tgt;
            dy_temp = location_contour.dy_mid_of_tgt;
            break;

        case 1:
            dx_temp = location_contour.dx_mid;
            dy_temp = location_contour.dy_mid;
            break;

        case 2:
            dx_temp = location_contour.dx_left;
            dy_temp = location_contour.dy_left;
            break;

        case 3:
            dx_temp = location_contour.dx_right;
            dy_temp = location_contour.dy_right;
            break;
        
        default:
            
            if(location_contour.L_shape == 1 && i == 4)
            {   // If we see an LShape then the fourth location should be the LShape edge point
                dx_temp = location_contour.dx_far;
                dy_temp = location_contour.dy_far;
                break;
            }

            switch (location_distribution)
            { // 0 = even on the sides, 1 = crowded on middle point, 2 = statistical reflection
            case 0: // even on the sides
                if(i % 2 == 0)
                { // Side
                    side_counter++;
                    dx_temp = location_contour.side_start_pt.X + location_contour.interval_side.X * side_counter;
                    dy_temp = location_contour.side_start_pt.Y + location_contour.interval_side.Y * side_counter;
                }
                else
                { // LShape
                    Lshape_counter++;
                    dx_temp = location_contour.Lshape_start_pt.X + location_contour.interval_Lshape.X * Lshape_counter;
                    dy_temp = location_contour.Lshape_start_pt.Y + location_contour.interval_Lshape.Y * Lshape_counter;
                }
                break;

            case 1: // crowded on middle point
                if(i % 2 == 0)
                { // Side
                    side_counter++;
                    dx_temp = location_contour.side_start_pt.X + location_contour.interval_side.X * pow(side_counter,2);
                    dy_temp = location_contour.side_start_pt.Y + location_contour.interval_side.Y * pow(side_counter,2);
                }
                else
                { // LShape
                    Lshape_counter++;
                    dx_temp = location_contour.Lshape_start_pt.X + location_contour.interval_Lshape.X * pow(Lshape_counter,2);
                    dy_temp = location_contour.Lshape_start_pt.Y + location_contour.interval_Lshape.Y * pow(Lshape_counter,2);
                }
                break;

            case 2: // statistical reflection model
                if(stat_ref_counter == 0)
                {   // only one time!
                    CReflectionModel.getReflections(aspect_angle, vrmLocs);
                    stat_ref_counter++;
                }

                z_x = vrmLocs[i].z_x;
                z_y = vrmLocs[i].z_y;
                // Ego Sensor perspective, Target LShape of rear bumper and right side -> this works due to the yaw angle given to the statistical model being from rear side of the tgt
                dx_temp = Sensor_CS.dx_rear_right + z_x * (Sensor_CS.dx_front_right - Sensor_CS.dx_rear_right) - z_y * (Sensor_CS.dx_rear_right - Sensor_CS.dx_rear_left);
                dy_temp = Sensor_CS.dy_rear_right + z_x * (Sensor_CS.dy_front_right - Sensor_CS.dy_rear_right) - z_y * (Sensor_CS.dy_rear_right - Sensor_CS.dy_rear_left);
                break;
            
            default:
                dx_temp = 3.141;
                dy_temp = 3.141;
                break;
            }
            break;
        }

        // Calculate the height of the location (Z coordinate)
        dz_temp = calculate_dz(radar_mode,object_type,height,mount_pos_z);
        
        // Save the dx and dy coordinates of the calculated location for further calculations in the RoadObj.cpp (f.e. FoV)
        location_cloud[i].loc_dx = dx_temp;
        location_cloud[i].loc_dy = dy_temp;

        // Save the location defining values
        location_cloud[i].radial_distance = calc_radial_distance(dx_temp, dy_temp, dz_temp);
        //location_cloud[i].radial_velocity = calc_radial_velocity(Sensor_CS.dx_ref_point, Sensor_CS.dy_ref_point, vx, vy);
        location_cloud[i].radial_velocity = calc_radial_velocity(dx_temp, dy_temp, vx, vy);
        location_cloud[i].azimuth_angle = calc_azimuth_angle(dx_temp, dy_temp);
        location_cloud[i].elevation_angle= calc_elevation_angle(dx_temp, dy_temp, dz_temp);

        // Increase the total location counter for each location calculated
        location_contour.total_loc_count = location_contour.total_loc_count + 1;
    }
}

void TargetCalculation::calculate_RoadBarrier_Locations(int nr_max_loc, int radar_mode, double mount_pos_z, double height, double vx, double vy)
{
    double dx_temp = 0.0, dy_temp = 0.0, dz_temp = 0.0;
    LPoint side_diff_pt = {0.0, 0.0};

    // TODO: Check what exactly is being sent from CM as Walls/Guard Rails/... -> maybe a check like this is needed if(length >= width)
    // For now we expect that the length of the RoadBarrier is always the one to distribute the locations on
    // Also we expect that the width is very small and by this for now the locations are distributed in the middle of the structure along the length of it
    //          P2
    //         x  \                        P1-x-P2
    //       P1 x  \                        | x |
    //        \  x  \                       | x |
    //         \  x P4                     P3-x-P4
    //          \  x                       
    //           P3
    location_contour.side_start_pt.X = Sensor_CS.dx_rear;
    location_contour.side_start_pt.Y = Sensor_CS.dy_rear;
    side_diff_pt.X = Sensor_CS.dx_front - Sensor_CS.dx_rear;
    side_diff_pt.Y = Sensor_CS.dy_front - Sensor_CS.dy_rear;

    double pt_space = nr_max_loc - 1;
    if(pt_space <= 0)
    {
        pt_space = 1;
    }

    location_contour.interval_side.X = side_diff_pt.X / pt_space;
    location_contour.interval_side.Y = side_diff_pt.Y / pt_space;

    // Calculate the 2D position of the location (X and Y coordinates), for RoadBarrier the distribution is always even
    // TODO: Depending on the needs and how big for example GuardRails are, it could make sense to introduce here some kind of fading out distribution. Basically the same as the even distribution, but less loc density with greater distance.
    for(int i = 0; i < nr_max_loc && i < max_loc; i++)
    {
        // Distribute the locations evenly over the full length of the object
        dx_temp = location_contour.side_start_pt.X + location_contour.interval_side.X * i;    // (i - 2) = side counter - 2 hardcoded points
        dy_temp = location_contour.side_start_pt.Y + location_contour.interval_side.Y * i;

        // Calculate the height of the location (Z coordinate)
        dz_temp = calculate_dz(radar_mode,2,height,mount_pos_z);
        
        // Save the dx and dy coordinates of the calculated location for further calculations in the RoadObj.cpp (f.e. FoV)
        location_cloud[i].loc_dx = dx_temp;
        location_cloud[i].loc_dy = dy_temp;

        // Save the location defining values
        location_cloud[i].radial_distance = calc_radial_distance(dx_temp, dy_temp, dz_temp);
        location_cloud[i].radial_velocity = calc_radial_velocity(dx_temp, dy_temp, vx, vy);
        location_cloud[i].azimuth_angle = calc_azimuth_angle(dx_temp, dy_temp);
        location_cloud[i].elevation_angle= calc_elevation_angle(dx_temp, dy_temp, dz_temp);

        // Increase the total location counter for each location calculated
        location_contour.total_loc_count = location_contour.total_loc_count + 1;
    }

}

void TargetCalculation::calculate_ACCS(double velocity_x, double velocity_y, double acceleration_x, double acceleration_y, 
                                        double edge_left_old, double edge_right_old, double edge_mid_old)
{
    /**
     * Visible view
    */
    double scalar_product;
    if(reference_point == ReferencePointPosition::FRONT || reference_point == ReferencePointPosition::REAR)
    {
        if(reference_point == ReferencePointPosition::FRONT)
        {
            scalar_product = Sensor_CS.dx_front * (Sensor_CS.dx_front_right - Sensor_CS.dx_front) + Sensor_CS.dy_front * (Sensor_CS.dy_front_right - Sensor_CS.dy_front);
        }
        else if(reference_point == ReferencePointPosition::REAR)
        {
            scalar_product = Sensor_CS.dx_rear * (Sensor_CS.dx_rear_right - Sensor_CS.dx_rear) + Sensor_CS.dy_rear * (Sensor_CS.dy_rear_right - Sensor_CS.dy_rear);
        }
    
        if(scalar_product > -(pow(target_width,2)/target_length) && scalar_product < (pow(target_width,2)/target_length))
        {   //~90° -> Classic
            visible_view = VisibleView::CLASSIC;
        }
        else
        {   //!=90° -> Classic LShape
            visible_view = VisibleView::CLASSIC_SIDE;
        }
    }
    else if(reference_point == ReferencePointPosition::LEFT || reference_point == ReferencePointPosition::RIGHT)
    {
        if(reference_point == ReferencePointPosition::LEFT)
        {
            scalar_product = Sensor_CS.dx_left * (Sensor_CS.dx_rear_left - Sensor_CS.dx_left) + Sensor_CS.dy_left * (Sensor_CS.dy_rear_left - Sensor_CS.dy_left);
        }
        else if(reference_point == ReferencePointPosition::RIGHT)
        {
            scalar_product = Sensor_CS.dx_right * (Sensor_CS.dx_rear_right - Sensor_CS.dx_right) + Sensor_CS.dy_right * (Sensor_CS.dy_rear_right - Sensor_CS.dy_right);
        }

        if(scalar_product > -(target_length) && scalar_product < (target_length))
        {   //~90° -> SIDE
            visible_view = VisibleView::SIDE;
        }
        else
        {   //!=90° -> SIDE LShape
            visible_view = VisibleView::SIDE_CLASSIC;
        }
    }

    /**
     * Calculate the left and right edge which are always the two edges of the referenced side
     * Implemented as tan(viewing_angle) = dy / dx
    */
    if(Sensor_CS.dx_ref_right != 0)
    {
        edge_right = Sensor_CS.dy_ref_right / Sensor_CS.dx_ref_right;
    }else{
        edge_right = edge_right_old;
    }
    if(Sensor_CS.dx_ref_left != 0)
    {
        edge_left = Sensor_CS.dy_ref_left / Sensor_CS.dx_ref_left;
    }else{
        edge_left = edge_left_old;
    }
    
    /**
     * Calculate the middle edge
    */
    if(visible_view == VisibleView::CLASSIC || visible_view == VisibleView::SIDE)
    {   //2 Edges
        edge_mid = 0;
    }
    else if(visible_view == VisibleView::CLASSIC_SIDE || visible_view == VisibleView::SIDE_CLASSIC)
    {   //3 Edges (LShape)
        double far_edges[2][3];
        if(reference_point == ReferencePointPosition::FRONT){
            far_edges[0][0] = sqrt(pow(Sensor_CS.dx_rear_left,2) + pow(Sensor_CS.dy_rear_left,2));
            far_edges[0][1] = Sensor_CS.dx_rear_left;
            far_edges[0][2] = Sensor_CS.dy_rear_left;
            far_edges[1][0] = sqrt(pow(Sensor_CS.dx_rear_right,2) + pow(Sensor_CS.dy_rear_right,2));
            far_edges[1][1] = Sensor_CS.dx_rear_right;
            far_edges[1][2] = Sensor_CS.dy_rear_right;
        }else if(reference_point == ReferencePointPosition::REAR){
            far_edges[0][0] = sqrt(pow(Sensor_CS.dx_front_left,2) + pow(Sensor_CS.dy_front_left,2));
            far_edges[0][1] = Sensor_CS.dx_front_left;
            far_edges[0][2] = Sensor_CS.dy_front_left;
            far_edges[1][0] = sqrt(pow(Sensor_CS.dx_front_right,2) + pow(Sensor_CS.dy_front_right,2));
            far_edges[1][1] = Sensor_CS.dx_front_right;
            far_edges[1][2] = Sensor_CS.dy_front_right;
        }else if(reference_point == ReferencePointPosition::LEFT){
            far_edges[0][0] = sqrt(pow(Sensor_CS.dx_rear_right,2) + pow(Sensor_CS.dy_rear_right,2));
            far_edges[0][1] = Sensor_CS.dx_rear_right;
            far_edges[0][2] = Sensor_CS.dy_rear_right;
            far_edges[1][0] = sqrt(pow(Sensor_CS.dx_front_right,2) + pow(Sensor_CS.dy_front_right,2));
            far_edges[1][1] = Sensor_CS.dx_front_right;
            far_edges[1][2] = Sensor_CS.dy_front_right;
        }else if(reference_point == ReferencePointPosition::RIGHT){
            far_edges[0][0] = sqrt(pow(Sensor_CS.dx_front_left,2) + pow(Sensor_CS.dy_front_left,2));
            far_edges[0][1] = Sensor_CS.dx_front_left;
            far_edges[0][2] = Sensor_CS.dy_front_left;
            far_edges[1][0] = sqrt(pow(Sensor_CS.dx_rear_left,2) + pow(Sensor_CS.dy_rear_left,2));
            far_edges[1][1] = Sensor_CS.dx_rear_left;
            far_edges[1][2] = Sensor_CS.dy_rear_left;
        }

        //Find the nearest edge
        double smallestElement = std::numeric_limits<double>::max();
        int indexSmallestElement;
        for(int i = 0; i < 2; i++)
        {
            if(far_edges[i][0] < smallestElement || i == 0){
                smallestElement = far_edges[i][0];
                indexSmallestElement = i;
            }
        }

        //Calculate far edge
        if(far_edges[indexSmallestElement][1] != 0){
            edge_mid = far_edges[indexSmallestElement][2] / far_edges[indexSmallestElement][1];
        }else{
            edge_mid = 0;
        }
    }

    /**
     * Calculate vertical edges
     * Top is 0 because the Camera is ~ on the top of the car
     * Bot is positive, because the coordinate system is flipped -> upward direction corresponds to negative value
    */
    if(Sensor_CS.dx_ref_point != 0){
        edge_top = 0 / Sensor_CS.dx_ref_point;
        edge_bottom = target_height / Sensor_CS.dx_ref_point;
    }else{
        edge_top = 0;
        edge_bottom = 0;
    }

    /**
     * Calculate normalized edge dynamics
    */
    if(Sensor_CS.dx_ref_left != 0)
    {
        norm_vel_y_edge_left = (velocity_y/Sensor_CS.dx_ref_left);
    }
    else
    {
        norm_vel_y_edge_left = 0;
    }
    if(Sensor_CS.dx_ref_right != 0)
    {
        norm_vel_y_edge_right = (velocity_y/Sensor_CS.dx_ref_right);
    }
    else
    {
        norm_vel_y_edge_right = 0;
    }

    /**
     * Calculate normalized target dynamics
     * Normalized edges 
    */
    if(Sensor_CS.dx_ref_point != 0)
    {
        norm_vel_x = (velocity_x/Sensor_CS.dx_ref_point);
        norm_vel_y = (velocity_y/Sensor_CS.dx_ref_point);
        norm_accel_x = (acceleration_x/Sensor_CS.dx_ref_point);
    }
    else
    {
        norm_vel_x = 0;
        norm_vel_y = 0;
        norm_accel_x = 0;
    }
}

/**
 * Define if only one side is seen by the radar or if there are two (LShape)
 * To check whether a side stands out from the view of the sensor, the cross product of a corner point of the reference side 
 * and the point behind it must be calculated. As an example in belows picture we say the reference side is between P3 and P4.
 * This would mean we need to calculate the cross product of P3 with P1 and P4 with P2. In the left picture this would result
 * in the cross product indicating that the side between P3 and P1 is also seen. In the right picture there is just one side.
 * 
 * 
 *          P2
 *         /  \                        P1---P2
 *       P1    \                        |   |
 *        \     \                       |   |
 *         \    P4                     P3---P4
 *          \  /                       
 *           P3
 * 
 *           v                            v
 *         |---|                        |---|
 *         |   |                        |   |
 *         |   |                        |   |
 *         |---|                        |---|
 *          EGO                          EGO
 * 
 * It would be more accurate to calculate the angle between the two vectors pointing to 
 * e.g. P1 and P3 (analogous to determining the reference point). However, this would also be much more complex.
 */
void TargetCalculation::calculate_Location_LShape()
{
    double cross_product_left = 0.0;
    double cross_product_right = 0.0;
    double extension_factor = 0.5;

    switch (reference_point)
    {
        case ReferencePointPosition::FRONT:
            // Crossproduct between two points a and b = a.x * b.y - a.y * b.x
            cross_product_left = (Sensor_CS.dx_front_right * Sensor_CS.dy_rear_right) - (Sensor_CS.dy_front_right * Sensor_CS.dx_rear_right);
            cross_product_right = (Sensor_CS.dx_front_left * Sensor_CS.dy_rear_left) - (Sensor_CS.dy_front_left * Sensor_CS.dx_rear_left);

            if(cross_product_left > (extension_factor * sqrt(pow(Sensor_CS.dx_front_right,2) + pow(Sensor_CS.dy_front_right,2))))
            {   // Crossproduct is bigger than the extension_factor -> LShape
                visible_view = VisibleView::CLASSIC_SIDE;
                location_contour.second_side_indicator = ReferencePointPosition::RIGHT;
                location_contour.dx_far = Sensor_CS.dx_rear_right;
                location_contour.dy_far = Sensor_CS.dy_rear_right;
                location_contour.L_shape = 1;
                break;
            }
            else if(cross_product_right < -(extension_factor * sqrt(pow(Sensor_CS.dx_front_left,2) + pow(Sensor_CS.dy_front_left,2))))
            {   // Crossproduct is bigger than the extension_factor -> LShape
                visible_view = VisibleView::CLASSIC_SIDE;
                location_contour.second_side_indicator = ReferencePointPosition::LEFT;
                location_contour.dx_far = Sensor_CS.dx_rear_left;
                location_contour.dy_far = Sensor_CS.dy_rear_left;
                location_contour.L_shape = 1;
                break;
            }
            else
            {   // Crossproduct is inside boundaries -> no LShape
                visible_view = VisibleView::CLASSIC;
                location_contour.dx_far = 0;
                location_contour.dy_far = 0;
                location_contour.L_shape = 0;
                break;
            }


        case ReferencePointPosition::REAR:
            // Crossproduct between two points a and b = a.x * b.y - a.y * b.x
            cross_product_left = (Sensor_CS.dx_rear_left * Sensor_CS.dy_front_left) - (Sensor_CS.dy_rear_left * Sensor_CS.dx_front_left);
            cross_product_right = (Sensor_CS.dx_rear_right * Sensor_CS.dy_front_right) - (Sensor_CS.dy_rear_right * Sensor_CS.dx_front_right);

            if(cross_product_left > (extension_factor * sqrt(pow(Sensor_CS.dx_rear_left,2) + pow(Sensor_CS.dy_rear_left,2))))
            {   // Crossproduct is bigger than the extension_factor -> LShape
                visible_view = VisibleView::CLASSIC_SIDE;
                location_contour.second_side_indicator = ReferencePointPosition::LEFT;
                location_contour.dx_far = Sensor_CS.dx_front_left;
                location_contour.dy_far = Sensor_CS.dy_front_left;
                location_contour.L_shape = 1;
                break;
            }
            else if(cross_product_right < -(extension_factor * sqrt(pow(Sensor_CS.dx_rear_right,2) + pow(Sensor_CS.dy_rear_right,2))))
            {   // Crossproduct is bigger than the extension_factor -> LShape
                visible_view = VisibleView::CLASSIC_SIDE;
                location_contour.second_side_indicator = ReferencePointPosition::RIGHT;
                location_contour.dx_far = Sensor_CS.dx_front_right;
                location_contour.dy_far = Sensor_CS.dy_front_right;
                location_contour.L_shape = 1;
                break;
            }
            else
            {   // Crossproduct is inside boundaries -> no LShape
                visible_view = VisibleView::CLASSIC;
                location_contour.dx_far = 0;
                location_contour.dy_far = 0;
                location_contour.L_shape = 0;
                break;
            }

        case ReferencePointPosition::LEFT:
            // Crossproduct between two points a and b = a.x * b.y - a.y * b.x
            cross_product_left = (Sensor_CS.dx_front_left * Sensor_CS.dy_front_right) - (Sensor_CS.dy_front_left * Sensor_CS.dx_front_right);
            cross_product_right = (Sensor_CS.dx_rear_left * Sensor_CS.dy_rear_right) - (Sensor_CS.dy_rear_left * Sensor_CS.dx_rear_right);

            if(cross_product_left > (extension_factor * sqrt(pow(Sensor_CS.dx_front_left,2) + pow(Sensor_CS.dy_front_left,2))))
            {   // Crossproduct is bigger than the extension_factor -> LShape
                visible_view = VisibleView::SIDE_CLASSIC;
                location_contour.second_side_indicator = ReferencePointPosition::FRONT;
                location_contour.dx_far = Sensor_CS.dx_front_right;
                location_contour.dy_far = Sensor_CS.dy_front_right;
                location_contour.L_shape = 1;
                break;
            }
            else if(cross_product_right < -(extension_factor * sqrt(pow(Sensor_CS.dx_rear_left,2) + pow(Sensor_CS.dy_rear_left,2))))
            {   // Crossproduct is bigger than the extension_factor -> LShape
                visible_view = VisibleView::SIDE_CLASSIC;
                location_contour.second_side_indicator = ReferencePointPosition::REAR;
                location_contour.dx_far = Sensor_CS.dx_rear_right;
                location_contour.dy_far = Sensor_CS.dy_rear_right;
                location_contour.L_shape = 1;
                break;
            }
            else
            {   // Crossproduct is inside boundaries -> no LShape
                visible_view = VisibleView::SIDE;
                location_contour.dx_far = 0;
                location_contour.dy_far = 0;
                location_contour.L_shape = 0;
                break;
            }

        case ReferencePointPosition::RIGHT:
            // Crossproduct between two points a and b = a.x * b.y - a.y * b.x
            cross_product_left = (Sensor_CS.dx_rear_right * Sensor_CS.dy_rear_left) - (Sensor_CS.dy_rear_right * Sensor_CS.dx_rear_left);
            cross_product_right = (Sensor_CS.dx_front_right * Sensor_CS.dy_front_left) - (Sensor_CS.dy_front_right * Sensor_CS.dx_front_left);

            if(cross_product_left > (extension_factor * sqrt(pow(Sensor_CS.dx_rear_right,2) + pow(Sensor_CS.dy_rear_right,2))))
            {   // Crossproduct is bigger than the extension_factor -> LShape
                visible_view = VisibleView::SIDE_CLASSIC;
                location_contour.second_side_indicator = ReferencePointPosition::REAR;
                location_contour.dx_far = Sensor_CS.dx_rear_left;
                location_contour.dy_far = Sensor_CS.dy_rear_left;
                location_contour.L_shape = 1;
                break;
            }
            else if(cross_product_right < -(extension_factor * sqrt(pow(Sensor_CS.dx_front_right,2) + pow(Sensor_CS.dy_front_right,2))))
            {   // Crossproduct is bigger than the extension_factor -> LShape
                visible_view = VisibleView::SIDE_CLASSIC;
                location_contour.second_side_indicator = ReferencePointPosition::FRONT;
                location_contour.dx_far = Sensor_CS.dx_front_left;
                location_contour.dy_far = Sensor_CS.dy_front_left;
                location_contour.L_shape = 1;
                break;
            }
            else
            {   // Crossproduct is inside boundaries -> no LShape
                visible_view = VisibleView::SIDE;
                location_contour.dx_far = 0;
                location_contour.dy_far = 0;
                location_contour.L_shape = 0;
                break;
            }
        
        default:
            break;
    }
}

/**
 * Calculate the height of the location (Z coordinate, from sensors perspective!)
 * For the parking usecase the Z value is randomly generated with the possibility peak at 0 (so on the sensors height)
 * For the driving usecase the Z value is hardcoded to 0
 */
double TargetCalculation::calculate_dz(int radar_mode, int object_type, double tgt_height, double sensor_mount_pos_z)
{
    double dz = 0;

    if (radar_mode == 1)
    {   // If the sensor is in parking mode, then the dz value should be calculated randomly
        std::random_device rd;  // Will be used to obtain a seed for the random number engine
        std::mt19937 gen(rd()); // Standard mersenne_twister_engine (random number) seeded with rd()

        // Since the height of the object is from the ground, we need to calculate the height from the sensor
        double height_from_sensor = tgt_height - sensor_mount_pos_z;

        // Generate random numbers by following a normal (Gaussian) distribution centered around center (from sensor perspective!) with a specified spread.
        double center, spread = 0.0;
        if (object_type == 4)
        {   // Pedestrian
            center = 0.0;
            spread = tgt_height / 2;
        }
        else
        {
            center = 0.0;
            spread = tgt_height / 6;
        }
        std::normal_distribution<> d(center,spread);

        // Reroll until dz until it is in thereal world height range of the object
        int loop_count = 0;
        do {
            dz = d(gen);
            loop_count++;
            if(loop_count > 10)
            {
                dz = 0;
                break;
            }   
        } while (dz < -sensor_mount_pos_z || dz > height_from_sensor);
    }
    else
    {   // If the sensor is in driving mode, then the dz value should be set to 0 for now
        dz = 0;
    }

    return dz;
}

/**
 * Radar Cross Section
 * rcs = A * Rr * Rt * w / (64 * pi^3)
 * A = object’s apparent area in the radar’s line of sight in m^2
 * Rr = radar reflection coefficient (0=no reflection;1=perfect reflection). Set = 1.
 * Rt = radar transmission coefficient (0=no transmission;1=perfect transmission). Set = 1.
 * w = radar wavelength in meters. Set = 3.701mm = 0.003701m
*/
/*
calculate_RCS(double height)
{
    double rectangle,distance = 0;
    if(visible_view == VisibleView::CLASSIC_SIDE || visible_view == VisibleView::SIDE_CLASSIC)
    { //far edge is visible
        if(location_contour.dy_far > location_contour.dy_right)
        { //far edge is visible on the right of the reference side, so apparent area is between left and far
            rectangle = height * sqrt(pow(location_contour.dx_far - location_contour.dx_left,2) + pow(location_contour.dy_far - location_contour.dy_left,2));
            distance = TargetCalculation::calc_radial_distance(location_contour.dx_mid, location_contour.dy_mid);
            location_contour.apparent_area = rectangle * rectangle / (height * distance);  //TBD: Not working!
        }
        else if(location_contour.dy_far < location_contour.dy_left)
        { //far edge is visible on the left of the reference side, so apparent area is between right and far
            rectangle = height * sqrt(pow(location_contour.dx_far - location_contour.dx_right,2) + pow(location_contour.dy_far - location_contour.dy_right,2));
            distance = TargetCalculation::calc_radial_distance(location_contour.dx_mid, location_contour.dy_mid);
            location_contour.apparent_area = rectangle * rectangle / (height * distance);  //TBD: Not working!
        }
    }
    else if(visible_view == VisibleView::CLASSIC || visible_view == VisibleView::SIDE)
    { //far edge is not visible
            rectangle = height * sqrt(pow(location_contour.dx_right - location_contour.dx_left,2) + pow(location_contour.dy_right - location_contour.dy_left,2));
            distance = TargetCalculation::calc_radial_distance(location_contour.dx_mid, location_contour.dy_mid);
            location_contour.apparent_area = rectangle * rectangle / (height * distance);  //TBD: Not working!
    }
    location_contour.rcs = (location_contour.apparent_area * 0.003701) / (64 * pow(M_PI,3));
}
*/

/**
 * Getter
*/
ReferencePointPosition TargetCalculation::get_reference_point(){
        return reference_point;
}
VisibleView TargetCalculation::get_visible_view(){
        return visible_view;
}
CoordinateSystem TargetCalculation::get_RCA(){
        return RCA;
}
CoordinateSystem TargetCalculation::get_Sensor_CS(){
        return Sensor_CS;
}
LocationContour TargetCalculation::get_location_contour(){
        return location_contour;
}
double TargetCalculation::get_norm_vel_x(){
    return norm_vel_x;
}
double TargetCalculation::get_norm_vel_y(){
    return norm_vel_y;
}
double TargetCalculation::get_norm_accel_x(){
    return norm_accel_x;
}
double TargetCalculation::get_edge_left(){
    return edge_left;
} 
double TargetCalculation::get_edge_right(){
    return edge_right;
}
double TargetCalculation::get_edge_mid(){
    return edge_mid;
}
double TargetCalculation::get_edge_top(){
    return edge_top;
}
double TargetCalculation::get_edge_bottom(){
    return edge_bottom;
}
double TargetCalculation::get_norm_vel_y_edge_left(){
    return norm_vel_y_edge_left;
}
double TargetCalculation::get_norm_vel_y_edge_right(){
    return norm_vel_y_edge_right;
}
