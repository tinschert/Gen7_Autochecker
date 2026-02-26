/**
 * @file        RoadObj.cpp
 * @copyright   2023 Robert Bosch GmbH
 * @author      Robin Walter <robin.walter@de.bosch.com>
 * @date        12.03.2024
 * @brief       Calculates object and location data for multiple sensors
 */

#include "RoadObj.hpp"
#include <cmath>
#include <iostream>
#include <chrono>
#include <algorithm>

using namespace SignalCalc;

void RoadObj::SensorHandler::calculate_all_sensor_target_data()
{
    // Start of the object/location calculation
    auto start = std::chrono::high_resolution_clock::now();

    /**
     * RADAR Calculation - TBD Video calc in another function
    */
   
    Sensor* sensor_pointer;
    Radar* radar_pointer;
    Video* video_pointer;
    int sensor_quantity = 6;

    for (int sensor_counter = 0; sensor_counter < sensor_quantity; sensor_counter++)
    {
        /**
         * Switch pointer between sensors - this allows the calculation code below to be executed for all the sensors
        */
        switch (sensor_counter)
        {
            case 0: // Radar Front Center
                sensor_pointer = &Radar_FC;
                radar_pointer = &Radar_FC;
                video_pointer = nullptr;

                // Ford specific flip azimuth and elevation of FL and RR in Ford
                flip_coeff = 1;
                break;

            case 1: // Radar Front Left
                sensor_pointer = &Radar_FL;
                radar_pointer = &Radar_FL;
                video_pointer = nullptr;

                // Ford specific flip azimuth and elevation of FL and RR in Ford
                flip_coeff = -1;
                break;

            case 2: // Radar Front Right
                sensor_pointer = &Radar_FR;
                radar_pointer = &Radar_FR;
                video_pointer = nullptr;

                // Ford specific flip azimuth and elevation of FL and RR in Ford
                flip_coeff = 1;
                break;

            case 3: // Radar Rear Left
                sensor_pointer = &Radar_RL;
                radar_pointer = &Radar_RL;
                video_pointer = nullptr;

                // Ford specific flip azimuth and elevation of FL and RR in Ford
                flip_coeff = 1;
                break;

            case 4: // Radar Rear Right
                sensor_pointer = &Radar_RR;
                radar_pointer = &Radar_RR;
                video_pointer = nullptr;

                // Ford specific flip azimuth and elevation of FL and RR in Ford
                flip_coeff = -1;
                break;

            case 5: // Video Front Center
                sensor_pointer = &Video_FC;
                radar_pointer = nullptr;
                video_pointer = &Video_FC;
                break;

            default:
                sensor_pointer = nullptr;
                radar_pointer = nullptr;
                video_pointer = nullptr;
                std::cout << "CARE: Pointer points to no Sensor!" << std::endl;
                break;
        }

        int given_ego_ref_pnt = 0;
        int rad_gen_max_loc = 0;    // Number of maximum locations due to the radar generation
        int dist_max_loc = 0;       // Number of maximum locations due to the distance
        int obj_counter = 0;        // Running variable to count objects on a sensor
        int location_counter = 0;   // Running variable to count locations on one object
        int total_loc_number = 0;   // Number of all locations for one radar containing all valid objects

        /**
         * Calculate
        */
        if(sensor_pointer != nullptr)
        {
            // Set the given point on the ego vehicle
            switch (i_simulator)
            {
            case Simulator::Classe :
                given_ego_ref_pnt = 0;break;
                
            case Simulator::CarMaker :
                given_ego_ref_pnt = 1;break;
                
            default:
                break;
            }

            // Delete the old location data in the CAN TP byte array
            if(i_transfer_protocol == RoadObj::Data_Transfer_Protocol::CAN_TP || i_transfer_protocol == RoadObj::Data_Transfer_Protocol::Ethernet)
            {
                for (int i = 0; i < sizeof(sensor_pointer->byte_array_loc); i++) {
                    sensor_pointer->byte_array_loc[i] = 0;
                }
                for (int i = 0; i < sizeof(sensor_pointer->byte_array_obj); i++) {
                    sensor_pointer->byte_array_obj[i] = 0;
                }
            }

            // Loop through the whole Obj array of the sensor
            for (int object_counter = 0; object_counter < maximum_object_quantity; object_counter++)
            {
                // For each object first use inputs to calculate RCA && sensor obj data
                RoadObj::SensorHandler::rotate_coordinates(sensor_pointer, object_counter, sensor_pointer->get_in_obj_length(object_counter), sensor_pointer->get_in_obj_yaw_angle(object_counter), sensor_pointer->get_in_obj_distance_x(object_counter), 
                                                        sensor_pointer->get_in_obj_distance_y(object_counter), sensor_pointer->get_in_obj_velocity_x(object_counter), sensor_pointer->get_in_obj_velocity_y(object_counter),
                                                        sensor_pointer->get_sensor_mount_pos_x(), sensor_pointer->get_sensor_mount_pos_y(), sensor_pointer->get_sensor_mount_pos_yaw(), given_ego_ref_pnt, 0);

                
                // Calculate with the sensor data the validity flag for this obj and store them in the input_obj struct
                sensor_pointer->calculate_validity_flag(static_cast<int>(i_simulator),object_counter,sensor_pointer->Sensor_RS.dx,sensor_pointer->Sensor_RS.dy);
                
                // Check if object is valid and not empty
                if(sensor_pointer->get_in_obj_validity_flag(object_counter) == 1 && sensor_pointer->get_in_obj_empty_flag(object_counter) == 0)
                {
                    if(radar_pointer != nullptr)
                    {   // Radar specific calculations
                        if(radar_pointer->get_radar_loc_sim() == 1)
                        {   // location interface

                            // Set the number of maximum locations depending on the specific radar generation
                            switch (i_transfer_protocol)
                            {
                            case RoadObj::Data_Transfer_Protocol::CAN_Bus :
                            case RoadObj::Data_Transfer_Protocol::CAN_TP :
                                rad_gen_max_loc = 500;break;
                                
                            case RoadObj::Data_Transfer_Protocol::Ethernet :
                                if(radar_pointer->get_radar_generation() == 1)
                                {   // Conti
                                    rad_gen_max_loc = 1056;break;
                                }
                                else
                                {   // Bosch Gen6
                                    rad_gen_max_loc = 1000;break;
                                }
                                
                            default:
                                rad_gen_max_loc = 500;break;
                                break;
                            }

                            switch (radar_pointer->get_radar_loc_model())
                            {
                            case 0: // 1objXloc model
                                //calculation_class.calculate_ref_point(height,width,length,rca_dist_x,rca_dist_y,rca_heading_angle,sensor_dist_x,sensor_dist_y,sensor_heading_angle);
                                calculation_class.calculate_ref_point(radar_pointer->get_in_obj_height(object_counter),radar_pointer->get_in_obj_width(object_counter),radar_pointer->get_in_obj_length(object_counter),
                                                                    radar_pointer->RCA_RS.dx,radar_pointer->RCA_RS.dy,radar_pointer->RCA_RS.heading,
                                                                    radar_pointer->Sensor_RS.dx,radar_pointer->Sensor_RS.dy,radar_pointer->Sensor_RS.heading);

                                // calculate locations
                                // TODO: This is now implemented as a dummy for obj type = 2 (RoadBarrier) -> Extend the object types for additional types (guard rails, walls but also bike etc)
                                if(radar_pointer->get_in_obj_type(object_counter) == 2)
                                {   // Object Type RoadBarrier (walls, guard rails etc)
                                    calculation_class.calculate_RoadBarrier_Locations(radar_pointer->get_radar_max_nr_of_loc(), radar_pointer->get_in_obj_sensor_mode(object_counter), radar_pointer->get_sensor_mount_pos_z(), 
                                                                    radar_pointer->get_in_obj_height(object_counter), radar_pointer->Sensor_RS.vx, radar_pointer->Sensor_RS.vy);
                                }
                                else
                                {
                                    calculation_class.calculate_Locations(radar_pointer->get_radar_max_nr_of_loc(), radar_pointer->get_radar_loc_distribution_model(), radar_pointer->get_in_obj_sensor_mode(object_counter),
                                                                    radar_pointer->get_in_obj_type(object_counter), radar_pointer->get_sensor_mount_pos_z(), radar_pointer->get_in_obj_height(object_counter), radar_pointer->Sensor_RS.vx, radar_pointer->Sensor_RS.vy);
                                }

                                // cache calculated data
                                locations = calculation_class.get_location_contour();

                                // Calculate the number of locations due to the distance based on the requested location amount so that every 50 meter further away the amount of location gets reduced by 20% with the lowest amount possible being 2
                                // Given max loc from CANoe panel - (Given max loc * (dx/50) * 20%)
                                dist_max_loc = (std::max)(radar_pointer->get_radar_max_nr_of_loc() - static_cast<int>(radar_pointer->get_radar_max_nr_of_loc() * static_cast<int>(calculation_class.location_cloud[0].radial_distance / 50) * 0.2), 2);
                                
                                // Loop through locations. loc_nr = locations for this object. location_counter = total locations for this sensor over all objects.
                                // Boundaries are: Given max loc from CANoe panel reduced based on the distance && 1objXloc calc && nr of fields in array && radar gen specific
                                for(int loc_nr = 0; loc_nr < dist_max_loc && loc_nr < locations.total_loc_count && location_counter < maximum_location_quantity && location_counter < rad_gen_max_loc; loc_nr++)
                                {
                                    // check radial distance must not be 0 - for now send 0.2 instead but could be changed to sending only locations if the distance is greater than 0
                                    // check location is in the FoV of the sensor (validity flags are only checked for objects)
                                    if(calculation_class.location_cloud[loc_nr].radial_distance > 0.1
                                        && atan2(calculation_class.location_cloud[loc_nr].loc_dy, calculation_class.location_cloud[loc_nr].loc_dx) < radar_pointer->get_sensor_def().i_fov
                                        && atan2(calculation_class.location_cloud[loc_nr].loc_dy, calculation_class.location_cloud[loc_nr].loc_dx) > -radar_pointer->get_sensor_def().i_fov)
                                    {   
                                        radar_pointer->Loc[location_counter].o_radial_distance = calculation_class.location_cloud[loc_nr].radial_distance;
                                        radar_pointer->Loc[location_counter].o_radial_velocity = calculation_class.location_cloud[loc_nr].radial_velocity;
                                        radar_pointer->Loc[location_counter].o_azimuth = calculation_class.location_cloud[loc_nr].azimuth_angle;
                                        radar_pointer->Loc[location_counter].o_elevation = calculation_class.location_cloud[loc_nr].elevation_angle;
                                        radar_pointer->Loc[location_counter].o_radar_cross_section = radar_pointer->get_in_obj_rcs(object_counter);
                                        radar_pointer->Loc[location_counter].o_snr = radar_pointer->get_in_obj_snr(object_counter); 
                                        radar_pointer->Loc[location_counter].o_rssi = radar_pointer->get_in_obj_signal_strength(object_counter); 
                                        
                                        // calculate and store data which is specfic for one generation
                                        if(radar_pointer->get_radar_generation() == 6)
                                        {   // Radar Gen6 Interface
                                            if(i_transfer_protocol == RoadObj::Data_Transfer_Protocol::CAN_TP || i_transfer_protocol == RoadObj::Data_Transfer_Protocol::Ethernet)
                                            {   // Ford specific calculation of byte array
                                                byte_array_generator.Write_ByteArray_RXX_Location(location_counter,radar_pointer,flip_coeff);
                                            }
                                        }
                                        else if(radar_pointer->get_radar_generation() == 1)
                                        {   // Conti Radar interface 
                                            // range extrapolated = range?! = rad dist?! -> since extrapolated range probably means
                                            
                                            // Conti Ethernet Byte Array stuffing
                                            conti_byte_array_generator.Write_ByteArray_Conti_Location(location_counter,radar_pointer,flip_coeff);
                                        }

                                        // add the calculated location to the total number of locations
                                        location_counter++;
                                    }
                                }
                                break;
                            
                            default:
                                break;
                            }
                        }
                        else
                        {   // object interface
                            // calculate reference point on the target
                            calculation_class.calculate_ref_point(radar_pointer->get_in_obj_height(object_counter),radar_pointer->get_in_obj_width(object_counter),radar_pointer->get_in_obj_length(object_counter),
                                                                radar_pointer->RCA_RS.dx,radar_pointer->RCA_RS.dy,radar_pointer->RCA_RS.heading,
                                                                radar_pointer->Sensor_RS.dx,radar_pointer->Sensor_RS.dy,radar_pointer->Sensor_RS.heading);

                            // cache calculated data
                            rca_cs = calculation_class.get_RCA();
                            sensor_cs = calculation_class.get_Sensor_CS();

                            // store object data in sensor structure
                            radar_pointer->Obj[object_counter].o_distance_x = rca_cs.dx_ref_point;
                            radar_pointer->Obj[object_counter].o_distance_y = rca_cs.dy_ref_point;
                            radar_pointer->Obj[object_counter].o_velocity_x = radar_pointer->RCA_RS.vx;
                            radar_pointer->Obj[object_counter].o_velocity_y = radar_pointer->RCA_RS.vy;
                            radar_pointer->Obj[object_counter].o_yaw_angle = radar_pointer->RCA_RS.heading;
                            radar_pointer->Obj[object_counter].o_reference_point = calc_radar_obj_ref_pnt(calculation_class.get_reference_point());

                            // calculate and store data which is specfic for one generation
                            if(radar_pointer->get_radar_generation() == 5)
                            {   // Radar Gen5 SGU interface
                                radar_pointer->Obj[object_counter].o_ra5_prob_moving = calc_prob_moving(radar_pointer->RCA_RS.vx,radar_pointer->RCA_RS.vy,Ego_Values.i_velocity_x,Ego_Values.i_velocity_y);
                                radar_pointer->Obj[object_counter].o_ra5_prob_non_obst = calc_prob_non_obst(radar_pointer->get_in_obj_type(object_counter));
                                radar_pointer->Obj[object_counter].o_ra5_prob_truck = calc_prob_truck(radar_pointer->get_in_obj_type(object_counter));
                                radar_pointer->Obj[object_counter].o_ra5_prob_car = calc_prob_car(radar_pointer->get_in_obj_type(object_counter));
                                radar_pointer->Obj[object_counter].o_ra5_prob_pedestrian = calc_prob_pedestrian(radar_pointer->get_in_obj_type(object_counter));
                                radar_pointer->Obj[object_counter].o_ra5_prob_2wheeler = calc_prob_2wheeler(radar_pointer->get_in_obj_type(object_counter));

                                // set Gen6 specific signals to 0
                                radar_pointer->Obj[object_counter].o_ra6_radar_cross_section = 0.0;
                                radar_pointer->Obj[object_counter].o_ra6_obj_type = 0;
                                radar_pointer->Obj[object_counter].o_ra6_moving_status = 0;
                            }
                            else if(radar_pointer->get_radar_generation() == 6)
                            {   // Radar Gen6 SGU interface
                                radar_pointer->Obj[object_counter].o_ra6_radar_cross_section = radar_pointer->get_in_obj_rcs(object_counter);
                                radar_pointer->Obj[object_counter].o_ra6_obj_type = calc_ra6_obj_type(radar_pointer->get_in_obj_type(object_counter));
                                radar_pointer->Obj[object_counter].o_ra6_moving_status = calc_ra6_moving_status(radar_pointer->RCA_RS.vx,radar_pointer->RCA_RS.vy,Ego_Values.i_velocity_x,Ego_Values.i_velocity_y);

                                // set Gen5 specific signals to 0
                                radar_pointer->Obj[object_counter].o_ra5_prob_moving = 0;
                                radar_pointer->Obj[object_counter].o_ra5_prob_non_obst = 0;
                                radar_pointer->Obj[object_counter].o_ra5_prob_truck = 0;
                                radar_pointer->Obj[object_counter].o_ra5_prob_car = 0;
                                radar_pointer->Obj[object_counter].o_ra5_prob_pedestrian = 0;
                                radar_pointer->Obj[object_counter].o_ra5_prob_2wheeler = 0;

                                // Radar Gen6 SGU interfaces uses ByteArrays for the CAN_TP protocol
                                if(i_transfer_protocol == RoadObj::Data_Transfer_Protocol::CAN_TP || i_transfer_protocol == RoadObj::Data_Transfer_Protocol::Ethernet)
                                {   // Calculation of byte array
                                    ra6sgu_byte_array_generator.Write_ByteArray_RXX_Object(object_counter, radar_pointer);
                                }
                            }
                        }
                    }
                    else if(video_pointer != nullptr)
                    {   //Video specific calculations
                        // calculate reference point on the target
                        calculation_class.calculate_ref_point(video_pointer->get_in_obj_height(object_counter),video_pointer->get_in_obj_width(object_counter),video_pointer->get_in_obj_length(object_counter),
                                                            video_pointer->RCA_RS.dx,video_pointer->RCA_RS.dy,video_pointer->RCA_RS.heading,
                                                            video_pointer->Sensor_RS.dx,video_pointer->Sensor_RS.dy,video_pointer->Sensor_RS.heading);

                        // cache calculated data
                        rca_cs = calculation_class.get_RCA();
                        sensor_cs = calculation_class.get_Sensor_CS();

                        //calc_accs
                        calculation_class.calculate_ACCS(video_pointer->Sensor_RS.vx,video_pointer->Sensor_RS.vy,video_pointer->get_in_obj_acceleration_x(object_counter),
                                                        video_pointer->get_in_obj_acceleration_x(object_counter),video_pointer->Obj[object_counter].o_phi_left,
                                                        video_pointer->Obj[object_counter].o_phi_right,video_pointer->Obj[object_counter].o_phi_mid);

                        //read values and store them in object structure
                        video_pointer->Obj[object_counter].o_distance_x = rca_cs.dx_ref_point;
                        video_pointer->Obj[object_counter].o_distance_y = rca_cs.dy_ref_point;
                        video_pointer->Obj[object_counter].o_velocity_x = video_pointer->Sensor_RS.vx;
                        video_pointer->Obj[object_counter].o_velocity_y = video_pointer->Sensor_RS.vy;
                        video_pointer->Obj[object_counter].o_yaw_angle = calc_video_object_orientation(video_pointer->RCA_RS.heading,video_pointer->get_in_obj_type(object_counter));

                        video_pointer->Obj[object_counter].o_norm_velocity_x = calculation_class.get_norm_vel_x();
                        video_pointer->Obj[object_counter].o_norm_velocity_y = calculation_class.get_norm_vel_y();
                        video_pointer->Obj[object_counter].o_norm_acceleration_x = calculation_class.get_norm_accel_x();
                        video_pointer->Obj[object_counter].o_brake_light = calc_brake_light(video_pointer->get_in_obj_acceleration_x(object_counter));
                        video_pointer->Obj[object_counter].o_turn_light = 1;
                        video_pointer->Obj[object_counter].o_movement_prob_long = calc_prob_moving(video_pointer->Sensor_RS.vx,Ego_Values.i_velocity_x);
                        video_pointer->Obj[object_counter].o_movement_prob_lat = calc_prob_moving(video_pointer->Sensor_RS.vy,Ego_Values.i_velocity_y);
                        video_pointer->Obj[object_counter].o_movement_observed = calc_movement_flag(video_pointer->Obj[object_counter].o_movement_prob_long,video_pointer->Obj[object_counter].o_movement_prob_lat);
                        video_pointer->Obj[object_counter].o_reliability = calc_reliability(video_pointer->Obj[object_counter].o_movement_prob_long,video_pointer->Obj[object_counter].o_movement_prob_lat);
                        video_pointer->Obj[object_counter].o_meas_source = calc_meas_source(video_pointer->get_in_obj_type(object_counter));

                        video_pointer->Obj[object_counter].o_phi_bottom = calculation_class.get_edge_bottom();
                        video_pointer->Obj[object_counter].o_phi_left = calculation_class.get_edge_left();
                        video_pointer->Obj[object_counter].o_phi_right = calculation_class.get_edge_right();
                        video_pointer->Obj[object_counter].o_phi_mid = calculation_class.get_edge_mid();
                        
                        video_pointer->Obj[object_counter].o_type = calc_video_type(video_pointer->get_in_obj_type(object_counter));
                        video_pointer->Obj[object_counter].o_head_orientation = calc_head_orientation(video_pointer->Sensor_RS.heading, rca_cs.dy_ref_point);
                        video_pointer->Obj[object_counter].o_visible_view = static_cast<int>(calculation_class.get_visible_view());
                        video_pointer->Obj[object_counter].o_classified_view = static_cast<int>(calculation_class.get_reference_point());
                        video_pointer->Obj[object_counter].o_oncoming = calc_oncoming(calculation_class.get_reference_point());
                        video_pointer->Obj[object_counter].o_target_acc_type = calc_target_acc_type(calculation_class.get_visible_view(),rca_cs.dy_ref_point);
                    }

                    // Set the number of calculated valid objects
                    obj_counter++;
                }
            }
            sensor_pointer->set_sensor_valid_obj_count(obj_counter);
            if(radar_pointer != nullptr){
                radar_pointer->set_radar_loc_count(location_counter);
            }
        }
    }
    // End of the object/location calculation
    auto end = std::chrono::high_resolution_clock::now();

    // Calculation of the duration in milliseconds and conversion to int
    calculation_duration = static_cast<int>(std::chrono::duration_cast<std::chrono::microseconds>(end - start).count());
}

