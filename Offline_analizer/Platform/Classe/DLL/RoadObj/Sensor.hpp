/**
 * @file        RoadObj.hpp
 * @copyright   2023 Robert Bosch GmbH
 * @author      Robin Walter <robin.walter@de.bosch.com>
 * @date        12.03.2024
 * @brief       Defines structures and classes for multiple sensor types
 */

#ifndef SENSOR_HPP
#define SENSOR_HPP

#include <stdint.h>

const int maximum_location_quantity = 1056;
const int maximum_object_quantity = 40;

/**
 * @brief Contains the data needed as inputs for further object/location calculations
*/
struct Sensor_Definitions
{
  /// @brief Mounting position of the sensor in longitudinal direction in reference to the rear center axle
  double i_mount_pos_x;
  /// @brief Mounting position of the sensor in lateral direction in reference to the rear center axle
  double i_mount_pos_y;
  /// @brief Mounting position of the sensor in vertical direction in reference to the rear center axle
  double i_mount_pos_z;
  /// @brief Mounting position yaw angle of the sensor in x-y-plane in reference to the rear center axle coordinate system
  double i_mount_pos_yaw;
  /// @brief Maximum Field of View Angle
  double i_fov;
  /// @brief Classe_Obj_Sim::ValidityFlags.validity_radar_fc_obj_on - Flag indicating if validity sending is active
  int i_validity_sending_flag;
  /// @brief hil_ctrl::radar_xx_obj_sim - Flag to activate calculations of object data for this sensor
  int i_sensor_sim_on;
  /// @brief Number of valid objects
  int o_valid_obj_count;
};

/**
 * @brief Contains the data needed as inputs for further object/location calculations
*/
struct Input_Object
{
  /// @brief @Classe_Obj_Sim::objdata.obj_sim_radar_xx_on - Flag indicating if the object is being simulated by this sensor and hence needs to be calculated - needed for Classe usecase only
  int i_obj_sim_on;
  /// @brief Sensor movement mode in which the object has been detected (0 = driving, 1 = parking)
  int i_obj_sensor_mode;
  /// @brief Object distance in longitudinal direction (in m)
  double i_distance_x;
  /// @brief Object distance in lateral direction (in m)
  double i_distance_y;
  /// @brief Object velocity in longitudinal direction (in m/s)
  double i_velocity_x;
  /// @brief Object velocity in lateral direction (in m/s)
  double i_velocity_y;
  /// @brief Object acceleration in longitudinal direction (in m/s2)
  double i_acceleration_x;
  /// @brief Object acceleration in lateral direction (in m/s2)
  double i_acceleration_y;
  /// @brief Object heading angle (in rad)
  double i_yaw_angle;
  /// @brief Object dimensions (in m)
  double i_width, i_length, i_height;
  /// @brief Type of the object
  int i_type;
  /// @brief Radar Cross Section (RCS) of the object. Radar specific.
  double i_radar_cross_section;
  /// @brief Signal Strength of the radar signal. Radar specific.
  double i_signal_strength;
  /// @brief Signal to noise ratio of the radar signal. Radar specific.
  double i_signal_noise_ratio;
  /// @brief Object distance in longitudinal direction (in m) from Sensors perspective used for fov calculation
  double fov_distance_x;
  /// @brief Object distance in lateral direction (in m) from Sensors perspective used for fov calculation
  double fov_distance_y;
  /// @brief Flag to indicate if the object is a valid object
  int o_validity_flag;
  /// @brief Flag to indicate if the object is an empty object
  int o_empty_flag;

};

/**
 *  @brief Struct for rotating basic data to different coordinate systems
 */
struct RotationSystem
{
  /// @brief Distance in longitudinal/lateral/vertical direction
  double dx, dy, dz;
  /// @brief Velocity in longitudinal/lateral direction
  double vx, vy;
  /// @brief Heading angle in x-y-plane
  double heading;
};

