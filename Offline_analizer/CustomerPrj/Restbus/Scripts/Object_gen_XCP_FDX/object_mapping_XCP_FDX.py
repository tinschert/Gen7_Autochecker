# -*- coding: utf-8 -*-
# @file object_mapping_XCP_FDX.py
# @author ADAS_HIL_TEAM
# @date 10-04-2022

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2022-2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################

# pre-defined headers

FRadar_header = '''/*@!Encoding:1252*/
/**
 * @file Road_Obj.can
 * @author Anton Rommel, Rafael Herrera
 * @date 19.08.2021
 * @brief Handles Radar object injection into XCP
 */

includes
{
}

variables
{
  /*
Integers in form of
byte (unsigned, 1 Byte)
word (unsigned, 2 Byte)
dword (unsigned, 4 Byte)
int (signed, 2 Byte)
long (signed, 4 Byte)
int64(signed, 8 Byte)
qword(unsigned, 8 Byte)
Individual character
char (1 Byte)
Floating point numbers
float (8 Byte)
double (8 Byte)
*/  
}

'''
FRadar_FDX_header = '''/*@!Encoding:1252*/
/**
 * @file Road_Obj.can
 * @author Rafael Herrera, Anton Rommel
 * @date 30.08.2021
 * @brief Handles Radar object injection into XCP
 */

includes
{
}

variables
{
  /*
Integers in form of
byte (unsigned, 1 Byte)
word (unsigned, 2 Byte)
dword (unsigned, 4 Byte)
int (signed, 2 Byte)
long (signed, 4 Byte)
int64(signed, 8 Byte)
qword(unsigned, 8 Byte)
Individual character
char (1 Byte)
Floating point numbers
float (8 Byte)
double (8 Byte)
*/  
}
'''

FVideo_header = '''/*@!Encoding:1252*/
/**
 * @file Road_Obj.can
 * @author Rafael Herrera, Anton Rommel
 * @date 19.08.2021
 * @brief Handles Video object creation into sys variables
 */

includes
{
}

variables
{
  double phiLeft = 0 ;
  double phiRight = 0 ;
  double phiMiddle[3] = {0,0,0};
  double phiMiddle_previous[3] = {0,0,0};
  double phiMiddle_vel[3] = {0,0,0};
  double dx_image_plane_crossing = 0;
  double tt_image_plane_crossing = 0;
  byte fvideo_obj_count = 0;
  byte closest_obj_id = 0;
  double fvideo_aeb_act_dx = 10.0;
}

void obj_sim_update_fvideo_bus(byte object_id)
{
  // Header values
  @FDP1_OBJ_DESC_1_CMF2_156::AEB_AVAILABILITY_Rv = 1;
  @FDP1_OBJ_DESC_1_CMF2_156::CAMERA_EE_STATUS_Rv = 1;
  @FDP1_OBJ_DESC_1_CMF2_156::CIPV_FCV_Rv = 3;
  // object ID of the closest object for AEB activation
  for(fvideo_obj_count = 1; fvideo_obj_count < (obj_max_allowed); fvideo_obj_count++)
  {
    if ((@Classe_Obj_Sim::obj_data.obj_dx[closest_obj_id] > 0 ) && (@Classe_Obj_Sim::obj_data.obj_dx[fvideo_obj_count] > 0))
    {
      if(@Classe_Obj_Sim::obj_data.obj_dx[closest_obj_id] < @Classe_Obj_Sim::obj_data.obj_dx[fvideo_obj_count] )
      {
        closest_obj_id = closest_obj_id;
      }
      else
      {
        closest_obj_id = fvideo_obj_count;
      }
    }
  }
  @FDP1_OBJ_DESC_1_CMF2_156::CIPV_ID_Rv = @Classe_Obj_Sim::obj_data.obj_id[closest_obj_id] + 1;
'''

Corner_header = '''/*@!Encoding:1252*/
/**
 * @file Road_Obj.can
 * @author Rafael Herrera, Anton Rommel
 * @date 19.08.2021
 * @brief Handles Corner object creation
 */

includes
{
}

variables
{

}

'''

CornerFR_header = '''/*@!Encoding:1252*/
/**
 * @file Road_Obj.can
 * @author Anton Rommel, Rafael Herrera
 * @date 19.08.2021
 * @brief Handles Radar object injection into XCP
 */

includes
{
}

variables
{
  /*
Integers in form of
byte (unsigned, 1 Byte)
word (unsigned, 2 Byte)
dword (unsigned, 4 Byte)
int (signed, 2 Byte)
long (signed, 4 Byte)
int64(signed, 8 Byte)
qword(unsigned, 8 Byte)
Individual character
char (1 Byte)
Floating point numbers
float (8 Byte)
double (8 Byte)
*/  
}
'''


# update Road_Obj_FRadar XCP
def update_FRadar_XCP(file_path, num_objects=9):
    """
    

    Args:
      file_path: 
      num_objects:  (Default value = 9)

    Returns:

    """
	# define object-independent script
    common_buffer = '@sysvar::XCP::RadarFC::_g_PER_Hil_ObjBypassingRunnable_ObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem'
                                                                                                                                                                                       
    script_list = [FRadar_header]
    
    script_list.append('void obj_sim_update_fradar_xcp(byte object_id)')
    script_list.append('{\n  //header')
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# switch for differect objects
    script_list.append('\n  switch (@Classe_Obj_Sim::obj_data.obj_id[object_id])')
    script_list.append('  {')
	# loop for generating multiple objects
    obj_types = ['Non-Obstacle', 'unknown', 'RoadSideBarrier', '2Wheeler', 'Pedestrian', 'Truck', 'PassengerCar']
    for obj_id in range(num_objects):
        object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_objectInformation', str(obj_id))
        script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
        script_list.append('    //constant')
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_Valid_b', '1'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_HandleN', '1'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_wExistProbN', '64880'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_isObjectAsil', '1'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', '128'))

        script_list.append('\n    //target movement\n')
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dxN', '@Classe_Obj_Sim::obj_data.obj_dx[{0}] * 128'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dyN', '@Classe_Obj_Sim::obj_data.obj_dy[{0}] * 128'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dzN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}] * 256'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@Classe_Obj_Sim::obj_data.obj_relative_vy[{0}] * 256'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '0'))

        script_list.append('\n    //target object moving or not')
        script_list.append('    if (abs(@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}]) != 0)'.format(str(obj_id)))
        script_list.append('    {')
        script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '126'))
        script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '126'))
        script_list.append('    }\n    else\n    {')
        script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '0'))
        script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '0'))

        script_list.append('    }\n')
        # switch for object type
        script_list.append('      //object classification')
        script_list.append('    switch (@Classe_Obj_Sim::obj_data.obj_type[{0}])'.format(str(obj_id)))
        script_list.append('    {')
        extend_object_buffer = '{0}::_m_perObjectType'.format(object_buffer)

        for index in range(len(obj_types)):

            script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if index>=2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index==0 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==1 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MobileN', '128' if index>=3 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StationaryN', '128' if index==2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstUnknownN', '128' if index<=1 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourPlusWheelerN', '128' if index>=5 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TwoWheelerN', '128' if index==3 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PedestrianN', '128' if index==4 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MovUnknownN', '128' if index<=2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1RoadsideBarrierN', '128' if index==2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StatUnknownN', '128' if index!=2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PassengerCarN', '128' if index==6 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TruckN', '128' if index==5 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourWheelUnknownN', '128' if index<=4 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '64' if (index==3 or index ==4) else '256'))            
            script_list.append('        break;')
            script_list.append('    }' if index == len(obj_types)-1 else '')
        script_list.append('    break;')
        script_list.append('  }' if obj_id == num_objects-1 else '')
    script_list.append('}')

    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

