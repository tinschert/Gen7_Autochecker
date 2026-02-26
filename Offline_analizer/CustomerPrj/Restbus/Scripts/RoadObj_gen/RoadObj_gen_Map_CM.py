# -*- coding: utf-8 -*-
# @file RoadObj_gen_Map_CM.py
# @author ADAS_HIL_TEAM
# @date 03-07-2023

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


# pre-defined headers
script_list = ""

Header = '''/*@!Encoding:1252*/
/**
 * @file Map_CM.cin
 * @author ADAS_HIL_TEAM
 * @date 03-21-2023
 * @brief Handles mapping for CM usecase for all sensors
 * 
 * ##################################################################
 * C O P Y R I G H T S
 * ----------------------------------------------------------------
 * Copyright (c) 2023 by Robert Bosch GmbH. All rights reserved.
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 * 
 * ##################################################################
 */

includes
{
}

variables
{
  int counter_CM = 0;
  int target_count_CM = 0;
  
  long obj_type_cm2classe[10] = {
    0, // 0 unknown
    4, // 1 Pedestrian
    3, // 2 Bike
    3, // 3 Motorbike
    6, // 4 Passanger car
    5, // 5 Truck
    0, // 6 Trailer
    0, // 7 reserved
    0, // 8 reserved
    0  // 9 reserved
  };
  
  // Star Model
  int loc_count_RFC_CM = 0;
  int loc_count_RFL_CM = 0;
  int loc_count_RFR_CM = 0;
  int loc_count_RRL_CM = 0;
  int loc_count_RRR_CM = 0;
  
  int number_of_locs_RFC_CM = 0;
  int number_of_locs_RFL_CM = 0;
  int number_of_locs_RFR_CM = 0;
  int number_of_locs_RRL_CM = 0;
  int number_of_locs_RRR_CM = 0;
  
  int total_number_of_locations_RFC_CM = 0;
  int total_number_of_locations_RFL_CM = 0;
  int total_number_of_locations_RFR_CM = 0;
  int total_number_of_locations_RRL_CM = 0;
  int total_number_of_locations_RRR_CM = 0;
  
  // Clara Model
  int clara_run_fc_CM = 0;
  int clara_run_fl_CM = 0;
  int clara_run_fr_CM = 0;
  int clara_run_rl_CM = 0;
  int clara_run_rr_CM = 0;
  
  int clara_radar_fc_deletion_needed_CM[20];
  int clara_radar_fl_deletion_needed_CM[20];
  int clara_radar_fr_deletion_needed_CM[20];
  int clara_radar_rl_deletion_needed_CM[20];
  int clara_radar_rr_deletion_needed_CM[20];
  
}
'''

