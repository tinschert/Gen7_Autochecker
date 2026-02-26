# -*- coding: utf-8 -*-
# @file RoadObj_gen_Inject_VFC.py
# @author ADAS_HIL_TEAM
# @date 03-21-2023

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


Header = '''/*@!Encoding:1252*/
/**
 * @file Inject_FVideo.cin
 * @author ADAS_HIL_TEAM
 * @date 03-21-2023
 * @brief Handles injection of front video
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
  int target_counter_fvideo = 0;
  int injection_counter_fvideo = -1;
}
'''

def update_Inject_VFC(file_path, num_objects):
    """
    Description: Main function for updating the injection file for the Front Video which orchestrates the update functions and saves the data in the file.

    Args:
      file_path: Path of the file which shall be updated/generated.
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    global script_list
    script_list = [Header]
    
    update_inject_fvideo_hdr()
    update_inject_fvideo_obj(num_objects)
    
    update_delete_fvideo_bus(num_objects)

    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

def update_inject_fvideo_hdr():
    """ 
    Description: Updates the injecting of the variable header values.

    Returns: Void
    
    """
    script_list.append('/** @brief Setting of variable header values')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void inject_fvideo_hdr(){')
    script_list.append('  $VFC_ObjectHdr::VFC_ObjHdr_NumValidObjects = @target_fvideo_sim::objdata.number_of_obj;')
    script_list.append('}')
    script_list.append('')

def update_inject_fvideo_obj(num_objects):
    """
    Description: Updates the injecting of object values.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
	# define object-independent script
    script_list.append('/** @brief Injects calculated object data stored in the target_fvideo_sim arrays.')
    script_list.append('  *        This is done the way so that all valid objects are being injected in a chain (no "holes" in between).')
    script_list.append('  * @param object_id ID of the object that shall be injected.')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void inject_fvideo_obj(byte object_id)')
    script_list.append('{')
    script_list.append('  target_counter_fvideo = 0;')
    script_list.append('  injection_counter_fvideo = -1;')
    script_list.append('  ')
    script_list.append('  for(target_counter_fvideo = 0; target_counter_fvideo <= object_id; target_counter_fvideo++){')
    script_list.append('    if(@target_fvideo_sim::objdata.empty_obj[target_counter_fvideo] == 0){')
    script_list.append('      injection_counter_fvideo++;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  ')
    
    script_list.append('  switch (injection_counter_fvideo)')
    script_list.append('  {')
    
    for obj_index in range(num_objects):
        obj_id = obj_index
        prefix = 'VFC_Obj{0}'.format("0"+str(obj_id) if obj_id < 10 else str(obj_id))
        object_buffer = '$VFC_Object{0}'.format("0"+str(obj_id) if obj_id < 10 else str(obj_id))
        
        script_list.append(f'      case {obj_index}: //"Object-{obj_index}"')
        
        script_list.append('      /**')
        script_list.append('        * Constant values')
        script_list.append('        */')
        script_list.append(f'      {object_buffer}::{prefix}_ObjId = injection_counter_fvideo + 1;')
        script_list.append(f'      {object_buffer}::{prefix}_AxStdDev = 0.1;')
        script_list.append(f'      {object_buffer}::{prefix}_AyStdDev = 0.1;')
        script_list.append(f'      {object_buffer}::{prefix}_PxStdDev = 0.05;')
        script_list.append(f'      {object_buffer}::{prefix}_PyStdDev = 0.05;')
        script_list.append(f'      {object_buffer}::{prefix}_OrientationYawStdDev = 0.01;')
        script_list.append(f'      {object_buffer}::{prefix}_HeightStdDev = 0.01;')
        script_list.append(f'      {object_buffer}::{prefix}_LengthStdDev = 0.05;')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormAxStdDev = 0.0025;')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormVxStdDev = 0.001;')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormVyStdDev = 0.001;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeBotStdDev = 0.0002;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeLeftStdDev = 0.0002;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeFarStdDev = 0.0002;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeRightStdDe = 0.0002;')
        script_list.append(f'      {object_buffer}::{prefix}_VxStdDev = 0.1;')
        script_list.append(f'      {object_buffer}::{prefix}_VyStdDev = 0.1;')
        script_list.append(f'      {object_buffer}::{prefix}_WidthStdDev = 0.01;')
        script_list.append(f'      {object_buffer}::{prefix}_MovementObservedMeasSt = 1;')
        script_list.append(f'      {object_buffer}::{prefix}_MovementStandingMeasSt = 1;')
        script_list.append(f'      {object_buffer}::{prefix}_OncomingMeasStatus = 1;')
        script_list.append(f'      {object_buffer}::{prefix}_OutsideRoadMeasStatus = 1;')
        script_list.append(f'      {object_buffer}::{prefix}_TargetObjTypeAccConf = 98;')
        script_list.append(f'      {object_buffer}::{prefix}_2DScaleChangeStdDev = 0.0001;')
        script_list.append(f'      {object_buffer}::{prefix}_2DScaleChange = 1;')
        script_list.append(f'      {object_buffer}::{prefix}_MeasurementStatus = 1;')
        script_list.append(f'      {object_buffer}::{prefix}_TypeConf = 98;')
        script_list.append(f'      {object_buffer}::{prefix}_ExistProb = 98;')
        script_list.append('      ')
        
        script_list.append('      /**')
        script_list.append('        * Variable values')
        script_list.append('        */')
        script_list.append(f'      {object_buffer}::{prefix}_Width = @target_fvideo_sim::objdata.obj_width[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_Length = @target_fvideo_sim::objdata.obj_length[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_Height = @target_fvideo_sim::objdata.obj_height[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_Px = @target_fvideo_sim::objdata.obj_distance_x[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_Py = @target_fvideo_sim::objdata.obj_distance_y[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_Vx = @target_fvideo_sim::objdata.obj_velocity_x[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_Vy = @target_fvideo_sim::objdata.obj_velocity_y[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_Ax = @target_fvideo_sim::objdata.obj_acceleration_x[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_Ay = @target_fvideo_sim::objdata.obj_acceleration_y[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormVx = @target_fvideo_sim::objdata.obj_norm_vel_x[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormVy = @target_fvideo_sim::objdata.obj_norm_vel_y[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormAx = @target_fvideo_sim::objdata.obj_norm_accel[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_LightStatBrakeLight = @target_fvideo_sim::objdata.obj_brake_light[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_OrientationYaw = @target_fvideo_sim::objdata.obj_heading_angle[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_LightStatTurnIndicator = @target_fvideo_sim::objdata.obj_turn_light[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_MovementProbLong = @target_fvideo_sim::objdata.obj_prob_moving_long[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_MovementProbLat = @target_fvideo_sim::objdata.obj_prob_moving_lat[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_MovementObserved = @target_fvideo_sim::objdata.obj_moving[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_MovementStanding = 1 - @target_fvideo_sim::objdata.obj_moving[object_id];')
        script_list.append(f'      ')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeBot = @target_fvideo_sim::objdata.obj_phi_bottom[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeLeft = @target_fvideo_sim::objdata.obj_phi_left[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeRight = @target_fvideo_sim::objdata.obj_phi_right[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeFar = @target_fvideo_sim::objdata.obj_phi_mid[object_id];')
        script_list.append(f'      ')
        script_list.append(f'      {object_buffer}::{prefix}_Type = @target_fvideo_sim::objdata.obj_type[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_TargetObjTypeAcc = @target_fvideo_sim::objdata.obj_target_acc_type[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_ClassifiedView = @target_fvideo_sim::objdata.obj_classified_view[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_VisibleView = @target_fvideo_sim::objdata.obj_visible_view[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_Oncoming = @target_fvideo_sim::objdata.obj_oncoming[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_OutsideRoad = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_Reliability = @target_fvideo_sim::objdata.obj_reliability[object_id];')
        script_list.append(f'      {object_buffer}::{prefix}_MeasurementSource = @target_fvideo_sim::objdata.obj_meas_source[object_id];')
        
        script_list.append('        break;')
        script_list.append('        ')

    script_list.append('  }')
    script_list.append('}\n')

    print('Inject FVideo updated successfully.')

def update_delete_fvideo_bus(num_objects):
    """
    Description: Updates the deletion of values on the bus.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    script_list.append('/** @brief Sets the signals to raw value 0 of the object which deletes it on the bus.')
    script_list.append('  * @param object_id ID of the object which shall be deleted.')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void delete_fvideo_bus(byte object_id)')
    script_list.append('{')
    script_list.append('  target_counter_fvideo = 0;')
    script_list.append('  injection_counter_fvideo = -1;')
    script_list.append('  ')
    script_list.append('  for(target_counter_fvideo = 0; target_counter_fvideo <= object_id; target_counter_fvideo++){')
    script_list.append('    if(@target_fvideo_sim::objdata.empty_obj[target_counter_fvideo] == 0 || target_counter_fvideo == object_id){')
    script_list.append('      injection_counter_fvideo++;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  ')
    
    script_list.append('  switch (injection_counter_fvideo)')
    script_list.append('  {')
    
    for obj_index in range(num_objects):
        obj_id = obj_index
        prefix = 'VFC_Obj{0}'.format("0"+str(obj_id) if obj_id < 10 else str(obj_id))
        object_buffer = '$VFC_Object{0}'.format("0"+str(obj_id) if obj_id < 10 else str(obj_id))
        
        script_list.append(f'    case {obj_index}:')
        script_list.append(f'      {object_buffer}::{prefix}_ObjId = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_ClassifiedView = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_AxStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_AyStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_PxStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_PyStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_OrientationYawStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_HeightStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_LengthStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormAxStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormVxStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormVyStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeBotStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeLeftStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeFarStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeRightStdDe = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_VxStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_VyStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_WidthStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_MovementObservedMeasSt = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_MovementStandingMeasSt = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_OncomingMeasStatus = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_OutsideRoadMeasStatus = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_TargetObjTypeAccConf = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_2DScaleChangeStdDev = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_2DScaleChange = 0.5;')
        script_list.append(f'      {object_buffer}::{prefix}_VisibleView = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_Oncoming = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_OutsideRoad = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_MeasurementStatus = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_TypeConf = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_ExistProb = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_MeasurementSource = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_Reliability = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_Width = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_Px = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_Py = -80;')
        script_list.append(f'      {object_buffer}::{prefix}_Vx = -154;')
        script_list.append(f'      {object_buffer}::{prefix}_Vy = -50;')
        script_list.append(f'      {object_buffer}::{prefix}_Ax = -16;')
        script_list.append(f'      {object_buffer}::{prefix}_Ay = -12;')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormVx = -40;')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormVy = -40;')
        script_list.append(f'      {object_buffer}::{prefix}_2DNormAx = -10;')
        script_list.append(f'      {object_buffer}::{prefix}_LightStatBrakeLight = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_OrientationYaw = -1.57;')
        script_list.append(f'      {object_buffer}::{prefix}_LightStatTurnIndicator = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_MovementProbLong = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_MovementProbLat = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_MovementObserved = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_MovementStanding = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeBot = -0.5;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeLeft = -1;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeRight = -1;')
        script_list.append(f'      {object_buffer}::{prefix}_2DAngPosEdgeFar = -1;')
        script_list.append(f'      {object_buffer}::{prefix}_Height = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_Length = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_Type = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_TargetObjTypeAcc = 0;')
        script_list.append('      break;')
        script_list.append('      ')

    script_list.append('  }')
    script_list.append('}')

    print('Delete FVideo updated successfully.')