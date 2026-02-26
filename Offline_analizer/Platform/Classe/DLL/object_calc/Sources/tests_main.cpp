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

std::vector<double> radial_distance;
std::vector<double> azimuth_angle;
std::vector<int> Loc_ID;
std::vector<std::string> colors;

// Includes of files with functions to test
#include "MathLibrary.hpp"

/**
 *  @brief Customized assert function
 */
#ifndef NDEBUG
#   define M_Assert(Expr, Msg) \
    __M_Assert(#Expr, Expr, __FILE__, __LINE__, Msg)
#else
#   define M_Assert(Expr, Msg) ;
#endif

void writeDataToGlobals(double radialDist, double azimuthAngle, int ID, const std::string& color) {
    radial_distance.push_back(radialDist);
    azimuth_angle.push_back(azimuthAngle);
    Loc_ID.push_back(ID);
    colors.push_back(color);
}
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

void writePointsToFile(const std::vector<double>& radial_distance, const std::vector<double>& azimuth_angle, const std::vector<int>& Loc_ID, const std::vector<std::string>& colors, const std::string& file_path) {
    std::ofstream file(file_path);
    if (file.is_open()) {
        for (size_t i = 0; i < radial_distance.size(); i++) {
            file << radial_distance[i] << "," << azimuth_angle[i] << "," << Loc_ID[i] << "," << colors[i] << std::endl;
        }
        file.close();
        std::cout << "Die Punkte wurden erfolgreich in die Datei geschrieben." << std::endl;
    } else {
        std::cerr << "Fehler beim Öffnen der Datei." << std::endl;
    }
}

/**
 * @brief Test function for the Sensor class
 */
void test_math_lib()
{
    MathLibrary::TargetCalculation testing_class;
    MathLibrary::LocationContour testing_locations;

    std::cout << "  Testing MathLibrary .." << std::endl;

    int loc_count = 0;
    // Setting sensor values
    //loc_count = 10;
    //testing_class.calculate_ref_point(1.5,2.0,4.0,15.0,0.0,0.785,16.8,0.0,0.785);
    //testing_class.calculate_Locations(loc_count,1.5,10.0,10.0);
    //testing_locations = testing_class.get_location_contour();
    //M_Assert(testing_locations.total_loc_count == 0, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
       //writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i);
    }

    //loc_count = 10;
    //testing_class.calculate_ref_point(1.5,2.0,4.0,5.0,0.0,-0.785,6.8,0.0,-0.785);
    //testing_class.calculate_Locations(loc_count,1.5,10.0,10.0);

    for(int i = 0; i < loc_count; i++)
    {
        //writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i);
    }

    // Even Location Distribution
    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,7.0,-4.5,0,3.6,-4.5,0);
    testing_class.calculate_Locations(loc_count,0,6,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i,"r");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,7.0,0,0,3.6,0,0);
    testing_class.calculate_Locations(loc_count,0,6,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i,"r");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,7.0,4.5,3.141,3.6,4.5,3.141);
    testing_class.calculate_Locations(loc_count,0,6,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i,"r");
    }
    
    // Crowded Middle Point (CMP) Location Distribution
    for(int i = 0; i < loc_count; i++)
    {
        //writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i);
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,17.0,-4.5,0,13.6,-4.5,0);
    testing_class.calculate_Locations(loc_count,1,6,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i,"b");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,17.0,0,0,13.6,0,0);
    testing_class.calculate_Locations(loc_count,1,6,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i,"b");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,17.0,4.5,3.141,13.6,4.5,3.141);
    testing_class.calculate_Locations(loc_count,1,6,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i,"b");
    }

    // Statistical Model Location Distribution
    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,27.0,-4.5,0,23.6,-4.5,0);
    testing_class.calculate_Locations(loc_count,2,6,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i,"g");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,27.0,0,0,23.6,0,0);
    testing_class.calculate_Locations(loc_count,2,6,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i,"g");
    }

    loc_count = 12;
    testing_class.calculate_ref_point(1.5,1.82,4.740,27.0,4.5,3.141,23.6,4.5,3.141);
    testing_class.calculate_Locations(loc_count,2,6,1.5,10.0,10.0);
    testing_locations = testing_class.get_location_contour();
    M_Assert(testing_locations.total_loc_count == loc_count, "Number of calculated locations doesnt fit the request");

    for(int i = 0; i < loc_count; i++)
    {
        writeDataToGlobals(testing_class.location_cloud[i].radial_distance,testing_class.location_cloud[i].azimuth_angle,i,"g");
    }

    std::cout << "  MathLibrary Tests passed!" << std::endl;
}

/**
 * @brief Main function to run all the test functions
 */
int main()
{
    std::cout << "Start Unit Tests .." << std::endl;

    test_math_lib();

    std::cout << "All Unit Tests passed!" << std::endl;
    
    //std::vector<double> radial_distance = {10, 20, 30, 40, 50};
    // = {45, 90, 135, 180, 225};
    std::string file_path = "data.txt";
    writePointsToFile(radial_distance, azimuth_angle, Loc_ID, colors, file_path);

    return 0;
}