# update Road_Obj_FRadar FDX
def update_FRadar_FDX(file_path, num_objects=9):
    """
    

    Args:
      file_path: 
      num_objects:  (Default value = 9)

    Returns:

    """
	# define object-independent script
    common_buffer = '@sysvar::XCP::RadarFC::_g_PER_Hil_ObjBypassingRunnable_ObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem'
    script_list = [FRadar_FDX_header]

    script_list.append('void obj_sim_update_fradar_fdx(byte object_id)')
    script_list.append('{\n  //header')
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# switch for differect objects
    script_list.append('\n  switch (object_id)')
    script_list.append('  {')
	# loop for generating multiple objects
    obj_types = ['unknown','Pedestrian','2Wheeler::Cloe-> Bike','2Wheeler::Cloe-> Motorbike','PassengerCar','Truck','Non-Obstacle::Cloe->Trailer', 'RoadSideBarrier']
    for obj_id in range(num_objects):
        object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_objectInformation', str(obj_id))
        script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
        script_list.append('    //constant')
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_Valid_b', '1'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_HandleN', '1'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_wExistProbN', '64880'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_isObjectAsil', '1'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', '128'))

        namespace_FDX_FrontRadar_Obj = "@FDX_in_HIL_specific_FRadar_Obj"
        FrontRadarSignalPre = "FDX_in_FRadar_"
        obj_count = obj_id -1
        script_list.append('\n      //target movement\n')
        script_list.append('{0}::{1} = {2}::{3}{4}{5};'.format(object_buffer, '_m_dxN', namespace_FDX_FrontRadar_Obj, FrontRadarSignalPre, obj_id, '_m_dxN'))
        script_list.append('{0}::{1} = {2}::{3}{4}{5};'.format(object_buffer, '_m_dyN', namespace_FDX_FrontRadar_Obj, FrontRadarSignalPre, obj_id, '_m_dyN'))
        script_list.append('{0}::{1} = {2}::{3}{4}{5};'.format(object_buffer, '_m_dzN', namespace_FDX_FrontRadar_Obj, FrontRadarSignalPre, obj_id, '_m_dzN'))
        script_list.append('{0}::{1} = {2}::{3}{4}{5};'.format(object_buffer, '_m_vxN', namespace_FDX_FrontRadar_Obj, FrontRadarSignalPre, obj_id, '_m_vxN'))
        script_list.append('{0}::{1} = {2}::{3}{4}{5};'.format(object_buffer, '_m_vyN', namespace_FDX_FrontRadar_Obj, FrontRadarSignalPre, obj_id, '_m_vyN'))
        script_list.append('{0}::{1} = {2}::{3}{4}{5};'.format(object_buffer, '_m_axN', namespace_FDX_FrontRadar_Obj, FrontRadarSignalPre, obj_id, '_m_axN'))
        script_list.append('{0}::{1} = {2}::{3}{4}{5};'.format(object_buffer, '_m_ayN', namespace_FDX_FrontRadar_Obj, FrontRadarSignalPre, obj_id, '_m_ayN'))
        script_list.append('{0}::{1} = {2}::{3}{4}{5};'.format(object_buffer, '_m_dLengthN', namespace_FDX_FrontRadar_Obj, FrontRadarSignalPre, obj_id, '_m_dLengthN'))
        script_list.append('{0}::{1} = {2}::{3}{4}{5};'.format(object_buffer, '_m_dWidthN', namespace_FDX_FrontRadar_Obj, FrontRadarSignalPre, obj_id, '_m_dWidthN'))
        script_list.append('{0}::{1} = {2}::{3}{4}{5};'.format(object_buffer, '_m_alpPiYawAngleN', namespace_FDX_FrontRadar_Obj, FrontRadarSignalPre, obj_id, '_m_alpPiYawAngleN'))
        script_list.append('\n      //target object moving or not')
        script_list.append('{0}{1}::{2}{3}{4}' .format('      if (abs(',namespace_FDX_FrontRadar_Obj,FrontRadarSignalPre,obj_id,'_m_vxN) != 0)'))
        script_list.append('      {')
        script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '126'))
        script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '126'))
        script_list.append('      }\n      else\n      {')
        script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '0'))
        script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '0'))

        script_list.append('      }\n')
        # switch for object type

        script_list.append('      //object classification')
        script_list.append('{0}::{1}{2}{3}'.format('    switch (@FDX_in_HIL_specific_FRadar_Obj','FDX_in_FRadar_',obj_id,'_Sensed_Object_Classification)'))
        script_list.append('    {')
        extend_object_buffer = '{0}::_m_perObjectType'.format(object_buffer)

        for index in range(len(obj_types)):

            script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if (index!= 0 and index!=6) else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index==6 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==0 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MobileN', '128' if (index!=0 and index !=7) else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StationaryN', '128' if index==7 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstUnknownN', '128' if index==0 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourPlusWheelerN', '128' if (index==4 or index==5) else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TwoWheelerN', '128' if (index == 2 or index==3) else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PedestrianN', '128' if index==1 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MovUnknownN', '128' if (index==0 or index == 6 or index == 7) else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1RoadsideBarrierN', '128' if index==7 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StatUnknownN', '128' if index!=7 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PassengerCarN', '128' if index==4 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TruckN', '128' if index==5 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourWheelUnknownN', '128' if (index!=4 and index!=5) else '0'))
            script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '64' if (index==1 or index ==2 or index ==3) else '256')) 
            
            script_list.append('          break;')
            script_list.append('      }' if index == len(obj_types)-1 else '')
        script_list.append('      break;')
        script_list.append('  }' if obj_id == num_objects-1 else '')
    script_list.append('}')


    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

# update Road_Obj_FRadar XCP
def update_CRadarFL_XCP(file_path, num_objects=9):
    """
    

    Args:
      file_path: 
      num_objects:  (Default value = 9)

    Returns:

    """
	# define object-independent script
    common_buffer = '  @sysvar::XCP::RadarFL::_g_PlReCoFw_PlReCoPer_ObjBypassingRunnable_ObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem::port_ens_r_obj_sensor_base::_'
    script_list = [CornerFR_header]
    
    script_list.append('void obj_sim_update_CRadarFL_xcp(byte object_id)')
    script_list.append('{\n  //header')
