/**
 * @file        MathLibrary.cpp
 * @copyright   2023 Robert Bosch GmbH
 * @author      Robin Walter <robin.walter@de.bosch.com>
 * @date        25.07.2023
 * @brief       Contains calculations for the distance of the target
 */

#include "SignalCalc.hpp"
#include <iostream>
#include <cmath>
#include <limits>

using namespace std;

// ============================================================================
// Radar LGU specific calculations
// ============================================================================

/**
 * Calculate radial distance from a given distance in x and y coordinates
*/
double SignalCalc::calc_radial_distance(double distance_x, double distance_y, double distance_z){
    double rad_distance = 0.0;
    rad_distance = sqrt(pow(distance_x,2) + pow(distance_y,2) + pow(distance_z,2));
    return rad_distance;
}

/**
 * Calculate radial velocity from a given relative velocity in x and y coordinates aswell as given distances in x and y coordinates
*/
double SignalCalc::calc_radial_velocity(double distance_x, double distance_y, double velocity_x, double velocity_y){
    double rad_dist, rad_velocity = 0.0;
    rad_dist = sqrt(pow(distance_x,2) + pow(distance_y,2));
    if(rad_dist == 0.0){
        rad_velocity = 0.0;
    }else{
        rad_velocity = (distance_x * velocity_x + distance_y * velocity_y) / rad_dist;
    }
    return rad_velocity;
}

/**
 * Calculate radial velocity from a given velocity in x and y coordinates
*/
double SignalCalc::calc_elevation_angle(double distance_x, double distance_y, double distance_z){
    double rad_dist, elevation_angle = 0.0;
    rad_dist = sqrt(pow(distance_x,2) + pow(distance_y,2) + pow(distance_z,2));
    if(rad_dist == 0.0){
        elevation_angle = 0.0;
    }else{
        elevation_angle = asin(distance_z / rad_dist);
    }
    return elevation_angle;
}

/**
 * Calculate radial velocity from a given velocity in x and y coordinates - RAD
*/
double SignalCalc::calc_azimuth_angle(double distance_x, double distance_y){
    double azimuth_angle = 0.0;
    if(distance_x == 0){
        azimuth_angle = azimuth_angle;
    }else{
        azimuth_angle = atan2(distance_y, distance_x);
    }
    return azimuth_angle;
}

// ============================================================================
// Radar SGU specific calculations
// ============================================================================

/**
 * Calculates the moving probability. In Percent.
 */
int SignalCalc::calc_prob_moving(double vx, double vy, double ego_vx, double ego_vy)
{
    int prob_moving = 0;
    double vx_abs = 0;
    double vy_abs = 0;
    
    vx_abs = vx + (ego_vx / 3.6);
    vy_abs = vy + (ego_vy / 3.6);
    
    //if((vx_abs > -0.1 && vx_abs < 0.1) && (vy_abs > -0.1 && vy_abs < 0.1)){
    if((vx_abs > -0.1 && vx_abs < 0.1) && vy_abs == 0.0){
        prob_moving = 0;
    }else{
        prob_moving = 100;
    }
    return prob_moving;
}
/**
 * Calculates the moving probability in one direction. In Percent.
 */
int SignalCalc::calc_prob_moving(double vel, double ego_vel)
{
    int prob_moving;
    double vel_abs;
    
    vel_abs = vel + (ego_vel / 3.6);
    
    if((vel_abs > -0.1 && vel_abs < 0.1)){
        prob_moving = 0;
    }else{
        prob_moving = 100;
    }
    return prob_moving;
}
/**
 * Calculates the probability for object being non-obstacle. In Percent.
 */
int SignalCalc::calc_prob_non_obst(int obj_type)
{
    int prob_non_obst;
    
    if(obj_type == 0){
        prob_non_obst = 100;
    }else{
        prob_non_obst = 0;
    }
    return prob_non_obst;
}
/**
 * Calculates the probability for object being a truck. In Percent.
 */
int SignalCalc::calc_prob_truck(int obj_type)
{
    int prob_truck;
    
    if(obj_type == 5){
        prob_truck = 100;
    }else{
        prob_truck = 0;
    }
    return prob_truck;
}
/**
 * Calculates the probability for object being a car. In Percent.
 */
