# -*- coding: utf-8 -*-
# @file RoadObj_gen_Inject_RFC.py
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
 * @file Inject_Radar_FC.cin
 * @author ADAS_HIL_TEAM
 * @date 03-21-2023
 * @brief Handles injection of front center radar
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
  int target_counter_radar_fc = 0;
  int injection_counter_radar_fc = -1;
}
'''

def update_Inject_RFC(file_path, num_objects):
    """
    Description: Main function for updating the injection file for the Radar Front Center which orchestrates the update functions and saves the data in the file.

    Args:
      file_path: Path of the file which shall be updated/generated.
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    global script_list
    script_list = [Header]
    
    update_inject_radar_fc_hdr()
    update_inject_radar_fc_loc(num_objects)
    update_inject_radar_fc_obj(num_objects)
    
    update_delete_radar_fc_bus_obj(num_objects)
    update_delete_radar_fc_bus(num_objects*10)
    update_delete_radar_fc_xcp(num_objects)
    update_delete_radar_fc_obj_xcp(num_objects)

    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

def update_inject_radar_fc_hdr():
    """ 
    Description: Updates the injecting of the variable header values.

    Returns: Void
    
    """
    script_list.append('/** @brief Setting of variable header values')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void inject_radar_fc_hdr(){')
    script_list.append('  if(@hil_ctrl::ra6_fc_lgu_loc_sim > 0){')
    script_list.append('//    $RFC_LocationHdrA::RFC_LocHdr_NumValidDetections = @target_radar_fc_sim::locdata.number_of_loc;')
    script_list.append('//    $RFC_LocationHdrA::RFC_LocHdr_SensorOriginPointX = @radarfc_par::mounting_pos_x;')
    script_list.append('//    $RFC_LocationHdrA::RFC_LocHdr_SensorOriginPointY = @radarfc_par::mounting_pos_y;')
    script_list.append('//    $RFC_LocationHdrA::RFC_LocHdr_SensorOriginPointZ = @radarfc_par::mounting_pos_z;')
    script_list.append('//    $RFC_LocationHdrA::RFC_LocHdr_SensorOrientYaw = @radarfc_par::mounting_ori_yaw;')
    script_list.append('    ')
    script_list.append('  }else if(@hil_ctrl::ra6_fc_sgu_obj_sim > 0){')
    script_list.append('    @CAN_RadarFC::RFC_Object::RFC_Object_ObjHdr_NumValidObjects = @target_radar_fc_sim::objdata.number_of_obj;')
    script_list.append('    @CAN_RadarFC::RFC_Object::RFC_Object_SpiHdr_SensorOriginPointX = @radarfc_par::mounting_pos_x;')
    script_list.append('    @CAN_RadarFC::RFC_Object::RFC_Object_SpiHdr_SensorOriginPointY = @radarfc_par::mounting_pos_y;')
    script_list.append('    @CAN_RadarFC::RFC_Object::RFC_Object_SpiHdr_SensorOriginPointZ = @radarfc_par::mounting_pos_z;')
    script_list.append('    @CAN_RadarFC::RFC_Object::RFC_Object_SpiHdr_SensorOrientYaw = @radarfc_par::mounting_ori_yaw;')
    script_list.append('    ')
    script_list.append('    // Set the number of objects to be put into the CAN TP ByteArray to be the object count, but atleast 1')
    script_list.append('    if (@target_radar_fc_sim::objdata.number_of_obj >= 1) @CAN_RadarFC_RFC_Object::Write_No_signals = @target_radar_fc_sim::objdata.number_of_obj; else @CAN_RadarFC_RFC_Object::Write_No_signals = 1;')
    script_list.append('  }')
    script_list.append('  ')
    script_list.append('}')
    script_list.append('')

def update_inject_radar_fc_loc(num_objects):
    """
    Description: Updates the injecting of location values.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
	# define object-independent script
    script_list.append('/** @brief Injects calculated location data stored in the target_radar_fc_sim arrays.')
    script_list.append('  *        This is done the way so that all valid objects are being injected in a chain (no "holes" in between).')
    script_list.append('  * @param object_id ID of the location that shall be injected.')
    script_list.append('  * @param injection_method Flag to decide if data shall be injected onto the BUS (=1) or via XCP (=2).')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void inject_radar_fc_loc(byte object_id, int injection_method)')
    script_list.append('{')
    script_list.append('  target_counter_radar_fc = 0;')
    script_list.append('  injection_counter_radar_fc = -1;')
    script_list.append('  ')
    script_list.append('  //all locations are filled into the array without holes and so being injected in this order')
    script_list.append('  injection_counter_radar_fc = object_id;')
    script_list.append('  ')
    
    script_list.append('  if (injection_method == 1)')
    script_list.append('  { //Simulated sensor -> BUS')
    
    script_list.append('    switch (injection_counter_radar_fc)')
    script_list.append('    {')
    
    for obj_index in range(num_objects*10):
        obj_id = obj_index
        obj_co_id = 0
        obj_coco_id = 0
        if obj_id % 3 == 0:
            obj_co_id = obj_index
            obj_coco_id = obj_index + 2
        elif obj_id % 3 == 1:
            obj_co_id = obj_index - 1
            obj_coco_id = obj_index + 1
        else:
            obj_co_id = obj_index - 2
            obj_coco_id = obj_index
        prefix = 'RFC_Loc{0}'.format("00"+str(obj_id) if (obj_id < 10) else ("0"+str(obj_id) if (obj_id >= 10 and obj_id < 100) else str(obj_id)))
        object_buffer = '$RFC_Location_{0}_{1}'.format( ("00"+str(obj_co_id)) if (obj_co_id < 10) else (("0"+str(obj_co_id)) if (obj_co_id >= 10 and obj_co_id < 100) else str(obj_co_id)),"00"+str(obj_coco_id) if (obj_coco_id < 10) else ("0"+str(obj_coco_id) if (obj_coco_id >= 10 and obj_coco_id < 100) else str(obj_coco_id)))
        
        script_list.append(f'      case {obj_index}: //"Object-{obj_index}"')
        
        script_list.append('        /**')
        script_list.append('          * Constant values')
        script_list.append('          */')
        script_list.append(f'        {object_buffer}::{prefix}_RadialDistanceVnce = 0.017;')
        script_list.append(f'        {object_buffer}::{prefix}_DistVelocityCoVnce = 0.0076;')
        script_list.append(f'        {object_buffer}::{prefix}_DistVelocityQuality = 255;')
        script_list.append(f'        {object_buffer}::{prefix}_ElevationQuality = 255;')
        script_list.append(f'        {object_buffer}::{prefix}_ElevationVnce = 0.092;')
        script_list.append(f'        {object_buffer}::{prefix}_AzimuthQuality = 255;')
        script_list.append(f'        {object_buffer}::{prefix}_AzimuthVnce = 0.092;')
        script_list.append(f'        {object_buffer}::{prefix}_RadialVelocityVnce = 0.0032;')
        script_list.append(f'        {object_buffer}::{prefix}_AzimuthalPartnerId = 1023;')
        script_list.append('        ')
        
        script_list.append('        /**')
        script_list.append('          * Variable values')
        script_list.append('          */')
        script_list.append(f'        {object_buffer}::{prefix}_RadialDistance = dllGetRadarFCLocRadialDistance(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}::{prefix}_RadialVelocity = dllGetRadarFCLocRadialVelocity(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}::{prefix}_Elevation = dllGetRadarFCLocElevationAngle(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}::{prefix}_Azimuth = dllGetRadarFCLocAzimuthAngle(@hil_ctrl::Handle_RoadObj, object_id) * 180 / PI;')
        script_list.append(f'        {object_buffer}::{prefix}_RadarCrossSection = dllGetRadarFCLocRCS(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}::{prefix}_RSSI = dllGetRadarFCLocRSSI(@hil_ctrl::Handle_RoadObj, object_id);')
        
        script_list.append('        break;')
        script_list.append('        ')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  else if(injection_method == 2)')
    script_list.append('  { //Real sensor -> XCP')
    XCP_name = "RadarFC_Loc"
    script_list.append(f'    @sysvar::XCP::{XCP_name}::_g_PL_AD_fw_Radar_1R1V_rpc_LocBypassingRunnable_LocBypassingRunnable_m_pad_ensRLocationsPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem::_m_SensState::_DataMeasured = 1;')
    script_list.append(f'    @sysvar::XCP::{XCP_name}::_g_PL_AD_fw_Radar_1R1V_rpc_LocBypassingRunnable_LocBypassingRunnable_m_pad_ensRLocationsPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem::_m_LocationList::_NumLocs = @target_radar_fc_sim::locdata.number_of_loc;')
    script_list.append('    ')
    
    script_list.append('    switch (injection_counter_radar_fc)')
    script_list.append('    {')
    
    for obj_index in range(num_objects):
        location_list_ns = "_g_PL_AD_fw_Radar_1R1V_rpc_LocBypassingRunnable_LocBypassingRunnable_m_pad_ensRLocationsPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem::_m_LocationList"
        script_list.append(f'      case {obj_index}: //"Object-{obj_index}"')
        
        script_list.append('        /**')
        script_list.append('          * Constant values')
        script_list.append('          */')
        #values from CLARA VW
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_dVar::_m_value = 0.012;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_dvCov::_m_value = -0.005;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_dvQly = 255;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_phiQly = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_phiVar::_m_value = 0.002;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_thetaQly = 1;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_thetaVar::_m_value = 0.0012;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_vVar::_m_value = 0.003;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_Rssi::_m_value = 83;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_idxAzimuthAmbiguityPeer = 65535;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_measStatus = 9;')
        script_list.append('        ')
        
        script_list.append('        /**')
        script_list.append('          * Variable values')
        script_list.append('          */')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_d = dllGetRadarFCLocRadialDistance(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_v = dllGetRadarFCLocRadialVelocity(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_phi::_m_value = dllGetRadarFCLocElevationAngle(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_theta::_m_value = dllGetRadarFCLocAzimuthAngle(@hil_ctrl::Handle_RoadObj, object_id) * 180 / PI;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_Rcs::_m_value = dllGetRadarFCLocRCS(@hil_ctrl::Handle_RoadObj, object_id);')
        
        script_list.append('        break;')
        script_list.append('        ')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('}\n')

    print('Inject Radar_FC updated successfully.')

def update_delete_radar_fc_bus(num_objects):
    """
    Description: Updates the deletion of values on the bus for objects and locations.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    script_list.append('/** @brief Sets the signals to raw value 0 of the location which deletes it on the bus.')
    script_list.append('  * @param object_id ID of the location that shall be deleted.')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void delete_radar_fc_bus_loc(byte object_id)')
    script_list.append('{')
    script_list.append('  target_counter_radar_fc = 0;')
    script_list.append('  injection_counter_radar_fc = -1;')
    script_list.append('  ')
    script_list.append('  //all locations are filled into the array without holes and so being deleted in this order')
    script_list.append('  injection_counter_radar_fc = object_id;')
    script_list.append('  ')

    script_list.append('  switch (injection_counter_radar_fc)')
    script_list.append('  {')
    
    for obj_index in range(num_objects):
        obj_id = obj_index
        obj_co_id = 0
        obj_coco_id = 0
        if obj_id % 3 == 0:
            obj_co_id = obj_index
            obj_coco_id = obj_index + 2
        elif obj_id % 3 == 1:
            obj_co_id = obj_index - 1
            obj_coco_id = obj_index + 1
        else:
            obj_co_id = obj_index - 2
            obj_coco_id = obj_index
        prefix = 'RFC_Loc{0}'.format("00"+str(obj_id) if (obj_id < 10) else ("0"+str(obj_id) if (obj_id >= 10 and obj_id < 100) else str(obj_id)))
        object_buffer = '$RFC_Location_{0}_{1}'.format( ("00"+str(obj_co_id)) if (obj_co_id < 10) else (("0"+str(obj_co_id)) if (obj_co_id >= 10 and obj_co_id < 100) else str(obj_co_id)),"00"+str(obj_coco_id) if (obj_coco_id < 10) else ("0"+str(obj_coco_id) if (obj_coco_id >= 10 and obj_coco_id < 100) else str(obj_coco_id)))
        
        script_list.append(f'    case {obj_index}:')
        script_list.append(f'      {object_buffer}::{prefix}_RadialDistanceVnce = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_DistVelocityCoVnce = -0.1024;')
        script_list.append(f'      {object_buffer}::{prefix}_DistVelocityQuality = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_ElevationQuality = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_ElevationVnce = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_AzimuthQuality = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_AzimuthVnce = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_RadialVelocityVnce = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_RadarCrossSection = -102.4;')
        script_list.append(f'      {object_buffer}::{prefix}_RSSI = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_AzimuthalPartnerId = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_RadialDistance = 0;')
        script_list.append(f'      {object_buffer}::{prefix}_RadialVelocity = -163.84;')
        script_list.append(f'      {object_buffer}::{prefix}_Elevation = -51.2;')
        script_list.append(f'      {object_buffer}::{prefix}_Azimuth = -102.4;')
        script_list.append('      break;')
        script_list.append('      ')

    script_list.append('  }')
    script_list.append('}\n')

    print('Delete Radar_FC updated successfully.')

def update_delete_radar_fc_xcp(num_objects):
    """
    Description: Updates the deletion of values via xcp for objects and locations.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    XCP_name = "RadarFC_Loc"
    script_list.append('/** @brief Sets the signals to raw value 0 of the object which deletes it on xcp.')
    script_list.append('  * @param object_id ID of the object that shall be deleted.')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void delete_radar_fc_xcp(byte object_id)')
    script_list.append('{')
    script_list.append('  target_counter_radar_fc = 0;')
    script_list.append('  injection_counter_radar_fc = -1;')
    script_list.append('  ')
    script_list.append('  for(target_counter_radar_fc = 0; target_counter_radar_fc <= object_id; target_counter_radar_fc++){')
    script_list.append('    if(@target_radar_fc_sim::objdata.empty_obj[target_counter_radar_fc] == 0 || target_counter_radar_fc == object_id){')
    script_list.append('      injection_counter_radar_fc++;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  ')
    
    script_list.append('    switch (injection_counter_radar_fc)')
    script_list.append('    {')
    for obj_index in range(num_objects):
        location_list_ns = "_g_PL_AD_fw_Radar_1R1V_rpc_LocBypassingRunnable_LocBypassingRunnable_m_pad_ensRLocationsPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem::_m_LocationList"
        script_list.append(f'      case {obj_index}: //"Object-{obj_index}"')
        #values from CLARA VW
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_dVar::_m_value = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_dvCov::_m_value = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_dvQly = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_phiQly = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_phiVar::_m_value = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_thetaQly = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_thetaVar::_m_value = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_vVar::_m_value = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_Rssi::_m_value = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_idxAzimuthAmbiguityPeer = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_measStatus = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_d = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_v = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_phi::_m_value = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_theta::_m_value = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_Item::_{obj_index}_::_Rcs::_m_value = 0;')
        
        script_list.append('        break;')
        script_list.append('        ')
    script_list.append('    }')
    script_list.append('}\n')

def update_inject_radar_fc_obj(num_objects):
    """
    Description: Updates the injecting of object values.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    location_list_ns = "_g_PL_AD_fw_Radar_1R1V_rpc_XilObjBypassingRunnable_XilObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem"
    XCP_name = "RadarFC_Obj"
    script_list.append('/** @brief Injects calculated object data stored in the target_radar_fc_sim arrays.')
    script_list.append('  *        This is done the way so that all valid objects are being injected in a chain (no "holes" in between).')
    script_list.append('  * @param object_id ID of the object that shall be injected.')
    script_list.append('  * @param injection_method Flag to decide if data shall be injected onto the BUS (=1) or via XCP (=2).')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void inject_radar_fc_obj(byte object_id, int injection_method)')
    script_list.append('{')
    script_list.append('  target_counter_radar_fc = 0;')
    script_list.append('  injection_counter_radar_fc = -1;')
    script_list.append('  ')
    script_list.append('  for(target_counter_radar_fc = 0; target_counter_radar_fc <= object_id; target_counter_radar_fc++){')
    script_list.append('    if(@target_radar_fc_sim::objdata.empty_obj[target_counter_radar_fc] == 0 && @target_radar_fc_sim::objdata.empty_obj[object_id] == 0){')
    script_list.append('      //increase the counter IF there is a valid object found AND only do so if the object we want to inject is valid')
    script_list.append('      injection_counter_radar_fc++;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  ')
    script_list.append('  if (injection_method == 1)')
    script_list.append('  { //Simulated sensor -> BUS')
    
    script_list.append('    switch (injection_counter_radar_fc)')
    script_list.append('    {')
    
    for obj_index in range(num_objects):
        obj_id = obj_index+1
        prefix = '@CAN_RadarFC::RFC_Object::RFC_Object_Obj{0}'.format("0"+str(obj_id) if obj_id < 10 else str(obj_id))
        object_buffer = '@CAN_RadarFC::RFC_Object::RFC_Object_Obj{0}'.format(str(obj_id) if obj_id < 10 else str(obj_id))
        
        script_list.append(f'      case {obj_index}: //"Object-{obj_index}"')
        
        script_list.append('        /**')
        script_list.append('          * Constant values')
        script_list.append('          */')
        script_list.append(f'        {object_buffer}.ObjId = injection_counter_radar_fc + 1;')
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
        script_list.append(f'        {object_buffer}.OrientationYaw = dllGetRadarFCObjYawAngle(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Width = dllGetRadarFCInputObjectWidth(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Length = dllGetRadarFCInputObjectLength(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.RCS = dllGetRadarFCObjRa6RCS(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Px = dllGetRadarFCObjDistX(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Py = dllGetRadarFCObjDistY(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Vx = dllGetRadarFCObjVelX(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Vy = dllGetRadarFCObjVelY(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Ax = dllGetRadarFCObjAccelX(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Ay = dllGetRadarFCObjAccelY(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.MovingStatus = dllGetRadarFCObjRa6MovingStatus(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.Age += front_corner_cycle_time * 10; //50 ms * 10 = unit is 100us')
        script_list.append(f'        {object_buffer}.ProbClassType = dllGetRadarFCObjRa6ObjType(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.ReferencePoint = dllGetRadarFCObjRefPnt(@hil_ctrl::Handle_RoadObj, object_id);')
        script_list.append(f'        {object_buffer}.FilterInformation = 0; // PER has not yet defined this signal')
        
        script_list.append('        break;')
        script_list.append('        ')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  else if(injection_method == 2)')
    script_list.append('  { //Real sensor -> XCP')
    script_list.append(f'    @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_alignment::_m_alpAzimuthAngOffsetN = -1146;')
    script_list.append(f'    @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_alignment::_m_alpMountAngleN = 0;')
    script_list.append(f'    @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_alignment::_m_dLongitudinalOffsetRearAxisN = @radarfc_par::mounting_pos_x * 128;')
    script_list.append(f'    @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_alignment::_m_dMountElevationN = @radarfc_par::mounting_pos_z * 32;')
    script_list.append(f'    @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_alignment::_m_dMountOffsetN = 0;')
    script_list.append('    ')
    script_list.append('    switch (object_id)')
    script_list.append('    {')
    for obj_index in range(num_objects):
        script_list.append(f'      case {obj_index}: //"Object-{obj_index}"')
        script_list.append('        // constant values')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_Valid_b = 1;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_HandleN = 1;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_alpPiVarYawAngleN = 3;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varAxN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varAyN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varVxN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varVyN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varDxN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varDyN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dVarLengthN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dVarWidthN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_wExistProbN = 64880;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_isObjectAsil = 1;')
        script_list.append('        ')
        script_list.append('        // target dimensions')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dWidthN = dllGetRadarFCInputObjectWidth(@hil_ctrl::Handle_RoadObj, 0) * 128;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dLengthN = dllGetRadarFCInputObjectLength(@hil_ctrl::Handle_RoadObj, 0) * 64;')
        script_list.append('          ')
        script_list.append('        // target movement')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dxN = dllGetRadarFCObjDistX(@hil_ctrl::Handle_RoadObj, 0) * 128;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dyN = dllGetRadarFCObjDistY(@hil_ctrl::Handle_RoadObj, 0) * 128;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dzN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_vxN = dllGetRadarFCObjVelX(@hil_ctrl::Handle_RoadObj, 0) * 256;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_vyN = dllGetRadarFCObjVelY(@hil_ctrl::Handle_RoadObj, 0) * 256;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_axN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_ayN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_alpPiYawAngleN = dllGetRadarFCObjYawAngle(@hil_ctrl::Handle_RoadObj, 0) * 128; // 128 correct?')
        script_list.append('        ')
        script_list.append('        // target probabilities')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_prob1HasBeenObservedMovingN = dllGetRadarFCObjProbMoving(@hil_ctrl::Handle_RoadObj, object_id) * 1.26;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_prob1MovingN = dllGetRadarFCObjProbMoving(@hil_ctrl::Handle_RoadObj, object_id) * 1.26;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1ObstacleN = (100 - dllGetRadarFCObjProbNonObst(@hil_ctrl::Handle_RoadObj, object_id)) * 1.28;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1NonObstacleN = dllGetRadarFCObjProbNonObst(@hil_ctrl::Handle_RoadObj, object_id) * 1.28;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1MobileN = dllGetRadarFCObjProbMoving(@hil_ctrl::Handle_RoadObj, object_id) * 1.28;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1StationaryN = (100 - dllGetRadarFCObjProbMoving(@hil_ctrl::Handle_RoadObj, object_id)) * 1.28;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1FourPlusWheelerN = (dllGetRadarFCObjProbCar(@hil_ctrl::Handle_RoadObj, object_id) + dllGetRadarFCObjProbTruck(@hil_ctrl::Handle_RoadObj, object_id)) * 1.28;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1TwoWheelerN = dllGetRadarFCObjProb2Wheeler(@hil_ctrl::Handle_RoadObj, object_id) * 1.28;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1PedestrianN = dllGetRadarFCObjProbPedestrian(@hil_ctrl::Handle_RoadObj, object_id) * 1.28;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1RoadsideBarrierN = (100 - dllGetRadarFCObjProbMoving(@hil_ctrl::Handle_RoadObj, object_id)) * 1.28;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1PassengerCarN = dllGetRadarFCObjProbCar(@hil_ctrl::Handle_RoadObj, object_id) * 1.28;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1TruckN = dllGetRadarFCObjProbTruck(@hil_ctrl::Handle_RoadObj, object_id) * 1.28;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1UnknownN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1MovUnknownN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1StatUnknownN = 0; // 128 previously')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1ObstUnknownN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1FourWheelUnknownN = 0;')
        script_list.append('        break;')
        script_list.append('        ')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('}\n')

def update_delete_radar_fc_bus_obj(num_objects):
    """
    Description: Updates the deletion of values on the bus.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    script_list.append('void delete_radar_fc_bus_obj(byte object_id)')
    script_list.append('{')
    script_list.append('  target_counter_radar_fc = 0;')
    script_list.append('  injection_counter_radar_fc = -1;')
    script_list.append('  ')
    script_list.append('  //object array can contain holes which is why the following code (injection_counter) closes those holes on the bus')
    script_list.append('  for(target_counter_radar_fc = 0; target_counter_radar_fc <= object_id; target_counter_radar_fc++){')
    script_list.append('    if(@target_radar_fc_sim::objdata.empty_obj[target_counter_radar_fc] == 0 || target_counter_radar_fc == object_id){')
    script_list.append('      injection_counter_radar_fc++;')
    script_list.append('    }')
    script_list.append('  }')
    script_list.append('  ')

    script_list.append('  switch (injection_counter_radar_fc)')
    script_list.append('  {')
    
    for obj_index in range(num_objects):
        obj_id = obj_index+1
        prefix = '@CAN_RadarFC::RFC_Object::RFC_Object_Obj{0}'.format("0"+str(obj_id) if obj_id < 10 else str(obj_id))
        object_buffer = '@CAN_RadarFC::RFC_Object::RFC_Object_Obj{0}'.format(str(obj_id) if obj_id < 10 else str(obj_id))
        
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

    print('Delete Radar_FL updated successfully.')

def update_delete_radar_fc_obj_xcp(num_objects):
    """
    Description: Updates the deletion of values via xcp for objects and locations.

    Args:
      num_objects: Number of objects which the updated file should be capable of handling.

    Returns: Void

    """
    location_list_ns = "_g_PL_AD_fw_Radar_1R1V_rpc_XilObjBypassingRunnable_XilObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem"
    XCP_name = "RadarFC_Obj"
    script_list.append('/** @brief Sets the signals to raw value 0 of the object which deletes it on xcp.')
    script_list.append('  * @param object_id ID of the object that shall be deleted.')
    script_list.append('  * @return void')
    script_list.append('  */')
    script_list.append('void delete_radar_fc_obj_xcp(byte object_id)')
    script_list.append('{')
    script_list.append('  switch (object_id)')
    script_list.append('  {')
    for obj_index in range(num_objects):
        script_list.append(f'      case {obj_index}: //"Object-{obj_index}"')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_Valid_b = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_HandleN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_alpPiVarYawAngleN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varAxN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varAyN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varVxN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varVyN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varDxN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_varDyN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dVarLengthN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dVarWidthN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_wExistProbN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_isObjectAsil = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dWidthN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dLengthN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dxN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dyN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_dzN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_vxN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_vyN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_axN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_ayN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_alpPiYawAngleN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_prob1HasBeenObservedMovingN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_prob1MovingN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1ObstacleN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1NonObstacleN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1MobileN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1StationaryN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1FourPlusWheelerN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1TwoWheelerN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1PedestrianN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1RoadsideBarrierN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1PassengerCarN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1TruckN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1UnknownN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1MovUnknownN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1StatUnknownN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1ObstUnknownN = 0;')
        script_list.append(f'        @sysvar::XCP::{XCP_name}::{location_list_ns}::_m_objectInformation::_{obj_index}_::_m_perObjectType::_m_prob1FourWheelUnknownN = 0;')
        script_list.append('        break;')
        script_list.append('        ')
    script_list.append('    }')
    script_list.append('}\n')