<<<<<<< HEAD
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# switch for differect objects
    script_list.append('\n  switch (@Classe_Obj_Sim::obj_data.obj_id[object_id])')
    script_list.append('  {')
	# loop for generating multiple objects
    obj_types = ['Non-Obstacle', 'unknown', 'RoadSideBarrier', '2Wheeler', 'Pedestrian', 'Truck', 'PassengerCar']
    for obj_id in range(num_objects):
        object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_movObjectInformation', str(obj_id))
        script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
        script_list.append('    //constant')
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Meas_b', '1'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Measurable_b', '1'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Valid_b', '1'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxVxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyVyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyWidthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarVxAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDxN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_wExistProbN', '64880'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_referencePtPosIndexN', '10'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
        script_list.append('\n    //target movement\n')
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dxN', '@Classe_Obj_Sim::obj_data.obj_dx[{0}] * 128'.format(str(obj_id))))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dyN', '@Classe_Obj_Sim::obj_data.obj_dy[{0}] * 128'.format(str(obj_id))))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dzN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}] * 256'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@Classe_Obj_Sim::obj_data.obj_relative_vy[{0}] * 256'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '0'))
        script_list.append('\n    //target object moving or not')
        script_list.append('    if (abs(@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}]) != 0)'.format(str(obj_id)))
        script_list.append('    {')
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '126'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '126'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '128'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '0'))
        script_list.append('    }\n    else\n    {')
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '128'))
        script_list.append('    }\n')
        # switch for object type
        script_list.append('      //object classification')
        script_list.append('    switch (@Classe_Obj_Sim::obj_data.obj_type[{0}])'.format(str(obj_id)))
        script_list.append('    {')
        extend_object_buffer = '{0}::STA_OBJECT_INFORMATION_ST::_::_m_ohyObjectType_st'.format(object_buffer)
        for index in range(len(obj_types)):
            script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index<1 else 0))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if index>1 else 0))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==1 else 0))
            # different signal names for type 2
            name0 = "_m_prob1UnknownN" if index != 2 else "_m_prob1MobileN"
            name1 = "_m_probMobile_st::_m_prob1FourPlusWheelerN" if index != 2 else "_m_prob1StationaryN"
            name2 = "_m_probMobile_st::_m_prob1PedestrianN" if index != 2 else "_m_prob1UnknownN"
            name3 = "_m_prob1TwoWheelerN" if index != 2 else "_m_prob1FourPlusWheelerN"
            name4 = "_m_prob1UnknownN" if index != 2 else "_m_prob1PedestrianN"
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name0), '128' if index<2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name1), '128' if index==2 or index>4 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name2), '128' if index==4 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name3), '128' if index==3 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name4), '128' if index<2 else '0'))
            if index == 2:
                script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1TwoWheelerN', '0'))
                script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1UnknownN', '0'))
            
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1PassengerCarN', '128' if index==6 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1TruckN', '128' if index==5 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1UnknownN', '128' if index in [0, 1, 3, 4] else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1RoadsideBarrierN', '128' if index==2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1UnknownN', '128' if index<2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', str(64 if index!=1 else 0)))
            script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '@Classe_Obj_Sim::obj_data.obj_width[{0}] * 128'.format(str(obj_id))))
            script_list.append('        break;')
            script_list.append('    }' if index == len(obj_types)-1 else '')
        script_list.append('    break;')
        script_list.append('  }' if obj_id == num_objects-1 else '')
=======
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# # switch for differect objects
    # script_list.append('\n  switch (@Classe_Obj_Sim::obj_data.obj_id[object_id])')
    # script_list.append('  {')
	# # loop for generating multiple objects
    # obj_types = ['Non-Obstacle', 'unknown', 'RoadSideBarrier', '2Wheeler', 'Pedestrian', 'Truck', 'PassengerCar']
    # for obj_id in range(num_objects):
    #     object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_movObjectInformation', str(obj_id))
    #     script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
    #     script_list.append('    //constant')
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Meas_b', '1'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Measurable_b', '1'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Valid_b', '1'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxAxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxVxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyVyN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyWidthN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarVxAxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDxN', '0'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDyN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_wExistProbN', '64880'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_referencePtPosIndexN', '10'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
    #     script_list.append('\n    //target movement\n')
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dxN', '@Classe_Obj_Sim::obj_data.obj_dx[{0}] * 128'.format(str(obj_id))))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dyN', '@Classe_Obj_Sim::obj_data.obj_dy[{0}] * 128'.format(str(obj_id))))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dzN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}] * 256'.format(str(obj_id))))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@Classe_Obj_Sim::obj_data.obj_relative_vy[{0}] * 256'.format(str(obj_id))))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '0'))
    #     script_list.append('\n    //target object moving or not')
    #     script_list.append('    if (abs(@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}]) != 0)'.format(str(obj_id)))
    #     script_list.append('    {')
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '126'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '126'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '128'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '0'))
    #     script_list.append('    }\n    else\n    {')
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '0'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '0'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '0'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '128'))
    #     script_list.append('    }\n')
    #     # switch for object type
    #     script_list.append('      //object classification')
    #     script_list.append('    switch (@Classe_Obj_Sim::obj_data.obj_type[{0}])'.format(str(obj_id)))
    #     script_list.append('    {')
    #     extend_object_buffer = '{0}::STA_OBJECT_INFORMATION_ST::_::_m_ohyObjectType_st'.format(object_buffer)
    #     for index in range(len(obj_types)):
    #         script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index<1 else 0))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if index>1 else 0))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==1 else 0))
    #         # different signal names for type 2
    #         name0 = "_m_prob1UnknownN" if index != 2 else "_m_prob1MobileN"
    #         name1 = "_m_probMobile_st::_m_prob1FourPlusWheelerN" if index != 2 else "_m_prob1StationaryN"
    #         name2 = "_m_probMobile_st::_m_prob1PedestrianN" if index != 2 else "_m_prob1UnknownN"
    #         name3 = "_m_prob1TwoWheelerN" if index != 2 else "_m_prob1FourPlusWheelerN"
    #         name4 = "_m_prob1UnknownN" if index != 2 else "_m_prob1PedestrianN"
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name0), '128' if index<2 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name1), '128' if index==2 or index>4 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name2), '128' if index==4 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name3), '128' if index==3 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name4), '128' if index<2 else '0'))
    #         if index == 2:
    #             script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1TwoWheelerN', '0'))
    #             script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1UnknownN', '0'))
            
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1PassengerCarN', '128' if index==6 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1TruckN', '128' if index==5 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1UnknownN', '128' if index in [0, 1, 3, 4] else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1RoadsideBarrierN', '128' if index==2 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1UnknownN', '128' if index<2 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', str(64 if index!=1 else 0)))
    #         script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '@Classe_Obj_Sim::obj_data.obj_width[{0}] * 128'.format(str(obj_id))))
    #         script_list.append('        break;')
    #         script_list.append('    }' if index == len(obj_types)-1 else '')
    #     script_list.append('    break;')
    #     script_list.append('  }' if obj_id == num_objects-1 else '')
>>>>>>> origin/Develop_ADAS_HIL_Platform
    script_list.append('}')

    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

