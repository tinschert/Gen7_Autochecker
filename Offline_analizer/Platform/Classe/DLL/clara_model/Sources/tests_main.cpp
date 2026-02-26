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
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <chrono>
#include <map>

// Includes of files with functions to test
#include "claraSim/framework/numericLib.h"
#include "claraSim/framework/CFloatVector.h"
#include "claraSim/framework/CMessage.h"
#include "claraSim/world/vehicle/sensor/CRadar.h"
#include "clara_MathLibrary.hpp"


std::vector<double> radial_distance;
std::vector<double> azimuth_angle;
std::vector<int> Loc_ID;
std::vector<std::string> colors;
double sim_time_old_;

// these members are linked ot the radar sensor model and stimulated later with the input data from cloe side
CMessageInput<CFloatVectorXYZ> xyzWorld_;
CMessageInput<CFloatVectorXYZ> velocityXYZWorld_;
CMessageInput<CFloatVectorXYZ> accelerationXYZVehicleEgo_;
CMessageInput<CFloatVectorXYZ> angleRollPitchYawEgo_;
CMessageInput<CFloat> yawRateEgo_;
//TODO (matthias): define number of dynamic and static objects, currently set to 0
CObstacles obstacles_r_{12, 0U};
CMessageInput<CBool> staticSimulation_;

// radar model
CRadar radar_model_;