class Sensor {
 public:
  Sensor() {
    Sensor_Def.i_mount_pos_x = 0.0;
    Sensor_Def.i_mount_pos_y = 0.0;
    Sensor_Def.i_mount_pos_z = 0.0;
    Sensor_Def.i_mount_pos_yaw = 0.0;
    Sensor_Def.i_fov = 0.0;
    Sensor_Def.i_validity_sending_flag = 0;
    Sensor_Def.i_sensor_sim_on = 0;
    Sensor_Def.o_valid_obj_count = 0;
    
    RCA_RS.dx = 0.0;
    RCA_RS.dy = 0.0;
    RCA_RS.dz = 0.0;
    RCA_RS.vx = 0.0;
    RCA_RS.vy = 0.0;
    RCA_RS.heading = 0.0;
    
    Sensor_RS.dx = 0.0;
    Sensor_RS.dy = 0.0;
    Sensor_RS.dz = 0.0;
    Sensor_RS.vx = 0.0;
    Sensor_RS.vy = 0.0;
    Sensor_RS.heading = 0.0;
    
    CoG_RS.dx = 0.0;
    CoG_RS.dy = 0.0;
    CoG_RS.dz = 0.0;
    CoG_RS.vx = 0.0;
    CoG_RS.vy = 0.0;
    CoG_RS.heading = 0.0;

    for(int i = 0; i < maximum_object_quantity; i++)
    {
      Input_Obj[i].i_obj_sim_on = 0;
      Input_Obj[i].i_obj_sensor_mode = 0;
      Input_Obj[i].i_distance_x = 0.0;
      Input_Obj[i].i_distance_y = 0.0;
      Input_Obj[i].i_velocity_x = 0.0;
      Input_Obj[i].i_velocity_y = 0.0;
      Input_Obj[i].i_acceleration_x = 0.0;
      Input_Obj[i].i_acceleration_y = 0.0;
      Input_Obj[i].i_yaw_angle = 0.0;
      Input_Obj[i].i_width = 0.0;
      Input_Obj[i].i_length = 0.0;
      Input_Obj[i].i_height = 0.0;
      Input_Obj[i].i_type = 0;
      Input_Obj[i].i_radar_cross_section = 0.0;
      Input_Obj[i].i_signal_strength = 0.0;
      Input_Obj[i].i_signal_noise_ratio = 0.0;
      Input_Obj[i].fov_distance_x = 0.0;
      Input_Obj[i].fov_distance_y = 0.0;
      Input_Obj[i].o_validity_flag = 0;
      Input_Obj[i].o_empty_flag = 0;
    }

    for(int i = 0; i < 71896; i++) //maximum length for Conti byte array
    {
      byte_array_loc[i] = 0;
    }

    for(int i = 0; i < 25728; i++)
    {
      byte_array_obj[i] = 0;
    }
  }
  
  /// @brief Basic object data shifted to Rear Center Axle coordinate system
  RotationSystem RCA_RS;
  /// @brief Basic object data shifted to Sensor coordinate system
  RotationSystem Sensor_RS;
  /// @brief Basic object data shifted to Center of Gravity coordinate system
  RotationSystem CoG_RS;
  /// @brief Byte array used for LGU RBS sending, set the length to the theoritical maximum (Conti with 68bytes for 1056 locs + 4 length field + 84bytes header padding : 71896)
  uint8_t byte_array_loc[71896];
  /// @brief Byte array used for SGU RBS sending, set the length to the theoritical maximum (kBufferSizeJumbo definition 3216 bytes, with 64 bytes per object : 25728)
  uint8_t byte_array_obj[25728];

  /**
   * @brief Calculates validity and empty obj flags using object data from sensors perspective as input
   * @param simulator Chosen simulator (Classe, CarMaker)
   * @param obj_id ID of the object for which the validity flag should be calculated
   * @param dx_sensor Distance in longitudinal direction from the sensors perspective
   * @param dy_sensor Distance in lateral direction from the sensors perspective
  */
  void calculate_validity_flag(int,int,double,double);

  /**
   * @brief Sets the superior sensor values
   * @param mount_dx Mounting position of the sensor in longitudinal direction in reference to the RCA
   * @param mount_dy Mounting position of the sensor in lateral direction in reference to the RCA
   * @param mount_dz Mounting position of the sensor in vertical direction in reference to the RCA
   * @param mount_yaw Mounting position yaw angle of the sensor in x-y-plane in reference to the rear center axle coordinate system
   * @param fov_angle Field of view angle of the sensor in radians 
   * @param validity_sending_active Flag to activate the validity sending. Used to set validity flags on the objects.
   * @param sensor_sim_active Flag to indicate that this sensor is currently being simulated and therefor calculations have to be run.
   * @param obj_count Number of valid objects (only used as input for CarMaker usecase, 0 for Classe)
  */
  void set_sensor_values(double,double,double,double,double,int,int,int);
  /**
   * @brief Reads the given inputs and stores them in the input object with the given ID
   * @param obj_id ID of the given object
   * @param obj_sim_on Classe_Obj_Sim::objdata.obj_sim_radar_xx_on - Flag indicating if the object is being simulated by this sensor and hence needs to be calculated - needed for Classe usecase only
   * @param obj_sensor_mode Sensor mode in which the object has been detected (0 = driving, 1 = parking)
   * @param dx Object distance in longitudinal direction (in m)
   * @param dy Object distance in lateral direction (in m)
   * @param vx Object velocity in longitudinal direction (in m/s)
   * @param vy Object velocity in lateral direction (in m/s)
   * @param ax Object acceleration in longitudinal direction (in m/s2)
   * @param ay Object acceleration in lateral direction (in m/s2)
   * @param yaw_angle Object heading angle (in rad)
   * @param width Object width (in m)
   * @param length Object length (in m)
   * @param height Object height (in m)
   * @param type Type of the object
   * @param rcs Radar Cross Section of the object
   * @param snr Signal to Noise Ratio of the radar signal
   * @param signal_strength Signal Strength of the radar signal
  */
  void set_object_values(int,int,int,double,double,double,double,double,double,double,double,double,double,int,double,double,double);

