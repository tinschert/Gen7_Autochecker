//============================================================================================================
// C O P Y R I G H T
//------------------------------------------------------------------------------------------------------------
/// \copyright (C) 2021 Robert Bosch GmbH.
//
// The reproduction, distribution and utilization of this file as
// well as the communication of its contents to others without express
// authorization is prohibited. Offenders will be held liable for the
// payment of damages. All rights reserved in the event of the grant
// of a patent, utility model or design.
//============================================================================================================

#include "RA6SGU_DataHandling.hpp"
#include <iostream>

void RA6SGU_DataHandler::copyBitsToByteArrayLE(uint64_t valueToCopy, uint8_t byteArray[], int64_t startBitIndex, int numBits)//Intel
{
  int i;
  int byteIndex;
  int bitIndex;
  int byteCnt;

  byteIndex = (int)startBitIndex / 8;
  bitIndex = (int)startBitIndex % 8;
  byteCnt = (bitIndex + numBits + 7) / 8;

  valueToCopy &= (((uint64_t)1<<numBits)-1); // limit value to numBits

  for (i = 0; i < byteCnt; ++i)
  {
    if(i==0)
      byteArray[byteIndex + i] |= (uint8_t)(valueToCopy << bitIndex);
    else
      byteArray[byteIndex + i] |= (uint8_t)(valueToCopy >> (i*8 - bitIndex));
  }
}

double RA6SGU_DataHandler::readBitsFromByteArrayLE(const uint8_t byteArray[], int64_t startBitIndex, int numBits, double Factor, double offset)
{
  int i;
  int byteIndex;
  int bitIndex;
  int byteCnt;
  uint64_t result = 0;
  double physical_value = 0.0;

  byteIndex = (int)startBitIndex / 8;
  bitIndex = (int)startBitIndex % 8;
  byteCnt = (bitIndex + numBits + 7) / 8;

  for (i = 0; i < byteCnt; ++i)
  {
    if(i==0)
      result |= (uint64_t)(byteArray[byteIndex + i] >> bitIndex);
    else
      result |= (uint64_t)(byteArray[byteIndex + i] << (i*8 - bitIndex));
  }

  result &= ((1<<numBits)-1); // limit result to numBits

  physical_value = result * Factor + offset;

  return physical_value;
}

uint64_t RA6SGU_DataHandler::convertPhysicalToRaw(double physicalValue, double Factor, double offset)
{
    return (uint64_t)((physicalValue - offset) / Factor);
}

double RA6SGU_DataHandler::convertRawToPhysical(double rawValue, double Factor, double offset)
{
    return (double)(rawValue * Factor + offset);
}