# update Road_Obj_CRadarFL_FDX
def update_CRadarFL_FDX(file_path, num_objects=9):
    """
    

    Args:
      file_path: 
      num_objects:  (Default value = 9)

    Returns:

    """
	# define object-independent script
    common_buffer = '@sysvar::XCP::RadarFC::_g_PER_Hil_ObjBypassingRunnable_ObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem'
    script_list = [Corner_header]

    script_list.append('void obj_sim_update_CRadarFL_fdx(byte object_id)')
    script_list.append('{\n  //header')
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# switch for differect objects
    # script_list.append('\n  switch (object_id)')
    # script_list.append('  {')
	# loop for generating multiple objects
    # obj_types = ['unknown','Pedestrian','2Wheeler::Cloe-> Bike','2Wheeler::Cloe-> Motorbike','PassengerCar','Truck','Non-Obstacle::Cloe->Trailer', 'RoadSideBarrier']
    # for obj_id in range(num_objects):
    #     object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_objectInformation', str(obj_id))
    #     script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
    #     script_list.append('    //constant')
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_Valid_b', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_HandleN', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_wExistProbN', '64880'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_isObjectAsil', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', '128'))

        # script_list.append('\n      //target movement\n')
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dxN', '@FDX_in_FRadar_0_m_dxN::FDX_in_FRadar_0_m_dxN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dyN', '@FDX_in_FRadar_0_m_dyN::FDX_in_FRadar_0_m_dyN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dzN', '@FDX_in_FRadar_0_m_dzN::FDX_in_FRadar_0_m_dzN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@FDX_in_FRadar_0_m_vxN::FDX_in_FRadar_0_m_vxN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@FDX_in_FRadar_0_m_vyN::FDX_in_FRadar_0_m_vyN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '@FDX_in_FRadar_0_m_axN::FDX_in_FRadar_0_m_axN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '@FDX_in_FRadar_0_m_ayN::FDX_in_FRadar_0_m_ayN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', '@FDX_in_FRadar_0_m_dLengthN::FDX_in_FRadar_0_m_dLengthN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '@FDX_in_FRadar_0_m_dWidthN::FDX_in_FRadar_0_m_dWidthN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '@FDX_in_FRadar_0_m_alpPiYawAngleN::FDX_in_FRadar_0_m_alpPiYawAngleN'))
        # script_list.append('\n      //target object moving or not')
        # script_list.append('      if (abs(@FDX_in_FRadar_0_m_vxN::FDX_in_FRadar_0_m_vxN) != 0)')
        # script_list.append('      {')
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '126'))
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '126'))
        # script_list.append('      }\n      else\n      {')
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '0'))
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '0'))

        # script_list.append('      }\n')
        # switch for object type

        # script_list.append('      //object classification')
        # script_list.append('    switch (@FDX_in_FRadar_Sensed_Object_0_Classification::FDX_in_FRadar_Sensed_Object_0_Classification)')
        # script_list.append('    {')
        # extend_object_buffer = '{0}::_m_perObjectType'.format(object_buffer)

        # for index in range(len(obj_types)):

        #     script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if (index!= 0 and index!=6) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index==6 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==0 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MobileN', '128' if (index!=0 and index !=7) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StationaryN', '128' if index==7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstUnknownN', '128' if index==0 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourPlusWheelerN', '128' if (index==4 or index==5) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TwoWheelerN', '128' if (index == 2 or index==3) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PedestrianN', '128' if index==1 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MovUnknownN', '128' if (index==0 or index == 6 or index == 7) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1RoadsideBarrierN', '128' if index==7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StatUnknownN', '128' if index!=7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PassengerCarN', '128' if index==4 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TruckN', '128' if index==5 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourWheelUnknownN', '128' if (index!=4 and index!=5) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '64' if (index==1 or index ==2 or index ==3) else '256')) 
            
        #     script_list.append('          break;')
        #     script_list.append('      }' if index == len(obj_types)-1 else '')
        # script_list.append('      break;')
        # script_list.append('  }' if obj_id == num_objects-1 else '')
    script_list.append('}')


    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

# update Road_Obj_FRadar XCP
def update_CRadarFR_XCP(file_path, num_objects=9):
    """
    

    Args:
      file_path: 
      num_objects:  (Default value = 9)

    Returns:

    """
	# define object-independent script
    common_buffer = '  @sysvar::XCP::RadarFR::_g_PlReCoFw_PlReCoPer_ObjBypassingRunnable_ObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem::port_ens_r_obj_sensor_base::_'
    script_list = [CornerFR_header]
    
    script_list.append('void obj_sim_update_CRadarFR_xcp(byte object_id)')
    script_list.append('{\n  //header')
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# switch for differect objects
    script_list.append('\n  switch (@Classe_Obj_Sim::obj_data.obj_id[object_id])')
    script_list.append('  {')
	# loop for generating multiple objects
    obj_types = ['Non-Obstacle', 'unknown', 'RoadSideBarrier', '2Wheeler', 'Pedestrian', 'Truck', 'PassengerCar']
    for obj_id in range(num_objects):
        object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_movObjectInformation', str(obj_id))
        script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
        script_list.append('    //constant')
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Meas_b', '1'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Measurable_b', '1'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Valid_b', '1'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxVxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyVyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyWidthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarVxAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDxN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_wExistProbN', '64880'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_referencePtPosIndexN', '10'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
        script_list.append('\n    //target movement\n')
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dxN', '@Classe_Obj_Sim::obj_data.obj_dx[{0}] * 128'.format(str(obj_id))))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dyN', '@Classe_Obj_Sim::obj_data.obj_dy[{0}] * 128'.format(str(obj_id))))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dzN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}] * 256'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@Classe_Obj_Sim::obj_data.obj_relative_vy[{0}] * 256'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '0'))
        script_list.append('\n    //target object moving or not')
        script_list.append('    if (abs(@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}]) != 0)'.format(str(obj_id)))
        script_list.append('    {')
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '126'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '126'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '128'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '0'))
        script_list.append('    }\n    else\n    {')
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '128'))
        script_list.append('    }\n')
        # switch for object type
        script_list.append('      //object classification')
        script_list.append('    switch (@Classe_Obj_Sim::obj_data.obj_type[{0}])'.format(str(obj_id)))
        script_list.append('    {')
        extend_object_buffer = '{0}::STA_OBJECT_INFORMATION_ST::_::_m_ohyObjectType_st'.format(object_buffer)
        for index in range(len(obj_types)):
            script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index<1 else 0))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if index>1 else 0))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==1 else 0))
            # different signal names for type 2
            name0 = "_m_prob1UnknownN" if index != 2 else "_m_prob1MobileN"
            name1 = "_m_probMobile_st::_m_prob1FourPlusWheelerN" if index != 2 else "_m_prob1StationaryN"
            name2 = "_m_probMobile_st::_m_prob1PedestrianN" if index != 2 else "_m_prob1UnknownN"
            name3 = "_m_prob1TwoWheelerN" if index != 2 else "_m_prob1FourPlusWheelerN"
            name4 = "_m_prob1UnknownN" if index != 2 else "_m_prob1PedestrianN"
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name0), '128' if index<2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name1), '128' if index==2 or index>4 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name2), '128' if index==4 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name3), '128' if index==3 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name4), '128' if index<2 else '0'))
            if index == 2:
                script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1TwoWheelerN', '0'))
                script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1UnknownN', '0'))
            
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1PassengerCarN', '128' if index==6 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1TruckN', '128' if index==5 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1UnknownN', '128' if index in [0, 1, 3, 4] else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1RoadsideBarrierN', '128' if index==2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1UnknownN', '128' if index<2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', str(64 if index!=1 else 0)))
            script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '@Classe_Obj_Sim::obj_data.obj_width[{0}] * 128'.format(str(obj_id))))
            script_list.append('        break;')
            script_list.append('    }' if index == len(obj_types)-1 else '')
        script_list.append('    break;')
        script_list.append('  }' if obj_id == num_objects-1 else '')
    script_list.append('}')

    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