def update_CM_reading(num_objects):
    """
    Description: Updates the reading function with reads the raw target data of the CarMaker simulator and stores it into the target array of each sensor.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    script_list.append('/** @brief Reading CM values, CarMaker is sending the distance in reference to the sensor position and reference point on the target is ALWAYS the rear bumper.')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void read_CM_data(){')
    
    script_list.append('  /**')
    script_list.append('    * Radar FC')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_distance_x_previous[{obj_id}] = @target_radar_fc_sim::objdata.obj_distance_x[{obj_id}];')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_distance_x[{obj_id}] = @CarMaker::RB::Radar::FC::object{obj_id}::dxN;')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_distance_y[{obj_id}] = @CarMaker::RB::Radar::FC::object{obj_id}::dyN;')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_velocity_x[{obj_id}] = @CarMaker::RB::Radar::FC::object{obj_id}::vxN;')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_velocity_y[{obj_id}] = @CarMaker::RB::Radar::FC::object{obj_id}::vyN;')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_heading_angle[{obj_id}] = @CarMaker::RB::Radar::FC::object{obj_id}::alpPiYawAngleN;')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_type[{obj_id}] = obj_type_cm2classe[@CarMaker::RB::Radar::FC::object{obj_id}::classification];')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_width[{obj_id}] = @CarMaker::RB::Radar::FC::object{obj_id}::dWidthN;')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_length[{obj_id}] = @CarMaker::RB::Radar::FC::object{obj_id}::dLengthN;')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append('  ')
        
    script_list.append('  /**')
    script_list.append('    * Front Video')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_fvideo_sim::objdata.obj_distance_x_previous[{obj_id}] = @target_fvideo_sim::objdata.obj_distance_x[{obj_id}];')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_distance_x[{obj_id}] = @CarMaker::RB::Video::FV::object{obj_id}::dxN;')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_distance_y[{obj_id}] = @CarMaker::RB::Video::FV::object{obj_id}::dyN;')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_velocity_x[{obj_id}] = @CarMaker::RB::Video::FV::object{obj_id}::vxN;')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_velocity_y[{obj_id}] = @CarMaker::RB::Video::FV::object{obj_id}::vyN;')
        script_list.append(f'//  @target_fvideo_sim::objdata.obj_acceleration_x[{obj_id}] = ;')
        script_list.append(f'//  @target_fvideo_sim::objdata.obj_acceleration_y[{obj_id}] = ;')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_heading_angle[{obj_id}] = @CarMaker::RB::Video::FV::object{obj_id}::alpPiYawAngleN;')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_type[{obj_id}] = obj_type_cm2classe[@CarMaker::RB::Radar::FC::object{obj_id}::classification];')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_width[{obj_id}] = @CarMaker::RB::Video::FV::object{obj_id}::dWidthN;')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_length[{obj_id}] = @CarMaker::RB::Video::FV::object{obj_id}::dLengthN;')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append('  ')
        
    script_list.append('  /**')
    script_list.append('    * Radar Front Left')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_distance_x_previous[{obj_id}] = @target_radar_fl_sim::objdata.obj_distance_x[{obj_id}];')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_distance_x[{obj_id}] = @CarMaker::RB::Radar::FL::object{obj_id}::dxN;')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_distance_y[{obj_id}] = @CarMaker::RB::Radar::FL::object{obj_id}::dyN;')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_velocity_x[{obj_id}] = @CarMaker::RB::Radar::FL::object{obj_id}::vxN;')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_velocity_y[{obj_id}] = @CarMaker::RB::Radar::FL::object{obj_id}::vyN;')
        script_list.append(f'//  @target_radar_fl_sim::objdata.obj_acceleration_x[{obj_id}] = ;')
        script_list.append(f'//  @target_radar_fl_sim::objdata.obj_acceleration_y[{obj_id}] = ;')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_heading_angle[{obj_id}] = @CarMaker::RB::Radar::FL::object{obj_id}::alpPiYawAngleN;')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_type[{obj_id}] = obj_type_cm2classe[@CarMaker::RB::Radar::FL::object{obj_id}::classification];')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_width[{obj_id}] = @CarMaker::RB::Radar::FL::object{obj_id}::dWidthN;')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_length[{obj_id}] = @CarMaker::RB::Radar::FL::object{obj_id}::dLengthN;')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append('  ')
        
    script_list.append('  /**')
    script_list.append('    * Radar Front Right')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_distance_x_previous[{obj_id}] = @target_radar_fr_sim::objdata.obj_distance_x[{obj_id}];')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_distance_x[{obj_id}] = @CarMaker::RB::Radar::FR::object{obj_id}::dxN;')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_distance_y[{obj_id}] = @CarMaker::RB::Radar::FR::object{obj_id}::dyN;')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_velocity_x[{obj_id}] = @CarMaker::RB::Radar::FR::object{obj_id}::vxN;')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_velocity_y[{obj_id}] = @CarMaker::RB::Radar::FR::object{obj_id}::vyN;')
        script_list.append(f'//  @target_radar_fr_sim::objdata.obj_acceleration_x[{obj_id}] = ;')
        script_list.append(f'//  @target_radar_fr_sim::objdata.obj_acceleration_y[{obj_id}] = ;')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_heading_angle[{obj_id}] = @CarMaker::RB::Radar::FR::object{obj_id}::alpPiYawAngleN;')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_type[{obj_id}] = obj_type_cm2classe[@CarMaker::RB::Radar::FR::object{obj_id}::classification];')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_width[{obj_id}] = @CarMaker::RB::Radar::FR::object{obj_id}::dWidthN;')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_length[{obj_id}] = @CarMaker::RB::Radar::FR::object{obj_id}::dLengthN;')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append('  ')
        
    script_list.append('  /**')
    script_list.append('    * Radar Rear Left')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_distance_x_previous[{obj_id}] = @target_radar_rl_sim::objdata.obj_distance_x[{obj_id}];')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_distance_x[{obj_id}] = @CarMaker::RB::Radar::RL::object{obj_id}::dxN;')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_distance_y[{obj_id}] = @CarMaker::RB::Radar::RL::object{obj_id}::dyN;')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_velocity_x[{obj_id}] = @CarMaker::RB::Radar::RL::object{obj_id}::vxN;')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_velocity_y[{obj_id}] = @CarMaker::RB::Radar::RL::object{obj_id}::vyN;')
        script_list.append(f'//  @target_radar_rl_sim::objdata.obj_acceleration_x[{obj_id}] = ;')
        script_list.append(f'//  @target_radar_rl_sim::objdata.obj_acceleration_y[{obj_id}] = ;')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_heading_angle[{obj_id}] = @CarMaker::RB::Radar::RL::object{obj_id}::alpPiYawAngleN;')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_type[{obj_id}] = obj_type_cm2classe[@CarMaker::RB::Radar::RL::object{obj_id}::classification];')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_width[{obj_id}] = @CarMaker::RB::Radar::RL::object{obj_id}::dWidthN;')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_length[{obj_id}] = @CarMaker::RB::Radar::RL::object{obj_id}::dLengthN;')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append('  ')
        
    script_list.append('  /**')
    script_list.append('    * Radar Rear Right')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_distance_x_previous[{obj_id}] = @target_radar_rr_sim::objdata.obj_distance_x[{obj_id}];')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_distance_x[{obj_id}] = @CarMaker::RB::Radar::RR::object{obj_id}::dxN;')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_distance_y[{obj_id}] = @CarMaker::RB::Radar::RR::object{obj_id}::dyN;')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_velocity_x[{obj_id}] = @CarMaker::RB::Radar::RR::object{obj_id}::vxN;')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_velocity_y[{obj_id}] = @CarMaker::RB::Radar::RR::object{obj_id}::vyN;')
        script_list.append(f'//  @target_radar_rr_sim::objdata.obj_acceleration_x[{obj_id}] = ;')
        script_list.append(f'//  @target_radar_rr_sim::objdata.obj_acceleration_y[{obj_id}] = ;')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_heading_angle[{obj_id}] = @CarMaker::RB::Radar::RR::object{obj_id}::alpPiYawAngleN;')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_type[{obj_id}] = obj_type_cm2classe[@CarMaker::RB::Radar::RR::object{obj_id}::classification];')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_width[{obj_id}] = @CarMaker::RB::Radar::RR::object{obj_id}::dWidthN;')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_length[{obj_id}] = @CarMaker::RB::Radar::RR::object{obj_id}::dLengthN;')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append('  ')
    script_list.append('}')
    script_list.append('')

def update_CM_mapping():
    """
    Description: Updates the main function in the mapping file.

    Returns: Void

    """
    script_list.append('/** @brief Main function to read all necessary data and calculate valid targets.')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void map_cm(){')
    script_list.append('  //Only read data on the first object, to decrease load')
    script_list.append('  set_CM_offsets();')
    script_list.append('  read_CM_data();')
    script_list.append('  read_CM_traffic_obj_ctrl_data();')
    script_list.append('  calculcate_valid_CM_targets();')
    script_list.append('  ')
    script_list.append('  clara_run_fc_CM = 1;  // flag to run Clara model')
    script_list.append('}')
    script_list.append('')

def update_CM_offsets():
    """
    Description: Updates the function which sets the mounting positions for each sensor.

    Returns: Void

    """
    script_list.append('/** @brief Set offsets')
    script_list.append('  *            Distances from rear center axle (RCA) to sensor mounting position')
    script_list.append('  *            Only x and y coordinates are taken into account')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void set_CM_offsets()')
    script_list.append('{')
    script_list.append('  // Front Center Radar')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_x_fc = @radarfc_par::mounting_pos_x;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_y_fc = @radarfc_par::mounting_pos_y;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_z_fc = @radarfc_par::mounting_pos_z;')
    script_list.append('  // Front Video')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_x_fv = @fvideo_par::mounting_pos_x;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_y_fv = @fvideo_par::mounting_pos_y;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_z_fv = @fvideo_par::mounting_pos_z;')
    script_list.append('  // Front Left Radar')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_x_fl = @radarfl_par::mounting_pos_x;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_y_fl = @radarfl_par::mounting_pos_y;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_z_fl = @radarfl_par::mounting_pos_z;')
    script_list.append('  // Front Right Radar')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_x_fr = @radarfr_par::mounting_pos_x;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_y_fr = @radarfr_par::mounting_pos_y;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_z_fr = @radarfr_par::mounting_pos_z;')
    script_list.append('  // Rear Left Radar')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_x_rl = @radarrl_par::mounting_pos_x;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_y_rl = @radarrl_par::mounting_pos_y;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_z_rl = @radarrl_par::mounting_pos_z;')
    script_list.append('  // Rear Right Radar')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_x_rr = @radarrr_par::mounting_pos_x;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_y_rr = @radarrr_par::mounting_pos_y;')
    script_list.append('  @Classe_Obj_Sim::RoadObj.offset_z_rr = @radarrr_par::mounting_pos_z;')
    script_list.append('}')
    script_list.append('')

def calculate_valid_CM_targets(num_objects):
    """
    Description: Updates the function for defining which targets are valid and setting of the validity flags accordingly.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    script_list.append('/** @brief Calculation of number of detected VALID targets for all the sensors and setting of validity and empty obj flags accordingly.')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void calculcate_valid_CM_targets(){')
    script_list.append('  //Radar Front Center')
    script_list.append('  @target_radar_fc_sim::objdata.number_of_obj = @CarMaker::RB::Radar::FC::object_count;')
    script_list.append('  for (counter_CM = 0; counter_CM < 9; counter_CM++)')
    script_list.append('  {')
    script_list.append('    if(counter_CM < @target_radar_fc_sim::objdata.number_of_obj)')
    script_list.append('    { //valid target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_FC[counter_CM] = 1;')
    script_list.append('      @target_radar_fc_sim::objdata.empty_obj[counter_CM] = 0;')
    script_list.append('    }')
    script_list.append('    else if(@Classe_Obj_Sim::ValidityFlags.validity_radar_fc_loc_on == 0 && @Classe_Obj_Sim::ValidityFlags.validity_radar_fc_obj_on == 0)')
    script_list.append('    { //only valid target sending off -> dummy target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_FC[counter_CM] = 1;')
    script_list.append('      @target_radar_fc_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('    else')
    script_list.append('    { //only valid target sending on -> empty target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_FC[counter_CM] = 0;')
    script_list.append('      @target_radar_fc_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  if(@hil_ctrl::radar_fc_loc_sim > 0)')
    script_list.append('  { //location based')
    script_list.append('    @target_radar_fc_sim::locdata.number_of_loc = 0;')
    script_list.append('    total_number_of_locations_RFC_CM = 0;')
    script_list.append('  }')
    script_list.append('  ')
    
    script_list.append('  //Front Video')
    script_list.append('  @target_fvideo_sim::objdata.number_of_obj = @CarMaker::RB::Radar::FC::object_count;')
    script_list.append('  for (counter_CM = 0; counter_CM < 9; counter_CM++)')
    script_list.append('  {')
    script_list.append('    if(counter_CM < @target_fvideo_sim::objdata.number_of_obj)')
    script_list.append('    { //valid target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_FV[counter_CM] = 1;')
    script_list.append('      @target_fvideo_sim::objdata.empty_obj[counter_CM] = 0;')
    script_list.append('    }')
    script_list.append('    else if(@Classe_Obj_Sim::ValidityFlags.validity_fvideo_on == 0)')
    script_list.append('    { //only valid target sending off -> dummy target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_FV[counter_CM] = 1;')
    script_list.append('      @target_fvideo_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('    else')
    script_list.append('    { //only valid target sending on -> empty target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_FV[counter_CM] = 0;')
    script_list.append('      @target_fvideo_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  ')
    
    script_list.append('  //Radar Front Left')
    script_list.append('  @target_radar_fl_sim::objdata.number_of_obj = @CarMaker::RB::Radar::FL::object_count;')
    script_list.append('  for (counter_CM = 0; counter_CM < 9; counter_CM++)')
    script_list.append('  {')
    script_list.append('    if(counter_CM < @target_radar_fl_sim::objdata.number_of_obj)')
    script_list.append('    { //valid target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_RFL[counter_CM] = 1;')
    script_list.append('      @target_radar_fl_sim::objdata.empty_obj[counter_CM] = 0;')
    script_list.append('    }')
    script_list.append('    else if(@Classe_Obj_Sim::ValidityFlags.validity_radar_fl_on == 0)')
    script_list.append('    { //only valid target sending off -> dummy target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_RFL[counter_CM] = 1;')
    script_list.append('      @target_radar_fl_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('    else')
    script_list.append('    { //only valid target sending on -> empty target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_RFL[counter_CM] = 0;')
    script_list.append('      @target_radar_fl_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  if(@hil_ctrl::radar_fl_loc_sim > 0)')
    script_list.append('  { //location based')
    script_list.append('    @target_radar_fl_sim::locdata.number_of_loc = 0;')
    script_list.append('    total_number_of_locations_RFL_CM = 0;')
    script_list.append('  }')
    script_list.append('  ')
    
    script_list.append('  //Radar Front Right')
    script_list.append('  @target_radar_fr_sim::objdata.number_of_obj = @CarMaker::RB::Radar::FR::object_count;')
    script_list.append('  for (counter_CM = 0; counter_CM < 9; counter_CM++)')
    script_list.append('  {')
    script_list.append('    if(counter_CM < @target_radar_fr_sim::objdata.number_of_obj)')
    script_list.append('    { //valid target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_RFR[counter_CM] = 1;')
    script_list.append('      @target_radar_fr_sim::objdata.empty_obj[counter_CM] = 0;')
    script_list.append('    }')
    script_list.append('    else if(@Classe_Obj_Sim::ValidityFlags.validity_radar_fr_on == 0)')
    script_list.append('    { //only valid target sending off -> dummy target')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_RFR[counter_CM] = 1;')
    script_list.append('        @target_radar_fr_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('    else')
    script_list.append('    { //only valid target sending on -> empty target')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_RFR[counter_CM] = 0;')
    script_list.append('        @target_radar_fr_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  if(@hil_ctrl::radar_fr_loc_sim > 0)')
    script_list.append('  { //location based')
    script_list.append('    @target_radar_fr_sim::locdata.number_of_loc = 0;')
    script_list.append('    total_number_of_locations_RFR_CM = 0;')
    script_list.append('  }')
    script_list.append('  ')

    script_list.append('  //Radar Rear Left')
    script_list.append('  @target_radar_rl_sim::objdata.number_of_obj = @CarMaker::RB::Radar::RL::object_count;')
    script_list.append('  for (counter_CM = 0; counter_CM < 9; counter_CM++)')
    script_list.append('  {')
    script_list.append('    if(counter_CM < @target_radar_rl_sim::objdata.number_of_obj)')
    script_list.append('    { //valid target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_RRL[counter_CM] = 1;')
    script_list.append('      @target_radar_rl_sim::objdata.empty_obj[counter_CM] = 0;')
    script_list.append('    }')
    script_list.append('    else if(@Classe_Obj_Sim::ValidityFlags.validity_radar_rl_on == 0)')
    script_list.append('    { //only valid target sending off -> dummy target')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_RRL[counter_CM] = 1;')
    script_list.append('        @target_radar_rl_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('    else')
    script_list.append('    { //only valid target sending on -> empty target')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_RRL[counter_CM] = 0;')
    script_list.append('        @target_radar_rl_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  if(@hil_ctrl::radar_rl_loc_sim > 0)')
    script_list.append('  { //location based')
    script_list.append('    @target_radar_rl_sim::locdata.number_of_loc = 0;')
    script_list.append('    total_number_of_locations_RRL_CM = 0;')
    script_list.append('  }')
    script_list.append('  ')
    
    script_list.append('  //Radar Rear Right')
    script_list.append('  @target_radar_rr_sim::objdata.number_of_obj = @CarMaker::RB::Radar::RR::object_count;')
    script_list.append('  for (counter_CM = 0; counter_CM < 9; counter_CM++)')
    script_list.append('  {')
    script_list.append('    if(counter_CM < @target_radar_rr_sim::objdata.number_of_obj)')
    script_list.append('    { //valid target')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_RRR[counter_CM] = 1;')
    script_list.append('      @target_radar_rr_sim::objdata.empty_obj[counter_CM] = 0;')
    script_list.append('    }')
    script_list.append('    else if(@Classe_Obj_Sim::ValidityFlags.validity_radar_rr_on == 0)')
    script_list.append('    { //only valid target sending off -> dummy target')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_RRR[counter_CM] = 1;')
    script_list.append('        @target_radar_rr_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('    else')
    script_list.append('    { //only valid target sending on -> empty target')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_RRR[counter_CM] = 0;')
    script_list.append('        @target_radar_rr_sim::objdata.empty_obj[counter_CM] = 1;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  if(@hil_ctrl::radar_rr_loc_sim > 0)')
    script_list.append('  { //location based')
    script_list.append('    @target_radar_rr_sim::locdata.number_of_loc = 0;')
    script_list.append('    total_number_of_locations_RRR_CM = 0;')
    script_list.append('  }')
    script_list.append('  ')
    
    script_list.append('  //activating or deactivating all the messages for all obj_ids greater than 0-8 depending on validity sending enabled for each sensor')
    script_list.append('  if(@Classe_Obj_Sim::ValidityFlags.validity_radar_fc_loc_on == 0 && @Classe_Obj_Sim::ValidityFlags.validity_radar_fc_obj_on == 0){')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_FC[9] = 1;')
    script_list.append('    @target_radar_fc_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }else{')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_FC[9] = 0;')
    script_list.append('    @target_radar_fc_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }')
    script_list.append('  ')
    script_list.append('  if(@Classe_Obj_Sim::ValidityFlags.validity_fvideo_on == 0){')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_FV[9] = 1;')
    script_list.append('    @target_fvideo_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }else{')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_FV[9] = 0;')
    script_list.append('    @target_fvideo_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }')
    script_list.append('  ')
    script_list.append('  if(@Classe_Obj_Sim::ValidityFlags.validity_radar_fl_on == 0){')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_RFL[9] = 1;')
    script_list.append('    @target_radar_fl_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }else{')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_RFL[9] = 0;')
    script_list.append('    @target_radar_fl_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }')
    script_list.append('  ')
    script_list.append('  if(@Classe_Obj_Sim::ValidityFlags.validity_radar_fr_on == 0){')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_RFR[9] = 1;')
    script_list.append('    @target_radar_fr_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }else{')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_RFR[9] = 0;')
    script_list.append('    @target_radar_fr_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }')
    script_list.append('  ')
    script_list.append('  if(@Classe_Obj_Sim::ValidityFlags.validity_radar_rl_on == 0){')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_RRL[9] = 1;')
    script_list.append('    @target_radar_rl_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }else{')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_RRL[9] = 0;')
    script_list.append('    @target_radar_rl_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }')
    script_list.append('  ')
    script_list.append('  if(@Classe_Obj_Sim::ValidityFlags.validity_radar_rr_on == 0){')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_RRR[9] = 1;')
    script_list.append('    @target_radar_rr_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }else{')
    script_list.append('    @Classe_Obj_Sim::ValidityFlags.validityFlag_RRR[9] = 0;')
    script_list.append('    @target_radar_rr_sim::objdata.empty_obj[9] = 1;')
    script_list.append('  }')
    script_list.append('}')
    script_list.append('')
    
def update_Map_CM(file_path, num_objects):
    """
    Description: Main function for updating the update file for the CarMaker usecase. Orchestrates the update functions and saves the data in the file.

    Args:
      file_path: Path of the file which shall be updated/generated.
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    global script_list
    script_list = [Header]
    
    update_CM_reading(num_objects)
    update_CM_offsets()
    calculate_valid_CM_targets(num_objects)
    update_CM_mapping()
    
    update_radar_fc_cm(num_objects)
    update_fvideo_cm(num_objects)
    update_radar_fl_cm(num_objects)
    update_radar_fr_cm(num_objects)
    update_radar_rl_cm(num_objects)
    update_radar_rr_cm(num_objects)
    
    update_traffic_obj_ctrl()
    
    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

def update_radar_fc_cm(num_objects):
    """
    Description: Updates the update function of the radar front center, which calculates further required object/location data.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    global script_list
	# define object-independent script
    script_list.append('/** @brief Update function for the Radar Front Center which calculates obj/loc data out of the read target data.')
    script_list.append('  *        Sensor model is location(1)/object(2) based')
    script_list.append('  * @return void')
    script_list.append('  */')
    
    script_list.append('void update_radar_fc_cm(byte object_id, int sensor_mod)')
    script_list.append('{')
    script_list.append('  if(sensor_mod == 1)')
    script_list.append('  { //location based')
    script_list.append('    //Calculate coordinate systems: RCA - mid of target geometry; Sensor position - mid of target geometry')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fc_sim::objdata.obj_length[object_id], @target_radar_fc_sim::objdata.obj_heading_angle[object_id], @target_radar_fc_sim::objdata.obj_distance_x[object_id], @target_radar_fc_sim::objdata.obj_distance_y[object_id], @target_radar_fc_sim::objdata.obj_velocity_x[object_id],  @target_radar_fc_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fc, @Classe_Obj_Sim::RoadObj.offset_y_fc, @radarfc_par::mounting_ori_yaw, 1, 0);')
    script_list.append('    ')
    script_list.append('    if(@target_radar_fc_sim::locdata.location_model == 0)')
    script_list.append('    { //1objXloc')
    script_list.append('      //Calculate reference point')
    script_list.append('      dllCalcObjectReferencePoint(gHandle_obj, @target_radar_fc_sim::objdata.obj_height[object_id], @target_radar_fc_sim::objdata.obj_width[object_id], @target_radar_fc_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('      //Calculate location values using the reference point position')
    script_list.append('      dllCalcLocations(gHandle_obj,4,1.5);  //handle,max_loc,height')
    script_list.append('      number_of_locs_RFC_CM = dllGetLocCount(gHandle_obj);')
    script_list.append('      ')
    script_list.append('      for(loc_count_RFC_CM=total_number_of_locations_RFC_CM; loc_count_RFC_CM < total_number_of_locations_RFC_CM+max_number_of_locations_starmodel && loc_count_RFC_CM < total_number_of_locations_RFC_CM+number_of_locs_RFC_CM; loc_count_RFC_CM++)')
    script_list.append('      {')
    script_list.append('        //radial distance')
    script_list.append('        @target_radar_fc_sim::locdata.loc_radial_distance[loc_count_RFC_CM] = dllGetLoc(gHandle_obj,loc_count_RFC_CM-total_number_of_locations_RFC_CM);')
    script_list.append('        ')
    script_list.append('        //radial velocity')
    script_list.append('        @target_radar_fc_sim::locdata.loc_radial_velocity[loc_count_RFC_CM] = calc_radial_velocity(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj), dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), @target_radar_fc_sim::locdata.loc_radial_velocity[object_id]);')
    script_list.append('        ')
    script_list.append('        //location angles')
    script_list.append('        @target_radar_fc_sim::locdata.loc_elevation_angle[loc_count_RFC_CM] = calc_elevation_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('        @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_CM] = dllGetLocAzimuth(gHandle_obj,loc_count_RFC_CM-total_number_of_locations_RFC_CM);')
    script_list.append('        ')
    script_list.append('        //SNR')
    script_list.append('        @target_radar_fc_sim::locdata.loc_signal_strength_indicator[loc_count_RFC_CM] = 100;')
    script_list.append('        ')
    script_list.append('        //RCS')
    script_list.append('        switch(object_id){')
    script_list.append('            case 0: @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = @CarMaker::RB::Radar::FC::object0::rcsN; break;')
    script_list.append('            case 1: @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = @CarMaker::RB::Radar::FC::object1::rcsN; break;')
    script_list.append('            case 2: @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = @CarMaker::RB::Radar::FC::object2::rcsN; break;')
    script_list.append('            case 3: @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = @CarMaker::RB::Radar::FC::object2::rcsN; break;')
    script_list.append('            case 4: @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = @CarMaker::RB::Radar::FC::object3::rcsN; break;')
    script_list.append('            case 5: @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = @CarMaker::RB::Radar::FC::object4::rcsN; break;')
    script_list.append('            case 6: @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = @CarMaker::RB::Radar::FC::object5::rcsN; break;')
    script_list.append('            case 7: @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = @CarMaker::RB::Radar::FC::object6::rcsN; break;')
    script_list.append('            case 8: @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = @CarMaker::RB::Radar::FC::object7::rcsN; break;')
    script_list.append('            case 9: @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = @CarMaker::RB::Radar::FC::object8::rcsN; break;')
    script_list.append('            case 10: @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = @CarMaker::RB::Radar::FC::object9::rcsN; break;')
    script_list.append('        }')
    script_list.append('      }')
    script_list.append('	  ')
    script_list.append('      //1objXloc')
    script_list.append('      total_number_of_locations_RFC_CM = total_number_of_locations_RFC_CM + _min(number_of_locs_RFC_CM, max_number_of_locations_starmodel);')
    script_list.append('      @target_radar_fc_sim::locdata.number_of_loc = total_number_of_locations_RFC_CM;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_fc_sim::locdata.location_model == 1)')
    script_list.append('    { //starmodel')
    script_list.append('      resultSetInputValues = dllSetInputValues(gHandle_star, object_id+1, dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot), 0, dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), 0, 0, dllRotationGetSensorHeading(gHandle_rot), @target_radar_fc_sim::objdata.obj_length[object_id], @target_radar_fc_sim::objdata.obj_width[object_id], @target_radar_fc_sim::objdata.obj_height[object_id], @target_radar_fc_sim::objdata.obj_type[object_id]); //no z axis and no accel')
    script_list.append('      resultStarModelRun = dllRunStarModel(gHandle_star, 2);')
    script_list.append('      number_of_locs_RFC_CM = dllGetNumLocs(gHandle_star);')
    script_list.append('      ')
    script_list.append('      for(loc_count_RFC_CM=total_number_of_locations_RFC_CM; loc_count_RFC_CM < total_number_of_locations_RFC_CM+@hil_ctrl::starmodel_max_loc_nr && loc_count_RFC_CM < total_number_of_locations_RFC_CM+number_of_locs_RFC_CM; loc_count_RFC_CM++)')
    script_list.append('      {')
    script_list.append('        @target_radar_fc_sim::locdata.loc_radial_distance[loc_count_RFC_CM] = dllGetDistance(gHandle_star, loc_count_RFC_CM-total_number_of_locations_RFC_CM);')
    script_list.append('        @target_radar_fc_sim::locdata.loc_radial_velocity[loc_count_RFC_CM] = -dllGetRelativeRadialVelocity(gHandle_star, loc_count_RFC_CM-total_number_of_locations_RFC_CM);')
    script_list.append('        @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_CM] = dllGetAzimuthAngle(gHandle_star, loc_count_RFC_CM-total_number_of_locations_RFC_CM);')
    script_list.append('        if(@target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_CM]>PI) ')
    script_list.append('        {')
    script_list.append('          @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_CM] = @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_CM]-2*PI;')
    script_list.append('        }')
    script_list.append('        @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_CM] = @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_CM] * 180 / pi;')
    script_list.append('        @target_radar_fc_sim::locdata.loc_elevation_angle[loc_count_RFC_CM] = dllGetElevationAngle(gHandle_star, loc_count_RFC_CM-total_number_of_locations_RFC_CM);')
    script_list.append('  	    @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_CM] = dllGetRcs(gHandle_star, loc_count_RFC_CM-total_number_of_locations_RFC_CM);')
    script_list.append('        @target_radar_fc_sim::locdata.loc_signal_strength_indicator[loc_count_RFC_CM] = 100;')
    script_list.append('      }')
    script_list.append('      total_number_of_locations_RFC_CM = total_number_of_locations_RFC_CM + _min(number_of_locs_RFC_CM, @hil_ctrl::starmodel_max_loc_nr);')
    script_list.append('      @target_radar_fc_sim::locdata.number_of_loc = total_number_of_locations_RFC_CM;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_fc_sim::locdata.location_model == 2)')
    script_list.append('    { // Clara model - needs all object data at once and gives back a unspecified number of locations which cannot be assigned to a specific object')
    script_list.append('      // This is why we do all of this in a separate loop on the call of the first target')
    script_list.append('      if(clara_run_fc_CM == 1)')
    script_list.append('      {')
    script_list.append('        int loc_id = 0;')
    script_list.append('        int i = 0;')
    script_list.append('        ')
    script_list.append('        // initialize the model onces to make sure correct mounting positions for the current scenario are loaded into the Clara model')
    script_list.append('        dllClaraInitModel(gHandle_clara_RFC,@Classe_Obj_Sim::RoadObj.offset_x_fc,@Classe_Obj_Sim::RoadObj.offset_y_fc,@Classe_Obj_Sim::RoadObj.offset_z_fc+0.4,@radarfc_par::mounting_ori_yaw,')
    script_list.append('                          @hil_ctrl::clara_model_loc_separation_angle,@hil_ctrl::clara_model_max_loc_nr_per_obj);')
    script_list.append('        ')
    script_list.append('        // loop through all objects and provide object data to Clara model')
    script_list.append('        for(i = 0; i < obj_max_allowed; i++)')
    script_list.append('        {')
    script_list.append('          // only provide data of valid objects or if an object needs to be deleted (This is very important! Failures are expected if Clara objects are not being deleted)')
    script_list.append('          if(@Classe_Obj_Sim::ValidityFlags.validityFlag_FC[i] == 1)')
    script_list.append('          { // valid object')
    script_list.append('            ')
    script_list.append('            // Calculate coordinate systems: RCA - mid of target geometry; Sensor position - mid of target geometry; Center of Gravity - mid of target geometry')
    script_list.append('            dllRotationCalcTarget(gHandle_rot, @target_radar_fc_sim::objdata.obj_length[i], @target_radar_fc_sim::objdata.obj_heading_angle[i], @target_radar_fc_sim::objdata.obj_distance_x[i], @target_radar_fc_sim::objdata.obj_distance_y[i], ')
    script_list.append('                                  @target_radar_fc_sim::objdata.obj_velocity_x[i],  @target_radar_fc_sim::objdata.obj_velocity_y[i], @Classe_Obj_Sim::RoadObj.offset_x_fc, @Classe_Obj_Sim::RoadObj.offset_y_fc, 0, 1, 0);')
    script_list.append('            ')
    script_list.append('            // update Ego vehicle - for now the Ego is set to standstill at (0/0/0) due to missing world coordinates')
    script_list.append('            dllClaraUpdateEgo(gHandle_clara_RFC);')
    script_list.append('            // handle, target_id, target_type, target_dx, target_dy, target_dz, target_vx, target_vy, target_vz, target_acceleration, target_yaw_angle, target_length, target_width, target_height')
    script_list.append('            dllClaraUpdateTgt(gHandle_clara_RFC,i,@target_radar_fc_sim::objdata.obj_type[i],dllRotationGetRCADx(gHandle_rot),dllRotationGetRCADy(gHandle_rot),0,')
    script_list.append('                              dllRotationGetRCAVx(gHandle_rot),dllRotationGetRCAVy(gHandle_rot),0,0,dllRotationGetRCAHeading(gHandle_rot),')
    script_list.append('                              @target_radar_fc_sim::objdata.obj_length[i],@target_radar_fc_sim::objdata.obj_width[i],@target_radar_fc_sim::objdata.obj_height[i]);')
    script_list.append('            ')
    script_list.append('            clara_radar_fc_deletion_needed_CM[i] = 1;')
    script_list.append('          }')
    script_list.append('          else if(clara_radar_fc_deletion_needed_CM[i] == 1)')
    script_list.append('          { // object deleted, only done once per object to save performance')
    script_list.append('            ')
    script_list.append('            // update Ego vehicle - for now the Ego is set to standstill at (0/0/0) due to missing world coordinates')
    script_list.append('            dllClaraUpdateEgo(gHandle_clara_RFC);')
    script_list.append('            // deletion means setting everything to 0 for that object')
    script_list.append('            dllClaraUpdateTgt(gHandle_clara_RFC,i,0,0,0,0,0,0,0,0,0,0,0,0);')
    script_list.append('            ')
    script_list.append('            clara_radar_fc_deletion_needed_CM[i] = 0;')
    script_list.append('          }')
    script_list.append('        }')
    script_list.append('        ')
    script_list.append('        // run the Clara model')
    script_list.append('        dllClaraCalc(gHandle_clara_RFC);')
    script_list.append('        ')
    script_list.append('        // read location data from Clara -> loop through locations')
    script_list.append('        loc_id = dllClaraGetNextValidLoc(gHandle_clara_RFC,-1);')
    script_list.append('        ')
    script_list.append('        // loc_id >= 0 means another location found; loc_id = -1 means no further locations; loc_id = -10 means error')
    script_list.append('        while(loc_id >= 0)')
    script_list.append('        {')
    script_list.append('          //radial distance')
    script_list.append('          @target_radar_fc_sim::locdata.loc_radial_distance[total_number_of_locations_RFC_CM] = dllClaraGetRadialDistance(gHandle_clara_RFC,loc_id);')
    script_list.append('          ')
    script_list.append('          //radial velocity')
    script_list.append('          @target_radar_fc_sim::locdata.loc_radial_velocity[total_number_of_locations_RFC_CM] = dllClaraGetRadialVelocity(gHandle_clara_RFC,loc_id);')
    script_list.append('          ')
    script_list.append('          //location angles')
    script_list.append('          @target_radar_fc_sim::locdata.loc_elevation_angle[total_number_of_locations_RFC_CM] = dllClaraGetElevationAngle(gHandle_clara_RFC,loc_id);')
    script_list.append('          @target_radar_fc_sim::locdata.loc_azimuth_angle[total_number_of_locations_RFC_CM] = dllClaraGetAzimuthAngle(gHandle_clara_RFC,loc_id);')
    script_list.append('          ')
    script_list.append('          //SNR + RCS')
    script_list.append('          @target_radar_fc_sim::locdata.loc_radar_cross_section[total_number_of_locations_RFC_CM] = dllClaraGetRCS(gHandle_clara_RFC,loc_id);')
    script_list.append('          @target_radar_fc_sim::locdata.loc_signal_strength_indicator[total_number_of_locations_RFC_CM] = 100;')
    script_list.append('          ')
    script_list.append('          // increase number of locations')
    script_list.append('          total_number_of_locations_RFC_CM++;')
    script_list.append('          @target_radar_fc_sim::locdata.number_of_loc = total_number_of_locations_RFC_CM;')
    script_list.append('          ')
    script_list.append('          // only accept as many locations as allowed')
    script_list.append('          if(total_number_of_locations_RFC_CM >= maximum_nr_loc)')
    script_list.append('          {')
    script_list.append('            break; ')
    script_list.append('          }')
    script_list.append('          ')
    script_list.append('          // get ID of next location')
    script_list.append('          loc_id = dllClaraGetNextValidLoc(gHandle_clara_RFC,loc_id);')
    script_list.append('        }')
    script_list.append('        ')
    script_list.append('        clara_run_fc_CM = 0;')
    script_list.append('      }')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  else if(sensor_mod == 2)')
    script_list.append('  { //object based')
    script_list.append('    //TBD')
    script_list.append('  }')
    script_list.append('}')
    script_list.append('')

    print('Radar_FC for Classe usecase updated successfully.')

def update_fvideo_cm(num_objects):
    """
    Description: Updates the update function of the front video, which calculates further required object data.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    global script_list
	# define object-independent script
    script_list.append('/** @brief Update function for the Front Video which calculates obj data out of the read target data.')
    script_list.append('  * @return void')
    script_list.append('  */')
    
    script_list.append('void update_fvideo_cm(byte object_id)')
    script_list.append('{')
    
    script_list.append('  //shift target data to have RCA and Sensor CS available')
    script_list.append('  dllRotationCalcTarget(gHandle_rot, @target_fvideo_sim::objdata.obj_length[object_id], @target_fvideo_sim::objdata.obj_heading_angle[object_id], @target_fvideo_sim::objdata.obj_distance_x[object_id], @target_fvideo_sim::objdata.obj_distance_y[object_id], @target_fvideo_sim::objdata.obj_velocity_x[object_id],  @target_fvideo_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fv, @Classe_Obj_Sim::RoadObj.offset_y_fv, @fvideo_par::mounting_ori_yaw, 1, 0);')
    script_list.append('  //calculate the reference point on the target')
    script_list.append('  dllCalcObjectReferencePoint(gHandle_obj, @target_fvideo_sim::objdata.obj_height[object_id], @target_fvideo_sim::objdata.obj_width[object_id], @target_fvideo_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('  //calculate Aligned Camera Coordinate System specific data')
    script_list.append('  dllCalcACCS(gHandle_obj, dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), @target_fvideo_sim::objdata.obj_acceleration_x[object_id], @target_fvideo_sim::objdata.obj_acceleration_y[object_id]);')
    script_list.append('  ')
    script_list.append('  //basic object data')
    script_list.append('  @target_fvideo_sim::objdata.obj_distance_x[object_id] = dllGetRCARefptDistX(gHandle_obj);')
    script_list.append('  @target_fvideo_sim::objdata.obj_distance_y[object_id] = dllGetRCARefptDistY(gHandle_obj);')
    script_list.append('  @target_fvideo_sim::objdata.obj_velocity_x[object_id] = dllRotationGetSensorVx(gHandle_rot);')
    script_list.append('  @target_fvideo_sim::objdata.obj_velocity_y[object_id] = dllRotationGetSensorVy(gHandle_rot);')
    script_list.append('  @target_fvideo_sim::objdata.obj_heading_angle[object_id] = dllRotationGetRCAHeading(gHandle_rot);')
    script_list.append('  ')
    script_list.append('  //normalized data and probabilities')
    script_list.append('  @target_fvideo_sim::objdata.obj_norm_vel_x[object_id] = dllGetACCSNormVx(gHandle_obj);')
    script_list.append('  @target_fvideo_sim::objdata.obj_norm_vel_y[object_id] = dllGetACCSNormVy(gHandle_obj);')
    script_list.append('  @target_fvideo_sim::objdata.obj_norm_accel[object_id] = dllGetACCSNormAx(gHandle_obj);')
    script_list.append('  @target_fvideo_sim::objdata.obj_brake_light[object_id] = calc_brake_light(@target_fvideo_sim::objdata.obj_acceleration_x[object_id]);')
    script_list.append('  @target_fvideo_sim::objdata.obj_turn_light[object_id] = 1;')
    script_list.append('  @target_fvideo_sim::objdata.obj_prob_moving_long[object_id] = calc_movement_probability_long(@target_fvideo_sim::objdata.obj_velocity_x[object_id]);')
    script_list.append('  @target_fvideo_sim::objdata.obj_prob_moving_lat[object_id] = calc_movement_probability_lat(@target_fvideo_sim::objdata.obj_velocity_y[object_id]);')
    script_list.append('  @target_fvideo_sim::objdata.obj_moving[object_id] = calc_movement_flag(@target_fvideo_sim::objdata.obj_prob_moving_long[object_id],@target_fvideo_sim::objdata.obj_prob_moving_lat[object_id]);')
    script_list.append('  @target_fvideo_sim::objdata.obj_reliability[object_id] = calc_reliability(@target_fvideo_sim::objdata.obj_prob_moving_long[object_id],@target_fvideo_sim::objdata.obj_prob_moving_lat[object_id]);')
    script_list.append('  @target_fvideo_sim::objdata.obj_meas_source[object_id] = calc_meas_source(@target_fvideo_sim::objdata.obj_type[object_id]);')
    script_list.append('  ')
    script_list.append('  //object angles')
    script_list.append('  @target_fvideo_sim::objdata.obj_phi_bottom[object_id] = dllGetACCSEdgeBottom(gHandle_obj);')
    script_list.append('  @target_fvideo_sim::objdata.obj_phi_left[object_id] = dllGetACCSEdgeLeft(gHandle_obj);')
    script_list.append('  @target_fvideo_sim::objdata.obj_phi_right[object_id] = dllGetACCSEdgeRight(gHandle_obj);')
    script_list.append('  @target_fvideo_sim::objdata.obj_phi_mid[object_id] = dllGetACCSEdgeMid(gHandle_obj);')
    script_list.append('  ')
    script_list.append('  //object classification')
    script_list.append('  @target_fvideo_sim::objdata.obj_type[object_id] = calc_obj_type(@target_fvideo_sim::objdata.obj_type[object_id]);')
    script_list.append('  @target_fvideo_sim::objdata.obj_head_orientation[object_id] = calc_head_orientation(@target_fvideo_sim::objdata.obj_heading_angle[object_id], @target_fvideo_sim::objdata.obj_distance_y[object_id]);')
    script_list.append('  @target_fvideo_sim::objdata.obj_classified_view[object_id] = dllGetACCSClassifiedView(gHandle_obj);')
    script_list.append('  @target_fvideo_sim::objdata.obj_visible_view[object_id] = dllGetACCSVisibleView(gHandle_obj);')
    script_list.append('  @target_fvideo_sim::objdata.obj_oncoming[object_id] = calc_oncoming(@target_fvideo_sim::objdata.obj_classified_view[object_id]);')
    script_list.append('  @target_fvideo_sim::objdata.obj_target_acc_type[object_id] = calc_target_acc_type(@target_fvideo_sim::objdata.obj_visible_view[object_id],@target_fvideo_sim::objdata.obj_distance_y[object_id]);')
    script_list.append('}')
    script_list.append('')
    
    print('FVideo for Classe usecase updated successfully.')
    
def update_radar_fl_cm(num_objects):
    """
    Description: Updates the update function of the radar front left, which calculates further required object/location data.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    global script_list
	# define object-independent script
    script_list.append('/** @brief Update function for the Radar Front Left which calculates obj/loc data out of the read target data.')
    script_list.append('  *        Sensor model is location(1)/object(2) based')
    script_list.append('  * @return void')
    script_list.append('  */')
    
    script_list.append('void update_radar_fl_cm(byte object_id, int sensor_mod)')
    script_list.append('{')
    
    script_list.append('  if(sensor_mod == 1)')
    script_list.append('  { //location based')
    script_list.append('    //Calculate coordinate systems: RCA - mid of target geometry; Sensor position - mid of target geometry')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fl_sim::objdata.obj_length[object_id], @target_radar_fl_sim::objdata.obj_heading_angle[object_id], @target_radar_fl_sim::objdata.obj_distance_x[object_id], @target_radar_fl_sim::objdata.obj_distance_y[object_id], @target_radar_fl_sim::objdata.obj_velocity_x[object_id],  @target_radar_fl_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fl, @Classe_Obj_Sim::RoadObj.offset_y_fl, @radarfl_par::mounting_ori_yaw, 1, 0);')
    script_list.append('    if(@target_radar_fl_sim::locdata.location_model == 0)')
    script_list.append('    { //1obj1loc')
    script_list.append('      //Calculate reference point')
    script_list.append('      dllCalcObjectReferencePoint(gHandle_obj, @target_radar_fl_sim::objdata.obj_height[object_id], @target_radar_fl_sim::objdata.obj_width[object_id], @target_radar_fl_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('      loc_count_RFL_CM=total_number_of_locations_RFL_CM;')
    script_list.append('      ')
    script_list.append('      //Calculate location values using the reference point position')
    script_list.append('      @target_radar_fl_sim::locdata.loc_radial_distance[loc_count_RFL_CM] = calc_radial_distance(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_fl_sim::locdata.loc_radial_velocity[loc_count_RFL_CM] = calc_radial_velocity(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj), dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), @target_radar_fc_sim::locdata.loc_radial_velocity[object_id]);')
    script_list.append('      ')
    script_list.append('      //location angles')
    script_list.append('      @target_radar_fl_sim::locdata.loc_elevation_angle[loc_count_RFL_CM] = calc_elevation_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_CM] = calc_azimuth_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      ')
    script_list.append('      //RCS + SNR')
    script_list.append('      @target_radar_fl_sim::locdata.loc_radar_cross_section[loc_count_RFL_CM] = calc_radar_cross_section(@target_radar_fl_sim::objdata.obj_type[object_id], @target_radar_fl_sim::locdata.loc_radial_distance[object_id]);')
    script_list.append('      @target_radar_fl_sim::locdata.loc_signal_strength_indicator[loc_count_RFL_CM] = 100;')
    script_list.append('	  ')
    script_list.append('      //1obj1loc')
    script_list.append('      total_number_of_locations_RFL_CM = total_number_of_locations_RFL_CM + 1;')
    script_list.append('      @target_radar_fl_sim::locdata.number_of_loc = total_number_of_locations_RFL_CM;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_fl_sim::locdata.location_model == 1)')
    script_list.append('    { //starmodel')
    script_list.append('      resultSetInputValues = dllSetInputValues(gHandle_star, object_id+1, dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot), 0, dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), 0, 0, dllRotationGetSensorHeading(gHandle_rot), @target_radar_fl_sim::objdata.obj_length[object_id], @target_radar_fl_sim::objdata.obj_width[object_id], @target_radar_fl_sim::objdata.obj_height[object_id], @target_radar_fl_sim::objdata.obj_type[object_id]);')
    script_list.append('      resultStarModelRun = dllRunStarModel(gHandle_star, 2);')
    script_list.append('      number_of_locs_RFL_CM = dllGetNumLocs(gHandle_star);')
    script_list.append('      for(loc_count_RFL_CM=total_number_of_locations_RFL_CM; loc_count_RFL_CM < total_number_of_locations_RFL_CM+@hil_ctrl::starmodel_max_loc_nr && loc_count_RFL_CM < total_number_of_locations_RFL_CM+number_of_locs_RFL_CM; loc_count_RFL_CM++)')
    script_list.append('      {')
    script_list.append('        @target_radar_fl_sim::locdata.loc_radial_distance[loc_count_RFL_CM] = dllGetDistance(gHandle_star, loc_count_RFL_CM-total_number_of_locations_RFL_CM);')
    script_list.append('        @target_radar_fl_sim::locdata.loc_radial_velocity[loc_count_RFL_CM] = -dllGetRelativeRadialVelocity(gHandle_star, loc_count_RFL_CM-total_number_of_locations_RFL_CM);')
    script_list.append('        @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_CM] = dllGetAzimuthAngle(gHandle_star, loc_count_RFL_CM-total_number_of_locations_RFL_CM);')
    script_list.append('        if(@target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_CM]>PI) ')
    script_list.append('        {')
    script_list.append('          @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_CM] = @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_CM]-2*PI;')
    script_list.append('        }')
    script_list.append('        @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_CM] = @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_CM] * 180 / pi;')
    script_list.append('        @target_radar_fl_sim::locdata.loc_elevation_angle[loc_count_RFL_CM] = -dllGetElevationAngle(gHandle_star, loc_count_RFL_CM-total_number_of_locations_RFL_CM);')
    script_list.append('  	    @target_radar_fl_sim::locdata.loc_radar_cross_section[loc_count_RFL_CM] = dllGetRcs(gHandle_star, loc_count_RFL_CM-total_number_of_locations_RFL_CM);')
    script_list.append('      }')
    script_list.append('    total_number_of_locations_RFL_CM = total_number_of_locations_RFL_CM + _min(number_of_locs_RFL_CM, @hil_ctrl::starmodel_max_loc_nr);')
    script_list.append('    @target_radar_fl_sim::locdata.number_of_loc = total_number_of_locations_RFL_CM;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  else if(sensor_mod == 2)')
    script_list.append('  { //object based')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fl_sim::objdata.obj_length[object_id], @target_radar_fl_sim::objdata.obj_heading_angle[object_id], @target_radar_fl_sim::objdata.obj_distance_x[object_id], @target_radar_fl_sim::objdata.obj_distance_y[object_id], @target_radar_fl_sim::objdata.obj_velocity_x[object_id],  @target_radar_fl_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fl, @Classe_Obj_Sim::RoadObj.offset_y_fl, @radarfl_par::mounting_ori_yaw, 1, 0);')
    script_list.append('    //calculate the reference point on the target')
    script_list.append('    dllCalcObjectReferencePoint(gHandle_obj, @target_radar_fl_sim::objdata.obj_height[object_id], @target_radar_fl_sim::objdata.obj_width[object_id], @target_radar_fl_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('    ')
    script_list.append('    //basic object data')
    script_list.append('    @target_radar_fl_sim::objdata.obj_distance_x[object_id] = dllGetRCARefptDistX(gHandle_obj);')
    script_list.append('    @target_radar_fl_sim::objdata.obj_distance_y[object_id] = dllGetRCARefptDistY(gHandle_obj);')
    script_list.append('    @target_radar_fl_sim::objdata.obj_velocity_x[object_id] = dllRotationGetRCAVx(gHandle_rot);')
    script_list.append('    @target_radar_fl_sim::objdata.obj_velocity_y[object_id] = dllRotationGetRCAVy(gHandle_rot);')
    script_list.append('    @target_radar_fl_sim::objdata.obj_heading_angle[object_id] = dllRotationGetRCAHeading(gHandle_rot);')
    script_list.append('    @target_radar_fl_sim::objdata.obj_ref_point[object_id] = calc_ref_pnt(dllGetSensorRefpt(gHandle_obj));')
    script_list.append('    ')
    script_list.append('    // type defining')
    script_list.append('    @target_radar_fl_sim::objdata.obj_prob_moving_status[object_id] = calc_moving_status(@target_radar_fl_sim::objdata.obj_velocity_x[object_id], @target_radar_fl_sim::objdata.obj_velocity_y[object_id]);')
    script_list.append('    @target_radar_fl_sim::objdata.obj_prob_obst_class[object_id] = calc_ra6_obj_type(@target_radar_fl_sim::objdata.obj_type[object_id]);')
    script_list.append('    switch(object_id)')
    script_list.append('    {')
    script_list.append('      case 0: @target_radar_fl_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FL::object0::rcsN; break;')
    script_list.append('      case 1: @target_radar_fl_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FL::object1::rcsN; break;')
    script_list.append('      case 2: @target_radar_fl_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FL::object2::rcsN; break;')
    script_list.append('      case 3: @target_radar_fl_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FL::object3::rcsN; break;')
    script_list.append('      case 4: @target_radar_fl_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FL::object4::rcsN; break;')
    script_list.append('      case 5: @target_radar_fl_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FL::object5::rcsN; break;')
    script_list.append('      case 6: @target_radar_fl_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FL::object6::rcsN; break;')
    script_list.append('      case 7: @target_radar_fl_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FL::object7::rcsN; break;')
    script_list.append('      case 8: @target_radar_fl_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FL::object8::rcsN; break;')
    script_list.append('      case 9: @target_radar_fl_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FL::object9::rcsN; break;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('}')
    script_list.append('')
    
    print('Radar_FL for Classe usecase updated successfully.')

def update_radar_fr_cm(num_objects):
    """
    Description: Updates the update function of the radar front right, which calculates further required object/location data.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    global script_list
	# define object-independent script
    script_list.append('/** @brief Update function for the Radar Front Right which calculates obj/loc data out of the read target data.')
    script_list.append('  *        Sensor model is location(1)/object(2) based')
    script_list.append('  * @return void')
    script_list.append('  */')
    
    script_list.append('void update_radar_fr_cm(byte object_id, int sensor_mod)')
    script_list.append('{')
    
    script_list.append('  if(sensor_mod == 1)')
    script_list.append('  { //location based')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fr_sim::objdata.obj_length[object_id], @target_radar_fr_sim::objdata.obj_heading_angle[object_id], @target_radar_fr_sim::objdata.obj_distance_x[object_id], @target_radar_fr_sim::objdata.obj_distance_y[object_id], @target_radar_fr_sim::objdata.obj_velocity_x[object_id],  @target_radar_fr_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fr, @Classe_Obj_Sim::RoadObj.offset_y_fr, @radarfr_par::mounting_ori_yaw, 1, 0);')
    script_list.append('    if(@target_radar_fr_sim::locdata.location_model == 0)')
    script_list.append('    { //1obj1loc')
    script_list.append('      //Calculate reference point')
    script_list.append('      dllCalcObjectReferencePoint(gHandle_obj, @target_radar_fr_sim::objdata.obj_height[object_id], @target_radar_fr_sim::objdata.obj_width[object_id], @target_radar_fr_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('      loc_count_RFR_CM=total_number_of_locations_RFR_CM;')
    script_list.append('      ')
    script_list.append('      //Calculate location values using the reference point position')
    script_list.append('      @target_radar_fr_sim::locdata.loc_radial_distance[loc_count_RFR_CM] = calc_radial_distance(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_fr_sim::locdata.loc_radial_velocity[loc_count_RFR_CM] = calc_radial_velocity(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj), dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), @target_radar_fc_sim::locdata.loc_radial_velocity[object_id]);')
    script_list.append('      ')
    script_list.append('      //location angles')
    script_list.append('      @target_radar_fr_sim::locdata.loc_elevation_angle[loc_count_RFR_CM] = calc_elevation_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_CM] = calc_azimuth_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      ')
    script_list.append('      //RCS + SNR')
    script_list.append('      @target_radar_fr_sim::locdata.loc_radar_cross_section[loc_count_RFR_CM] = calc_radar_cross_section(@target_radar_fr_sim::objdata.obj_type[object_id], @target_radar_fr_sim::locdata.loc_radial_distance[object_id]);')
    script_list.append('      @target_radar_fr_sim::locdata.loc_signal_strength_indicator[loc_count_RFR_CM] = 100;')
    script_list.append('	  ')
    script_list.append('      //1obj1loc')
    script_list.append('      total_number_of_locations_RFR_CM = total_number_of_locations_RFR_CM + 1;')
    script_list.append('      @target_radar_fr_sim::locdata.number_of_loc = total_number_of_locations_RFR_CM;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_fr_sim::locdata.location_model == 1)')
    script_list.append('    { //starmodel')
    script_list.append('      resultSetInputValues = dllSetInputValues(gHandle_star, object_id+1, dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot), 0, dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), 0, 0, dllRotationGetSensorHeading(gHandle_rot), @target_radar_fr_sim::objdata.obj_length[object_id], @target_radar_fr_sim::objdata.obj_width[object_id], @target_radar_fr_sim::objdata.obj_height[object_id], @target_radar_fr_sim::objdata.obj_type[object_id]);')
    script_list.append('      resultStarModelRun = dllRunStarModel(gHandle_star, 2);')
    script_list.append('      number_of_locs_RFR_CM = dllGetNumLocs(gHandle_star);')
    script_list.append('      ')
    script_list.append('      for(loc_count_RFR_CM=total_number_of_locations_RFR_CM; loc_count_RFR_CM < total_number_of_locations_RFR_CM+@hil_ctrl::starmodel_max_loc_nr && loc_count_RFR_CM < total_number_of_locations_RFR_CM+number_of_locs_RFR_CM; loc_count_RFR_CM++)')
    script_list.append('      {')
    script_list.append('        @target_radar_fr_sim::locdata.loc_radial_distance[loc_count_RFR_CM] = dllGetDistance(gHandle_star, loc_count_RFR_CM-total_number_of_locations_RFR_CM);')
    script_list.append('        @target_radar_fr_sim::locdata.loc_radial_velocity[loc_count_RFR_CM] = -dllGetRelativeRadialVelocity(gHandle_star, loc_count_RFR_CM-total_number_of_locations_RFR_CM);')
    script_list.append('        @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_CM] = dllGetAzimuthAngle(gHandle_star, loc_count_RFR_CM-total_number_of_locations_RFR_CM);')
    script_list.append('        if(@target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_CM]>PI) ')
    script_list.append('        {')
    script_list.append('          @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_CM] = @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_CM]-2*PI;')
    script_list.append('        }')
    script_list.append('        @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_CM] = @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_CM] * 180 / pi;')
    script_list.append('        @target_radar_fr_sim::locdata.loc_elevation_angle[loc_count_RFR_CM] = dllGetElevationAngle(gHandle_star, loc_count_RFR_CM-total_number_of_locations_RFR_CM);')
    script_list.append('  	    @target_radar_fr_sim::locdata.loc_radar_cross_section[loc_count_RFR_CM] = dllGetRcs(gHandle_star, loc_count_RFR_CM-total_number_of_locations_RFR_CM);')
    script_list.append('      }')
    script_list.append('      total_number_of_locations_RFR_CM = total_number_of_locations_RFR_CM + _min(number_of_locs_RFR_CM, @hil_ctrl::starmodel_max_loc_nr);')
    script_list.append('      @target_radar_fr_sim::locdata.number_of_loc = total_number_of_locations_RFR_CM;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  else if(sensor_mod == 2)')
    script_list.append('  { //object based')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fr_sim::objdata.obj_length[object_id], @target_radar_fr_sim::objdata.obj_heading_angle[object_id], @target_radar_fr_sim::objdata.obj_distance_x[object_id], @target_radar_fr_sim::objdata.obj_distance_y[object_id], @target_radar_fr_sim::objdata.obj_velocity_x[object_id],  @target_radar_fr_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fr, @Classe_Obj_Sim::RoadObj.offset_y_fr, @radarfr_par::mounting_ori_yaw, 1, 0);')
    script_list.append('    //calculate the reference point on the target')
    script_list.append('    dllCalcObjectReferencePoint(gHandle_obj, @target_radar_fr_sim::objdata.obj_height[object_id], @target_radar_fr_sim::objdata.obj_width[object_id], @target_radar_fr_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('    ')
    script_list.append('    //basic object data')
    script_list.append('    @target_radar_fr_sim::objdata.obj_distance_x[object_id] = dllGetRCARefptDistX(gHandle_obj);')
    script_list.append('    @target_radar_fr_sim::objdata.obj_distance_y[object_id] = dllGetRCARefptDistY(gHandle_obj);')
    script_list.append('    @target_radar_fr_sim::objdata.obj_velocity_x[object_id] = dllRotationGetRCAVx(gHandle_rot);')
    script_list.append('    @target_radar_fr_sim::objdata.obj_velocity_y[object_id] = dllRotationGetRCAVy(gHandle_rot);')
    script_list.append('    @target_radar_fr_sim::objdata.obj_heading_angle[object_id] = dllRotationGetRCAHeading(gHandle_rot);')
    script_list.append('    @target_radar_fr_sim::objdata.obj_ref_point[object_id] = calc_ref_pnt(dllGetSensorRefpt(gHandle_obj));')
    script_list.append('    ')
    script_list.append('    // type defining')
    script_list.append('    @target_radar_fr_sim::objdata.obj_prob_moving_status[object_id] = calc_moving_status(@target_radar_fr_sim::objdata.obj_velocity_x[object_id], @target_radar_fr_sim::objdata.obj_velocity_y[object_id]);')
    script_list.append('    @target_radar_fr_sim::objdata.obj_prob_obst_class[object_id] = calc_ra6_obj_type(@target_radar_fr_sim::objdata.obj_type[object_id]);')
    script_list.append('    switch(object_id)')
    script_list.append('    {')
    script_list.append('      case 0: @target_radar_fr_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FR::object0::rcsN; break;')
    script_list.append('      case 1: @target_radar_fr_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FR::object1::rcsN; break;')
    script_list.append('      case 2: @target_radar_fr_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FR::object2::rcsN; break;')
    script_list.append('      case 3: @target_radar_fr_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FR::object3::rcsN; break;')
    script_list.append('      case 4: @target_radar_fr_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FR::object4::rcsN; break;')
    script_list.append('      case 5: @target_radar_fr_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FR::object5::rcsN; break;')
    script_list.append('      case 6: @target_radar_fr_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FR::object6::rcsN; break;')
    script_list.append('      case 7: @target_radar_fr_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FR::object7::rcsN; break;')
    script_list.append('      case 8: @target_radar_fr_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FR::object8::rcsN; break;')
    script_list.append('      case 9: @target_radar_fr_sim::objdata.obj_radar_cross_section[object_id] = @CarMaker::RB::Radar::FR::object9::rcsN; break;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('}')
    script_list.append('')
    
    print('Radar_FR for Classe usecase updated successfully.')
    
def update_radar_rl_cm(num_objects):
    """
    Description: Updates the update function of the radar rear left, which calculates further required object/location data.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    global script_list
	# define object-independent script
    script_list.append('/** @brief Update function for the Radar Rear Left which calculates obj/loc data out of the read target data.')
    script_list.append('  *        Sensor model is location(1)/object(2) based')
    script_list.append('  * @return void')
    script_list.append('  */')
    
    script_list.append('void update_radar_rl_cm(byte object_id, int sensor_mod)')
    script_list.append('{')
    
    script_list.append('  if(sensor_mod == 1)')
    script_list.append('  { //location based')
    script_list.append('    ')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_rl_sim::objdata.obj_length[object_id], @target_radar_rl_sim::objdata.obj_heading_angle[object_id], @target_radar_rl_sim::objdata.obj_distance_x[object_id], @target_radar_rl_sim::objdata.obj_distance_y[object_id], @target_radar_rl_sim::objdata.obj_velocity_x[object_id],  @target_radar_rl_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_rl, @Classe_Obj_Sim::RoadObj.offset_y_rl, @radarrl_par::mounting_ori_yaw, 1, 0);')
    script_list.append('    if(@target_radar_rl_sim::locdata.location_model == 0)')
    script_list.append('    { //1obj1loc')
    script_list.append('      //Calculate reference point')
    script_list.append('      dllCalcObjectReferencePoint(gHandle_obj, @target_radar_rl_sim::objdata.obj_height[object_id], @target_radar_rl_sim::objdata.obj_width[object_id], @target_radar_rl_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('      loc_count_RRL_CM=total_number_of_locations_RRL_CM;')
    script_list.append('      ')
    script_list.append('      //Calculate location values using the reference point position')
    script_list.append('      @target_radar_rl_sim::locdata.loc_radial_distance[loc_count_RRL_CM] = calc_radial_distance(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_rl_sim::locdata.loc_radial_velocity[loc_count_RRL_CM] = calc_radial_velocity(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj), dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), @target_radar_fc_sim::locdata.loc_radial_velocity[object_id]);')
    script_list.append('      ')
    script_list.append('      //location angles')
    script_list.append('      @target_radar_rl_sim::locdata.loc_elevation_angle[loc_count_RRL_CM] = calc_elevation_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_CM] = calc_azimuth_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      ')
    script_list.append('      //RCS + SNR')
    script_list.append('      @target_radar_rl_sim::locdata.loc_radar_cross_section[loc_count_RRL_CM] = calc_radar_cross_section(@target_radar_rl_sim::objdata.obj_type[object_id], @target_radar_rl_sim::locdata.loc_radial_distance[object_id]);')
    script_list.append('      @target_radar_rl_sim::locdata.loc_signal_strength_indicator[loc_count_RRL_CM] = 100;')
    script_list.append('	  ')
    script_list.append('      //1obj1loc')
    script_list.append('      total_number_of_locations_RRL_CM = total_number_of_locations_RRL_CM + 1;')
    script_list.append('      @target_radar_rl_sim::locdata.number_of_loc = total_number_of_locations_RRL_CM;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_rl_sim::locdata.location_model == 1)')
    script_list.append('    { //starmodel')
    script_list.append('      resultSetInputValues = dllSetInputValues(gHandle_star, object_id+1, dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot), 0, dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), 0, 0, dllRotationGetSensorHeading(gHandle_rot), @target_radar_rl_sim::objdata.obj_length[object_id], @target_radar_rl_sim::objdata.obj_width[object_id], @target_radar_rl_sim::objdata.obj_height[object_id], @target_radar_rl_sim::objdata.obj_type[object_id]);')
    script_list.append('      resultStarModelRun = dllRunStarModel(gHandle_star, 2);')
    script_list.append('      number_of_locs_RRL_CM = dllGetNumLocs(gHandle_star);')
    script_list.append('      for(loc_count_RRL_CM=total_number_of_locations_RRL_CM; loc_count_RRL_CM < total_number_of_locations_RRL_CM+@hil_ctrl::starmodel_max_loc_nr && loc_count_RRL_CM < total_number_of_locations_RRL_CM+number_of_locs_RRL_CM; loc_count_RRL_CM++)')
    script_list.append('      {')
    script_list.append('        @target_radar_rl_sim::locdata.loc_radial_distance[loc_count_RRL_CM] = dllGetDistance(gHandle_star, loc_count_RRL_CM-total_number_of_locations_RRL_CM);')
    script_list.append('        @target_radar_rl_sim::locdata.loc_radial_velocity[loc_count_RRL_CM] = -dllGetRelativeRadialVelocity(gHandle_star, loc_count_RRL_CM-total_number_of_locations_RRL_CM);')
    script_list.append('        @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_CM] = dllGetAzimuthAngle(gHandle_star, loc_count_RRL_CM-total_number_of_locations_RRL_CM);')
    script_list.append('        if(@target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_CM]>PI) ')
    script_list.append('        {')
    script_list.append('          @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_CM] = @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_CM]-2*PI;')
    script_list.append('        }')
    script_list.append('        @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_CM] = @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_CM] * 180 / pi;')
    script_list.append('        @target_radar_rl_sim::locdata.loc_elevation_angle[loc_count_RRL_CM] = dllGetElevationAngle(gHandle_star, loc_count_RRL_CM-total_number_of_locations_RRL_CM);')
    script_list.append('	    @target_radar_rl_sim::locdata.loc_radar_cross_section[loc_count_RRL_CM] = dllGetRcs(gHandle_star, loc_count_RRL_CM-total_number_of_locations_RRL_CM);')
    script_list.append('    }')
    script_list.append('    total_number_of_locations_RRL_CM = total_number_of_locations_RRL_CM + _min(number_of_locs_RRL_CM, @hil_ctrl::starmodel_max_loc_nr);')
    script_list.append('    @target_radar_rl_sim::locdata.number_of_loc = total_number_of_locations_RRL_CM;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  else if(sensor_mod == 2)')
    script_list.append('  { //object based')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_rl_sim::objdata.obj_length[object_id], @target_radar_rl_sim::objdata.obj_heading_angle[object_id], @target_radar_rl_sim::objdata.obj_distance_x[object_id], @target_radar_rl_sim::objdata.obj_distance_y[object_id], @target_radar_rl_sim::objdata.obj_velocity_x[object_id],  @target_radar_rl_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_rl, @Classe_Obj_Sim::RoadObj.offset_y_rl, @radarrl_par::mounting_ori_yaw, 1, 0);')
    script_list.append('    //calculate the reference point on the target')
    script_list.append('    dllCalcObjectReferencePoint(gHandle_obj, @target_radar_rl_sim::objdata.obj_height[object_id], @target_radar_rl_sim::objdata.obj_width[object_id], @target_radar_rl_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('    ')
    script_list.append('    //basic object data')
    script_list.append('    @target_radar_rl_sim::objdata.obj_distance_x[object_id] = dllGetRCARefptDistX(gHandle_obj);')
    script_list.append('    @target_radar_rl_sim::objdata.obj_distance_y[object_id] = dllGetRCARefptDistY(gHandle_obj);')
    script_list.append('    @target_radar_rl_sim::objdata.obj_velocity_x[object_id] = dllRotationGetRCAVx(gHandle_rot);')
    script_list.append('    @target_radar_rl_sim::objdata.obj_velocity_y[object_id] = dllRotationGetRCAVy(gHandle_rot);')
    script_list.append('    @target_radar_rl_sim::objdata.obj_heading_angle[object_id] = dllRotationGetRCAHeading(gHandle_rot);')
    script_list.append('    @target_radar_rl_sim::objdata.obj_ref_point[object_id] = calc_ref_pnt(dllGetSensorRefpt(gHandle_obj));')
    script_list.append('    ')
    script_list.append('    //probabilities')
    script_list.append('    @target_radar_rl_sim::objdata.obj_prob_moving[object_id] = calc_prob_moving(@target_radar_rl_sim::objdata.obj_velocity_x[object_id], @target_radar_rl_sim::objdata.obj_velocity_y[object_id]);')
    script_list.append('    @target_radar_rl_sim::objdata.obj_prob_non_obst[object_id] = calc_prob_non_obst(@target_radar_rl_sim::objdata.obj_type[object_id]);')
    script_list.append('    @target_radar_rl_sim::objdata.obj_prob_truck[object_id] = calc_prob_truck(@target_radar_rl_sim::objdata.obj_type[object_id]);')
    script_list.append('    @target_radar_rl_sim::objdata.obj_prob_car[object_id] = calc_prob_car(@target_radar_rl_sim::objdata.obj_type[object_id]);')
    script_list.append('    @target_radar_rl_sim::objdata.obj_prob_pedestrian[object_id] = calc_prob_pedestrian(@target_radar_rl_sim::objdata.obj_type[object_id]);')
    script_list.append('    @target_radar_rl_sim::objdata.obj_prob_2wheeler[object_id] = calc_prob_2wheeler(@target_radar_rl_sim::objdata.obj_type[object_id]);')
    script_list.append('  }')
    script_list.append('}')
    script_list.append('')
    
    print('Radar_RL for Classe usecase updated successfully.')

def update_radar_rr_cm(num_objects):
    """
    Description: Updates the update function of the radar rear right, which calculates further required object/location data.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    global script_list
	# define object-independent script
    script_list.append('/** @brief Update function for the Radar Rear Right which calculates obj/loc data out of the read target data.')
    script_list.append('  *        Sensor model is location(1)/object(2) based')
    script_list.append('  * @return void')
    script_list.append('  */')
    
    script_list.append('void update_radar_rr_cm(byte object_id, int sensor_mod)')
    script_list.append('{')
    
    script_list.append('  if(sensor_mod == 1)')
    script_list.append('  { //location based')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_rr_sim::objdata.obj_length[object_id], @target_radar_rr_sim::objdata.obj_heading_angle[object_id], @target_radar_rr_sim::objdata.obj_distance_x[object_id], @target_radar_rr_sim::objdata.obj_distance_y[object_id], @target_radar_rr_sim::objdata.obj_velocity_x[object_id],  @target_radar_rr_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_rr, @Classe_Obj_Sim::RoadObj.offset_y_rr, @radarrr_par::mounting_ori_yaw, 1, 0);')
    script_list.append('    if(@target_radar_rr_sim::locdata.location_model == 0)')
    script_list.append('    { //1obj1loc')
    script_list.append('      //Calculate reference point')
    script_list.append('      dllCalcObjectReferencePoint(gHandle_obj, @target_radar_rr_sim::objdata.obj_height[object_id], @target_radar_rr_sim::objdata.obj_width[object_id], @target_radar_rr_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('      loc_count_RRR_CM=total_number_of_locations_RRR_CM;')
    script_list.append('      ')
    script_list.append('      //Calculate location values using the reference point position')
    script_list.append('      @target_radar_rr_sim::locdata.loc_radial_distance[loc_count_RRR_CM] = calc_radial_distance(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_rr_sim::locdata.loc_radial_velocity[loc_count_RRR_CM] = calc_radial_velocity(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj), dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), @target_radar_fc_sim::locdata.loc_radial_velocity[object_id]);')
    script_list.append('      ')
    script_list.append('      //location angles')
    script_list.append('      @target_radar_rr_sim::locdata.loc_elevation_angle[loc_count_RRR_CM] = calc_elevation_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_CM] = calc_azimuth_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      ')
    script_list.append('      //RCS + SNR')
    script_list.append('      @target_radar_rr_sim::locdata.loc_radar_cross_section[loc_count_RRR_CM] = calc_radar_cross_section(@target_radar_rr_sim::objdata.obj_type[object_id], @target_radar_rr_sim::locdata.loc_radial_distance[object_id]);')
    script_list.append('      @target_radar_rr_sim::locdata.loc_signal_strength_indicator[loc_count_RRR_CM] = 100;')
    script_list.append('	  ')
    script_list.append('      //1obj1loc')
    script_list.append('      total_number_of_locations_RRR_CM = total_number_of_locations_RRR_CM + 1;')
    script_list.append('      @target_radar_rr_sim::locdata.number_of_loc = total_number_of_locations_RRR_CM;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_rr_sim::locdata.location_model == 1)')
    script_list.append('    { //starmodel')
    script_list.append('      resultSetInputValues = dllSetInputValues(gHandle_star, object_id+1, dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot), 0, dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), 0, 0, dllRotationGetSensorHeading(gHandle_rot), @target_radar_rr_sim::objdata.obj_length[object_id], @target_radar_rr_sim::objdata.obj_width[object_id], @target_radar_rr_sim::objdata.obj_height[object_id], @target_radar_rr_sim::objdata.obj_type[object_id]);')
    script_list.append('      resultStarModelRun = dllRunStarModel(gHandle_star, 2);')
    script_list.append('      number_of_locs_RRR_CM = dllGetNumLocs(gHandle_star);')
    script_list.append('      for(loc_count_RRR_CM=total_number_of_locations_RRR_CM; loc_count_RRR_CM < total_number_of_locations_RRR_CM+@hil_ctrl::starmodel_max_loc_nr && loc_count_RRR_CM < total_number_of_locations_RRR_CM+number_of_locs_RRR_CM; loc_count_RRR_CM++)')
    script_list.append('      {')
    script_list.append('        @target_radar_rr_sim::locdata.loc_radial_distance[loc_count_RRR_CM] = dllGetDistance(gHandle_star, loc_count_RRR_CM-total_number_of_locations_RRR_CM);')
    script_list.append('        @target_radar_rr_sim::locdata.loc_radial_velocity[loc_count_RRR_CM] = -dllGetRelativeRadialVelocity(gHandle_star, loc_count_RRR_CM-total_number_of_locations_RRR_CM);')
    script_list.append('        @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_CM] = dllGetAzimuthAngle(gHandle_star, loc_count_RRR_CM-total_number_of_locations_RRR_CM);')
    script_list.append('        if(@target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_CM]>PI) ')
    script_list.append('        {')
    script_list.append('          @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_CM] = @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_CM]-2*PI;')
    script_list.append('        }')
    script_list.append('        @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_CM] = @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_CM] * 180 / pi;')
    script_list.append('        @target_radar_rr_sim::locdata.loc_elevation_angle[loc_count_RRR_CM] = dllGetElevationAngle(gHandle_star, loc_count_RRR_CM-total_number_of_locations_RRR_CM);')
    script_list.append('  	    @target_radar_rr_sim::locdata.loc_radar_cross_section[loc_count_RRR_CM] = dllGetRcs(gHandle_star, loc_count_RRR_CM-total_number_of_locations_RRR_CM);')
    script_list.append('      }')
    script_list.append('      total_number_of_locations_RRR_CM = total_number_of_locations_RRR_CM + _min(number_of_locs_RRR_CM, @hil_ctrl::starmodel_max_loc_nr);')
    script_list.append('      @target_radar_rr_sim::locdata.number_of_loc = total_number_of_locations_RRR_CM;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  else if(sensor_mod == 2)')
    script_list.append('  { //object based')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_rr_sim::objdata.obj_length[object_id], @target_radar_rr_sim::objdata.obj_heading_angle[object_id], @target_radar_rr_sim::objdata.obj_distance_x[object_id], @target_radar_rr_sim::objdata.obj_distance_y[object_id], @target_radar_rr_sim::objdata.obj_velocity_x[object_id],  @target_radar_rr_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_rr, @Classe_Obj_Sim::RoadObj.offset_y_rr, @radarrr_par::mounting_ori_yaw, 1, 0);')
    script_list.append('    //calculate the reference point on the target')
    script_list.append('    dllCalcObjectReferencePoint(gHandle_obj, @target_radar_rr_sim::objdata.obj_height[object_id], @target_radar_rr_sim::objdata.obj_width[object_id], @target_radar_rr_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('    ')
    script_list.append('    //basic object data')
    script_list.append('    @target_radar_rr_sim::objdata.obj_distance_x[object_id] = dllGetRCARefptDistX(gHandle_obj);')
    script_list.append('    @target_radar_rr_sim::objdata.obj_distance_y[object_id] = dllGetRCARefptDistY(gHandle_obj);')
    script_list.append('    @target_radar_rr_sim::objdata.obj_velocity_x[object_id] = dllRotationGetRCAVx(gHandle_rot);')
    script_list.append('    @target_radar_rr_sim::objdata.obj_velocity_y[object_id] = dllRotationGetRCAVy(gHandle_rot);')
    script_list.append('    @target_radar_rr_sim::objdata.obj_heading_angle[object_id] = dllRotationGetRCAHeading(gHandle_rot);')
    script_list.append('    @target_radar_rr_sim::objdata.obj_ref_point[object_id] = calc_ref_pnt(dllGetSensorRefpt(gHandle_obj));')
    script_list.append('    ')
    script_list.append('    //probabilities')
    script_list.append('    @target_radar_rr_sim::objdata.obj_prob_moving[object_id] = calc_prob_moving(@target_radar_rr_sim::objdata.obj_velocity_x[object_id], @target_radar_rr_sim::objdata.obj_velocity_y[object_id]);')
    script_list.append('    @target_radar_rr_sim::objdata.obj_prob_non_obst[object_id] = calc_prob_non_obst(@target_radar_rr_sim::objdata.obj_type[object_id]);')
    script_list.append('    @target_radar_rr_sim::objdata.obj_prob_truck[object_id] = calc_prob_truck(@target_radar_rr_sim::objdata.obj_type[object_id]);')
    script_list.append('    @target_radar_rr_sim::objdata.obj_prob_car[object_id] = calc_prob_car(@target_radar_rr_sim::objdata.obj_type[object_id]);')
    script_list.append('    @target_radar_rr_sim::objdata.obj_prob_pedestrian[object_id] = calc_prob_pedestrian(@target_radar_rr_sim::objdata.obj_type[object_id]);')
    script_list.append('    @target_radar_rr_sim::objdata.obj_prob_2wheeler[object_id] = calc_prob_2wheeler(@target_radar_rr_sim::objdata.obj_type[object_id]);')
    script_list.append('  }')
    script_list.append('}')
    script_list.append('')
    
    print('Radar_RR for Classe usecase updated successfully.')
    
def update_traffic_obj_ctrl():
    """
    Description: Updates the traffic control function.

    Returns: Void

    """
    global script_list
	# define object-independent script
    script_list.append('/** @brief Reads the controlled object data')
    script_list.append('  * @return void')
    script_list.append('  */')
  
    script_list.append('void read_CM_traffic_obj_ctrl_data()')
    script_list.append('{')
    script_list.append('  // -------------------------')
    script_list.append('  // Target obj control output')
    script_list.append('  ')
    script_list.append('  if(@hil_ctrl::init_cm_done == @hil_ctrl::init_cm_done::done)')
    script_list.append('  {')
    script_list.append('    @Classe_Obj_Sim::obj_ctrl.nbr_of_obj = @CarMaker::RB::TrafficObj::nObjs;')
    script_list.append('    t_stamp_us = @CarMaker::RB::TrafficObj::tStamp;')
    script_list.append('    ')
    script_list.append('    g_ext_traffic_obj[0].lat_offset = @CarMaker::RB::TrafficObj::object0::tRoad;')
    script_list.append('    g_ext_traffic_obj[1].lat_offset = @CarMaker::RB::TrafficObj::object1::tRoad;')
    script_list.append('    g_ext_traffic_obj[2].lat_offset = @CarMaker::RB::TrafficObj::object2::tRoad;')
    script_list.append('    g_ext_traffic_obj[3].lat_offset = @CarMaker::RB::TrafficObj::object3::tRoad;')
    script_list.append('    g_ext_traffic_obj[4].lat_offset = @CarMaker::RB::TrafficObj::object4::tRoad;')
    script_list.append('    g_ext_traffic_obj[5].lat_offset = @CarMaker::RB::TrafficObj::object5::tRoad;')
    script_list.append('    g_ext_traffic_obj[6].lat_offset = 0;')
    script_list.append('    g_ext_traffic_obj[7].lat_offset = 0;')
    script_list.append('    g_ext_traffic_obj[8].lat_offset = 0;')
    script_list.append('    g_ext_traffic_obj[9].lat_offset = 0;')
    script_list.append('    ')
    script_list.append('    g_ext_traffic_obj[0].v_long = @CarMaker::RB::TrafficObj::object0::LongVel * 3.6;')
    script_list.append('    g_ext_traffic_obj[1].v_long = @CarMaker::RB::TrafficObj::object1::LongVel * 3.6;')
    script_list.append('    g_ext_traffic_obj[2].v_long = @CarMaker::RB::TrafficObj::object2::LongVel * 3.6;')
    script_list.append('    g_ext_traffic_obj[3].v_long = @CarMaker::RB::TrafficObj::object3::LongVel * 3.6;')
    script_list.append('    g_ext_traffic_obj[4].v_long = @CarMaker::RB::TrafficObj::object4::LongVel * 3.6;')
    script_list.append('    g_ext_traffic_obj[5].v_long = @CarMaker::RB::TrafficObj::object5::LongVel * 3.6;')
    script_list.append('    g_ext_traffic_obj[6].v_long = 0;')
    script_list.append('    g_ext_traffic_obj[7].v_long = 0;')
    script_list.append('    g_ext_traffic_obj[8].v_long = 0;')
    script_list.append('    g_ext_traffic_obj[9].v_long = 0;')
    script_list.append('    ')
    script_list.append('    g_ext_traffic_obj[0].pos_x = @CarMaker::RB::TrafficObj::object0::dtx;')
    script_list.append('    g_ext_traffic_obj[1].pos_x = @CarMaker::RB::TrafficObj::object1::dtx;')
    script_list.append('    g_ext_traffic_obj[2].pos_x = @CarMaker::RB::TrafficObj::object2::dtx;')
    script_list.append('    g_ext_traffic_obj[3].pos_x = @CarMaker::RB::TrafficObj::object3::dtx;')
    script_list.append('    g_ext_traffic_obj[4].pos_x = @CarMaker::RB::TrafficObj::object4::dtx;')
    script_list.append('    g_ext_traffic_obj[5].pos_x = @CarMaker::RB::TrafficObj::object5::dtx;')
    script_list.append('    g_ext_traffic_obj[6].pos_x = 0;')
    script_list.append('    g_ext_traffic_obj[7].pos_x = 0;')
    script_list.append('    g_ext_traffic_obj[8].pos_x = 0;')
    script_list.append('    g_ext_traffic_obj[9].pos_x = 0;')
    script_list.append('    ')
    script_list.append('    g_ext_traffic_obj[0].pos_y = @CarMaker::RB::TrafficObj::object0::dty;')
    script_list.append('    g_ext_traffic_obj[1].pos_y = @CarMaker::RB::TrafficObj::object1::dty;')
    script_list.append('    g_ext_traffic_obj[2].pos_y = @CarMaker::RB::TrafficObj::object2::dty;')
    script_list.append('    g_ext_traffic_obj[3].pos_y = @CarMaker::RB::TrafficObj::object3::dty;')
    script_list.append('    g_ext_traffic_obj[4].pos_y = @CarMaker::RB::TrafficObj::object4::dty;')
    script_list.append('    g_ext_traffic_obj[5].pos_y = @CarMaker::RB::TrafficObj::object5::dty;')
    script_list.append('    g_ext_traffic_obj[6].pos_y = 0;')
    script_list.append('    g_ext_traffic_obj[7].pos_y = 0;')
    script_list.append('    g_ext_traffic_obj[8].pos_y = 0;')
    script_list.append('    g_ext_traffic_obj[9].pos_y = 0;')
    script_list.append('    ')
    script_list.append('    g_ext_traffic_obj[0].rot_z = @CarMaker::RB::TrafficObj::object0::drz;')
    script_list.append('    g_ext_traffic_obj[1].rot_z = @CarMaker::RB::TrafficObj::object1::drz;')
    script_list.append('    g_ext_traffic_obj[2].rot_z = @CarMaker::RB::TrafficObj::object2::drz;')
    script_list.append('    g_ext_traffic_obj[3].rot_z = @CarMaker::RB::TrafficObj::object3::drz;')
    script_list.append('    g_ext_traffic_obj[4].rot_z = @CarMaker::RB::TrafficObj::object4::drz;')
    script_list.append('    g_ext_traffic_obj[5].rot_z = @CarMaker::RB::TrafficObj::object5::drz;')
    script_list.append('    g_ext_traffic_obj[6].rot_z = 0;')
    script_list.append('    g_ext_traffic_obj[7].rot_z = 0;')
    script_list.append('    g_ext_traffic_obj[8].rot_z = 0;')
    script_list.append('    g_ext_traffic_obj[9].rot_z = 0;')
    script_list.append('    ')
    script_list.append('    g_ext_traffic_obj[0].a_lat = @CarMaker::RB::TrafficObj::object0::LatAcc;')
    script_list.append('    g_ext_traffic_obj[1].a_lat = @CarMaker::RB::TrafficObj::object1::LatAcc;')
    script_list.append('    g_ext_traffic_obj[2].a_lat = @CarMaker::RB::TrafficObj::object2::LatAcc;')
    script_list.append('    g_ext_traffic_obj[3].a_lat = @CarMaker::RB::TrafficObj::object3::LatAcc;')
    script_list.append('    g_ext_traffic_obj[4].a_lat = @CarMaker::RB::TrafficObj::object4::LatAcc;')
    script_list.append('    g_ext_traffic_obj[5].a_lat = @CarMaker::RB::TrafficObj::object5::LatAcc;')
    script_list.append('    g_ext_traffic_obj[6].a_lat = @CarMaker::RB::TrafficObj::object6::LatAcc;')
    script_list.append('    g_ext_traffic_obj[7].a_lat = @CarMaker::RB::TrafficObj::object7::LatAcc;')
    script_list.append('    g_ext_traffic_obj[8].a_lat = @CarMaker::RB::TrafficObj::object8::LatAcc;')
    script_list.append('    g_ext_traffic_obj[9].a_lat = @CarMaker::RB::TrafficObj::object9::LatAcc;')
    script_list.append('    ')
    script_list.append('    g_ext_traffic_obj[0].a_long = 0; // @CarMaker::RB::TrafficObj::object0::LongAcc;')
    script_list.append('    g_ext_traffic_obj[1].a_long = 0; // @CarMaker::RB::TrafficObj::object1::LongAcc;')
    script_list.append('    g_ext_traffic_obj[2].a_long = 0; // @CarMaker::RB::TrafficObj::object2::LongAcc;')
    script_list.append('    g_ext_traffic_obj[3].a_long = 0; // @CarMaker::RB::TrafficObj::object3::LongAcc;')
    script_list.append('    g_ext_traffic_obj[4].a_long = 0; // @CarMaker::RB::TrafficObj::object4::LongAcc;')
    script_list.append('    g_ext_traffic_obj[5].a_long = 0; // @CarMaker::RB::TrafficObj::object5::LongAcc;')
    script_list.append('    g_ext_traffic_obj[6].a_long = 0;')
    script_list.append('    g_ext_traffic_obj[7].a_long = 0;')
    script_list.append('    g_ext_traffic_obj[8].a_long = 0;')
    script_list.append('    g_ext_traffic_obj[9].a_long = 0;')
    script_list.append('  }')
    script_list.append('}')