void RA6SGU_DataHandler::Write_ByteArray_RXX_Object(int64 obj_index, Radar *radar_ptr)
{
    uint64_t raw_value;
    uint64_t object_data_length = 512;
    raw_value = convertPhysicalToRaw(radar_ptr->Obj[obj_index].o_acceleration_y, 0.0625, -16.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.Ay
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1206, 9);

    raw_value = convertPhysicalToRaw(0, 0.005, 0.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.WidthVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1184, 12);

    raw_value = convertPhysicalToRaw(radar_ptr->Obj[obj_index].o_ra6_radar_cross_section, 0.2, -102.4);   // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.RCS
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1196, 10);

    raw_value = convertPhysicalToRaw(0, 0.005, 0.0); // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.VxVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1248, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, 0.0); // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.AyVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1216, 12);

    raw_value = convertPhysicalToRaw(radar_ptr->Obj[obj_index].o_velocity_x, 0.0625, -128.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.Vx
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1228, 12);

    raw_value = convertPhysicalToRaw(obj_index+1.0, 1.0, 0.0);   // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.ObjId
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1240, 7);

    raw_value = convertPhysicalToRaw(0, 0.0003, 0.0);   // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.OrientationYawVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1164, 12);

    raw_value = convertPhysicalToRaw(radar_ptr->get_in_obj_width((int) obj_index), 0.125, 0.0); // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.Width
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1176, 7);

    raw_value = convertPhysicalToRaw(0, 0.005, 0.0);    // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.LengthVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1120, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, 0.0);    // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.AxVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1152, 12);

    raw_value = convertPhysicalToRaw(radar_ptr->Obj[obj_index].o_yaw_angle, 0.0175, -4.48);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.OrientationYaw
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1142, 9);

    raw_value = convertPhysicalToRaw(radar_ptr->Obj[obj_index].o_acceleration_x, 0.03125, -16.0);   // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.Ax
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1132, 10);

    raw_value = convertPhysicalToRaw(radar_ptr->Obj[obj_index].o_velocity_y, 0.125, -64.0); // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.Vy
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1262, 10);

    raw_value = convertPhysicalToRaw(radar_ptr->get_in_obj_length((int) obj_index), 0.125, 0.0); // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.Length
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1112, 7);

    raw_value = convertPhysicalToRaw(0, 0.005, 0.0);    // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.PyVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1100, 12);

    raw_value = convertPhysicalToRaw(radar_ptr->Obj[obj_index].o_distance_y, 0.0625, -128.0); // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.Py
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1088, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, 0.0);    // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.PxVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1076, 12);

    raw_value = convertPhysicalToRaw(radar_ptr->Obj[obj_index].o_distance_x, 0.0625, -512.0);   // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.Px
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1062, 14);

    raw_value = convertPhysicalToRaw(100, 2.0, 0.0);   // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.ProbClassConfidence
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1056, 6);

    raw_value = convertPhysicalToRaw(radar_ptr->Obj[obj_index].o_ra6_moving_status, 1.0, 0.0);   // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.MovingStatus
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1260, 2);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.PxPyCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1292, 12);

    raw_value = convertPhysicalToRaw(100, 2.0, 0.0);    // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.ExistProb
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1272, 6);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.PyAxCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1408, 12);

    raw_value = convertPhysicalToRaw(0, 1.0, 0.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.Age !!! TODO: Implement a way to track the age of an object
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1536, 32);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.AxAyCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1516, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.VyAyCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1504, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.VyAxCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1484, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.VxAyCoVnce 
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1472, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.VxAxCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1452, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.VxVyCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1440, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, 0.0);    // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.VyVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1280, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.PyAyCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1420, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.PxAyCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1388, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.PxAxCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1376, 12);

    raw_value = convertPhysicalToRaw(radar_ptr->Obj[obj_index].o_reference_point, 1.0, 0.0);    // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.ReferencePoint
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1368, 4);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.PyVyCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1356, 12);

    raw_value = convertPhysicalToRaw(0, 1.0, 0.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.FilterInformation
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1336, 8);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.PxVyCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1324, 12);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.PxVxCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1312, 12);

    raw_value = convertPhysicalToRaw(radar_ptr->Obj[obj_index].o_ra6_obj_type, 1.0, 0.0);   // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.ProbClassType
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1307, 4);

    raw_value = convertPhysicalToRaw(0, 1.0, 0.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.MeasurementStatus
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1304, 3);

    raw_value = convertPhysicalToRaw(0, 0.005, -10.0);  // @CAN_RadarFR::RFR_Object::RFR_Object_ObjX.PyVxCoVnce
    RA6SGU_DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_obj, obj_index * object_data_length + 1344, 12);
}


double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_Distance_X(const uint8_t byte_array[], int obj_index)
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, obj_index * object_data_length + 1062, 14, 0.0625, -512.0);
}
double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_Distance_Y(const uint8_t byte_array[], int obj_index)
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, obj_index * object_data_length + 1088, 12, 0.0625, -128.0);
}
double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_Velocity_X(const uint8_t byte_array[], int obj_index)
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, obj_index * object_data_length + 1228, 12, 0.0625, -128.0);
}
double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_Velocity_Y(const uint8_t byte_array[], int obj_index)
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, obj_index * object_data_length + 1262, 10, 0.125, -64.0);
}
double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_Yaw_Angle(const uint8_t byte_array[], int obj_index)
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, obj_index * object_data_length + 1142, 9, 0.0175, -4.48);
}
double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_RCS(const uint8_t byte_array[], int obj_index)
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, obj_index * object_data_length + 1196, 10, 0.2, -102.4);
}
double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_Reference_Point(const uint8_t byte_array[], int obj_index)
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, obj_index * object_data_length + 1368, 4, 1.0, 0.0);
}
double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_Mounting_Position_X(const uint8_t byte_array[])
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, 937, 9, 0.02, -5.12);
}
double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_Mounting_Position_Y(const uint8_t byte_array[])
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, 946, 8, 0.01, -1.28);
}
double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_Mounting_Position_Z(const uint8_t byte_array[])
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, 954, 5, 0.05, 0.0);
}
double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_Mounting_Position_Yaw(const uint8_t byte_array[])
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, 416, 16, 0.00017, -5.57056);
}
double RA6SGU_DataHandler::Read_ByteArray_RA6SGU_Num_Valid_Obj(const uint8_t byte_array[])
{
    uint64_t object_data_length = 512;
    
    return RA6SGU_DataHandler::readBitsFromByteArrayLE(byte_array, 72, 10, 1.0, 0.0);
}