# update Road_Obj_CRadarFR_FDX
def update_CRadarFR_FDX(file_path, num_objects=9):
    """
    

    Args:
      file_path: 
      num_objects:  (Default value = 9)

    Returns:

    """
	# define object-independent script
    common_buffer = '@sysvar::XCP::RadarFC::_g_PER_Hil_ObjBypassingRunnable_ObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem'
    script_list = [Corner_header]

    script_list.append('void obj_sim_update_CRadarFR_fdx(byte object_id)')
    script_list.append('{\n  //header')
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# switch for differect objects
    # script_list.append('\n  switch (object_id)')
    # script_list.append('  {')
	# loop for generating multiple objects
    # obj_types = ['unknown','Pedestrian','2Wheeler::Cloe-> Bike','2Wheeler::Cloe-> Motorbike','PassengerCar','Truck','Non-Obstacle::Cloe->Trailer', 'RoadSideBarrier']
    # for obj_id in range(num_objects):
    #     object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_objectInformation', str(obj_id))
    #     script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
    #     script_list.append('    //constant')
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_Valid_b', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_HandleN', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_wExistProbN', '64880'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_isObjectAsil', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', '128'))

        # script_list.append('\n      //target movement\n')
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dxN', '@FDX_in_FRadar_0_m_dxN::FDX_in_FRadar_0_m_dxN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dyN', '@FDX_in_FRadar_0_m_dyN::FDX_in_FRadar_0_m_dyN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dzN', '@FDX_in_FRadar_0_m_dzN::FDX_in_FRadar_0_m_dzN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@FDX_in_FRadar_0_m_vxN::FDX_in_FRadar_0_m_vxN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@FDX_in_FRadar_0_m_vyN::FDX_in_FRadar_0_m_vyN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '@FDX_in_FRadar_0_m_axN::FDX_in_FRadar_0_m_axN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '@FDX_in_FRadar_0_m_ayN::FDX_in_FRadar_0_m_ayN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', '@FDX_in_FRadar_0_m_dLengthN::FDX_in_FRadar_0_m_dLengthN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '@FDX_in_FRadar_0_m_dWidthN::FDX_in_FRadar_0_m_dWidthN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '@FDX_in_FRadar_0_m_alpPiYawAngleN::FDX_in_FRadar_0_m_alpPiYawAngleN'))
        # script_list.append('\n      //target object moving or not')
        # script_list.append('      if (abs(@FDX_in_FRadar_0_m_vxN::FDX_in_FRadar_0_m_vxN) != 0)')
        # script_list.append('      {')
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '126'))
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '126'))
        # script_list.append('      }\n      else\n      {')
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '0'))
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '0'))

        # script_list.append('      }\n')
        # switch for object type

        # script_list.append('      //object classification')
        # script_list.append('    switch (@FDX_in_FRadar_Sensed_Object_0_Classification::FDX_in_FRadar_Sensed_Object_0_Classification)')
        # script_list.append('    {')
        # extend_object_buffer = '{0}::_m_perObjectType'.format(object_buffer)

        # for index in range(len(obj_types)):

        #     script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if (index!= 0 and index!=6) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index==6 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==0 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MobileN', '128' if (index!=0 and index !=7) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StationaryN', '128' if index==7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstUnknownN', '128' if index==0 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourPlusWheelerN', '128' if (index==4 or index==5) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TwoWheelerN', '128' if (index == 2 or index==3) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PedestrianN', '128' if index==1 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MovUnknownN', '128' if (index==0 or index == 6 or index == 7) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1RoadsideBarrierN', '128' if index==7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StatUnknownN', '128' if index!=7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PassengerCarN', '128' if index==4 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TruckN', '128' if index==5 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourWheelUnknownN', '128' if (index!=4 and index!=5) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '64' if (index==1 or index ==2 or index ==3) else '256')) 
            
        #     script_list.append('          break;')
        #     script_list.append('      }' if index == len(obj_types)-1 else '')
        # script_list.append('      break;')
        # script_list.append('  }' if obj_id == num_objects-1 else '')
    script_list.append('}')


    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

# update Road_Obj_FRadar XCP
def update_CRadarRL_XCP(file_path, num_objects=9):
    """
    

    Args:
      file_path: 
      num_objects:  (Default value = 9)

    Returns:

    """
	# define object-independent script
    common_buffer = '  @sysvar::XCP::RadarRL::_g_PlReCoFw_PlReCoPer_ObjBypassingRunnable_ObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem::port_ens_r_obj_sensor_base::_'
    script_list = [CornerFR_header]
    
    script_list.append('void obj_sim_update_CRadarRL_xcp(byte object_id)')
    script_list.append('{\n  //header')
<<<<<<< HEAD
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# switch for differect objects
    script_list.append('\n  switch (@Classe_Obj_Sim::obj_data.obj_id[object_id])')
    script_list.append('  {')
	# loop for generating multiple objects
    obj_types = ['Non-Obstacle', 'unknown', 'RoadSideBarrier', '2Wheeler', 'Pedestrian', 'Truck', 'PassengerCar']
    for obj_id in range(num_objects):
        object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_movObjectInformation', str(obj_id))
        script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
        script_list.append('    //constant')
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Meas_b', '1'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Measurable_b', '1'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Valid_b', '1'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxVxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyVyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyWidthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarVxAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDxN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_wExistProbN', '64880'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_referencePtPosIndexN', '10'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
        script_list.append('\n    //target movement\n')
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dxN', '@Classe_Obj_Sim::obj_data.obj_dx[{0}] * 128'.format(str(obj_id))))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dyN', '@Classe_Obj_Sim::obj_data.obj_dy[{0}] * 128'.format(str(obj_id))))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dzN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}] * 256'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@Classe_Obj_Sim::obj_data.obj_relative_vy[{0}] * 256'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '0'))
        script_list.append('\n    //target object moving or not')
        script_list.append('    if (abs(@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}]) != 0)'.format(str(obj_id)))
        script_list.append('    {')
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '126'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '126'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '128'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '0'))
        script_list.append('    }\n    else\n    {')
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '128'))
        script_list.append('    }\n')
        # switch for object type
        script_list.append('      //object classification')
        script_list.append('    switch (@Classe_Obj_Sim::obj_data.obj_type[{0}])'.format(str(obj_id)))
        script_list.append('    {')
        extend_object_buffer = '{0}::STA_OBJECT_INFORMATION_ST::_::_m_ohyObjectType_st'.format(object_buffer)
        for index in range(len(obj_types)):
            script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index<1 else 0))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if index>1 else 0))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==1 else 0))
            # different signal names for type 2
            name0 = "_m_prob1UnknownN" if index != 2 else "_m_prob1MobileN"
            name1 = "_m_probMobile_st::_m_prob1FourPlusWheelerN" if index != 2 else "_m_prob1StationaryN"
            name2 = "_m_probMobile_st::_m_prob1PedestrianN" if index != 2 else "_m_prob1UnknownN"
            name3 = "_m_prob1TwoWheelerN" if index != 2 else "_m_prob1FourPlusWheelerN"
            name4 = "_m_prob1UnknownN" if index != 2 else "_m_prob1PedestrianN"
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name0), '128' if index<2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name1), '128' if index==2 or index>4 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name2), '128' if index==4 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name3), '128' if index==3 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name4), '128' if index<2 else '0'))
            if index == 2:
                script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1TwoWheelerN', '0'))
                script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1UnknownN', '0'))
            
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1PassengerCarN', '128' if index==6 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1TruckN', '128' if index==5 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1UnknownN', '128' if index in [0, 1, 3, 4] else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1RoadsideBarrierN', '128' if index==2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1UnknownN', '128' if index<2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', str(64 if index!=1 else 0)))
            script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '@Classe_Obj_Sim::obj_data.obj_width[{0}] * 128'.format(str(obj_id))))
            script_list.append('        break;')
            script_list.append('    }' if index == len(obj_types)-1 else '')
        script_list.append('    break;')
        script_list.append('  }' if obj_id == num_objects-1 else '')
