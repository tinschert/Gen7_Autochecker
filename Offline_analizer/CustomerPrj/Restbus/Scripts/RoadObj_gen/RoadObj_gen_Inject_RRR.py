# -*- coding: utf-8 -*-
# @file RoadObj_gen_Inject_RRR.py
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
 * @file Inject_Radar_RR.cin
 * @author ADAS_HIL_TEAM
 * @date 03-21-2023
 * @brief Handles injection of rear right radar
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
  #pragma library("..\..\..\..\Platform\Classe\DLL\Release64\RoadObj.dll")
}

variables
{
  int target_counter_radar_rr = 0;
  int injection_counter_radar_rr = -1;
}
'''

def update_Inject_RRR(file_path, num_objects):
    """
    Description: Main function for updating the injection file for the Radar Rear Right which orchestrates the update functions and saves the data in the file.

    Args:
      file_path: Path of the file which shall be updated/generated.
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    global script_list
    script_list = [Header]
    
    update_inject_radar_rr_hdr()
    update_inject_radar_rr_obj(num_objects)
    
    update_delete_radar_rr_bus(num_objects)
    update_delete_radar_rr_xcp(num_objects)

    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

def update_inject_radar_rr_hdr():
    """ 
    Description: Updates the injecting of the variable header values.

    Returns: Void
    
    """
    script_list.append('/** @brief Setting of variable header values')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void inject_radar_rr_hdr(){')
    script_list.append('  @CAN_RadarRR::RRR_Object::RRR_Object_ObjHdr_NumValidObjects = @target_radar_rr_sim::objdata.number_of_obj;')
    script_list.append('  @CAN_RadarRR::RRR_Object::RRR_Object_SpiHdr_SensorOriginPointX = @radarrr_par::mounting_pos_x;')
    script_list.append('  @CAN_RadarRR::RRR_Object::RRR_Object_SpiHdr_SensorOriginPointY = @radarrr_par::mounting_pos_y;')
    script_list.append('  @CAN_RadarRR::RRR_Object::RRR_Object_SpiHdr_SensorOriginPointZ = @radarrr_par::mounting_pos_z;')
    script_list.append('  @CAN_RadarRR::RRR_Object::RRR_Object_SpiHdr_SensorOrientYaw = @radarrr_par::mounting_ori_yaw;')
    script_list.append('    ')
    script_list.append('    // Set the number of objects to be put into the CAN TP ByteArray to be the object count, but atleast 1')
    script_list.append('    if (@target_radar_rr_sim::objdata.number_of_obj >= 1) @CAN_RadarRR_RRR_Object::Write_No_signals = @target_radar_rr_sim::objdata.number_of_obj; else @CAN_RadarRR_RRR_Object::Write_No_signals = 1;')
    script_list.append('}')
    script_list.append('')

def update_inject_radar_rr_obj(num_objects):
    """
    Description: Updates the injecting of object values.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
	# define object-independent script
    script_list.append('/** @brief Injects calculated object data stored in the target_radar_rr_sim arrays.')
    script_list.append('  *        This is done the way so that all valid objects are being injected in a chain (no "holes" in between).')
    script_list.append('  * @param object_id ID of the object that shall be injected.')
    script_list.append('  * @param injection_method Flag to decide if data shall be injected onto the BUS (=1) or via XCP (=2).')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void inject_radar_rr_obj(byte object_id, int injection_method)')
    script_list.append('{')
    script_list.append('  target_counter_radar_rr = 0;')
    script_list.append('  injection_counter_radar_rr = -1;')
    script_list.append('  ')
    script_list.append('  for(target_counter_radar_rr = 0; target_counter_radar_rr <= object_id; target_counter_radar_rr++){')
    script_list.append('    if(@target_radar_rr_sim::objdata.empty_obj[target_counter_radar_rr] == 0 && @target_radar_rr_sim::objdata.empty_obj[object_id] == 0){')
    script_list.append('      //increase the counter IF there is a valid object found AND only do so if the object we want to inject is valid')
    script_list.append('      injection_counter_radar_rr++;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  ')
    
    script_list.append('  if (injection_method == 1)')
    script_list.append('  { //Simulated sensor -> BUS')
    
    script_list.append('    switch (injection_counter_radar_rr)')
    script_list.append('    {')
    
    for obj_index in range(num_objects):
        obj_id = obj_index+1
        prefix = '@CAN_RadarRR::RRR_Object::RRR_Object_Obj{0}'.format("0"+str(obj_id) if obj_id < 10 else str(obj_id))
        object_buffer = '@CAN_RadarRR::RRR_Object::RRR_Object_Obj{0}'.format(str(obj_id) if obj_id < 10 else str(obj_id))
        
        script_list.append(f'      case {obj_index}: //"Object-{obj_index}"')
        
        script_list.append('        /**')
        script_list.append('          * Constant values')
        script_list.append('          */')
        script_list.append(f'        {object_buffer}.ObjId = injection_counter_radar_rr + 1;')
        script_list.append(f'        {object_buffer}.WidthVnce = 0;')
        script_list.append(f'        {object_buffer}.VxVnce = 0;')
        script_list.append(f'        {object_buffer}.AyVnce = 0;')
        script_list.append(f'        {object_buffer}.OrientationYawVnce = 0;')
        script_list.append(f'        {object_buffer}.LengthVnce = 0;')
        script_list.append(f'        {object_buffer}.AxVnce = 0;')
        script_list.append(f'        {object_buffer}.PyVnce = 0;')
        script_list.append(f'        {object_buffer}.PxVnce = 0;')
        script_list.append(f'        {object_buffer}.PxPyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PyAxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.AxAyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VyAyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VyAxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VxAyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VxAxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VxVyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VyVnce = 0;')
        script_list.append(f'        {object_buffer}.PyAyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PxAyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PxAxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PyVyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PxVyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PxVxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PyVxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.ExistProb = 100;')
        script_list.append(f'        {object_buffer}.ProbClassConfidence = 100;')
        script_list.append(f'        {object_buffer}.MeasurementStatus = 0; // always measured')
        script_list.append('        ')
        
        script_list.append('        /**')
        script_list.append('          * Variable values')
        script_list.append('          */')
        script_list.append(f'        {object_buffer}.OrientationYaw = dllGetRadarRRObjYawAngle(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Width = dllGetRadarRRInputObjectWidth(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Length = dllGetRadarRRInputObjectLength(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.RCS = dllGetRadarRRObjRa6RCS(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Px = dllGetRadarRRObjDistX(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Py = dllGetRadarRRObjDistY(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Vx = dllGetRadarRRObjVelX(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Vy = dllGetRadarRRObjVelY(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Ax = dllGetRadarRRObjAccelX(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Ay = dllGetRadarRRObjAccelY(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.MovingStatus = dllGetRadarRRObjRa6MovingStatus(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Age += front_corner_cycle_time * 10; //50 ms * 10 = unit is 100us')
        script_list.append(f'        {object_buffer}.ProbClassType = dllGetRadarRRObjRa6ObjType(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.ReferencePoint = dllGetRadarRRObjRefPnt(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.FilterInformation = 0; // PER has not yet defined this signal')
        
        script_list.append('        break;')
        script_list.append('        ')
    script_list.append('    }')

    script_list.append('  }')
    script_list.append('  else if(injection_method == 2)')
    script_list.append('  { //Real sensor -> XCP')
    script_list.append('    /**')
    script_list.append('      * TBD')
    script_list.append('      */')
    script_list.append('  }')
    script_list.append('}\n')

    print('Inject Radar_RR updated successfully.')

def update_delete_radar_rr_bus(num_objects):
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
    script_list.append('void delete_radar_rr_bus(byte object_id)')
    script_list.append('{')
    script_list.append('  target_counter_radar_rr = 0;')
    script_list.append('  injection_counter_radar_rr = -1;')
    script_list.append('  ')
    script_list.append('  for(target_counter_radar_rr = 0; target_counter_radar_rr <= object_id; target_counter_radar_rr++){')
    script_list.append('    if(@target_radar_rr_sim::objdata.empty_obj[target_counter_radar_rr] == 0 || target_counter_radar_rr == object_id){')
    script_list.append('      injection_counter_radar_rr++;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  ')

    script_list.append('  switch (injection_counter_radar_rr)')
    script_list.append('  {')
    
    for obj_index in range(num_objects):
        obj_id = obj_index+1
        prefix = '@CAN_RadarRR::RRR_Object::RRR_Object_Obj{0}'.format("0"+str(obj_id) if obj_id < 10 else str(obj_id))
        object_buffer = '@CAN_RadarRR::RRR_Object::RRR_Object_Obj{0}'.format(str(obj_id) if obj_id < 10 else str(obj_id))
        
        script_list.append(f'    case {obj_index}:')
        script_list.append(f'        {object_buffer}.ObjId = 0;')
        script_list.append(f'        {object_buffer}.WidthVnce = 0;')
        script_list.append(f'        {object_buffer}.VxVnce = 0;')
        script_list.append(f'        {object_buffer}.AyVnce = 0;')
        script_list.append(f'        {object_buffer}.OrientationYawVnce = 0;')
        script_list.append(f'        {object_buffer}.LengthVnce = 0;')
        script_list.append(f'        {object_buffer}.AxVnce = 0;')
        script_list.append(f'        {object_buffer}.PyVnce = 0;')
        script_list.append(f'        {object_buffer}.PxVnce = 0;')
        script_list.append(f'        {object_buffer}.PxPyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PyAxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.AxAyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VyAyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VyAxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VxAyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VxAxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VxVyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.VyVnce = 0;')
        script_list.append(f'        {object_buffer}.PyAyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PxAyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PxAxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PyVyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PxVyCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PxVxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.PyVxCoVnce = 0;')
        script_list.append(f'        {object_buffer}.ExistProb = 0;')
        script_list.append(f'        {object_buffer}.ProbClassConfidence = 0;')
        script_list.append(f'        {object_buffer}.MeasurementStatus = 0;')
        script_list.append(f'        {object_buffer}.OrientationYaw = -4.48;')
        script_list.append(f'        {object_buffer}.Width = 0;')
        script_list.append(f'        {object_buffer}.Length = 0;')
        script_list.append(f'        {object_buffer}.RCS = -102.4;')
        script_list.append(f'        {object_buffer}.Px = -512;')
        script_list.append(f'        {object_buffer}.Py = -128;')
        script_list.append(f'        {object_buffer}.Vx = -128;')
        script_list.append(f'        {object_buffer}.Vy = -64;')
        script_list.append(f'        {object_buffer}.Ax = -16;')
        script_list.append(f'        {object_buffer}.Ay = -16;')
        script_list.append(f'        {object_buffer}.MovingStatus = 0;')
        script_list.append(f'        {object_buffer}.Age = 0;')
        script_list.append(f'        {object_buffer}.ProbClassType = 0;')
        script_list.append(f'        {object_buffer}.ReferencePoint = 0;')
        script_list.append(f'        {object_buffer}.FilterInformation = 0;')
        script_list.append('      break;')
        script_list.append('      ')

    script_list.append('  }')
    script_list.append('}\n')

    print('Delete Radar_RR updated successfully.')

def update_delete_radar_rr_xcp(num_objects):
    """
    Description: Updates the deletion of values via xcp.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    script_list.append('/** @brief Sets the signals to raw value 0 of the object which deletes it on xcp.')
    script_list.append('  * @param object_id ID of the object which shall be deleted.')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void delete_radar_rr_xcp(byte object_id)')
    script_list.append('{')
    script_list.append('  /**')
    script_list.append('    * TBD')
    script_list.append('    */')
    script_list.append('}\n')