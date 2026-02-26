/**
 * @file        tests_main.cpp
 * @copyright   2024 Robert Bosch GmbH
 * @author      Robin Walter <robin.walter@de.bosch.com>
 * @date        08.04.2024
 * @brief       Implements unit test functions for the full RoadObj and provides a main functions to run that unit test
 */

// General includes
#include <iostream>
#include <cassert>
#include <fstream>
#include <vector>

// Includes of files with functions to test
#include "../RoadObj/Sensor.hpp"
#include "../RoadObj/Radar.hpp"
#include "../RoadObj/Video.hpp"
#include "../RoadObj/RoadObj.hpp"
#include "../object_calc/Sources/MathLibrary.hpp"

// Global testing variables
std::vector<double> radial_distance;
std::vector<double> azimuth_angle;
std::vector<double> elevation_angle;
std::vector<int> Loc_ID;
std::vector<int> three_dimensions;
std::vector<std::string> colors;

/**
 *  @brief Customized assert function
 */
#ifndef NDEBUG
#   define M_Assert(Expr, Msg) \
    __M_Assert(#Expr, Expr, __FILE__, __LINE__, Msg)
#   define M_Assert_Integer(Expr, Msg, Int) \
    __M_Assert_Integer(#Expr, Expr, __FILE__, __LINE__, Msg, Int)
#else
#   define M_Assert(Expr, Msg) ;
#endif

/**
 * @brief Customized assert function to display the informations in a more readable way
 */
void __M_Assert(const char* expr_str, bool expr, const char* file, int line, const char* msg)
{
    if (!expr)
    {
        std::cerr << "Assert failed:\t" << msg << "\n"
            << "Expected:\t" << expr_str << "\n"
            << "Source:\t\t" << file << ", line " << line << "\n";
        abort();
    }
}
void __M_Assert_Integer(const char* expr_str, bool expr, const char* file, int line, const char* msg, int value)
{
    if (!expr)
    {
        std::cerr << "Assert failed:\t" << msg << "\n"
            << "Expected:\t" << expr_str << "\n"
            << "Value:\t\t" << value << "\n"
            << "Source:\t\t" << file << ", line " << line << "\n";
        abort();
    }
}

void writeDataToGlobals(double radialDist, double azimuthAngle, double elevationAngle, int ID, int threeDimensions, const std::string& color) {
    radial_distance.push_back(radialDist);
    azimuth_angle.push_back(azimuthAngle);
    elevation_angle.push_back(elevationAngle);
    Loc_ID.push_back(ID);
    three_dimensions.push_back(threeDimensions);
    colors.push_back(color);
}

void resetDataVariables() {
    radial_distance.clear();
    azimuth_angle.clear();
    elevation_angle.clear();
    Loc_ID.clear();
    three_dimensions.clear();
    colors.clear();
}

void writePointsToFile(const std::vector<double>& radial_distance, const std::vector<double>& azimuth_angle, const std::vector<double>& elevation_angle, const std::vector<int>& Loc_ID, const std::vector<std::string>& colors, const std::string& file_path, const std::vector<int>& three_dimensions) {
    std::ofstream file(file_path);
    if (file.is_open()) {
        for (size_t i = 0; i < radial_distance.size(); i++) {
            file << radial_distance[i] << "," << azimuth_angle[i] << "," << elevation_angle[i] << "," << Loc_ID[i] << "," << colors[i] << "," << three_dimensions[i] << std::endl;
        }
        file.close();
        std::cout << "  Locations were successfully written to the file." << std::endl;
    } else {
        std::cerr << "  Error opening the file." << std::endl;
    }
}

/**
 * @brief Test function for the Sensor class
 */
void test_sensor()
{
    Sensor testing_sensor;
    std::cout << "  Testing Sensor .." << std::endl;

    // Setting sensor values
    testing_sensor.set_sensor_values(1.5, 0.0, 0.0, 0.0, 1.309, 1, 1, 0);
    M_Assert(testing_sensor.get_sensor_mount_pos_x() == 1.5, "Sensor mounting position not stored correctly in Sensor struct");

    // Setting object values for 1 object in 30m distance
    testing_sensor.set_object_values(0, 1, 0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 0, 0.0, 0.0, 0.0);
    M_Assert(testing_sensor.get_in_obj_distance_x(0) == 30.0, "Object distance not stored correctly in Sensor struct");

    // Calculating validity flags for this object
    testing_sensor.calculate_validity_flag(testing_sensor.get_in_obj_sim_on(0), 0,
                                            testing_sensor.get_in_obj_distance_x(0),testing_sensor.get_in_obj_distance_y(0));
    M_Assert(testing_sensor.get_in_obj_validity_flag(0) == 1, "Validity flag calculation for object in FoV not correct");
    
    // Calculating validity flags for an object which is out of the Field of View of +-75° = 1.309rad
    testing_sensor.set_object_values(1, 1, 0, 5.0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 0, 0., 0.0, 0.0);
    testing_sensor.calculate_validity_flag(testing_sensor.get_in_obj_sim_on(1), 1,
                                            testing_sensor.get_in_obj_distance_x(1),testing_sensor.get_in_obj_distance_y(1));
    M_Assert(testing_sensor.get_in_obj_validity_flag(1) == 0, "Validity flag calculation for object out of FoV not correct");
    
    // Change FoV to +-90° for the 2nd object to also be in the FoV
    testing_sensor.set_sensor_values(1.5, 0.0, 0.0, 0.0, 1.5708, 1, 1, 0);
    testing_sensor.calculate_validity_flag(testing_sensor.get_in_obj_sim_on(1), 1,
                                            testing_sensor.get_in_obj_distance_x(1),testing_sensor.get_in_obj_distance_y(1));
    M_Assert(testing_sensor.get_in_obj_validity_flag(1) == 1, "CHanging the FoV results in wrong validity flag calculation");

    std::cout << "  Sensor Tests passed!" << std::endl;
}

/**
 * @brief Test function for the Radar class
 */
void test_radar()
{
    Radar testing_radar;
    std::cout << "  Testing Radar .." << std::endl;

    // Setting radar values
    testing_radar.set_radar_values(0, 1, 1, 20, 1.2, 6);
    M_Assert(testing_radar.get_radar_max_nr_of_loc() == 20, "Maximum number of locations per object not stored correctly in Radar struct");

    std::cout << "  Radar Tests passed!" << std::endl;
}

/**
 * @brief Test function for the Video class
 */
void test_video()
{
    Video testing_video;
    std::cout << "  Testing Video .." << std::endl;

    std::cout << "  Video Tests passed!" << std::endl;
}

/**
 * @brief Test function for the RoadObj class
 */
void test_road_obj()
{
    RoadObj::SensorHandler testing_road_obj;
    std::cout << "  Testing RoadObj .." << std::endl;

    // Testing Classe Mode
    testing_road_obj.i_simulator = RoadObj::Simulator::Classe;
    testing_road_obj.i_transfer_protocol = RoadObj::Data_Transfer_Protocol::CAN_TP;
    std::cout << "    Testing Classe mode .." << std::endl;

    // Set Radar FC Definitions
    testing_road_obj.Radar_FC.set_sensor_values(1.5, 0.0, 0.73, 0.0, 1.309, 1, 1, 0);
    testing_road_obj.Radar_FC.set_radar_values(0, 1, 1, 10, 1.2, 6);

    // Set Radar FL Definitions
    testing_road_obj.Radar_FL.set_sensor_values(1.5, 0.8, 0.73, 0.785, 1.309, 0, 1, 0);
    testing_road_obj.Radar_FL.set_radar_values(0, 0, 0, 0, 0, 5);

    // Set Radar FR Definitions
    testing_road_obj.Radar_FR.set_sensor_values(1.5, -0.8, 0.73, -0.785, 1.309, 0, 1, 0);
    testing_road_obj.Radar_FR.set_radar_values(0, 0, 0, 0, 0, 5);

    // Set Radar RL Definitions
    testing_road_obj.Radar_RL.set_sensor_values(-1.16, 0.955, 0.73, 2.234, 1.309, 1, 1, 0);
    testing_road_obj.Radar_RL.set_radar_values(0, 2, 1, 10, 1.2, 6);

    // Set Radar RR Definitions
    testing_road_obj.Radar_RR.set_sensor_values(-1.16, -0.955, 0.73, -2.234, 1.309, 1, 1, 0);
    testing_road_obj.Radar_RR.set_radar_values(0, 2, 1, 10, 1.2, 6);

    // Set Video FC Definitions
    testing_road_obj.Video_FC.set_sensor_values(0.8, 0.0, 0.0, 0.0, 1.309, 1, 1, 0);

    // Add object seen by all of them
    testing_road_obj.Radar_FC.set_object_values(0, 1, 0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(0, 1, 0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FR.set_object_values(0, 1, 0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Video_FC.set_object_values(0, 1, 0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);

    // Add object seen exceptionally by Radar FL
    testing_road_obj.Radar_FC.set_object_values(1, 1, 0, 5.0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 6, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(1, 1, 0, 5.0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 6, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FR.set_object_values(1, 1, 0, 5.0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 6, 0.0, 0.0, 0.0);

    // Add object seen exceptionally by Radar FR
    testing_road_obj.Radar_FC.set_object_values(2, 1, 0, 5.0, -30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 6, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(2, 1, 0, 5.0, -30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 6, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FR.set_object_values(2, 1, 0, 5.0, -30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0, 1.5, 6, 0.0, 0.0, 0.0);

    // Calculating sensor data such as validity flags and obj/loc data
    testing_road_obj.calculate_all_sensor_target_data();

    // Checking Validity Flags and Empty Object Flags for Radar FC (validity sending active)
    M_Assert(testing_road_obj.Radar_FC.get_in_obj_validity_flag(0) == 1 && testing_road_obj.Radar_FC.get_in_obj_empty_flag(0) == 0, 
            "Validity flag calculation for Radar FC for object in FoV not correct");
    M_Assert(testing_road_obj.Radar_FC.get_in_obj_validity_flag(1) == 0 && testing_road_obj.Radar_FC.get_in_obj_empty_flag(1) == 1, 
            "Validity flag calculation for Radar FC for object out of FoV not correct");
    M_Assert(testing_road_obj.Radar_FC.get_in_obj_validity_flag(2) == 0 && testing_road_obj.Radar_FC.get_in_obj_empty_flag(2) == 1, 
            "Validity flag calculation for Radar FC for object out of FoV not correct");

    // Checking Validity Flags and Empty Object Flags for Radar FL (validity sending not active)
    M_Assert(testing_road_obj.Radar_FL.get_in_obj_validity_flag(0) == 1 && testing_road_obj.Radar_FL.get_in_obj_empty_flag(0) == 0, 
            "Validity flag calculation for Radar FL for object in FoV not correct");
    M_Assert(testing_road_obj.Radar_FL.get_in_obj_validity_flag(1) == 1 && testing_road_obj.Radar_FL.get_in_obj_empty_flag(1) == 0, 
            "Validity flag calculation for Radar FL for object in FoV not correct");
    M_Assert(testing_road_obj.Radar_FL.get_in_obj_validity_flag(2) == 1 && testing_road_obj.Radar_FL.get_in_obj_empty_flag(2) == 1, 
            "Validity flag calculation for Radar FL for object out of FoV not correct");

    // Checking Validity Flags and Empty Object Flags for Radar FR (validity sending not active)
    M_Assert(testing_road_obj.Radar_FR.get_in_obj_validity_flag(0) == 1 && testing_road_obj.Radar_FR.get_in_obj_empty_flag(0) == 0, 
            "Validity flag calculation for Radar FR for object in FoV not correct");
    M_Assert(testing_road_obj.Radar_FR.get_in_obj_validity_flag(1) == 1 && testing_road_obj.Radar_FR.get_in_obj_empty_flag(1) == 1, 
            "Validity flag calculation for Radar FR for object out of FoV not correct");
    M_Assert(testing_road_obj.Radar_FR.get_in_obj_validity_flag(2) == 1 && testing_road_obj.Radar_FR.get_in_obj_empty_flag(2) == 0, 
            "Validity flag calculation for Radar FR for object in FoV not correct");

    // Checking number of calculated valid objects
    M_Assert_Integer(testing_road_obj.Radar_FC.get_sensor_valid_obj_count() == 1, 
            "Calculated number of valid objects of Radar FC not correct", testing_road_obj.Radar_FC.get_sensor_valid_obj_count());
    M_Assert_Integer(testing_road_obj.Radar_FL.get_sensor_valid_obj_count() == 2, 
            "Calculated number of valid objects of Radar FC not correct", testing_road_obj.Radar_FL.get_sensor_valid_obj_count());
    M_Assert_Integer(testing_road_obj.Radar_FR.get_sensor_valid_obj_count() == 2, 
            "Calculated number of valid objects of Radar FC not correct", testing_road_obj.Radar_FR.get_sensor_valid_obj_count());

    // Checking radar object interface
    M_Assert_Integer(testing_road_obj.Radar_FL.Obj[0].o_ra5_prob_car == 100, 
            "Radar FL object type probability for type car not recognized correctly", testing_road_obj.Radar_FL.Obj[0].o_ra5_prob_car);

    // Checking video object interface
    M_Assert_Integer(testing_road_obj.Video_FC.Obj[0].o_classified_view == 2, 
            "Radar FL object type probability for type car not recognized correctly", testing_road_obj.Video_FC.Obj[0].o_classified_view);

    // Testing 1objXloc with CMP in RoadObj
    testing_road_obj.Radar_FC.set_radar_values(0, 1, 1, 10, 1.2, 6);
    testing_road_obj.Radar_FC.set_object_values(0, 1, 0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.785, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.calculate_all_sensor_target_data();

    M_Assert_Integer(testing_road_obj.Radar_FC.get_radar_valid_loc_count() == 10, 
            "Calculated number of valid locations of Radar FC not correct", testing_road_obj.Radar_FC.get_radar_valid_loc_count());
    for(int i = 0; i < testing_road_obj.Radar_FC.get_radar_valid_loc_count(); i++)
    {
        writeDataToGlobals(testing_road_obj.Radar_FC.Loc[i].o_radial_distance,testing_road_obj.Radar_FC.Loc[i].o_azimuth,testing_road_obj.Radar_FC.Loc[i].o_elevation,i,0,"b");
    } 

    // Testing 1objXloc with Statistical distribution in RoadObj
    testing_road_obj.Radar_FC.set_radar_values(0, 2, 1, 10, 1.2, 6);
    testing_road_obj.Radar_FC.set_object_values(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FC.set_object_values(1, 1, 0, 15.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.785, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FC.set_object_values(2, 1, 0, 15.0, -5.0, 0.0, 0.0, 0.0, 0.0, 0.785, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.calculate_all_sensor_target_data();

    M_Assert_Integer(testing_road_obj.Radar_FC.get_radar_valid_loc_count() == 20, 
            "Calculated number of valid locations of Radar FC not correct", testing_road_obj.Radar_FC.get_radar_valid_loc_count());
    M_Assert_Integer(testing_road_obj.Radar_FC.get_sensor_valid_obj_count() == 2, 
            "Calculated number of valid objects of Radar FC not correct", testing_road_obj.Radar_FC.get_sensor_valid_obj_count());
    for(int i = 0; i < testing_road_obj.Radar_FC.get_radar_valid_loc_count(); i++)
    {
        writeDataToGlobals(testing_road_obj.Radar_FC.Loc[i].o_radial_distance,testing_road_obj.Radar_FC.Loc[i].o_azimuth,testing_road_obj.Radar_FC.Loc[i].o_elevation,i,0,"g");
    } 

    // Testing parking usecase with 1objXloc with Statistical distribution in RoadObj
    testing_road_obj.Radar_FC.set_radar_values(0, 2, 1, 10, 1.2, 6);
    testing_road_obj.Radar_FC.set_object_values(1, 1, 1, 25.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.785, 0.5, 10.0, 5, 2, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FC.set_object_values(2, 1, 1, 25.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.785, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FC.set_object_values(3, 1, 1, 25.0, -5.0, 0.0, 0.0, 0.0, 0.0, 0.785, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FC.set_object_values(4, 1, 1, 25.0, -15.0, 0.0, 0.0, 0.0, 0.0, 0.785, 0.5, 10.0, 1, 2, 20.0, 100.0, 0.0);
    testing_road_obj.calculate_all_sensor_target_data();

    M_Assert_Integer(testing_road_obj.Radar_FC.get_radar_valid_loc_count() == 40, 
            "Calculated number of valid locations of Radar FC not correct", testing_road_obj.Radar_FC.get_radar_valid_loc_count());
    M_Assert_Integer(testing_road_obj.Radar_FC.get_sensor_valid_obj_count() == 4, 
            "Calculated number of valid objects of Radar FC not correct", testing_road_obj.Radar_FC.get_sensor_valid_obj_count());
    for(int i = 0; i < testing_road_obj.Radar_FC.get_radar_valid_loc_count(); i++)
    {
        writeDataToGlobals(testing_road_obj.Radar_FC.Loc[i].o_radial_distance,testing_road_obj.Radar_FC.Loc[i].o_azimuth,testing_road_obj.Radar_FC.Loc[i].o_elevation,i,1,"r");
    } 

    // Testing reset of object and location counter
    testing_road_obj.Radar_FC.set_radar_values(0, 2, 1, 10, 1.2, 6);
    testing_road_obj.Radar_FC.set_object_values(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FC.set_object_values(1, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FC.set_object_values(2, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FC.set_object_values(3, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FC.set_object_values(4, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(1, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(2, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FR.set_object_values(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FR.set_object_values(1, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Radar_FR.set_object_values(2, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.Video_FC.set_object_values(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0);
    testing_road_obj.calculate_all_sensor_target_data();

    M_Assert_Integer(testing_road_obj.Radar_FC.get_radar_valid_loc_count() == 0, 
            "Calculated number of valid locations of Radar FC not correct", testing_road_obj.Radar_FC.get_radar_valid_loc_count());
    M_Assert_Integer(testing_road_obj.Radar_FC.get_sensor_valid_obj_count() == 0, 
            "Calculated number of valid objects of Radar FC not correct", testing_road_obj.Radar_FC.get_sensor_valid_obj_count());
    for(int i = 0; i < testing_road_obj.Radar_FC.get_radar_valid_loc_count(); i++)
    {
        writeDataToGlobals(testing_road_obj.Radar_FC.Loc[i].o_radial_distance,testing_road_obj.Radar_FC.Loc[i].o_azimuth,testing_road_obj.Radar_FC.Loc[i].o_elevation,i,0,"y");
    } 

    // Testing Corner Ford radars
    int i = 0;
    double dx = 0.0;
    double dy = 0.0;

    // One object moving in several cycles
    /*
    for(int i = 0; i < 7; i++){
        dx = -8 + i * 2.0;
        dy = -10 + i * 1.0;
        testing_road_obj.Radar_FL.set_object_values(0, 1, 30, dy, 0.0, 1.0, 0.0, 0.0, -1.57, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
        //testing_road_obj.Radar_FR.set_object_values(0, 1, -40.0, dy, 0.0, 1.0, 0.0, 0.0, -1.57, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
        //testing_road_obj.Radar_RL.set_object_values(0, 1, -40.0, dy, 0.0, 1.0, 0.0, 0.0, -1.57, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
        //testing_road_obj.Radar_RR.set_object_values(0, 1, -40.0, dy, 0.0, 1.0, 0.0, 0.0, -1.57, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
        testing_road_obj.calculate_all_sensor_target_data();
        
        // This can be used to debug a hardcoded driving sequence on the RL radar
        for(int k = 0; k < testing_road_obj.Radar_RL.get_radar_valid_loc_count(); k++)
        {
            switch (i)
            {
            case 0:
                writeDataToGlobals(testing_road_obj.Radar_FL.Loc[k].o_radial_distance,testing_road_obj.Radar_FL.Loc[k].o_azimuth,k,"y");
                break;
            case 1:
                writeDataToGlobals(testing_road_obj.Radar_FL.Loc[k].o_radial_distance,testing_road_obj.Radar_FL.Loc[k].o_azimuth,k,"r");
                break;
            case 2:
                writeDataToGlobals(testing_road_obj.Radar_FL.Loc[k].o_radial_distance,testing_road_obj.Radar_FL.Loc[k].o_azimuth,k,"b");
                break;
            case 3:
                writeDataToGlobals(testing_road_obj.Radar_FL.Loc[k].o_radial_distance,testing_road_obj.Radar_FL.Loc[k].o_azimuth,k,"g");
                break;
            case 4:
                writeDataToGlobals(testing_road_obj.Radar_FL.Loc[k].o_radial_distance,testing_road_obj.Radar_FL.Loc[k].o_azimuth,k,"c");
                break;
            case 5:
                writeDataToGlobals(testing_road_obj.Radar_FL.Loc[k].o_radial_distance,testing_road_obj.Radar_FL.Loc[k].o_azimuth,k,"y");
                break;
            case 6:
                writeDataToGlobals(testing_road_obj.Radar_FL.Loc[k].o_radial_distance,testing_road_obj.Radar_FL.Loc[k].o_azimuth,k,"r");
                break;
            
            default:
                break;
            }
            
        } 
        
    }*/
    /*
    // Several objects at once
    testing_road_obj.Radar_FL.set_sensor_values(4.26, 0.96, 0.7, 1.047, 1.309, 0, 1, 0);
    testing_road_obj.Radar_FL.set_radar_values(0, 2, 1, 10, 1.2, 6);

    testing_road_obj.Radar_FL.set_object_values(0, 1, 31, -4, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(1, 1, 43, -4, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(2, 1, 55, -3, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(3, 1, 35, 4, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(4, 1, 45, 4, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(5, 1, 55, 3, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(6, 1, 30, 1, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(7, 1, 40, -1, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(8, 1, 75, -1, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(9, 1, 120, -1, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(10, 1, 150, -1, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);
    testing_road_obj.Radar_FL.set_object_values(11, 1, 200, -1, 0.0, 1.0, 0.0, 0.0, 0, 2.0, 4.0, 1.5, 6, 20.0, 100.0, 0.0);

    testing_road_obj.calculate_all_sensor_target_data();
    std::cout << testing_road_obj.Radar_FL.get_radar_valid_loc_count() << std::endl;
       
    // This can be used to debug a hardcoded driving sequence on the RL radar
    for(int k = 0; k < testing_road_obj.Radar_FL.get_radar_valid_loc_count(); k++)
    {
        writeDataToGlobals(testing_road_obj.Radar_FL.Loc[k].o_radial_distance,testing_road_obj.Radar_FL.Loc[k].o_azimuth,k,"r");
    }*/

    std::cout << "      Classe Tests passed!" << std::endl;

    // Testing CarMaker Mode
    testing_road_obj.i_simulator = RoadObj::Simulator::CarMaker;
    std::cout << "      Testing CarMaker mode .." << std::endl;

    std::cout << "      CarMaker Tests passed!" << std::endl;

    std::cout << "  RoadObj Tests passed!" << std::endl;
}

/**
 * @brief Test function for the Sensor class
 */
void test_math_lib()
{
    MathLibrary::TargetCalculation testing_class;
    MathLibrary::LocationContour testing_locations;

    std::cout << "  Testing All 1objXloc .." << std::endl;

    int loc_count = 0;

    // Even Location Distribution
    std::cout << "    Testing Even Location Distribution .." << std::endl;
    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,7.0,-4.5,0,3.6,-4.5,0);
    testing_class.calculate_Locations(loc_count,0,0,6,0.3,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,testing_class.location_cloud[i].elevation_angle,i,0,"r");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,7.0,0,0,3.6,0,0);
    testing_class.calculate_Locations(loc_count,0,0,6,0.3,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,testing_class.location_cloud[i].elevation_angle,i,0,"r");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,7.0,4.5,3.141,3.6,4.5,3.141);
    testing_class.calculate_Locations(loc_count,0,0,6,0.3,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,testing_class.location_cloud[i].elevation_angle,i,0,"r");
    }
    
    // Crowded Middle Point (CMP) Location Distribution
    std::cout << "    Testing CMP Location Distribution .." << std::endl;
    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,17.0,-4.5,0,13.6,-4.5,0);
    testing_class.calculate_Locations(loc_count,1,0,6,0.3,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,testing_class.location_cloud[i].elevation_angle,i,0,"b");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,17.0,0,0,13.6,0,0);
    testing_class.calculate_Locations(loc_count,1,0,6,0.3,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,testing_class.location_cloud[i].elevation_angle,i,0,"b");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,17.0,4.5,3.141,13.6,4.5,3.141);
    testing_class.calculate_Locations(loc_count,1,0,6,0.3,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,testing_class.location_cloud[i].elevation_angle,i,0,"b");
    }

    // Statistical Model Location Distribution
    std::cout << "    Testing Statistical Location Distribution .." << std::endl;
    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,27.0,-4.5,0,23.6,-4.5,0);
    testing_class.calculate_Locations(loc_count,2,0,6,0.3,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,testing_class.location_cloud[i].elevation_angle,i,0,"g");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,27.0,0,0,23.6,0,0);
    testing_class.calculate_Locations(loc_count,2,0,6,0.3,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,testing_class.location_cloud[i].elevation_angle,i,0,"g");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,27.0,4.5,3.141,23.6,4.5,3.141);
    testing_class.calculate_Locations(loc_count,2,0,6,0.3,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,testing_class.location_cloud[i].elevation_angle,i,0,"g");
    }

    std::cout << "  All 1objXloc Tests passed!" << std::endl;
}

/**
 * @brief Main function to run all the test functions
 */
int main()
{
    std::cout << "Start Unit Tests .." << std::endl;

    test_sensor();
    test_radar();
    test_video();

    test_math_lib();
    std::string file_path = "data.txt";
    writePointsToFile(radial_distance, azimuth_angle, elevation_angle, Loc_ID, colors, file_path, three_dimensions);
    resetDataVariables();

    test_road_obj();
    file_path = "data_RoadObj.txt";
    writePointsToFile(radial_distance, azimuth_angle, elevation_angle, Loc_ID, colors, file_path, three_dimensions);
    resetDataVariables();

    std::cout << "All Unit Tests passed!" << std::endl;
}