int SignalCalc::calc_prob_car(int obj_type)
{
    int prob_car;
    
    if(obj_type == 6){
        prob_car = 100;
    }else{
        prob_car = 0;
    }
    return prob_car;
}
/**
 * Calculates the probability for object being a pedestrian. In Percent.
 */
int SignalCalc::calc_prob_pedestrian(int obj_type)
{
    int prob_pedestrian;
    
    if(obj_type == 4){
        prob_pedestrian = 100;
    }else{
        prob_pedestrian = 0;
    }
    return prob_pedestrian;
}
/**
 * Calculates the probability for object being a 2wheeler. In Percent.
 */
int SignalCalc::calc_prob_2wheeler(int obj_type)
{
    int prob_2wheeler;
    
    if(obj_type == 3){
        prob_2wheeler = 100;
    }else{
        prob_2wheeler = 0;
    }
    return prob_2wheeler;
}
/**
 * Calculates the moving status for the RA6 SGU variant.
 */
int SignalCalc::calc_ra6_moving_status(double vx, double vy, double ego_vx, double ego_vy)
{
    int moving_stat = 0;
    double vx_abs = 0;
    double vy_abs = 0;
    
    vx_abs = vx + (ego_vx / 3.6);
    vy_abs = vy + (ego_vy / 3.6);
    
    //if((vx_abs > -0.1 && vx_abs < 0.1) && (vy_abs > -0.1 && vy_abs < 0.1)){
    if((vx_abs > -0.1 && vx_abs < 0.1) && (vy_abs > -0.1 && vy_abs < 0.1))
    { // Object standing still
        moving_stat = 3;
    }
    else
    { // Object Moving
        moving_stat = 1;
    }
    return moving_stat;
}
/**
 * Calculates the object type for the RA6 SGU variant.
 */
int SignalCalc::calc_ra6_obj_type(int type)
{
    int obj_type = 0;
    
    switch (type)
    {
        case 0: //"Non-Obstacle"
        obj_type = 0;
        break;
        
        case 1: //"unknown"
        obj_type = 0;
        break;
        
        case 2: //"RoadSideBarrier"
        obj_type = 0;
        break;
        
        case 3: //"Motorbike"
        obj_type = 3;
        break;
        
        case 4: //"Pedestrian"
        obj_type = 1;
        break;
        
        case 5: //"Truck"
        obj_type = 5;
        break;
        
        case 6: //"PassengerCar"
        obj_type = 4;
        break;
        
        default:
        obj_type = 0;
        break;
    } 
    return obj_type;
}
/**
 * Calculates the radar specific reference point.
 */
int SignalCalc::calc_radar_obj_ref_pnt(SignalCalc::ReferencePointPosition ref_pnt)
{
    int adapted_ref_point;
    
    switch(ref_pnt)
    {
        case SignalCalc::ReferencePointPosition::UNKNOWN: //"Unknown"
            adapted_ref_point = 15;
            break;
        
        case SignalCalc::ReferencePointPosition::FRONT: //"Front"
            adapted_ref_point = 1;
            break;
        
        case SignalCalc::ReferencePointPosition::REAR: //"Rear"
            adapted_ref_point = 10;
            break;
        
        case SignalCalc::ReferencePointPosition::LEFT: //"Left"
            adapted_ref_point = 5;
            break;
        
        case SignalCalc::ReferencePointPosition::RIGHT: //"Right"
            adapted_ref_point = 6;
            break;
    } 
    
    return adapted_ref_point;
}

// ============================================================================
// Front Video specific calculations
// ============================================================================

/**
 * Calculates if the objects front is facing the Ego.
 */
int SignalCalc::calc_oncoming(SignalCalc::ReferencePointPosition ref_pnt)
{
    int oncoming = 0;
    
    if(ref_pnt == SignalCalc::ReferencePointPosition::FRONT)
    { // Classified view is the front
        oncoming = 1;
    }
    else
    {
        oncoming = 0;
    }
    return oncoming;
}
/**
 * Calculates the acceleration type of the object.
 */
int SignalCalc::calc_target_acc_type(SignalCalc::VisibleView vis_view, double dy)
{
    int target_acc_type = 0;
    
    if(static_cast<int>(vis_view) < 3)
    { // In Ego Lane
        target_acc_type = 1;
    }
    else
    {
        if(dy > 0)
        { // Left Lane
        target_acc_type = 3;
        }
        else
        { // Right Lane
        target_acc_type = 5;
        }
    }
    return target_acc_type;
}        
/**
 * Classifiction of the break lights
 */
