# -*- coding: utf-8 -*-
# @file RoadObj_gen_Map_Classe.py
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
 * @file Map_Classe.cin
 * @author ADAS_HIL_TEAM
 * @date 03-21-2023
 * @brief Handles mapping for Classe usecase for all sensors
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
  int counter_Classe = 0;
  int target_count_Classe = 0;
  
  //Star Model
  int loc_count_RFC_Classe = 0;
  int loc_count_RFL_Classe = 0;
  int loc_count_RFR_Classe = 0;
  int loc_count_RRL_Classe = 0;
  int loc_count_RRR_Classe = 0;
  
  int number_of_locs_RFC_Classe = 0;
  int number_of_locs_RFL_Classe = 0;
  int number_of_locs_RFR_Classe = 0;
  int number_of_locs_RRL_Classe = 0;
  int number_of_locs_RRR_Classe = 0;
  
  int total_number_of_locations_RFC_Classe = 0;
  int total_number_of_locations_RFL_Classe = 0;
  int total_number_of_locations_RFR_Classe = 0;
  int total_number_of_locations_RRL_Classe = 0;
  int total_number_of_locations_RRR_Classe = 0;
  
  //Field of View
  double fov_dx_fvideo[20];
  double fov_dx_radar_fc[20];
  double fov_dx_radar_fl[20];
  double fov_dx_radar_fr[20];
  double fov_dx_radar_rl[20];
  double fov_dx_radar_rr[20];
  double fov_dy_fvideo[20];
  double fov_dy_radar_fc[20];
  double fov_dy_radar_fl[20];
  double fov_dy_radar_fr[20];
  double fov_dy_radar_rl[20];
  double fov_dy_radar_rr[20];
  
  // Clara Model
  int clara_run_fc_Classe = 0;
  int clara_run_fl_Classe = 0;
  int clara_run_fr_Classe = 0;
  int clara_run_rl_Classe = 0;
  int clara_run_rr_Classe = 0;
  
  int clara_radar_fc_deletion_needed_Classe[20];
  int clara_radar_fl_deletion_needed_Classe[20];
  int clara_radar_fr_deletion_needed_Classe[20];
  int clara_radar_rl_deletion_needed_Classe[20];
  int clara_radar_rr_deletion_needed_Classe[20];
}
'''

def update_Map_Classe(file_path, num_objects):
    """
    Description: Main function for updating the update file for the Classe usecase. Orchestrates the update functions and saves the data in the file.

    Args:
      file_path: Path of the file which shall be updated/generated.
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    global script_list
    script_list = [Header]
    
    update_Classe_reading(num_objects)
    update_Classe_offsets()
    calculate_valid_Classe_targets(num_objects)
    update_Classe_mapping()
    read_Classe_fov(num_objects)
    
    update_radar_fc_classe(num_objects)
    update_fvideo_classe(num_objects)
    update_radar_fl_classe(num_objects)
    update_radar_fr_classe(num_objects)
    update_radar_rl_classe(num_objects)
    update_radar_rr_classe(num_objects)
    
    
    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

def update_Classe_reading(num_objects):
    """
    Description: Updates the reading function with reads the raw target data of the Classe simulator and stores it into the target array of each sensor.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    script_list.append('/** @brief Reading Classe values, Classe is sending everything in reference to the rear center axle (RCA).')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void read_Classe_data(){')
    
    script_list.append('  /**')
    script_list.append('    * Radar FC')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_distance_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dx[{obj_id}];')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_distance_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dy[{obj_id}];')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_velocity_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vx[{obj_id}];')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_velocity_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vy[{obj_id}];')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_acceleration_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ax[{obj_id}];')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_acceleration_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ay[{obj_id}];')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_type[{obj_id}] = @Classe_Obj_Sim::objdata.obj_type[{obj_id}];')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_width[{obj_id}] = @Classe_Obj_Sim::objdata.obj_width[{obj_id}];')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_length[{obj_id}] = calc_target_length(@target_radar_fc_sim::objdata.obj_type[{obj_id}]);')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append(f'  @target_radar_fc_sim::objdata.obj_heading_angle[{obj_id}] = calc_heading_angle(@Classe_Obj_Sim::objdata.obj_vx[{obj_id}], @Classe_Obj_Sim::objdata.obj_vy[{obj_id}]);')
        script_list.append('  ')
    
    script_list.append('  /**')
    script_list.append('    * Front Video')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_fvideo_sim::objdata.obj_distance_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dx[{obj_id}];')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_distance_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dy[{obj_id}];')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_velocity_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vx[{obj_id}];')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_velocity_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vy[{obj_id}];')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_acceleration_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ax[{obj_id}];')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_acceleration_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ay[{obj_id}];')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_type[{obj_id}] = @Classe_Obj_Sim::objdata.obj_type[{obj_id}];')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_width[{obj_id}] = @Classe_Obj_Sim::objdata.obj_width[{obj_id}];')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_length[{obj_id}] = calc_target_length(@target_fvideo_sim::objdata.obj_type[{obj_id}]);')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append(f'  @target_fvideo_sim::objdata.obj_heading_angle[{obj_id}] = calc_heading_angle(@Classe_Obj_Sim::objdata.obj_vx[{obj_id}], @Classe_Obj_Sim::objdata.obj_vy[{obj_id}]);')
        script_list.append('  ')
    
    script_list.append('  /**')
    script_list.append('    * Radar FL')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_distance_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dx[{obj_id}];')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_distance_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dy[{obj_id}];')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_velocity_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vx[{obj_id}];')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_velocity_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vy[{obj_id}];')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_acceleration_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ax[{obj_id}];')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_acceleration_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ay[{obj_id}];')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_type[{obj_id}] = @Classe_Obj_Sim::objdata.obj_type[{obj_id}];')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_width[{obj_id}] = @Classe_Obj_Sim::objdata.obj_width[{obj_id}];')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_length[{obj_id}] = calc_target_length(@target_radar_fl_sim::objdata.obj_type[{obj_id}]);')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append(f'  @target_radar_fl_sim::objdata.obj_heading_angle[{obj_id}] = calc_heading_angle(@Classe_Obj_Sim::objdata.obj_vx[{obj_id}], @Classe_Obj_Sim::objdata.obj_vy[{obj_id}]);')
        script_list.append('  ')
    
    script_list.append('  /**')
    script_list.append('    * Radar FR')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_distance_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dx[{obj_id}];')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_distance_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dy[{obj_id}];')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_velocity_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vx[{obj_id}];')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_velocity_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vy[{obj_id}];')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_acceleration_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ax[{obj_id}];')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_acceleration_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ay[{obj_id}];')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_type[{obj_id}] = @Classe_Obj_Sim::objdata.obj_type[{obj_id}];')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_width[{obj_id}] = @Classe_Obj_Sim::objdata.obj_width[{obj_id}];')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_length[{obj_id}] = calc_target_length(@target_radar_fr_sim::objdata.obj_type[{obj_id}]);')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append(f'  @target_radar_fr_sim::objdata.obj_heading_angle[{obj_id}] = calc_heading_angle(@Classe_Obj_Sim::objdata.obj_vx[{obj_id}], @Classe_Obj_Sim::objdata.obj_vy[{obj_id}]);')
        script_list.append('  ')
    
    script_list.append('  /**')
    script_list.append('    * Radar RL')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_distance_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dx[{obj_id}];')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_distance_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dy[{obj_id}];')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_velocity_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vx[{obj_id}];')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_velocity_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vy[{obj_id}];')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_acceleration_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ax[{obj_id}];')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_acceleration_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ay[{obj_id}];')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_type[{obj_id}] = @Classe_Obj_Sim::objdata.obj_type[{obj_id}];')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_width[{obj_id}] = @Classe_Obj_Sim::objdata.obj_width[{obj_id}];')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_length[{obj_id}] = calc_target_length(@target_radar_rl_sim::objdata.obj_type[{obj_id}]);')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append(f'  @target_radar_rl_sim::objdata.obj_heading_angle[{obj_id}] = calc_heading_angle(@Classe_Obj_Sim::objdata.obj_vx[{obj_id}], @Classe_Obj_Sim::objdata.obj_vy[{obj_id}]);')
        script_list.append('  ')
    
    script_list.append('  /**')
    script_list.append('    * Radar RR')
    script_list.append('    */')
    for obj_index in range(num_objects):
        obj_id = obj_index
        
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_distance_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dx[{obj_id}];')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_distance_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_dy[{obj_id}];')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_velocity_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vx[{obj_id}];')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_velocity_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_relative_vy[{obj_id}];')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_acceleration_x[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ax[{obj_id}];')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_acceleration_y[{obj_id}] = @Classe_Obj_Sim::objdata.obj_ay[{obj_id}];')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_type[{obj_id}] = @Classe_Obj_Sim::objdata.obj_type[{obj_id}];')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_width[{obj_id}] = @Classe_Obj_Sim::objdata.obj_width[{obj_id}];')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_length[{obj_id}] = calc_target_length(@target_radar_rr_sim::objdata.obj_type[{obj_id}]);')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_height[{obj_id}] = 1.5;')
        script_list.append(f'  @target_radar_rr_sim::objdata.obj_heading_angle[{obj_id}] = calc_heading_angle(@Classe_Obj_Sim::objdata.obj_vx[{obj_id}], @Classe_Obj_Sim::objdata.obj_vy[{obj_id}]);')
        script_list.append('  ')
    script_list.append('}')
    script_list.append('')

def update_Classe_offsets():
    """
    Description: Updates the function which sets the mounting positions for each sensor.

    Returns: Void

    """
    script_list.append('/** @brief Set offsets')
    script_list.append('  *            Distances from rear center axle (RCA) to sensor mounting position')
    script_list.append('  *            Only x and y coordinates are taken into account')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void set_Classe_offsets(){')
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

def update_Classe_mapping():
    """
    Description: Updates the main function in the mapping file.

    Returns: Void

    """
    script_list.append('/** @brief Main function to read all necessary data and calculate valid targets.')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void map_classe(){')
    script_list.append('  set_Classe_offsets();')
    script_list.append('  read_Classe_data();')
    script_list.append('  update_distances_for_fov_calc();')
    script_list.append('  calculcate_valid_Classe_targets();')
    script_list.append('  ')
    script_list.append('  clara_run_fc_Classe = 1;  // flag to run Clara model')
    script_list.append('}')
    script_list.append('')

def calculate_valid_Classe_targets(num_objects):
    """
    Description: Updates the function for defining which targets are valid and setting of the validity flags accordingly.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    script_list.append('/** @brief Calculation of number of detected VALID targets for all the sensors and setting of validity and empty obj flags accordingly.')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void calculcate_valid_Classe_targets(){')
    script_list.append('  //Radar Front Center')
    script_list.append('  target_count_Classe = 0;')
    script_list.append('  counter_Classe = 0;')
    script_list.append('  ')
    script_list.append(f'  for (counter_Classe = 0; counter_Classe < {num_objects}; counter_Classe++)')
    script_list.append('  {')
    script_list.append('    if(fov_dx_radar_fc[counter_Classe] > 0 && @Classe_Obj_Sim::objdata.obj_sim_fradar_on[counter_Classe] == 1){  //FOV && Sensor is being used on this obj')
    script_list.append('      //this object is valid')
    script_list.append('      target_count_Classe++;')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_FC[counter_Classe] = 1;')
    script_list.append('      @target_radar_fc_sim::objdata.empty_obj[counter_Classe] = 0;')
    script_list.append('      ')
    script_list.append('    }else{')
    script_list.append('      //this object is not valid, setting of the validity flags according to the chosen mode')
    script_list.append('      if(@Classe_Obj_Sim::ValidityFlags.validity_radar_fc_loc_on == 0 && @Classe_Obj_Sim::ValidityFlags.validity_radar_fc_obj_on == 0){')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_FC[counter_Classe] = 1;')
    script_list.append('        @target_radar_fc_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('        ')
    script_list.append('      }else{')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_FC[counter_Classe] = 0;')
    script_list.append('        @target_radar_fc_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('      }')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  @target_radar_fc_sim::objdata.number_of_obj = target_count_Classe;')
    script_list.append('  if(@hil_ctrl::radar_fc_loc_sim > 0)')
    script_list.append('  { //location based')
    script_list.append('    @target_radar_fc_sim::locdata.number_of_loc = 0;')
    script_list.append('    total_number_of_locations_RFC_Classe = 0;')
    script_list.append('  }')  
    script_list.append('  ')
    
    script_list.append('  //Front Video')
    script_list.append('  target_count_Classe = 0;')
    script_list.append(f'  for (counter_Classe = 0; counter_Classe < {num_objects}; counter_Classe++)')
    script_list.append('  {')
    script_list.append('    if(fov_dx_fvideo[counter_Classe] > 0 && @Classe_Obj_Sim::objdata.obj_sim_fvideo_on[counter_Classe] == 1){  //FOV && Sensor is being used on this obj')
    script_list.append('      //this object is valid')
    script_list.append('      target_count_Classe++;')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_FV[counter_Classe] = 1;')
    script_list.append('      @target_fvideo_sim::objdata.empty_obj[counter_Classe] = 0;')
    script_list.append('      ')
    script_list.append('    }else{')
    script_list.append('      //this object is not valid, setting of the validity flags according to the chosen mode')
    script_list.append('      if(@Classe_Obj_Sim::ValidityFlags.validity_fvideo_on == 0){')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_FV[counter_Classe] = 1;')
    script_list.append('        @target_fvideo_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('        ')
    script_list.append('      }else{')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_FV[counter_Classe] = 0;')
    script_list.append('        @target_fvideo_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('      }')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  @target_fvideo_sim::objdata.number_of_obj = target_count_Classe;')
    script_list.append('  ')
    
    script_list.append('  //Radar Front Left')
    script_list.append('  target_count_Classe = 0;')
    script_list.append(f'  for (counter_Classe = 0; counter_Classe < {num_objects}; counter_Classe++)')
    script_list.append('  {')
    script_list.append('    if(fov_dx_radar_fl[counter_Classe] > 0){')
    script_list.append('      if(arctan(fov_dy_radar_fl[counter_Classe] / fov_dx_radar_fl[counter_Classe]) < 1.30883 ')
    script_list.append('        && arctan(fov_dy_radar_fl[counter_Classe] / fov_dx_radar_fl[counter_Classe]) > -1.30883')
    script_list.append('        && @Classe_Obj_Sim::objdata.obj_sim_cradarfl_on[counter_Classe] == 1){  //+-75° FOV + Sensor is being used on this obj')
    script_list.append('        //this object is valid')
    script_list.append('        target_count_Classe++;')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_RFL[counter_Classe] = 1;')
    script_list.append('        @target_radar_fl_sim::objdata.empty_obj[counter_Classe] = 0;')
    script_list.append('        ')
    script_list.append('      }else{')
    script_list.append('        //this object is not valid, setting of the validity flags according to the chosen mode')
    script_list.append('        if(@Classe_Obj_Sim::ValidityFlags.validity_radar_fl_on == 0){')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RFL[counter_Classe] = 1;')
    script_list.append('          @target_radar_fl_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('          ')
    script_list.append('        }else{')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RFL[counter_Classe] = 0;')
    script_list.append('          @target_radar_fl_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('        }')
    script_list.append('      }')
    script_list.append('    }else if(@Classe_Obj_Sim::ValidityFlags.validity_radar_fl_on == 0){')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RFL[counter_Classe] = 1;')
    script_list.append('          @target_radar_fl_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('    }else{')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_RFL[counter_Classe] = 0;')
    script_list.append('      @target_radar_fl_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  @target_radar_fl_sim::objdata.number_of_obj = target_count_Classe;')
    script_list.append('  if(@hil_ctrl::radar_fl_loc_sim > 0)')
    script_list.append('  { //location based')
    script_list.append('    @target_radar_fl_sim::locdata.number_of_loc = 0;')
    script_list.append('    total_number_of_locations_RFL_Classe = 0;')
    script_list.append('  }')
    script_list.append('  ')
    
    script_list.append('  //Radar Front Right')
    script_list.append('  target_count_Classe = 0;')
    script_list.append(f'  for (counter_Classe = 0; counter_Classe < {num_objects}; counter_Classe++)')
    script_list.append('  {')
    script_list.append('    if(fov_dx_radar_fr[counter_Classe] > 0){')
    script_list.append('      if(arctan(fov_dy_radar_fr[counter_Classe] / fov_dx_radar_fr[counter_Classe]) < 1.30883  ')
    script_list.append('        && arctan(fov_dy_radar_fr[counter_Classe] / fov_dx_radar_fr[counter_Classe]) > -1.30883  ')
    script_list.append('        && @Classe_Obj_Sim::objdata.obj_sim_cradarfr_on[counter_Classe] == 1){  //+-75° FOV + Sensor is being used on this obj')
    script_list.append('        //this object is valid')
    script_list.append('        target_count_Classe++;')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_RFR[counter_Classe] = 1;')
    script_list.append('        @target_radar_fr_sim::objdata.empty_obj[counter_Classe] = 0;')
    script_list.append('        ')
    script_list.append('      }else{')
    script_list.append('        //this object is not valid, setting of the validity flags according to the chosen mode')
    script_list.append('        if(@Classe_Obj_Sim::ValidityFlags.validity_radar_fr_on == 0){')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RFR[counter_Classe] = 1;')
    script_list.append('          @target_radar_fr_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('          ')
    script_list.append('        }else{')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RFR[counter_Classe] = 0;')
    script_list.append('          @target_radar_fr_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('        }')
    script_list.append('      }')
    script_list.append('    }else if(@Classe_Obj_Sim::ValidityFlags.validity_radar_fr_on == 0){')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RFR[counter_Classe] = 1;')
    script_list.append('          @target_radar_fr_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('    }else{')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_RFR[counter_Classe] = 0;')
    script_list.append('      @target_radar_fr_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  @target_radar_fr_sim::objdata.number_of_obj = target_count_Classe;')
    script_list.append('  if(@hil_ctrl::radar_fr_loc_sim > 0)')
    script_list.append('  { //location based')
    script_list.append('    @target_radar_fr_sim::locdata.number_of_loc = 0;')
    script_list.append('    total_number_of_locations_RFR_Classe = 0;')
    script_list.append('  }')
    script_list.append('  ')

    script_list.append('  //Radar Rear Left')
    script_list.append('  target_count_Classe = 0;')
    script_list.append('  for (counter_Classe = 0; counter_Classe < 9; counter_Classe++)')
    script_list.append('  {')
    script_list.append('    if(fov_dx_radar_rl[counter_Classe] > 0){')
    script_list.append('      if(arctan(fov_dy_radar_rl[counter_Classe] / fov_dx_radar_rl[counter_Classe]) < 1.30883  ')
    script_list.append('        && arctan(fov_dy_radar_rl[counter_Classe] / fov_dx_radar_rl[counter_Classe]) > -1.30883  ')
    script_list.append('        && @Classe_Obj_Sim::objdata.obj_sim_cradarrl_on[counter_Classe] == 1){  //+-75° FOV + Sensor is being used on this obj')
    script_list.append('        //this object is valid')
    script_list.append('        target_count_Classe++;')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_RRL[counter_Classe] = 1;')
    script_list.append('        @target_radar_rl_sim::objdata.empty_obj[counter_Classe] = 0;')
    script_list.append('        ')
    script_list.append('      }else{')
    script_list.append('        //this object is not valid, setting of the validity flags according to the chosen mode')
    script_list.append('        if(@Classe_Obj_Sim::ValidityFlags.validity_radar_rl_on == 0){')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RRL[counter_Classe] = 1;')
    script_list.append('          @target_radar_rl_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('          ')
    script_list.append('        }else{')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RRL[counter_Classe] = 0;')
    script_list.append('          @target_radar_rl_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('        }')
    script_list.append('      }')
    script_list.append('    }else if(@Classe_Obj_Sim::ValidityFlags.validity_radar_rl_on == 0){')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RRL[counter_Classe] = 1;')
    script_list.append('          @target_radar_rl_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('    }else{')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_RRL[counter_Classe] = 0;')
    script_list.append('      @target_radar_rl_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  @target_radar_rl_sim::objdata.number_of_obj = target_count_Classe;')
    script_list.append('  if(@hil_ctrl::radar_rl_loc_sim > 0)')
    script_list.append('  { //location based')
    script_list.append('    @target_radar_rl_sim::locdata.number_of_loc = 0;')
    script_list.append('    total_number_of_locations_RRL_Classe = 0;')
    script_list.append('  }')
    script_list.append('  ')
    
    script_list.append('  //Radar Rear Right')
    script_list.append('  target_count_Classe = 0;')
    script_list.append('  for (counter_Classe = 0; counter_Classe < 9; counter_Classe++)')
    script_list.append('  {')
    script_list.append('    if(fov_dx_radar_rr[counter_Classe] > 0){')
    script_list.append('      if(arctan(fov_dy_radar_rr[counter_Classe] / fov_dx_radar_rr[counter_Classe]) < 1.30883  ')
    script_list.append('        && arctan(fov_dy_radar_rr[counter_Classe] / fov_dx_radar_rr[counter_Classe]) > -1.30883  ')
    script_list.append('        && @Classe_Obj_Sim::objdata.obj_sim_cradarrr_on[counter_Classe] == 1){  //+-75° FOV + Sensor is being used on this obj')
    script_list.append('        //this object is valid')
    script_list.append('        target_count_Classe++;')
    script_list.append('        @Classe_Obj_Sim::ValidityFlags.validityFlag_RRR[counter_Classe] = 1;')
    script_list.append('        @target_radar_rr_sim::objdata.empty_obj[counter_Classe] = 0;')
    script_list.append('        ')
    script_list.append('      }else{')
    script_list.append('        //this object is not valid, setting of the validity flags according to the chosen mode')
    script_list.append('        if(@Classe_Obj_Sim::ValidityFlags.validity_radar_rr_on == 0){')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RRR[counter_Classe] = 1;')
    script_list.append('          @target_radar_rr_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('          ')
    script_list.append('        }else{')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RRR[counter_Classe] = 0;')
    script_list.append('          @target_radar_rr_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('        }')
    script_list.append('      }')
    script_list.append('    }else if(@Classe_Obj_Sim::ValidityFlags.validity_radar_rr_on == 0){')
    script_list.append('          @Classe_Obj_Sim::ValidityFlags.validityFlag_RRR[counter_Classe] = 1;')
    script_list.append('          @target_radar_rr_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('    }else{')
    script_list.append('      @Classe_Obj_Sim::ValidityFlags.validityFlag_RRR[counter_Classe] = 0;')
    script_list.append('      @target_radar_rr_sim::objdata.empty_obj[counter_Classe] = 1;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  @target_radar_rr_sim::objdata.number_of_obj = target_count_Classe;')
    script_list.append('  if(@hil_ctrl::radar_rr_loc_sim > 0)')
    script_list.append('  { //location based')
    script_list.append('    @target_radar_rr_sim::locdata.number_of_loc = 0;')
    script_list.append('    total_number_of_locations_RRR_Classe = 0;')
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

def read_Classe_fov(num_objects):
    """
    Description: Updates the function which reads the distances of the sensor position for each target and each sensor to calculate later in the valid_targets function which targets are in the FoV of the specific sensor.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    script_list.append('/** @brief Update FoV arrays for calculation of valid targets')
    script_list.append('  *        For FoV determination the middle of the geometry is being considered')
    script_list.append('  * @return void')
    script_list.append('  */')
    
    script_list.append('void update_distances_for_fov_calc(){')
    script_list.append('  int counter = 0;')
    script_list.append('  for(counter = 0; counter < 9; counter++){')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fc_sim::objdata.obj_length[counter], @target_radar_fc_sim::objdata.obj_heading_angle[counter], @target_radar_fc_sim::objdata.obj_distance_x[counter], @target_radar_fc_sim::objdata.obj_distance_y[counter], @target_radar_fc_sim::objdata.obj_velocity_x[counter],  @target_radar_fc_sim::objdata.obj_velocity_y[counter], @Classe_Obj_Sim::RoadObj.offset_x_fc, @Classe_Obj_Sim::RoadObj.offset_y_fc, @radarfc_par::mounting_ori_yaw, 0, 0);')
    script_list.append('    //fill sensor perspective into fov array')
    script_list.append('    fov_dx_radar_fc[counter] = dllRotationGetSensorDx(gHandle_rot);')
    script_list.append('    fov_dy_radar_fc[counter] = dllRotationGetSensorDy(gHandle_rot);')
    script_list.append('    ')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_fvideo_sim::objdata.obj_length[counter], @target_fvideo_sim::objdata.obj_heading_angle[counter], @target_fvideo_sim::objdata.obj_distance_x[counter], @target_fvideo_sim::objdata.obj_distance_y[counter], @target_fvideo_sim::objdata.obj_velocity_x[counter],  @target_fvideo_sim::objdata.obj_velocity_y[counter], @Classe_Obj_Sim::RoadObj.offset_x_fv, @Classe_Obj_Sim::RoadObj.offset_y_fv, @fvideo_par::mounting_ori_yaw, 0, 0);')
    script_list.append('    //fill sensor perspective into fov array')
    script_list.append('    fov_dx_fvideo[counter] = dllRotationGetSensorDx(gHandle_rot);')
    script_list.append('    fov_dy_fvideo[counter] = dllRotationGetSensorDy(gHandle_rot);')
    script_list.append('    ')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fl_sim::objdata.obj_length[counter], @target_radar_fl_sim::objdata.obj_heading_angle[counter], @target_radar_fl_sim::objdata.obj_distance_x[counter], @target_radar_fl_sim::objdata.obj_distance_y[counter], @target_radar_fl_sim::objdata.obj_velocity_x[counter],  @target_radar_fl_sim::objdata.obj_velocity_y[counter], @Classe_Obj_Sim::RoadObj.offset_x_fl, @Classe_Obj_Sim::RoadObj.offset_y_fl, @radarfl_par::mounting_ori_yaw, 0, 0);')
    script_list.append('    //fill sensor perspective into fov array')
    script_list.append('    fov_dx_radar_fl[counter] = dllRotationGetSensorDx(gHandle_rot);')
    script_list.append('    fov_dy_radar_fl[counter] = dllRotationGetSensorDy(gHandle_rot);')
    script_list.append('    ')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fr_sim::objdata.obj_length[counter], @target_radar_fr_sim::objdata.obj_heading_angle[counter], @target_radar_fr_sim::objdata.obj_distance_x[counter], @target_radar_fr_sim::objdata.obj_distance_y[counter], @target_radar_fr_sim::objdata.obj_velocity_x[counter],  @target_radar_fr_sim::objdata.obj_velocity_y[counter], @Classe_Obj_Sim::RoadObj.offset_x_fr, @Classe_Obj_Sim::RoadObj.offset_y_fr, @radarfr_par::mounting_ori_yaw, 0, 0);')
    script_list.append('    //fill sensor perspective into fov array')
    script_list.append('    fov_dx_radar_fr[counter] = dllRotationGetSensorDx(gHandle_rot);')
    script_list.append('    fov_dy_radar_fr[counter] = dllRotationGetSensorDy(gHandle_rot);')
    script_list.append('    ')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_rl_sim::objdata.obj_length[counter], @target_radar_rl_sim::objdata.obj_heading_angle[counter], @target_radar_rl_sim::objdata.obj_distance_x[counter], @target_radar_rl_sim::objdata.obj_distance_y[counter], @target_radar_rl_sim::objdata.obj_velocity_x[counter],  @target_radar_rl_sim::objdata.obj_velocity_y[counter], @Classe_Obj_Sim::RoadObj.offset_x_rl, @Classe_Obj_Sim::RoadObj.offset_y_rl, @radarrl_par::mounting_ori_yaw, 0, 0);')
    script_list.append('    //fill sensor perspective into fov array')
    script_list.append('    fov_dx_radar_rl[counter] = dllRotationGetSensorDx(gHandle_rot);')
    script_list.append('    fov_dy_radar_rl[counter] = dllRotationGetSensorDy(gHandle_rot);')
    script_list.append('    ')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_rr_sim::objdata.obj_length[counter], @target_radar_rr_sim::objdata.obj_heading_angle[counter], @target_radar_rr_sim::objdata.obj_distance_x[counter], @target_radar_rr_sim::objdata.obj_distance_y[counter], @target_radar_rr_sim::objdata.obj_velocity_x[counter],  @target_radar_rr_sim::objdata.obj_velocity_y[counter], @Classe_Obj_Sim::RoadObj.offset_x_rr, @Classe_Obj_Sim::RoadObj.offset_y_rr, @radarrr_par::mounting_ori_yaw, 0, 0);')
    script_list.append('    //fill sensor perspective into fov array')
    script_list.append('    fov_dx_radar_rr[counter] = dllRotationGetSensorDx(gHandle_rot);')
    script_list.append('    fov_dy_radar_rr[counter] = dllRotationGetSensorDy(gHandle_rot);')
    script_list.append('  }')
    script_list.append('}')
    script_list.append('')

def update_radar_fc_classe(num_objects):
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
    
    script_list.append('void update_radar_fc_classe(byte object_id, int sensor_mod)')
    script_list.append('{')
    script_list.append('  if(sensor_mod == 1)')
    script_list.append('  { //location based')
    script_list.append('    //Calculate coordinate systems: RCA - mid of target geometry; Sensor position - mid of target geometry')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fc_sim::objdata.obj_length[object_id], @target_radar_fc_sim::objdata.obj_heading_angle[object_id], @target_radar_fc_sim::objdata.obj_distance_x[object_id], @target_radar_fc_sim::objdata.obj_distance_y[object_id], @target_radar_fc_sim::objdata.obj_velocity_x[object_id],  @target_radar_fc_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fc, @Classe_Obj_Sim::RoadObj.offset_y_fc, @radarfc_par::mounting_ori_yaw, 0, 0);')
    script_list.append('    ')
    script_list.append('    if(@target_radar_fc_sim::locdata.location_model == 0)')
    script_list.append('    { //1objXloc')
    script_list.append('      //Calculate reference point')
    script_list.append('      dllCalcObjectReferencePoint(gHandle_obj, @target_radar_fc_sim::objdata.obj_height[object_id], @target_radar_fc_sim::objdata.obj_width[object_id], @target_radar_fc_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('      //Calculate location values using the reference point position')
    script_list.append('      dllCalcLocations(gHandle_obj,4,1.5);  //handle,max_loc,height')
    script_list.append('      number_of_locs_RFC_Classe = dllGetLocCount(gHandle_obj);')
    script_list.append('      ')
    script_list.append('      for(loc_count_RFC_Classe=total_number_of_locations_RFC_Classe; loc_count_RFC_Classe < total_number_of_locations_RFC_Classe+max_number_of_locations_starmodel && loc_count_RFC_Classe < total_number_of_locations_RFC_Classe+number_of_locs_RFC_Classe; loc_count_RFC_Classe++)')
    script_list.append('      {')
    script_list.append('        //radial distance')
    script_list.append('        @target_radar_fc_sim::locdata.loc_radial_distance[loc_count_RFC_Classe] = dllGetLoc(gHandle_obj,loc_count_RFC_Classe-total_number_of_locations_RFC_Classe);')
    script_list.append('        ')
    script_list.append('        //radial velocity')
    script_list.append('        @target_radar_fc_sim::locdata.loc_radial_velocity[loc_count_RFC_Classe] = calc_radial_velocity(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj), dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), @target_radar_fc_sim::locdata.loc_radial_velocity[object_id]);')
    script_list.append('        ')
    script_list.append('        //location angles')
    script_list.append('        @target_radar_fc_sim::locdata.loc_elevation_angle[loc_count_RFC_Classe] = calc_elevation_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('        @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_Classe] = dllGetLocAzimuth(gHandle_obj,loc_count_RFC_Classe-total_number_of_locations_RFC_Classe);')
    script_list.append('        ')
    script_list.append('        //RCS + SNR')
    script_list.append('        @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_Classe] = calc_radar_cross_section(@target_radar_fc_sim::objdata.obj_type[object_id], @target_radar_fc_sim::locdata.loc_radial_distance[object_id]);')
    script_list.append('        @target_radar_fc_sim::locdata.loc_signal_strength_indicator[loc_count_RFC_Classe] = 100;')
    script_list.append('      }')
    script_list.append('      ')
    script_list.append('      //1objXloc')
    script_list.append('      total_number_of_locations_RFC_Classe = total_number_of_locations_RFC_Classe + _min(number_of_locs_RFC_Classe, max_number_of_locations_starmodel);')
    script_list.append('      @target_radar_fc_sim::locdata.number_of_loc = total_number_of_locations_RFC_Classe;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_fc_sim::locdata.location_model == 1)')
    script_list.append('    { //starmodel')
    script_list.append('      resultSetInputValues = dllSetInputValues(gHandle_star, object_id+1, dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot), 0, dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), 0, 0, dllRotationGetSensorHeading(gHandle_rot), @target_radar_fc_sim::objdata.obj_length[object_id], @target_radar_fc_sim::objdata.obj_width[object_id], @target_radar_fc_sim::objdata.obj_height[object_id], @target_radar_fc_sim::objdata.obj_type[object_id]);')
    script_list.append('      resultStarModelRun = dllRunStarModel(gHandle_star, 2);')
    script_list.append('      number_of_locs_RFC_Classe = dllGetNumLocs(gHandle_star);')
    script_list.append('      ')
    script_list.append('      for(loc_count_RFC_Classe=total_number_of_locations_RFC_Classe; loc_count_RFC_Classe < total_number_of_locations_RFC_Classe+@hil_ctrl::starmodel_max_loc_nr && loc_count_RFC_Classe < total_number_of_locations_RFC_Classe+number_of_locs_RFC_Classe; loc_count_RFC_Classe++)')
    script_list.append('      {')
    script_list.append('        @target_radar_fc_sim::locdata.loc_radial_distance[loc_count_RFC_Classe] = dllGetDistance(gHandle_star, loc_count_RFC_Classe-total_number_of_locations_RFC_Classe);')
    script_list.append('        @target_radar_fc_sim::locdata.loc_radial_velocity[loc_count_RFC_Classe] = -dllGetRelativeRadialVelocity(gHandle_star, loc_count_RFC_Classe-total_number_of_locations_RFC_Classe);')
    script_list.append('        @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_Classe] = dllGetAzimuthAngle(gHandle_star, loc_count_RFC_Classe-total_number_of_locations_RFC_Classe);')
    script_list.append('        if(@target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_Classe]>PI) ')
    script_list.append('        {')
    script_list.append('          @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_Classe] = @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_Classe]-2*PI;')
    script_list.append('        }')
    script_list.append('        @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_Classe] = @target_radar_fc_sim::locdata.loc_azimuth_angle[loc_count_RFC_Classe] * 180 / pi;')
    script_list.append('        @target_radar_fc_sim::locdata.loc_elevation_angle[loc_count_RFC_Classe] = dllGetElevationAngle(gHandle_star, loc_count_RFC_Classe-total_number_of_locations_RFC_Classe);')
    script_list.append('  	    @target_radar_fc_sim::locdata.loc_radar_cross_section[loc_count_RFC_Classe] = dllGetRcs(gHandle_star, loc_count_RFC_Classe-total_number_of_locations_RFC_Classe);')
    script_list.append('        @target_radar_fc_sim::locdata.loc_signal_strength_indicator[loc_count_RFC_Classe] = 100;')
    script_list.append('      }')
    script_list.append('      total_number_of_locations_RFC_Classe = total_number_of_locations_RFC_Classe + _min(number_of_locs_RFC_Classe, @hil_ctrl::starmodel_max_loc_nr);')
    script_list.append('      @target_radar_fc_sim::locdata.number_of_loc = total_number_of_locations_RFC_Classe;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_fc_sim::locdata.location_model == 2)')
    script_list.append('    { // Clara model - needs all object data at once and gives back a unspecified number of locations which cannot be assigned to a specific object')
    script_list.append('      // This is why we do all of this in a separate loop on the call of the first target')
    script_list.append('      if(clara_run_fc_Classe == 1)')
    script_list.append('      {')
    script_list.append('        int loc_id = 0;')
    script_list.append('        int i = 0;')
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
    script_list.append('                                  @target_radar_fc_sim::objdata.obj_velocity_x[i],  @target_radar_fc_sim::objdata.obj_velocity_y[i], @Classe_Obj_Sim::RoadObj.offset_x_fc, @Classe_Obj_Sim::RoadObj.offset_y_fc, 0, 0, 0);')
    script_list.append('            ')
    script_list.append('            // update Ego vehicle - for now the Ego is set to standstill at (0/0/0) due to missing world coordinates')
    script_list.append('            dllClaraUpdateEgo(gHandle_clara_RFC);')
    script_list.append('            // handle, target_id, target_type, target_dx, target_dy, target_dz, target_vx, target_vy, target_vz, target_acceleration, target_yaw_angle, target_length, target_width, target_height')
    script_list.append('            dllClaraUpdateTgt(gHandle_clara_RFC,i,@target_radar_fc_sim::objdata.obj_type[i],dllRotationGetRCADx(gHandle_rot),dllRotationGetRCADy(gHandle_rot),0,')
    script_list.append('                              dllRotationGetRCAVx(gHandle_rot),dllRotationGetRCAVy(gHandle_rot),0,0,dllRotationGetRCAHeading(gHandle_rot),')
    script_list.append('                              @target_radar_fc_sim::objdata.obj_length[i],@target_radar_fc_sim::objdata.obj_width[i],@target_radar_fc_sim::objdata.obj_height[i]);')
    script_list.append('            ')
    script_list.append('            clara_radar_fc_deletion_needed_Classe[i] = 1;')
    script_list.append('          }')
    script_list.append('          else if(clara_radar_fc_deletion_needed_Classe[i] == 1)')
    script_list.append('          { // object deleted, only done once per object to save performance')
    script_list.append('            ')
    script_list.append('            // update Ego vehicle - for now the Ego is set to standstill at (0/0/0) due to missing world coordinates')
    script_list.append('            dllClaraUpdateEgo(gHandle_clara_RFC);')
    script_list.append('            // deletion means setting everything to 0 for that object')
    script_list.append('            dllClaraUpdateTgt(gHandle_clara_RFC,i,0,0,0,0,0,0,0,0,0,0,0,0);')
    script_list.append('            ')
    script_list.append('            clara_radar_fc_deletion_needed_Classe[i] = 0;')
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
    script_list.append('          @target_radar_fc_sim::locdata.loc_radial_distance[total_number_of_locations_RFC_Classe] = dllClaraGetRadialDistance(gHandle_clara_RFC,loc_id);')
    script_list.append('          ')
    script_list.append('          //radial velocity')
    script_list.append('          @target_radar_fc_sim::locdata.loc_radial_velocity[total_number_of_locations_RFC_Classe] = dllClaraGetRadialVelocity(gHandle_clara_RFC,loc_id);')
    script_list.append('          ')
    script_list.append('          //location angles')
    script_list.append('          @target_radar_fc_sim::locdata.loc_elevation_angle[total_number_of_locations_RFC_Classe] = dllClaraGetElevationAngle(gHandle_clara_RFC,loc_id);')
    script_list.append('          @target_radar_fc_sim::locdata.loc_azimuth_angle[total_number_of_locations_RFC_Classe] = dllClaraGetAzimuthAngle(gHandle_clara_RFC,loc_id);')
    script_list.append('          ')
    script_list.append('          //SNR + RCS')
    script_list.append('          @target_radar_fc_sim::locdata.loc_radar_cross_section[total_number_of_locations_RFC_Classe] = dllClaraGetRCS(gHandle_clara_RFC,loc_id);')
    script_list.append('          @target_radar_fc_sim::locdata.loc_signal_strength_indicator[total_number_of_locations_RFC_Classe] = 100;')
    script_list.append('          ')
    script_list.append('          // increase number of locations')
    script_list.append('          total_number_of_locations_RFC_Classe++;')
    script_list.append('          @target_radar_fc_sim::locdata.number_of_loc = total_number_of_locations_RFC_Classe;')
    script_list.append('          ')
    script_list.append('          // only accept as many locations as allowed')
    script_list.append('          if(total_number_of_locations_RFC_Classe >= maximum_nr_loc)')
    script_list.append('          {')
    script_list.append('            break; ')
    script_list.append('          }')
    script_list.append('          ')
    script_list.append('          // get ID of next location')
    script_list.append('          loc_id = dllClaraGetNextValidLoc(gHandle_clara_RFC,loc_id);')
    script_list.append('        }')
    script_list.append('        ')
    script_list.append('        clara_run_fc_Classe = 0;')
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

def update_fvideo_classe(num_objects):
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
    
    script_list.append('void update_fvideo_classe(byte object_id)')
    script_list.append('{')
    
    script_list.append('  //shift target data to have RCA and Sensor CS available')
    script_list.append('  dllRotationCalcTarget(gHandle_rot, @target_fvideo_sim::objdata.obj_length[object_id], @target_fvideo_sim::objdata.obj_heading_angle[object_id], @target_fvideo_sim::objdata.obj_distance_x[object_id], @target_fvideo_sim::objdata.obj_distance_y[object_id], @target_fvideo_sim::objdata.obj_velocity_x[object_id],  @target_fvideo_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fv, @Classe_Obj_Sim::RoadObj.offset_y_fv, @fvideo_par::mounting_ori_yaw, 0, 0);')
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
    
def update_radar_fl_classe(num_objects):
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
    
    script_list.append('void update_radar_fl_classe(byte object_id, int sensor_mod)')
    script_list.append('{')
    
    script_list.append('  if(sensor_mod == 1)')
    script_list.append('  { //location based')
    script_list.append('    //Calculate coordinate systems: RCA - mid of target geometry; Sensor position - mid of target geometry')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fl_sim::objdata.obj_length[object_id], @target_radar_fl_sim::objdata.obj_heading_angle[object_id], @target_radar_fl_sim::objdata.obj_distance_x[object_id], @target_radar_fl_sim::objdata.obj_distance_y[object_id], @target_radar_fl_sim::objdata.obj_velocity_x[object_id],  @target_radar_fl_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fl, @Classe_Obj_Sim::RoadObj.offset_y_fl, @radarfl_par::mounting_ori_yaw, 0, 0);')
    script_list.append('    if(@target_radar_fl_sim::locdata.location_model == 0)')
    script_list.append('    { //1obj1loc')
    script_list.append('      //Calculate reference point')
    script_list.append('      dllCalcObjectReferencePoint(gHandle_obj, @target_radar_fl_sim::objdata.obj_height[object_id], @target_radar_fl_sim::objdata.obj_width[object_id], @target_radar_fl_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('      loc_count_RFL_Classe=total_number_of_locations_RFL_Classe;')
    script_list.append('      ')
    script_list.append('      //Calculate location values using the reference point position')
    script_list.append('      @target_radar_fl_sim::locdata.loc_radial_distance[loc_count_RFL_Classe] = calc_radial_distance(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_fl_sim::locdata.loc_radial_velocity[loc_count_RFL_Classe] = calc_radial_velocity(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj), dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), @target_radar_fc_sim::locdata.loc_radial_velocity[object_id]);')
    script_list.append('      ')
    script_list.append('      //location angles')
    script_list.append('      @target_radar_fl_sim::locdata.loc_elevation_angle[loc_count_RFL_Classe] = calc_elevation_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_Classe] = calc_azimuth_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      ')
    script_list.append('      //RCS')
    script_list.append('      @target_radar_fl_sim::locdata.loc_radar_cross_section[loc_count_RFL_Classe] = calc_radar_cross_section(@target_radar_fl_sim::objdata.obj_type[object_id], @target_radar_fl_sim::locdata.loc_radial_distance[object_id]);')
    script_list.append('      @target_radar_fl_sim::locdata.loc_signal_strength_indicator[loc_count_RFL_Classe] = 100;')
    script_list.append('	  ')
    script_list.append('      //1obj1loc')
    script_list.append('      total_number_of_locations_RFL_Classe = total_number_of_locations_RFL_Classe + 1;')
    script_list.append('      @target_radar_fl_sim::locdata.number_of_loc = total_number_of_locations_RFL_Classe;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_fl_sim::locdata.location_model == 1)')
    script_list.append('    { //starmodel')
    script_list.append('      //TBD')
    script_list.append('      resultSetInputValues = dllSetInputValues(gHandle_star, object_id+1, dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot), 0, dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), 0, 0, dllRotationGetSensorHeading(gHandle_rot), @target_radar_fl_sim::objdata.obj_length[object_id], @target_radar_fl_sim::objdata.obj_width[object_id], @target_radar_fl_sim::objdata.obj_height[object_id], @target_radar_fl_sim::objdata.obj_type[object_id]);')
    script_list.append('      resultStarModelRun = dllRunStarModel(gHandle_star, 2);')
    script_list.append('      number_of_locs_RFL_Classe = dllGetNumLocs(gHandle_star);')
    script_list.append('      for(loc_count_RFL_Classe=total_number_of_locations_RFL_Classe; loc_count_RFL_Classe < total_number_of_locations_RFL_Classe+@hil_ctrl::starmodel_max_loc_nr && loc_count_RFL_Classe < total_number_of_locations_RFL_Classe+number_of_locs_RFL_Classe; loc_count_RFL_Classe++)')
    script_list.append('      {')
    script_list.append('        @target_radar_fl_sim::locdata.loc_radial_distance[loc_count_RFL_Classe] = dllGetDistance(gHandle_star, loc_count_RFL_Classe-total_number_of_locations_RFL_Classe);')
    script_list.append('        @target_radar_fl_sim::locdata.loc_radial_velocity[loc_count_RFL_Classe] = -dllGetRelativeRadialVelocity(gHandle_star, loc_count_RFL_Classe-total_number_of_locations_RFL_Classe);')
    script_list.append('        @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_Classe] = dllGetAzimuthAngle(gHandle_star, loc_count_RFL_Classe-total_number_of_locations_RFL_Classe);')
    script_list.append('        if(@target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_Classe]>PI) ')
    script_list.append('        {')
    script_list.append('          @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_Classe] = @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_Classe]-2*PI;')
    script_list.append('        }')
    script_list.append('        @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_Classe] = @target_radar_fl_sim::locdata.loc_azimuth_angle[loc_count_RFL_Classe] * 180 / pi;')
    script_list.append('        @target_radar_fl_sim::locdata.loc_elevation_angle[loc_count_RFL_Classe] = -dllGetElevationAngle(gHandle_star, loc_count_RFL_Classe-total_number_of_locations_RFL_Classe);')
    script_list.append('  	    @target_radar_fl_sim::locdata.loc_radar_cross_section[loc_count_RFL_Classe] = dllGetRcs(gHandle_star, loc_count_RFL_Classe-total_number_of_locations_RFL_Classe);')
    script_list.append('      }')
    script_list.append('    total_number_of_locations_RFL_Classe = total_number_of_locations_RFL_Classe + _min(number_of_locs_RFL_Classe, @hil_ctrl::starmodel_max_loc_nr);')
    script_list.append('    @target_radar_fl_sim::locdata.number_of_loc = total_number_of_locations_RFL_Classe;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  else if(sensor_mod == 2)')
    script_list.append('  { //object based')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fl_sim::objdata.obj_length[object_id], @target_radar_fl_sim::objdata.obj_heading_angle[object_id], @target_radar_fl_sim::objdata.obj_distance_x[object_id], @target_radar_fl_sim::objdata.obj_distance_y[object_id], @target_radar_fl_sim::objdata.obj_velocity_x[object_id],  @target_radar_fl_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fl, @Classe_Obj_Sim::RoadObj.offset_y_fl, @radarfl_par::mounting_ori_yaw, 0, 0);')
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
    script_list.append('    @target_radar_fl_sim::objdata.obj_radar_cross_section[object_id] = calc_radar_cross_section(@target_radar_fl_sim::objdata.obj_type[object_id], calc_radial_distance(dllGetRCARefptDistX(gHandle_obj),dllGetRCARefptDistY(gHandle_obj)));')
    script_list.append('  }')
    script_list.append('}')
    script_list.append('')
    
    print('Radar_FL for Classe usecase updated successfully.')

def update_radar_fr_classe(num_objects):
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
    
    script_list.append('void update_radar_fr_classe(byte object_id, int sensor_mod)')
    script_list.append('{')
    
    script_list.append('  if(sensor_mod == 1)')
    script_list.append('  { //location based')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fr_sim::objdata.obj_length[object_id], @target_radar_fr_sim::objdata.obj_heading_angle[object_id], @target_radar_fr_sim::objdata.obj_distance_x[object_id], @target_radar_fr_sim::objdata.obj_distance_y[object_id], @target_radar_fr_sim::objdata.obj_velocity_x[object_id],  @target_radar_fr_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fr, @Classe_Obj_Sim::RoadObj.offset_y_fr, @radarfr_par::mounting_ori_yaw, 0, 0);')
    script_list.append('    if(@target_radar_fr_sim::locdata.location_model == 0)')
    script_list.append('    { //1obj1loc')
    script_list.append('      //Calculate reference point')
    script_list.append('      dllCalcObjectReferencePoint(gHandle_obj, @target_radar_fr_sim::objdata.obj_height[object_id], @target_radar_fr_sim::objdata.obj_width[object_id], @target_radar_fr_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('      loc_count_RFR_Classe=total_number_of_locations_RFR_Classe;')
    script_list.append('      ')
    script_list.append('      //location values')
    script_list.append('      @target_radar_fr_sim::locdata.loc_radial_distance[loc_count_RFR_Classe] = calc_radial_distance(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_fr_sim::locdata.loc_radial_velocity[loc_count_RFR_Classe] = calc_radial_velocity(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj), dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), @target_radar_fc_sim::locdata.loc_radial_velocity[object_id]);')
    script_list.append('      ')
    script_list.append('      //location angles')
    script_list.append('      @target_radar_fr_sim::locdata.loc_elevation_angle[loc_count_RFR_Classe] = calc_elevation_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_Classe] = calc_azimuth_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      ')
    script_list.append('      //RCS')
    script_list.append('      @target_radar_fr_sim::locdata.loc_radar_cross_section[loc_count_RFR_Classe] = calc_radar_cross_section(@target_radar_fr_sim::objdata.obj_type[object_id], @target_radar_fr_sim::locdata.loc_radial_distance[object_id]);')
    script_list.append('      @target_radar_fr_sim::locdata.loc_signal_strength_indicator[loc_count_RFR_Classe] = 100;')
    script_list.append('	  ')
    script_list.append('      //1obj1loc')
    script_list.append('      total_number_of_locations_RFR_Classe = total_number_of_locations_RFR_Classe + 1;')
    script_list.append('      @target_radar_fr_sim::locdata.number_of_loc = total_number_of_locations_RFR_Classe;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_fr_sim::locdata.location_model == 1)')
    script_list.append('    { //starmodel')
    script_list.append('      resultSetInputValues = dllSetInputValues(gHandle_star, object_id+1, dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot), 0, dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), 0, 0, dllRotationGetSensorHeading(gHandle_rot), @target_radar_fr_sim::objdata.obj_length[object_id], @target_radar_fr_sim::objdata.obj_width[object_id], @target_radar_fr_sim::objdata.obj_height[object_id], @target_radar_fr_sim::objdata.obj_type[object_id]);')
    script_list.append('      resultStarModelRun = dllRunStarModel(gHandle_star, 2);')
    script_list.append('      number_of_locs_RFR_Classe = dllGetNumLocs(gHandle_star);')
    script_list.append('      ')
    script_list.append('      for(loc_count_RFR_Classe=total_number_of_locations_RFR_Classe; loc_count_RFR_Classe < total_number_of_locations_RFR_Classe+@hil_ctrl::starmodel_max_loc_nr && loc_count_RFR_Classe < total_number_of_locations_RFR_Classe+number_of_locs_RFR_Classe; loc_count_RFR_Classe++)')
    script_list.append('      {')
    script_list.append('        @target_radar_fr_sim::locdata.loc_radial_distance[loc_count_RFR_Classe] = dllGetDistance(gHandle_star, loc_count_RFR_Classe-total_number_of_locations_RFR_Classe);')
    script_list.append('        @target_radar_fr_sim::locdata.loc_radial_velocity[loc_count_RFR_Classe] = -dllGetRelativeRadialVelocity(gHandle_star, loc_count_RFR_Classe-total_number_of_locations_RFR_Classe);')
    script_list.append('        @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_Classe] = dllGetAzimuthAngle(gHandle_star, loc_count_RFR_Classe-total_number_of_locations_RFR_Classe);')
    script_list.append('        if(@target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_Classe]>PI) ')
    script_list.append('        {')
    script_list.append('          @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_Classe] = @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_Classe]-2*PI;')
    script_list.append('        }')
    script_list.append('        @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_Classe] = @target_radar_fr_sim::locdata.loc_azimuth_angle[loc_count_RFR_Classe] * 180 / pi;')
    script_list.append('        @target_radar_fr_sim::locdata.loc_elevation_angle[loc_count_RFR_Classe] = dllGetElevationAngle(gHandle_star, loc_count_RFR_Classe-total_number_of_locations_RFR_Classe);')
    script_list.append('  	    @target_radar_fr_sim::locdata.loc_radar_cross_section[loc_count_RFR_Classe] = dllGetRcs(gHandle_star, loc_count_RFR_Classe-total_number_of_locations_RFR_Classe);')
    script_list.append('      }')
    script_list.append('      total_number_of_locations_RFR_Classe = total_number_of_locations_RFR_Classe + _min(number_of_locs_RFR_Classe, @hil_ctrl::starmodel_max_loc_nr);')
    script_list.append('      @target_radar_fr_sim::locdata.number_of_loc = total_number_of_locations_RFR_Classe;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  else if(sensor_mod == 2)')
    script_list.append('  { //object based')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_fr_sim::objdata.obj_length[object_id], @target_radar_fr_sim::objdata.obj_heading_angle[object_id], @target_radar_fr_sim::objdata.obj_distance_x[object_id], @target_radar_fr_sim::objdata.obj_distance_y[object_id], @target_radar_fr_sim::objdata.obj_velocity_x[object_id],  @target_radar_fr_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_fr, @Classe_Obj_Sim::RoadObj.offset_y_fr, @radarfr_par::mounting_ori_yaw, 0, 0);')
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
    script_list.append('    @target_radar_fr_sim::objdata.obj_radar_cross_section[object_id] = calc_radar_cross_section(@target_radar_fr_sim::objdata.obj_type[object_id], calc_radial_distance(dllGetRCARefptDistX(gHandle_obj),dllGetRCARefptDistY(gHandle_obj)));')
    script_list.append('  }')
    script_list.append('}')
    script_list.append('')
    
    print('Radar_FR for Classe usecase updated successfully.')
    
def update_radar_rl_classe(num_objects):
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
    
    script_list.append('void update_radar_rl_classe(byte object_id, int sensor_mod)')
    script_list.append('{')
    
    script_list.append('  if(sensor_mod == 1)')
    script_list.append('  { //location based')
    script_list.append('    ')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_rl_sim::objdata.obj_length[object_id], @target_radar_rl_sim::objdata.obj_heading_angle[object_id], @target_radar_rl_sim::objdata.obj_distance_x[object_id], @target_radar_rl_sim::objdata.obj_distance_y[object_id], @target_radar_rl_sim::objdata.obj_velocity_x[object_id],  @target_radar_rl_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_rl, @Classe_Obj_Sim::RoadObj.offset_y_rl, @radarrl_par::mounting_ori_yaw, 0, 0);')
    script_list.append('    if(@target_radar_rl_sim::locdata.location_model == 0)')
    script_list.append('    { //1obj1loc')
    script_list.append('      //Calculate reference point')
    script_list.append('      dllCalcObjectReferencePoint(gHandle_obj, @target_radar_rl_sim::objdata.obj_height[object_id], @target_radar_rl_sim::objdata.obj_width[object_id], @target_radar_rl_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('      loc_count_RRL_Classe=total_number_of_locations_RRL_Classe;')
    script_list.append('      ')
    script_list.append('      //location values')
    script_list.append('      @target_radar_rl_sim::locdata.loc_radial_distance[loc_count_RRL_Classe] = calc_radial_distance(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_rl_sim::locdata.loc_radial_velocity[loc_count_RRL_Classe] = calc_radial_velocity(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj), dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), @target_radar_fc_sim::locdata.loc_radial_velocity[object_id]);')
    script_list.append('      ')
    script_list.append('      //location angles')
    script_list.append('      @target_radar_rl_sim::locdata.loc_elevation_angle[loc_count_RRL_Classe] = calc_elevation_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_Classe] = calc_azimuth_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      ')
    script_list.append('      //RCS')
    script_list.append('      @target_radar_rl_sim::locdata.loc_radar_cross_section[loc_count_RRL_Classe] = calc_radar_cross_section(@target_radar_rl_sim::objdata.obj_type[object_id], @target_radar_rl_sim::locdata.loc_radial_distance[object_id]);')
    script_list.append('      @target_radar_rl_sim::locdata.loc_signal_strength_indicator[loc_count_RRL_Classe] = 100;')
    script_list.append('	  ')
    script_list.append('      //1obj1loc')
    script_list.append('    total_number_of_locations_RRL_Classe = total_number_of_locations_RRL_Classe + 1;')
    script_list.append('      @target_radar_rl_sim::locdata.number_of_loc = total_number_of_locations_RRL_Classe;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_rl_sim::locdata.location_model == 1)')
    script_list.append('    { //starmodel')
    script_list.append('      resultSetInputValues = dllSetInputValues(gHandle_star, object_id+1, dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot), 0, dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), 0, 0, dllRotationGetSensorHeading(gHandle_rot), @target_radar_rl_sim::objdata.obj_length[object_id], @target_radar_rl_sim::objdata.obj_width[object_id], @target_radar_rl_sim::objdata.obj_height[object_id], @target_radar_rl_sim::objdata.obj_type[object_id]);')
    script_list.append('      resultStarModelRun = dllRunStarModel(gHandle_star, 2);')
    script_list.append('      number_of_locs_RRL_Classe = dllGetNumLocs(gHandle_star);')
    script_list.append('      for(loc_count_RRL_Classe=total_number_of_locations_RRL_Classe; loc_count_RRL_Classe < total_number_of_locations_RRL_Classe+@hil_ctrl::starmodel_max_loc_nr && loc_count_RRL_Classe < total_number_of_locations_RRL_Classe+number_of_locs_RRL_Classe; loc_count_RRL_Classe++)')
    script_list.append('      {')
    script_list.append('        @target_radar_rl_sim::locdata.loc_radial_distance[loc_count_RRL_Classe] = dllGetDistance(gHandle_star, loc_count_RRL_Classe-total_number_of_locations_RRL_Classe);')
    script_list.append('        @target_radar_rl_sim::locdata.loc_radial_velocity[loc_count_RRL_Classe] = -dllGetRelativeRadialVelocity(gHandle_star, loc_count_RRL_Classe-total_number_of_locations_RRL_Classe);')
    script_list.append('        @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_Classe] = dllGetAzimuthAngle(gHandle_star, loc_count_RRL_Classe-total_number_of_locations_RRL_Classe);')
    script_list.append('        if(@target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_Classe]>PI) ')
    script_list.append('        {')
    script_list.append('          @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_Classe] = @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_Classe]-2*PI;')
    script_list.append('        }')
    script_list.append('        @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_Classe] = @target_radar_rl_sim::locdata.loc_azimuth_angle[loc_count_RRL_Classe] * 180 / pi;')
    script_list.append('        @target_radar_rl_sim::locdata.loc_elevation_angle[loc_count_RRL_Classe] = dllGetElevationAngle(gHandle_star, loc_count_RRL_Classe-total_number_of_locations_RRL_Classe);')
    script_list.append('	    @target_radar_rl_sim::locdata.loc_radar_cross_section[loc_count_RRL_Classe] = dllGetRcs(gHandle_star, loc_count_RRL_Classe-total_number_of_locations_RRL_Classe);')
    script_list.append('    }')
    script_list.append('    total_number_of_locations_RRL_Classe = total_number_of_locations_RRL_Classe + _min(number_of_locs_RRL_Classe, @hil_ctrl::starmodel_max_loc_nr);')
    script_list.append('    @target_radar_rl_sim::locdata.number_of_loc = total_number_of_locations_RRL_Classe;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  else if(sensor_mod == 2)')
    script_list.append('  { //object based')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_rl_sim::objdata.obj_length[object_id], @target_radar_rl_sim::objdata.obj_heading_angle[object_id], @target_radar_rl_sim::objdata.obj_distance_x[object_id], @target_radar_rl_sim::objdata.obj_distance_y[object_id], @target_radar_rl_sim::objdata.obj_velocity_x[object_id],  @target_radar_rl_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_rl, @Classe_Obj_Sim::RoadObj.offset_y_rl, @radarrl_par::mounting_ori_yaw, 0, 0);')
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

def update_radar_rr_classe(num_objects):
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
    
    script_list.append('void update_radar_rr_classe(byte object_id, int sensor_mod)')
    script_list.append('{')
    
    script_list.append('  if(sensor_mod == 1)')
    script_list.append('  { //location based')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_rr_sim::objdata.obj_length[object_id], @target_radar_rr_sim::objdata.obj_heading_angle[object_id], @target_radar_rr_sim::objdata.obj_distance_x[object_id], @target_radar_rr_sim::objdata.obj_distance_y[object_id], @target_radar_rr_sim::objdata.obj_velocity_x[object_id],  @target_radar_rr_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_rr, @Classe_Obj_Sim::RoadObj.offset_y_rr, @radarrr_par::mounting_ori_yaw, 0, 0);')
    script_list.append('    if(@target_radar_rr_sim::locdata.location_model == 0)')
    script_list.append('    { //1obj1loc')
    script_list.append('      //Calculate reference point')
    script_list.append('      dllCalcObjectReferencePoint(gHandle_obj, @target_radar_rr_sim::objdata.obj_height[object_id], @target_radar_rr_sim::objdata.obj_width[object_id], @target_radar_rr_sim::objdata.obj_length[object_id], dllRotationGetRCADx(gHandle_rot), dllRotationGetRCADy(gHandle_rot), dllRotationGetRCAHeading(gHandle_rot), dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot),dllRotationGetSensorHeading(gHandle_rot));')
    script_list.append('      loc_count_RRR_Classe=total_number_of_locations_RRR_Classe;')
    script_list.append('      ')
    script_list.append('      //location values')
    script_list.append('      @target_radar_rr_sim::locdata.loc_radial_distance[loc_count_RRR_Classe] = calc_radial_distance(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_rr_sim::locdata.loc_radial_velocity[loc_count_RRR_Classe] = calc_radial_velocity(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj), dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), @target_radar_fc_sim::locdata.loc_radial_velocity[object_id]);')
    script_list.append('      ')
    script_list.append('      //location angles')
    script_list.append('      @target_radar_rr_sim::locdata.loc_elevation_angle[loc_count_RRR_Classe] = calc_elevation_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_Classe] = calc_azimuth_angle(dllGetSensorRefptDistX(gHandle_obj), dllGetSensorRefptDistY(gHandle_obj));')
    script_list.append('      ')
    script_list.append('      //RCS')
    script_list.append('      @target_radar_rr_sim::locdata.loc_radar_cross_section[loc_count_RRR_Classe] = calc_radar_cross_section(@target_radar_rr_sim::objdata.obj_type[object_id], @target_radar_rr_sim::locdata.loc_radial_distance[object_id]);')
    script_list.append('      @target_radar_rr_sim::locdata.loc_signal_strength_indicator[loc_count_RRR_Classe] = 100;')
    script_list.append('	  ')
    script_list.append('      //1obj1loc')
    script_list.append('      total_number_of_locations_RRR_Classe = total_number_of_locations_RRR_Classe + 1;')
    script_list.append('      @target_radar_rr_sim::locdata.number_of_loc = total_number_of_locations_RRR_Classe;')
    script_list.append('    }')
    script_list.append('    else if(@target_radar_rr_sim::locdata.location_model == 1)')
    script_list.append('    { //starmodel')
    script_list.append('      resultSetInputValues = dllSetInputValues(gHandle_star, object_id+1, dllRotationGetSensorDx(gHandle_rot), dllRotationGetSensorDy(gHandle_rot), 0, dllRotationGetSensorVx(gHandle_rot), dllRotationGetSensorVy(gHandle_rot), 0, 0, dllRotationGetSensorHeading(gHandle_rot), @target_radar_rr_sim::objdata.obj_length[object_id], @target_radar_rr_sim::objdata.obj_width[object_id], @target_radar_rr_sim::objdata.obj_height[object_id], @target_radar_rr_sim::objdata.obj_type[object_id]);')
    script_list.append('      resultStarModelRun = dllRunStarModel(gHandle_star, 2);')
    script_list.append('      number_of_locs_RRR_Classe = dllGetNumLocs(gHandle_star);')
    script_list.append('      for(loc_count_RRR_Classe=total_number_of_locations_RRR_Classe; loc_count_RRR_Classe < total_number_of_locations_RRR_Classe+@hil_ctrl::starmodel_max_loc_nr && loc_count_RRR_Classe < total_number_of_locations_RRR_Classe+number_of_locs_RRR_Classe; loc_count_RRR_Classe++)')
    script_list.append('      {')
    script_list.append('        @target_radar_rr_sim::locdata.loc_radial_distance[loc_count_RRR_Classe] = dllGetDistance(gHandle_star, loc_count_RRR_Classe-total_number_of_locations_RRR_Classe);')
    script_list.append('        @target_radar_rr_sim::locdata.loc_radial_velocity[loc_count_RRR_Classe] = -dllGetRelativeRadialVelocity(gHandle_star, loc_count_RRR_Classe-total_number_of_locations_RRR_Classe);')
    script_list.append('        @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_Classe] = dllGetAzimuthAngle(gHandle_star, loc_count_RRR_Classe-total_number_of_locations_RRR_Classe);')
    script_list.append('        if(@target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_Classe]>PI) ')
    script_list.append('        {')
    script_list.append('          @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_Classe] = @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_Classe]-2*PI;')
    script_list.append('        }')
    script_list.append('        @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_Classe] = @target_radar_rr_sim::locdata.loc_azimuth_angle[loc_count_RRR_Classe] * 180 / pi;')
    script_list.append('        @target_radar_rr_sim::locdata.loc_elevation_angle[loc_count_RRR_Classe] = dllGetElevationAngle(gHandle_star, loc_count_RRR_Classe-total_number_of_locations_RRR_Classe);')
    script_list.append('  	    @target_radar_rr_sim::locdata.loc_radar_cross_section[loc_count_RRR_Classe] = dllGetRcs(gHandle_star, loc_count_RRR_Classe-total_number_of_locations_RRR_Classe);')
    script_list.append('      }')
    script_list.append('      total_number_of_locations_RRR_Classe = total_number_of_locations_RRR_Classe + _min(number_of_locs_RRR_Classe, @hil_ctrl::starmodel_max_loc_nr);')
    script_list.append('      @target_radar_rr_sim::locdata.number_of_loc = total_number_of_locations_RRR_Classe;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  else if(sensor_mod == 2)')
    script_list.append('  { //object based')
    script_list.append('    //shift target data to have RCA and Sensor CS available')
    script_list.append('    dllRotationCalcTarget(gHandle_rot, @target_radar_rr_sim::objdata.obj_length[object_id], @target_radar_rr_sim::objdata.obj_heading_angle[object_id], @target_radar_rr_sim::objdata.obj_distance_x[object_id], @target_radar_rr_sim::objdata.obj_distance_y[object_id], @target_radar_rr_sim::objdata.obj_velocity_x[object_id],  @target_radar_rr_sim::objdata.obj_velocity_y[object_id], @Classe_Obj_Sim::RoadObj.offset_x_rr, @Classe_Obj_Sim::RoadObj.offset_y_rr, @radarrr_par::mounting_ori_yaw, 0, 0);')
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