=======
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# # switch for differect objects
    # script_list.append('\n  switch (@Classe_Obj_Sim::obj_data.obj_id[object_id])')
    # script_list.append('  {')
	# # loop for generating multiple objects
    # obj_types = ['Non-Obstacle', 'unknown', 'RoadSideBarrier', '2Wheeler', 'Pedestrian', 'Truck', 'PassengerCar']
    # for obj_id in range(num_objects):
    #     object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_movObjectInformation', str(obj_id))
    #     script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
    #     script_list.append('    //constant')
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Meas_b', '1'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Measurable_b', '1'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Valid_b', '1'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxAxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxVxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyVyN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyWidthN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarVxAxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDxN', '0'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDyN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_wExistProbN', '64880'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_referencePtPosIndexN', '10'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
    #     script_list.append('\n    //target movement\n')
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dxN', '@Classe_Obj_Sim::obj_data.obj_dx[{0}] * 128'.format(str(obj_id))))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dyN', '@Classe_Obj_Sim::obj_data.obj_dy[{0}] * 128'.format(str(obj_id))))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dzN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}] * 256'.format(str(obj_id))))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@Classe_Obj_Sim::obj_data.obj_relative_vy[{0}] * 256'.format(str(obj_id))))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '0'))
    #     script_list.append('\n    //target object moving or not')
    #     script_list.append('    if (abs(@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}]) != 0)'.format(str(obj_id)))
    #     script_list.append('    {')
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '126'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '126'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '128'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '0'))
    #     script_list.append('    }\n    else\n    {')
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '0'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '0'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '0'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '128'))
    #     script_list.append('    }\n')
    #     # switch for object type
    #     script_list.append('      //object classification')
    #     script_list.append('    switch (@Classe_Obj_Sim::obj_data.obj_type[{0}])'.format(str(obj_id)))
    #     script_list.append('    {')
    #     extend_object_buffer = '{0}::STA_OBJECT_INFORMATION_ST::_::_m_ohyObjectType_st'.format(object_buffer)
    #     for index in range(len(obj_types)):
    #         script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index<1 else 0))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if index>1 else 0))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==1 else 0))
    #         # different signal names for type 2
    #         name0 = "_m_prob1UnknownN" if index != 2 else "_m_prob1MobileN"
    #         name1 = "_m_probMobile_st::_m_prob1FourPlusWheelerN" if index != 2 else "_m_prob1StationaryN"
    #         name2 = "_m_probMobile_st::_m_prob1PedestrianN" if index != 2 else "_m_prob1UnknownN"
    #         name3 = "_m_prob1TwoWheelerN" if index != 2 else "_m_prob1FourPlusWheelerN"
    #         name4 = "_m_prob1UnknownN" if index != 2 else "_m_prob1PedestrianN"
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name0), '128' if index<2 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name1), '128' if index==2 or index>4 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name2), '128' if index==4 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name3), '128' if index==3 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name4), '128' if index<2 else '0'))
    #         if index == 2:
    #             script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1TwoWheelerN', '0'))
    #             script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1UnknownN', '0'))
            
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1PassengerCarN', '128' if index==6 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1TruckN', '128' if index==5 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1UnknownN', '128' if index in [0, 1, 3, 4] else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1RoadsideBarrierN', '128' if index==2 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1UnknownN', '128' if index<2 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', str(64 if index!=1 else 0)))
    #         script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '@Classe_Obj_Sim::obj_data.obj_width[{0}] * 128'.format(str(obj_id))))
    #         script_list.append('        break;')
    #         script_list.append('    }' if index == len(obj_types)-1 else '')
    #     script_list.append('    break;')
    #     script_list.append('  }' if obj_id == num_objects-1 else '')
>>>>>>> origin/Develop_ADAS_HIL_Platform
    script_list.append('}')

    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

# update Road_Obj_CRadarRL_FDX
def update_CRadarRL_FDX(file_path, num_objects=9):
    """
    

    Args:
      file_path: 
      num_objects:  (Default value = 9)

    Returns:

    """
	# define object-independent script
    common_buffer = '@sysvar::XCP::RadarFC::_g_PER_Hil_ObjBypassingRunnable_ObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem'
    script_list = [Corner_header]

    script_list.append('void obj_sim_update_CRadarRL_fdx(byte object_id)')
    script_list.append('{\n  //header')
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# switch for differect objects
    # script_list.append('\n  switch (object_id)')
    # script_list.append('  {')
	# loop for generating multiple objects
    # obj_types = ['unknown','Pedestrian','2Wheeler::Cloe-> Bike','2Wheeler::Cloe-> Motorbike','PassengerCar','Truck','Non-Obstacle::Cloe->Trailer', 'RoadSideBarrier']
    # for obj_id in range(num_objects):
    #     object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_objectInformation', str(obj_id))
    #     script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
    #     script_list.append('    //constant')
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_Valid_b', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_HandleN', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_wExistProbN', '64880'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_isObjectAsil', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', '128'))

        # script_list.append('\n      //target movement\n')
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dxN', '@FDX_in_FRadar_0_m_dxN::FDX_in_FRadar_0_m_dxN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dyN', '@FDX_in_FRadar_0_m_dyN::FDX_in_FRadar_0_m_dyN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dzN', '@FDX_in_FRadar_0_m_dzN::FDX_in_FRadar_0_m_dzN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@FDX_in_FRadar_0_m_vxN::FDX_in_FRadar_0_m_vxN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@FDX_in_FRadar_0_m_vyN::FDX_in_FRadar_0_m_vyN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '@FDX_in_FRadar_0_m_axN::FDX_in_FRadar_0_m_axN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '@FDX_in_FRadar_0_m_ayN::FDX_in_FRadar_0_m_ayN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', '@FDX_in_FRadar_0_m_dLengthN::FDX_in_FRadar_0_m_dLengthN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '@FDX_in_FRadar_0_m_dWidthN::FDX_in_FRadar_0_m_dWidthN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '@FDX_in_FRadar_0_m_alpPiYawAngleN::FDX_in_FRadar_0_m_alpPiYawAngleN'))
        # script_list.append('\n      //target object moving or not')
        # script_list.append('      if (abs(@FDX_in_FRadar_0_m_vxN::FDX_in_FRadar_0_m_vxN) != 0)')
        # script_list.append('      {')
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '126'))
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '126'))
        # script_list.append('      }\n      else\n      {')
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '0'))
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '0'))

        # script_list.append('      }\n')
        # switch for object type

        # script_list.append('      //object classification')
        # script_list.append('    switch (@FDX_in_FRadar_Sensed_Object_0_Classification::FDX_in_FRadar_Sensed_Object_0_Classification)')
        # script_list.append('    {')
        # extend_object_buffer = '{0}::_m_perObjectType'.format(object_buffer)

        # for index in range(len(obj_types)):

        #     script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if (index!= 0 and index!=6) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index==6 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==0 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MobileN', '128' if (index!=0 and index !=7) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StationaryN', '128' if index==7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstUnknownN', '128' if index==0 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourPlusWheelerN', '128' if (index==4 or index==5) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TwoWheelerN', '128' if (index == 2 or index==3) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PedestrianN', '128' if index==1 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MovUnknownN', '128' if (index==0 or index == 6 or index == 7) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1RoadsideBarrierN', '128' if index==7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StatUnknownN', '128' if index!=7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PassengerCarN', '128' if index==4 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TruckN', '128' if index==5 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourWheelUnknownN', '128' if (index!=4 and index!=5) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '64' if (index==1 or index ==2 or index ==3) else '256')) 
            
        #     script_list.append('          break;')
        #     script_list.append('      }' if index == len(obj_types)-1 else '')
        # script_list.append('      break;')
        # script_list.append('  }' if obj_id == num_objects-1 else '')
    script_list.append('}')


    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