int SignalCalc::calc_brake_light(double ax)
{
    int brake_light;
    
    if(ax < 0)
    {
        brake_light = 3;
    }else{
        brake_light = 1;
    }
    return brake_light;
}
/**
 * Classifiction of the movement flag
 */
int SignalCalc::calc_movement_flag(int move_long, int move_lat)
{
    int moving = 0;
    
    if(move_long == 0 && move_lat == 0)
    { //Target is standing still
        moving = 0;
    }
    else
    {
        moving = 1;
    }
    return moving;
}
/**
 * Classification of Reliability
 */
int SignalCalc::calc_reliability(int move_long, int move_lat)
{
    int reliability = 0;
    
    if(move_long == 0 && move_lat == 0)
    { //Target is standing still
        reliability = 56;
    }
    else
    {
        reliability = 57;
    }
    return reliability;
}
/**
 * Classification of measurement source
 */
int SignalCalc::calc_meas_source(int type)
{
    int meas_source = 0;
    
    if(type == 4)
    { //Pedestrian
        meas_source = 2;
    }
    else
    {
        meas_source = 4;
    }
    return meas_source;
}
/**
 * Classification of the video specific type
 */
int SignalCalc::calc_video_type(int type)
{
    int obj_type = 0;

    switch (type)
    {
    case 0: //"Non-Obstacle"
        obj_type = 1;
        break;
        
    case 1: //"unknown"
        obj_type = 0;
        break;
        
    case 2: //"RoadSideBarrier"
        obj_type = 0;
        break;
        
    case 3: //"2Wheeler"
        obj_type = 3;
        break;
        
    case 4: //"Pedestrian"
        obj_type = 7;
        break;
        
    case 5: //"Truck"
        obj_type = 2;
        break;
        
    case 6: //"PassengerCar"
        obj_type = 1;
        break;
    } 
    return obj_type;
}
/**
 * Classification of the video specific type
 */
int SignalCalc::calc_head_orientation(double heading_angle, double dy)
{
    int head_orientation = 0;

    if(heading_angle < -0.785){
    //left
    head_orientation = 7;
    }else if(heading_angle > 0.785){
    //right
    head_orientation = 3;
    }else{
        if(dy > 1){
            //oncoming traffic
            head_orientation = 1;
        }else{
            //ongoing traffic
            head_orientation = 5;
        }
    }
    return head_orientation;
}
/**
 * Classification of the video specific type
 */
double SignalCalc::calc_video_object_orientation(double heading_angle, int obj_type)
{
    double angle = 0.0;

    if(obj_type == 4)
    {   // For pedestrians always 0 - TODO: needs to be tested first
        //return 0;
    }

    // For all other types the yaw angle is modulo 180°
    //angle = normAnglePosNegHalfPI(heading_angle);
    angle = heading_angle;
    return angle;
}

// ============================================================================
// Common calculations
// ============================================================================

/* Mathematical source for the inclined reader (German, 07.05.2020):
http://www.hinterseher.de/Diplomarbeit/TrigonometrischeFunktionen.html#Winkel%20modulo%20[-Pi,%20Pi]
NOTE: "f_angle + M_PI" is calculated to compare in the next step l_angle
        against zero instead of "plus/minus PI" as stated in the above
        resource. This calculation needs to be considered by
        - in case of positive l_angle: reverting the rotation backwards (" - M_PI")
        - in case of negative l_angle: finishing the full convolution of two pi (" + M_PI")
        The algorithm is very elegant, but hard to understand when reading for the
        first time, so I decided to describe it.
*/
double SignalCalc::normAnglePosNegPI(double f_angle)
{
    double l_angle = ::std::fmod( f_angle + M_PI, 2 * M_PI );
    return l_angle >= 0 ? ( l_angle - M_PI ) : ( l_angle + M_PI );
}
double SignalCalc::normAnglePosNegHalfPI(double f_angle) 
{ 
    double l_angle = ::std::fmod(f_angle + M_PI_2, M_PI); 
    return l_angle >= 0 ? (l_angle - M_PI_2) : (l_angle + M_PI_2); 
}