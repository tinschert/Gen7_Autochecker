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

#include "DataHandling.hpp"
#include <iostream>

void DataHandler::copyBitsToByteArrayLE(uint64_t valueToCopy, uint8_t byteArray[], int64_t startBitIndex, int numBits)//Intel
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

double DataHandler::readBitsFromByteArrayLE(const uint8_t byteArray[], int64_t startBitIndex, int numBits, double Factor, double offset)
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

uint64_t DataHandler::convertPhysicalToRaw(double physicalValue, double Factor, double offset)
{
    return (uint64_t)((physicalValue - offset) / Factor);
}

double DataHandler::convertRawToPhysical(double rawValue, double Factor, double offset)
{
    return (double)(rawValue * Factor + offset);
}

void DataHandler::Write_ByteArray_RXX_Location(int64 locIndex, Radar *radar_ptr, int flip)
{
    // switch(locIndex + 1)
    // {
    // case 1:
    // DataHandler::RXX_Location_Loc1_write(locIndex, radar_ptr, flip);break;
    // }

    uint64_t raw_value;
    uint64_t location_data_length = 192;
    raw_value = DataHandler::convertPhysicalToRaw(radar_ptr->Loc[locIndex].o_radial_distance, 0.01, 0.0);
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1024, 16);

    raw_value = DataHandler::convertPhysicalToRaw(radar_ptr->Loc[locIndex].o_radial_velocity, 0.01, -150.0);
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1040, 15);

    raw_value = 119;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1056, 11);

    raw_value = 0;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1067, 10);

    raw_value = 489;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1077, 10);

    raw_value = 30;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1088, 9);

    raw_value = 100;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1097, 7);

    raw_value = 0;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1104, 14);

    raw_value = DataHandler::convertPhysicalToRaw(flip*radar_ptr->Loc[locIndex].o_azimuth, 0.00175, -1.792);
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1120, 11);

    raw_value = DataHandler::convertPhysicalToRaw(radar_ptr->Loc[locIndex].o_snr, 0.2, 0.0);
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1131, 10);

    raw_value = DataHandler::convertPhysicalToRaw(flip*radar_ptr->Loc[locIndex].o_elevation, 0.00175, -0.448);
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1141, 9);

    raw_value = 100;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1152, 7);

    raw_value = 100;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1159, 7);

    raw_value = 100;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1166, 7);

    raw_value = 0;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1173, 10);

    raw_value = DataHandler::convertPhysicalToRaw(radar_ptr->Loc[locIndex].o_radar_cross_section, 0.5, -50.0);
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1184, 8);

    raw_value = 1;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1192, 8);

    raw_value = 1;
    DataHandler::copyBitsToByteArrayLE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1200, 7);

}

double DataHandler::Read_ByteArray_Location_Distance(const uint8_t byte_array[], int loc_index)
{
    uint64_t location_data_length = 192;
    
    return DataHandler::readBitsFromByteArrayLE(byte_array, loc_index * location_data_length + 1024, 16, 0.01, 0.0);
}

double DataHandler::Read_ByteArray_Location_Velocity(const uint8_t byte_array[], int loc_index)
{
    uint64_t location_data_length = 192;
    
    return DataHandler::readBitsFromByteArrayLE(byte_array, loc_index * location_data_length + 1040, 15, 0.01, -150.0);
}

double DataHandler::Read_ByteArray_Location_Azimuth(const uint8_t byte_array[], int loc_index)
{
    uint64_t location_data_length = 192;
    
    return DataHandler::readBitsFromByteArrayLE(byte_array, loc_index * location_data_length + 1120, 11, 0.00175, -1.792);
}

double DataHandler::Read_ByteArray_Location_RCS(const uint8_t byte_array[], int loc_index)
{
    uint64_t location_data_length = 192;
    
    return DataHandler::readBitsFromByteArrayLE(byte_array, loc_index * location_data_length + 1184, 11, 0.5, -50.0);
}

double DataHandler::Read_ByteArray_Mounting_Position_X(const uint8_t byte_array[])
{
    uint64_t location_data_length = 192;
    
    return DataHandler::readBitsFromByteArrayLE(byte_array, 937, 9, 0.02, -5.12);
}

double DataHandler::Read_ByteArray_Mounting_Position_Y(const uint8_t byte_array[])
{
    uint64_t location_data_length = 192;
    
    return DataHandler::readBitsFromByteArrayLE(byte_array, 946, 8, 0.01, -1.28);
}

double DataHandler::Read_ByteArray_Mounting_Position_Z(const uint8_t byte_array[])
{
    uint64_t location_data_length = 192;
    
    return DataHandler::readBitsFromByteArrayLE(byte_array, 954, 5, 0.05, 0.0);
}

double DataHandler::Read_ByteArray_Mounting_Position_Yaw(const uint8_t byte_array[])
{
    uint64_t location_data_length = 192;
    
    return DataHandler::readBitsFromByteArrayLE(byte_array, 416, 16, 0.00017, -5.57056);
}

double DataHandler::Read_ByteArray_Num_Valid_Loc(const uint8_t byte_array[])
{
    uint64_t location_data_length = 192;
    
    return DataHandler::readBitsFromByteArrayLE(byte_array, 72, 10, 1.0, 0.0);
}