# update Road_Obj_FRadar XCP
def update_CRadarRR_XCP(file_path, num_objects=9):
    """
    

    Args:
      file_path: 
      num_objects:  (Default value = 9)

    Returns:

    """
	# define object-independent script
    common_buffer = '  @sysvar::XCP::RadarRR::_g_PlReCoFw_PlReCoPer_ObjBypassingRunnable_ObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem::port_ens_r_obj_sensor_base::_'
    script_list = [CornerFR_header]
    
    script_list.append('void obj_sim_update_CRadarRR_xcp(byte object_id)')
    script_list.append('{\n  //header')
<<<<<<< HEAD
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# switch for differect objects
    script_list.append('\n  switch (@Classe_Obj_Sim::obj_data.obj_id[object_id])')
    script_list.append('  {')
	# loop for generating multiple objects
    obj_types = ['Non-Obstacle', 'unknown', 'RoadSideBarrier', '2Wheeler', 'Pedestrian', 'Truck', 'PassengerCar']
    for obj_id in range(num_objects):
        object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_movObjectInformation', str(obj_id))
        script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
        script_list.append('    //constant')
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Meas_b', '1'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Measurable_b', '1'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Valid_b', '1'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxVxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyVyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyWidthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarVxAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDxN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDyN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_wExistProbN', '64880'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_referencePtPosIndexN', '10'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
        script_list.append('\n    //target movement\n')
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dxN', '@Classe_Obj_Sim::obj_data.obj_dx[{0}] * 128'.format(str(obj_id))))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dyN', '@Classe_Obj_Sim::obj_data.obj_dy[{0}] * 128'.format(str(obj_id))))
        script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dzN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}] * 256'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@Classe_Obj_Sim::obj_data.obj_relative_vy[{0}] * 256'.format(str(obj_id))))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '0'))
        script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '0'))
        script_list.append('\n    //target object moving or not')
        script_list.append('    if (abs(@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}]) != 0)'.format(str(obj_id)))
        script_list.append('    {')
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '126'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '126'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '128'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '0'))
        script_list.append('    }\n    else\n    {')
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '0'))
        script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '128'))
        script_list.append('    }\n')
        # switch for object type
        script_list.append('      //object classification')
        script_list.append('    switch (@Classe_Obj_Sim::obj_data.obj_type[{0}])'.format(str(obj_id)))
        script_list.append('    {')
        extend_object_buffer = '{0}::STA_OBJECT_INFORMATION_ST::_::_m_ohyObjectType_st'.format(object_buffer)
        for index in range(len(obj_types)):
            script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index<1 else 0))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if index>1 else 0))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==1 else 0))
            # different signal names for type 2
            name0 = "_m_prob1UnknownN" if index != 2 else "_m_prob1MobileN"
            name1 = "_m_probMobile_st::_m_prob1FourPlusWheelerN" if index != 2 else "_m_prob1StationaryN"
            name2 = "_m_probMobile_st::_m_prob1PedestrianN" if index != 2 else "_m_prob1UnknownN"
            name3 = "_m_prob1TwoWheelerN" if index != 2 else "_m_prob1FourPlusWheelerN"
            name4 = "_m_prob1UnknownN" if index != 2 else "_m_prob1PedestrianN"
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name0), '128' if index<2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name1), '128' if index==2 or index>4 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name2), '128' if index==4 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name3), '128' if index==3 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name4), '128' if index<2 else '0'))
            if index == 2:
                script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1TwoWheelerN', '0'))
                script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1UnknownN', '0'))
            
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1PassengerCarN', '128' if index==6 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1TruckN', '128' if index==5 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1UnknownN', '128' if index in [0, 1, 3, 4] else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1RoadsideBarrierN', '128' if index==2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1UnknownN', '128' if index<2 else '0'))
            script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', str(64 if index!=1 else 0)))
            script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '@Classe_Obj_Sim::obj_data.obj_width[{0}] * 128'.format(str(obj_id))))
            script_list.append('        break;')
            script_list.append('    }' if index == len(obj_types)-1 else '')
        script_list.append('    break;')
        script_list.append('  }' if obj_id == num_objects-1 else '')
=======
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# # switch for differect objects
    # script_list.append('\n  switch (@Classe_Obj_Sim::obj_data.obj_id[object_id])')
    # script_list.append('  {')
	# # loop for generating multiple objects
    # obj_types = ['Non-Obstacle', 'unknown', 'RoadSideBarrier', '2Wheeler', 'Pedestrian', 'Truck', 'PassengerCar']
    # for obj_id in range(num_objects):
    #     object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_movObjectInformation', str(obj_id))
    #     script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
    #     script_list.append('    //constant')
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Meas_b', '1'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Measurable_b', '1'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_Valid_b', '1'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxAxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDxVxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyVyN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarDyWidthN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_covarVxAxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDxN', '0'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_varDyN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_wExistProbN', '64880'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_referencePtPosIndexN', '10'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
    #     script_list.append('\n    //target movement\n')
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dxN', '@Classe_Obj_Sim::obj_data.obj_dx[{0}] * 128'.format(str(obj_id))))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dyN', '@Classe_Obj_Sim::obj_data.obj_dy[{0}] * 128'.format(str(obj_id))))
    #     script_list.append('{0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_dzN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}] * 256'.format(str(obj_id))))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@Classe_Obj_Sim::obj_data.obj_relative_vy[{0}] * 256'.format(str(obj_id))))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '0'))
    #     script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '0'))
    #     script_list.append('\n    //target object moving or not')
    #     script_list.append('    if (abs(@Classe_Obj_Sim::obj_data.obj_relative_vx[{0}]) != 0)'.format(str(obj_id)))
    #     script_list.append('    {')
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '126'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '126'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '128'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '0'))
    #     script_list.append('    }\n    else\n    {')
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1HasBeenObservedMovingN', '0'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_prob1MovingN', '0'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1MobileN', '0'))
    #     script_list.append('  {0}::{1}::_::{2} = {3};'.format(object_buffer, 'STA_OBJECT_INFORMATION_ST', '_m_ohyObjectType_st::_m_probObstacle_st::_m_prob1StationaryN', '128'))
    #     script_list.append('    }\n')
    #     # switch for object type
    #     script_list.append('      //object classification')
    #     script_list.append('    switch (@Classe_Obj_Sim::obj_data.obj_type[{0}])'.format(str(obj_id)))
    #     script_list.append('    {')
    #     extend_object_buffer = '{0}::STA_OBJECT_INFORMATION_ST::_::_m_ohyObjectType_st'.format(object_buffer)
    #     for index in range(len(obj_types)):
    #         script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index<1 else 0))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if index>1 else 0))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==1 else 0))
    #         # different signal names for type 2
    #         name0 = "_m_prob1UnknownN" if index != 2 else "_m_prob1MobileN"
    #         name1 = "_m_probMobile_st::_m_prob1FourPlusWheelerN" if index != 2 else "_m_prob1StationaryN"
    #         name2 = "_m_probMobile_st::_m_prob1PedestrianN" if index != 2 else "_m_prob1UnknownN"
    #         name3 = "_m_prob1TwoWheelerN" if index != 2 else "_m_prob1FourPlusWheelerN"
    #         name4 = "_m_prob1UnknownN" if index != 2 else "_m_prob1PedestrianN"
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name0), '128' if index<2 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name1), '128' if index==2 or index>4 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::{0}'.format(name2), '128' if index==4 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name3), '128' if index==3 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::{0}'.format(name4), '128' if index<2 else '0'))
    #         if index == 2:
    #             script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1TwoWheelerN', '0'))
    #             script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_prob1UnknownN', '0'))
            
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1PassengerCarN', '128' if index==6 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1TruckN', '128' if index==5 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probMobile_st::_m_probFourPlusWheeler_st::_m_prob1UnknownN', '128' if index in [0, 1, 3, 4] else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1RoadsideBarrierN', '128' if index==2 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_probObstacle_st::_m_probStationary_st::_m_prob1UnknownN', '128' if index<2 else '0'))
    #         script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', str(64 if index!=1 else 0)))
    #         script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '@Classe_Obj_Sim::obj_data.obj_width[{0}] * 128'.format(str(obj_id))))
    #         script_list.append('        break;')
    #         script_list.append('    }' if index == len(obj_types)-1 else '')
    #     script_list.append('    break;')
    #     script_list.append('  }' if obj_id == num_objects-1 else '')