// math functions
MathLibrary::TargetCalculation calculation_class;
MathLibrary::CoordinateSystem contour_cs;

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
void initClara(int max_loc)
{
    std::cout << "  Initialize Clara Model .." << std::endl;
    
    // Initialize the Clara model by giving Clara references to where the data will be written in later cycles
    radar_model_.init(xyzWorld_,
                velocityXYZWorld_,
                accelerationXYZVehicleEgo_,
                angleRollPitchYawEgo_,
                yawRateEgo_,
                obstacles_r_,
                staticSimulation_);
    
    // TODO(matthias): check if more parameters need to be set, currently a lot of default values are taken
    radar_model_.p_sensorConfiguration.set(1);  // -1 means connector up

    // Set the mounting yaw angle of the sensor
    CFloatVectorXYZ rpy{0.0F, 0.0F, 0.0F};
    radar_model_.p_angleRollPitchYawVehicleMounting.set(rpy);

    // Set the mounting position of the sensor
    CFloatVectorXYZ mount_from_cog_clara{2.0, 0, 0};
    radar_model_.p_xyzVehicleMountingPos.set(mount_from_cog_clara);

    // Set parameters to steer the number of generated locations
    radar_model_.p_angleSeparationSensor.set(0.1 / 180.0F * M_PI);  // 7 degree is the default value provided by CLARA
    radar_model_.p_maxNumberOfReflectionsPerObstacles.set(max_loc);

    // Set some further parameters of the radar, values come from Cloe integration of the Clara model
    radar_model_.p_anglesFieldOfViewSegments.set(
        sim::to_radians({-90.0F, -45.0F, -10.0F, 10.0F, 45.0F, 90.0F}));
    radar_model_.p_maxRangesFieldOfViewSegments.set({510.0F, 510.0F, 510.0F, 510.0F, 510.0F});
    radar_model_.p_closeRange.set(0.0F); // 30.0F - 30 m is the default value provided by CLARA

    std::cout << "  Initialization complete." << std::endl;
}
void initEgo()
{
    std::cout << "  Initialize Ego Vehicle .." << std::endl;
    
    IMessageValue<CFloatVectorXYZ>* xyzWorld_comm = xyzWorld_.getLinkPointer();
    IMessageValue<CFloatVectorXYZ>* velocityXYZWorld_comm = velocityXYZWorld_.getLinkPointer();
    IMessageValue<CFloatVectorXYZ>* accelerationXYZVehicleEgo_comm =
        accelerationXYZVehicleEgo_.getLinkPointer();
    IMessageValue<CFloatVectorXYZ>* angleRollPitchYawEgo_comm =
        angleRollPitchYawEgo_.getLinkPointer();
    IMessageValue<CFloat>* yawRateEgo_comm = yawRateEgo_.getLinkPointer();

    // now from the link pointer we get a reference to the value itself so that we can write to it and stimulate it
    CFloatVectorXYZ& xyzWorld_ref = xyzWorld_comm->getValue();
    CFloatVectorXYZ& velocityXYZWorld_ref = velocityXYZWorld_comm->getValue();
    CFloatVectorXYZ& accelerationXYZVehicleEgo_ref = accelerationXYZVehicleEgo_comm->getValue();
    CFloatVectorXYZ& angleRollPitchYawEgo_ref = angleRollPitchYawEgo_comm->getValue();
    CFloat& yawRateEgo_ref = yawRateEgo_comm->getValue();

    // provide the ego distance in world frame
    xyzWorld_ref.X(0.0);
    xyzWorld_ref.Y(0.0);
    xyzWorld_ref.Z(0.0);
  
    // provide the ego velocity in world frame
    velocityXYZWorld_ref.X(0.0);
    velocityXYZWorld_ref.Y(0.0);
    velocityXYZWorld_ref.Z(0.0);

    // provide the ego acceleration in ego coordinate frame
    accelerationXYZVehicleEgo_ref.X(0.0);
    accelerationXYZVehicleEgo_ref.Y(0.0);
    accelerationXYZVehicleEgo_ref.Z(0.0);

    // provide the ego yaw pitch and roll in world frame
    angleRollPitchYawEgo_ref.X(0.0);
    angleRollPitchYawEgo_ref.Y(0.0);
    angleRollPitchYawEgo_ref.Z(0.0);

    // provide the ego yaw rate in world frame
    yawRateEgo_ref = 0.0;
    std::cout << "  Initialization complete." << std::endl;
}
void updateTgt(int target_id, int target_type, double target_dx, double target_dy, double target_dz, double target_vx, double target_vy, double target_vz,
                double target_acceleration, double target_yaw_angle, double target_length, double target_width, double target_height)
{
    std::cout << "  Update Target Vehicle .." << std::endl;
    
    // Clara expects target data to be from ego cog to tgt cog
    // Here we are referring to the link pointer of our intern members. Unfortunately, there does not seem to be a simpler option.
    // These members were linked in the radar_model_.init() as references to the radar model.
    // The link pointer receives the communication pointer of the respective wrapper class.
    // later in the call of the radar_model_.process() method clara will write the communication pointer value to the work value
    IMessageValue<CFloatVectorXYZ>* dyn_xyzWorld =
        obstacles_r_.ObstacleDynamic.at(target_id).o_xyzWorld.getLinkPointer();
    IMessageValue<CFloatVectorXYZ>* dyn_vWorld =
        obstacles_r_.ObstacleDynamic.at(target_id).o_vWorld.getLinkPointer();
    IMessageValue<CFloat>* dyn_acc_object_frame =
        obstacles_r_.ObstacleDynamic.at(target_id).o_acceleration.getLinkPointer();
    IMessageValue<CFloat>* dyn_yawAngleWorld =
        obstacles_r_.ObstacleDynamic.at(target_id).o_yawAngle.getLinkPointer();

    IMessageValue<CFloat>* dyn_pVisibility =
        obstacles_r_.ObstacleDynamic.at(target_id).p_visibility.getLinkPointer();
    IMessageValue<CInt>* dyn_pType = 
        obstacles_r_.ObstacleDynamic.at(target_id).p_type.getLinkPointer();
    IMessageValue<CFloat>* dyn_depth =
        obstacles_r_.ObstacleDynamic.at(target_id).p_depth.getLinkPointer();
    IMessageValue<CFloat>* dyn_height =
        obstacles_r_.ObstacleDynamic.at(target_id).p_height.getLinkPointer();
    IMessageValue<CFloat>* dyn_width =
        obstacles_r_.ObstacleDynamic.at(target_id).p_width.getLinkPointer();

    IMessageValue<CFloatVector>* dyn_xWorldContour =
        obstacles_r_.ObstacleDynamic.at(target_id).o_xWorldContour.getLinkPointer();
    IMessageValue<CFloatVector>* dyn_yWorldContour =
        obstacles_r_.ObstacleDynamic.at(target_id).o_yWorldContour.getLinkPointer();
    IMessageValue<CFloatVector>* dyn_zWorldContour =
        obstacles_r_.ObstacleDynamic.at(target_id).o_zWorldContour.getLinkPointer();

    // now from the link pointer we get a reference to the value itself so that we can write to it and stimulate it
    CFloatVectorXYZ& dyn_xyzWorld_ref = dyn_xyzWorld->getValue();
    CFloatVectorXYZ& dyn_vWorld_ref = dyn_vWorld->getValue();
    CFloat& dyn_acc_object_frame_ref = dyn_acc_object_frame->getValue();
    CFloat& dyn_yawAngleWorld_ref = dyn_yawAngleWorld->getValue();

    CFloat& dyn_pVisibility_ref = dyn_pVisibility->getValue();
    CInt& dyn_pType_ref = dyn_pType->getValue();
    CFloat& dyn_depth_ref = dyn_depth->getValue();
    CFloat& dyn_height_ref = dyn_height->getValue();
    CFloat& dyn_width_ref = dyn_width->getValue();
    CFloatVector& dyn_xWorldContour_ref = dyn_xWorldContour->getValue();
    CFloatVector& dyn_yWorldContour_ref = dyn_yWorldContour->getValue();
    CFloatVector& dyn_zWorldContour_ref = dyn_zWorldContour->getValue();

    // provide the target distance in world frame
    dyn_xyzWorld_ref.X(target_dx);
    dyn_xyzWorld_ref.Y(target_dy);
    dyn_xyzWorld_ref.Z(target_dz);
  
    // provide the target velocity in world frame
    dyn_vWorld_ref.X(target_vx);
    dyn_vWorld_ref.Y(target_vy);
    dyn_vWorld_ref.Z(target_vz);

    // provide the target acceleration in target coordinate frame
    dyn_acc_object_frame_ref = target_acceleration;

    // provide the target yaw pitch and roll in world frame
    dyn_yawAngleWorld_ref = target_yaw_angle;

    // set the visibility, type, depth, height and width of the object.
    dyn_pVisibility_ref = 1.0;  // existence probability always set to 100%
    dyn_pType_ref = calculation_class.map_type(target_type);
    dyn_depth_ref = target_length;
    dyn_height_ref = target_width;
    dyn_width_ref = target_height;

    // provide contour (edges) points P1 to P4
    // @verbatim
    //       LF           RF
    //         ____________
    //        |\          .\
    //   P4-->| \         .<--P3
    //        |. \ . . . ..  \
    //        \   \           \
    //   depth \   \___________\
    //          \  |   o       | height
    //        P1-->|           |<--P2
    //            \|___________|
    //                 width
    //            LR           RR
    calculation_class.calculate_contour(target_height,target_width,target_length,target_dx,target_dy,target_yaw_angle);
    contour_cs = calculation_class.get_CS();

    /// provide contour points to clara
    dyn_xWorldContour_ref[0] = contour_cs.dx_rear_left;
    dyn_xWorldContour_ref[1] = contour_cs.dx_rear_right;
    dyn_xWorldContour_ref[2] = contour_cs.dx_front_right;
    dyn_xWorldContour_ref[3] = contour_cs.dx_front_left;

    dyn_yWorldContour_ref[0] = contour_cs.dy_rear_left;
    dyn_yWorldContour_ref[1] = contour_cs.dy_rear_right;
    dyn_yWorldContour_ref[2] = contour_cs.dy_front_right;
    dyn_yWorldContour_ref[3] = contour_cs.dy_front_left;

    dyn_zWorldContour_ref[0] = target_height/2;
    dyn_zWorldContour_ref[1] = target_height/2;
    dyn_zWorldContour_ref[2] = target_height/2;
    dyn_zWorldContour_ref[3] = target_height/2;

    std::cout << "  Update complete." << std::endl;
}
int getNextValidLoc(int previous_loc_nr)
{
    int numlocs = (int) radar_model_.o_xRadarLocation.get().size();
    int buffer = 0;

    // We expect on CANoe side that the initial request has the ID -1
    // In this case we switch the buffer to 0 to fulfill idx != previous_loc_nr later on
    if(previous_loc_nr == -1)
    {
        buffer = 0;
    }
    else
    {
        buffer = previous_loc_nr;
    }

    // loop through locations to find NEXT valid location
    for (int idx = buffer; idx < numlocs; idx++) {
        // do not consider a location if visibility is set to very small value and only take next id
        if (radar_model_.o_visibilityLocation.get()[idx] > 0.001 && idx != previous_loc_nr) {
            return idx;
        }
    }
    return -1;
}
/**
 * @brief Test function for the Sensor class
 */