  /// @return Returns the mounting position of the sensor in longitudinal direction
  double get_sensor_mount_pos_x();
  /// @return Returns the mounting position of the sensor in lateral direction
  double get_sensor_mount_pos_y();
  /// @return Returns the mounting position of the sensor in vertical direction
  double get_sensor_mount_pos_z();
  /// @return Returns the mounting position of the sensor in vertical direction
  double get_sensor_mount_pos_yaw();
  /// @return Returns the maximum field of view
  double get_sensor_fov();
  /// @return Returns the flag indicating if validity sending is active
  int get_sensor_validity_sending_flag();
  /// @return Returns the flag to indicating that this sensor is being simulated and therefor activate calculations for this sensor
  int get_sensor_sim_on();
  /// @return Returns the number of calculated valid objects
  int get_sensor_valid_obj_count();
  /// @brief Sets the number of valid objects for this sensor
  void set_sensor_valid_obj_count(int);

  /// @brief Returns the flag indicating if the object is being simulated by this sensor and hence needs to be calculated - needed for Classe usecase only
  int get_in_obj_sim_on(int);
  /// @brief Returns the sensor mode in which the object has been detected (0 = driving, 1 = parking)
  int get_in_obj_sensor_mode(int);
  /// @brief Returns the object distance in longitudinal direction (in m)
  double get_in_obj_distance_x(int);
  /// @brief Returns the object distance in lateral direction (in m)
  double get_in_obj_distance_y(int);
  /// @brief Returns the object velocity in longitudinal direction (in m/s)
  double get_in_obj_velocity_x(int);
  /// @brief Returns the object velocity in lateral direction (in m/s)
  double get_in_obj_velocity_y(int);
  /// @brief Returns the object acceleration in longitudinal direction (in m/s2)
  double get_in_obj_acceleration_x(int);
  /// @brief Returns the object acceleration in lateral direction (in m/s2)
  double get_in_obj_acceleration_y(int);
  /// @brief Returns the object heading angle (in rad)
  double get_in_obj_yaw_angle(int);
  /// @brief Returns the object dimensions (in m)
  double get_in_obj_width(int); 
  /// @brief Returns the object dimensions (in m)
  double get_in_obj_length(int); 
  /// @brief Returns the object dimensions (in m)
  double get_in_obj_height(int);
  /// @brief Returns the type of the object
  int get_in_obj_type(int);
  /// @brief Returns the radar cross section of the object
  double get_in_obj_rcs(int);
  /// @brief Returns the signal to noise ratio of the radar signal
  double get_in_obj_snr(int);
  /// @brief Returns the signal strength of the radar signal
  double get_in_obj_signal_strength(int);
  /// @brief Returns the object distance in longitudinal direction (in m) from Sensors perspective used for fov calculation
  double get_in_obj_fov_distance_x(int);
  /// @brief Returns the object distance in lateral direction (in m) from Sensors perspective used for fov calculation
  double get_in_obj_fov_distance_y(int);
  /// @brief Returns the flag to indicate if the object is a valid object
  int get_in_obj_validity_flag(int);
  /// @brief Returns the flag to indicate if the object is an empty object
  int get_in_obj_empty_flag(int);

  /// @return Returns the sensor definitions struct
  Sensor_Definitions get_sensor_def();
  /// @return Returns the input object struct of the given object ID
  Input_Object get_input_obj(int);

 protected:
  /// @brief Values defining the sensor
  Sensor_Definitions Sensor_Def;
  /// @brief Array of object structure containing the data needed as inputs for further object/location calculations
  Input_Object Input_Obj[maximum_object_quantity];
};

#endif // SENSOR_HPP