>>>>>>> origin/Develop_ADAS_HIL_Platform
    script_list.append('}')

    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')

# update Road_Obj_CRadarRR_FDX
def update_CRadarRR_FDX(file_path, num_objects=9):
    """
    

    Args:
      file_path: 
      num_objects:  (Default value = 9)

    Returns:

    """
	# define object-independent script
    common_buffer = '@sysvar::XCP::RadarFC::_g_PER_Hil_ObjBypassingRunnable_ObjBypassingRunnable_m_pad_radarObjPort_par_out_local::TChangeableMemPool::_::_::_m_arrayPool::_0_::_elem'
    script_list = [Corner_header]

    script_list.append('void obj_sim_update_CRadarRR_fdx(byte object_id)')
    script_list.append('{\n  //header')
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpAzimuthAngOffsetN', '-1146'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_alpMountAngleN', '0'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dLongitudinalOffsetRearAxisN', '455'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountElevationN', '20'))
    # script_list.append('{0}::{1}::{2} = {3};'.format(common_buffer, '_m_alignment', '_m_dMountOffsetN', '0'))
	# switch for differect objects
    # script_list.append('\n  switch (object_id)')
    # script_list.append('  {')
	# loop for generating multiple objects
    # obj_types = ['unknown','Pedestrian','2Wheeler::Cloe-> Bike','2Wheeler::Cloe-> Motorbike','PassengerCar','Truck','Non-Obstacle::Cloe->Trailer', 'RoadSideBarrier']
    # for obj_id in range(num_objects):
    #     object_buffer = "  {0}::{1}::_{2}_".format(common_buffer, '_m_objectInformation', str(obj_id))
    #     script_list.append('    case {0}: //"Object-{0}"'.format(obj_id))
    #     script_list.append('    //constant')
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_Valid_b', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_HandleN', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiVarYawAngleN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varAyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varVyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDxN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_varDyN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarLengthN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dVarWidthN', '0'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_wExistProbN', '64880'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_isObjectAsil', '1'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', '128'))

        # script_list.append('\n      //target movement\n')
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dxN', '@FDX_in_FRadar_0_m_dxN::FDX_in_FRadar_0_m_dxN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dyN', '@FDX_in_FRadar_0_m_dyN::FDX_in_FRadar_0_m_dyN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dzN', '@FDX_in_FRadar_0_m_dzN::FDX_in_FRadar_0_m_dzN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vxN', '@FDX_in_FRadar_0_m_vxN::FDX_in_FRadar_0_m_vxN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_vyN', '@FDX_in_FRadar_0_m_vyN::FDX_in_FRadar_0_m_vyN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_axN', '@FDX_in_FRadar_0_m_axN::FDX_in_FRadar_0_m_axN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_ayN', '@FDX_in_FRadar_0_m_ayN::FDX_in_FRadar_0_m_ayN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dLengthN', '@FDX_in_FRadar_0_m_dLengthN::FDX_in_FRadar_0_m_dLengthN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '@FDX_in_FRadar_0_m_dWidthN::FDX_in_FRadar_0_m_dWidthN'))
        # script_list.append('{0}::{1} = {2};'.format(object_buffer, '_m_alpPiYawAngleN', '@FDX_in_FRadar_0_m_alpPiYawAngleN::FDX_in_FRadar_0_m_alpPiYawAngleN'))
        # script_list.append('\n      //target object moving or not')
        # script_list.append('      if (abs(@FDX_in_FRadar_0_m_vxN::FDX_in_FRadar_0_m_vxN) != 0)')
        # script_list.append('      {')
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '126'))
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '126'))
        # script_list.append('      }\n      else\n      {')
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1HasBeenObservedMovingN', '0'))
        # script_list.append('  {0}::{1} = {2};'.format(object_buffer, '_m_prob1MovingN', '0'))

        # script_list.append('      }\n')
        # switch for object type

        # script_list.append('      //object classification')
        # script_list.append('    switch (@FDX_in_FRadar_Sensed_Object_0_Classification::FDX_in_FRadar_Sensed_Object_0_Classification)')
        # script_list.append('    {')
        # extend_object_buffer = '{0}::_m_perObjectType'.format(object_buffer)

        # for index in range(len(obj_types)):

        #     script_list.append('      case {0}: //"{1}"'.format(str(index), obj_types[index]))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstacleN', '128' if (index!= 0 and index!=6) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1NonObstacleN', '128' if index==6 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1UnknownN', '128' if index==0 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MobileN', '128' if (index!=0 and index !=7) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StationaryN', '128' if index==7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1ObstUnknownN', '128' if index==0 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourPlusWheelerN', '128' if (index==4 or index==5) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TwoWheelerN', '128' if (index == 2 or index==3) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PedestrianN', '128' if index==1 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1MovUnknownN', '128' if (index==0 or index == 6 or index == 7) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1RoadsideBarrierN', '128' if index==7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1StatUnknownN', '128' if index!=7 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1PassengerCarN', '128' if index==4 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1TruckN', '128' if index==5 else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(extend_object_buffer, '_m_prob1FourWheelUnknownN', '128' if (index!=4 and index!=5) else '0'))
            # script_list.append('    {0}::{1} = {2};'.format(object_buffer, '_m_dWidthN', '64' if (index==1 or index ==2 or index ==3) else '256')) 
            
        #     script_list.append('          break;')
        #     script_list.append('      }' if index == len(obj_types)-1 else '')
        # script_list.append('      break;')
        # script_list.append('  }' if obj_id == num_objects-1 else '')
    script_list.append('}')


    with open(file_path, 'w') as file:
        file.write('\n'.join(script_list))
        file.close()
    print(file_path + ' updated successfully.')



###### main creation of files ###########
update_FRadar_XCP(file_path='../../Nodes/RoadObjects/Road_Obj_FRadar_XCP.cin')
update_FRadar_FDX(file_path='../../Nodes/RoadObjects/Road_Obj_FRadar_FDX.cin')
update_CRadarFL_FDX(file_path='../../Nodes/RoadObjects/Road_Obj_CRadarFL_FDX.cin')
update_CRadarFL_XCP(file_path='../../Nodes/RoadObjects/Road_Obj_CRadarFL_XCP.cin')
update_CRadarFR_FDX(file_path='../../Nodes/RoadObjects/Road_Obj_CRadarFR_FDX.cin')
update_CRadarFR_XCP(file_path='../../Nodes/RoadObjects/Road_Obj_CRadarFR_XCP.cin')
update_CRadarRL_FDX(file_path='../../Nodes/RoadObjects/Road_Obj_CRadarRL_FDX.cin')
update_CRadarRL_XCP(file_path='../../Nodes/RoadObjects/Road_Obj_CRadarRL_XCP.cin')
update_CRadarRR_FDX(file_path='../../Nodes/RoadObjects/Road_Obj_CRadarRR_FDX.cin')
update_CRadarRR_XCP(file_path='../../Nodes/RoadObjects/Road_Obj_CRadarRR_XCP.cin')