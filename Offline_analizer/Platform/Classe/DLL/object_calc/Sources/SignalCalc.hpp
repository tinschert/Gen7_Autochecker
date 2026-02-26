/**
 * @file      MathLibrary.h
 * @copyright 2023 Robert Bosch GmbH
 * @author    Robin Walter <robin.walter@de.bosch.com>
 * @date      25.07.2023
 * @brief     Contains definition of variables and functions used in the util_lib
 */

//#pragma once
#ifndef SIGNAL_CALC_HPP
#define SIGNAL_CALC_HPP

#ifndef M_PI
    #define M_PI    3.14159265358979323846   // pi
#endif

#ifndef M_PI_2
    #define M_PI_2     1.57079632679489661923   // pi/2
#endif

namespace SignalCalc {
    /**
     *  @brief Nearest side of the target
     * @param FRONT = 1
     * @param REAR = 2
     * @param LEFT = 3
     * @param RIGHT = 4
     */
    enum class ReferencePointPosition {
        UNKNOWN = 0,
        FRONT = 1,
        REAR = 2,
        LEFT = 3,
        RIGHT = 4
    };

    /**
     *  @brief View on the target
     * @param CLASSIC = 1, One side detected, Front/Rear
     * @param SIDE = 2, One side detected, Left/Right
     * @param CLASSIC_SIDE = 3, L Shape detected, Front/Rear being the "main" sides viewed
     * @param SIDE_CLASSIC = 4, L Shape detected, Left/Right being the "main" sides viewed
     */
    enum class VisibleView {
        UNKNOWN = 0,
        CLASSIC = 1,
        SIDE = 2,
        CLASSIC_SIDE = 3,
        SIDE_CLASSIC = 4,
    };

    /**
     * @brief Calculates the radial relative distance out of a given distance in x and y coordinates. In m.
     * @param distance_x Longitudinal relative distance of the location
     * @param distance_y Lateral relative distance of the location
     * @param distance_z Vertical relative distance of the location
     */
    double calc_radial_distance(double, double, double);
    /**
     * @brief Calculates the radial relative velocity. In m/s.
     * @param distance_x Longitudinal relative distance of the location
     * @param distance_y Lateral relative distance of the location
     * @param velocity_x Longitudinal relative velocity of the location
     * @param velocity_y Lateral relative velocity of the location
     */
    double calc_radial_velocity(double, double, double, double);
    /**
     * @brief Calculates the elevatio angle in spherical coordinates. In degree.
     * @param distance_x Longitudinal relative distance of the location
     * @param distance_y Lateral relative distance of the location
     * @param distance_z Vertical relative distance of the location
     */
    double calc_elevation_angle(double, double, double);
    /**
     * @brief Calculates the azimuth angle in spherical coordinates. In degree.
     * @param distance_x Longitudinal relative distance of the location
     * @param distance_y Lateral relative distance of the location
     */
    double calc_azimuth_angle(double, double);
    /**
     * @brief Calculates the moving probability. In Percent.
     * @param velocity_x Longitudinal velocity of the object
     * @param velocity_y Lateral velocity of the object
     * @param ego_velocity_x Longitudinal velocity of the object
     * @param ego_velocity_y Lateral velocity of the object
     */
    int calc_prob_moving(double, double, double, double);
    /**
     * @brief Calculates the moving probability in one direction. In Percent.
     * @param velocity Velocity of the object
     * @param ego_velocity Velocity of the object
     */
    int calc_prob_moving(double, double);
    /**
     * @brief Calculates the moving status enum according to radar gen6.
     * @param velocity_x Longitudinal velocity of the object
     * @param velocity_y Lateral velocity of the object
     * @param ego_velocity_x Longitudinal velocity of the object
     * @param ego_velocity_y Lateral velocity of the object
     */
    int calc_ra6_moving_status(double, double, double, double);
    /**
     * @brief Calculates the moving status enum according to radar gen6.
     * @param type Given Classe object type
     */
    int calc_ra6_obj_type(int);
    /**
     * @brief Calculates the probability for object being non-obstacle. In Percent.
     * @param type Object type
     */
    int calc_prob_non_obst(int);
    /**
     * @brief Calculates the probability for object being a truck. In Percent.
     * @param type Object type
     */
    int calc_prob_truck(int);
    /**
     * @brief Calculates the probability for object being a car. In Percent.
     * @param type Object type
     */
    int calc_prob_car(int);
    /**
     * @brief Calculates the probability for object being a pedestrian. In Percent.
     * @param type Object type
     */
    int calc_prob_pedestrian(int);
    /**
     * @brief Calculates the probability for object being a 2wheeler. In Percent.
     * @param type Object type
     */
    int calc_prob_2wheeler(int);
    /**
     * @brief Calculates the radar specific reference point.
     */
    int calc_radar_obj_ref_pnt(ReferencePointPosition);
    /**
     * @brief Calculates if the objects front is facing the Ego.
     */
    int calc_oncoming(ReferencePointPosition);
    /**
     * @brief Calculates the acceleration type of the object.
     * @param dy Lateral relative distance of the object
     */
    int calc_target_acc_type(VisibleView,double);
    /**
     * @brief Calculates the brake light of the object.
     * @param ax Longitudinal acceleration
     */
    int calc_brake_light(double);
    /**
     * @brief Calculates the brake light of the object.
     * @param move_long Longitudinal movement probability
     * @param move_lat Lateral movement probability
     */
    int calc_movement_flag(int,int);
    /**
     * @brief Classification of Reliability
     * @param move_long Longitudinal movement probability
     * @param move_lat Lateral movement probability
     */
    int calc_reliability(int,int);
    /**
     * @brief Classification of measurement source
     * @param type Object type
     */
    int calc_meas_source(int);
    /**
     * @brief Classification of the video specific type
     * @param type Object type
     */
    int calc_video_type(int);
    /**
     * @brief Classification of the video specific head orientation of pedestrians
     * @param heading_angle Yaw angle of the object in sensors perspective
     * @param dy Lateral distance of the object
     */
    int calc_head_orientation(double,double);
    /**
     * @brief Calculates the video specific yaw angle
     * @param heading_angle Yaw angle of the object in sensors perspective
     * @param type Object type
     */
    double calc_video_object_orientation(double,int);

    /**
     * @brief Normalizes a given angle to be in the range [-PI, PI]
     * @param f_angle Angle which should be normalized
     */
    double normAnglePosNegPI(double);
    /**
     * @brief Normalizes a given angle to be in the range [-PI/2, PI/2]
     * @param f_angle Angle which should be normalized
     */
    double normAnglePosNegHalfPI(double);
}

#endif // SIGNAL_CALC_HPP