void RoadObj::SensorHandler::rotate_coordinates(Sensor* radar_ptr,int obj_id, double length, double heading_angle, double dist_x,
                                                double dist_y, double vel_x, double vel_y, double mount_pos_dx, double mount_pos_dy, 
                                                double mount_pos_yaw, int ego_current_ref_point, int target_current_ref_point)
{
    /**
     * Shift the distances, velocities and heading_angle if needed via the current_ref_point
     * ego_current_ref_point == 0 -> RCA
     * ego_current_ref_point == 1 -> Sensor
     * The formula for the x component is: x * cos(+-yaw) - y * sin(+-yaw)
     * The formula for the y component is: x * sin(+-yaw) + y * cos(+-yaw)
     * The sign results from the fact that the coordinate system is rotated clockwise when the sign is positive
    */
    if(ego_current_ref_point == 0)
    {   //ref_point == RCA
        //RCA values = inputs
        radar_ptr->RCA_RS.dx = dist_x;
        radar_ptr->RCA_RS.dy = dist_y;
        radar_ptr->RCA_RS.vx = vel_x;
        radar_ptr->RCA_RS.vy = vel_y;
        radar_ptr->RCA_RS.heading = heading_angle;
        
        //Sensor values have to be rotated to fit the sensor cs -> sign is the opposite of the mount_yaw
        radar_ptr->Sensor_RS.dx = (dist_x-mount_pos_dx)*cos(mount_pos_yaw)+(dist_y-mount_pos_dy)*sin(mount_pos_yaw);
        radar_ptr->Sensor_RS.dy = (dist_y-mount_pos_dy)*cos(mount_pos_yaw)-(dist_x-mount_pos_dx)*sin(mount_pos_yaw);
        radar_ptr->Sensor_RS.vx = vel_x * cos(-mount_pos_yaw) - vel_y * sin(-mount_pos_yaw);
        radar_ptr->Sensor_RS.vy = vel_x * sin(-mount_pos_yaw) + vel_y * cos(-mount_pos_yaw);
        radar_ptr->Sensor_RS.heading = heading_angle - mount_pos_yaw;
    }
    else if(ego_current_ref_point == 1)
    {   //ref_point == Sensor
        //Sensor values have to be rotated to fit the rca -> sign is the same as the mount_yaw
        radar_ptr->RCA_RS.dx = dist_x * cos(mount_pos_yaw) - dist_y * sin(mount_pos_yaw) + mount_pos_dx;
        radar_ptr->RCA_RS.dy = dist_x * sin(mount_pos_yaw) + dist_y * cos(mount_pos_yaw) + mount_pos_dy;
        radar_ptr->RCA_RS.vx = vel_x * cos(mount_pos_yaw) - vel_y * sin(mount_pos_yaw);
        radar_ptr->RCA_RS.vy = vel_x * sin(mount_pos_yaw) + vel_y * cos(mount_pos_yaw);
        radar_ptr->RCA_RS.heading = heading_angle + mount_pos_yaw;

        //Sensor values = inputs
        radar_ptr->Sensor_RS.dx = dist_x;
        radar_ptr->Sensor_RS.dy = dist_y;
        radar_ptr->Sensor_RS.vx = vel_x;
        radar_ptr->Sensor_RS.vy = vel_y;
        radar_ptr->Sensor_RS.heading = heading_angle;
    }

    // Center of Gravity on Ego side
    // Basically the same as RCA just moved longitudinal from mid of rear axle to the geometrical middle of the Ego vehicle
    radar_ptr->CoG_RS.dx = radar_ptr->RCA_RS.dx + 0.32 * length;  // Assumption: rear bumper to RCA is 0.18 * length
    radar_ptr->CoG_RS.dy = radar_ptr->RCA_RS.dy;
    //RCA values = inputs
    radar_ptr->CoG_RS.vx = radar_ptr->RCA_RS.vx;
    radar_ptr->CoG_RS.vy = radar_ptr->RCA_RS.vy;
    radar_ptr->CoG_RS.heading = radar_ptr->RCA_RS.heading;

    if(target_current_ref_point==0)
    {  //Target reference is Mid Rear Bumper
        //Calculate middle of Geometry
        radar_ptr->RCA_RS.dx = radar_ptr->RCA_RS.dx+(length/2.0f)*cos(radar_ptr->RCA_RS.heading);
        radar_ptr->RCA_RS.dy = radar_ptr->RCA_RS.dy+(length/2.0f)*sin(radar_ptr->RCA_RS.heading);

        radar_ptr->Sensor_RS.dx = radar_ptr->Sensor_RS.dx+(length/2.0f)*cos(radar_ptr->Sensor_RS.heading);
        radar_ptr->Sensor_RS.dy = radar_ptr->Sensor_RS.dy+(length/2.0f)*sin(radar_ptr->Sensor_RS.heading);
    }
}

/**
 * Sets the values of the ego vehicle 
 */
void RoadObj::SensorHandler::set_ego_values(double velocity_x,double velocity_y)
{
    Ego_Values.i_velocity_x = velocity_x;
    Ego_Values.i_velocity_y = velocity_y;
}