void test_math_lib()
{
    int loc_count = 10;

    initClara(loc_count);
    initEgo();
    //updateTgt( target_id,  target_type,  target_dx,  target_dy,  target_dz,  target_vx,  target_vy,  target_vz,  target_acceleration,  target_yaw_angle,  target_length,  target_width,  target_height)
    updateTgt(0, 6, 20.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0, 4.0, 2.0, 1.5);
    updateTgt(1, 6, 20.0, -4.5, 0.0, 3.0, 0.0, 0.0, 0.0, 0, 4.0, 2.0, 1.5);
    updateTgt(2, 6, 20.0, 4.5, 0.0, 3.0, 0.0, 0.0, 0.0, 3.141, 4.0, 2.0, 1.5);

    std::cout << "  Running Clara Model .." << std::endl;

    /// the sim time delta
    sim_time_old_ = 500000;
    const auto sim_time_now = std::chrono::system_clock::now().time_since_epoch();
    const auto sim_time_now_seconds = 
        static_cast<double>(std::chrono::duration_cast< std::chrono::nanoseconds >(sim_time_now).count());
    const auto sim_time_delta = sim_time_now_seconds - sim_time_old_;
    sim_time_old_ = sim_time_now_seconds;

    // at least one object detected, set
    // copies values from com pointer to work value inside "i_ signals" from CRadar and CSensor
    // we need to set this extern trigger, otherwise the clara does not calculate any locations
    radar_model_.setExternTrigger();

    // the process method copies the communication values to the work values for input signals,
    // and copies the work values to communication values for the out signals
    radar_model_.process(sim_time_delta, sim_time_now_seconds);

    std::cout << "  Reading Clara Model .." << std::endl;

    double radial_distance = 0.0;
    double azimuth_angle = 0.0;
    int numlocs = (int) radar_model_.o_xRadarLocation.get().size();
    int buffer = 0;
    int generated_loc = 0;
    int loc_id = 0;

    loc_id = getNextValidLoc(-1);

    while (loc_id >= 0)
    {
        radial_distance = std::sqrt(std::pow(radar_model_.o_xRadarLocation.get()[loc_id], 2) +
                                         std::pow(radar_model_.o_yRadarLocation.get()[loc_id], 2) +
                                         std::pow(radar_model_.o_zRadarLocation.get()[loc_id], 2));
                                         
        azimuth_angle = radar_model_.o_alphaRadarLocation.get()[loc_id];

        writeDataToGlobals(radial_distance,azimuth_angle,generated_loc,"b");
        generated_loc++;

        loc_id = getNextValidLoc(loc_id);
    }

    std::cout << "      Number of generated locations: " << generated_loc << std::endl;
    std::cout << "  Clara Model Tests passed!" << std::endl;
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