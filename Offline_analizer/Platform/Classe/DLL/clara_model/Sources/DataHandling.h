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

#ifndef DATA_HANDLING_H
#define DATA_HANDLING_H

/// standard includes
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <map>
#include "../../Includes/cdll.h"
#include "../../Includes/VIA.h"
#include "../../Includes/VIA_CDLL.h"

/**
 * @brief TODO
*/

void copyBitsToByteArrayBE(uint64_t valueTocopy, byte byteArray[], int64 startBitIndex, int numBits)//Motorola
{

    int i;
    int byteIndex;
    int bitIndex;
    byte bitValue;
  
    for (i = 0; i < numBits; i++)
    {
        byteIndex = (int)startBitIndex / 8;
        bitIndex = (int)startBitIndex % 8;
  
        bitValue = (byte) (valueTocopy >> i) & 1;

        byteArray[byteIndex] |= (byte)(bitValue << bitIndex);
  
        if (bitIndex == 7)
        {
            startBitIndex -= 15;
        }
        else
        {
            startBitIndex++;
        }
    }
}

void copyBitsToByteArrayLE(uint64_t valueToCopy, byte byteArray[], int64 startBitIndex, int numBits)//Intel
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
      byteArray[byteIndex + i] |= (byte)(valueToCopy << bitIndex);
    else
      byteArray[byteIndex + i] |= (byte)(valueToCopy >> (i*8 - bitIndex));
  }
}



uint64_t convertPhysicalToRaw(double physicalValue, double Factor, double offset)
{
    return (uint64_t)((physicalValue - offset) / Factor);
}

uint64_t copyBitsFromByteArrayLE( byte byteArray[], int64 startBitIndex, int64 numBits)
{
  uint64_t result;
  byte temp;
  int64 byteIndex,bitIndex;
  int64 endBitIndex;
  int64 i;//For looping

  result = 0;
  endBitIndex = startBitIndex + numBits - 1;
  for (i = startBitIndex; i <= endBitIndex; i++) 
  {
    byteIndex = i / 8;
    bitIndex = i % 8;
    temp = (byteArray[byteIndex] >> bitIndex) & 0x01;
    result |= temp << (i - startBitIndex);
  }
  return result;
}

uint64_t copyBitsFromByteArrayBE(byte byteArray[], int64 startBitIndex, int64 numBits)
{
  uint64_t result;
  byte temp;
  int64 byteIndex, bitIndex;
  int64 endBitIndex;
  int64 i; // For looping

  result = 0;
  endBitIndex = startBitIndex + numBits - 1;
  for (i = endBitIndex; i >= startBitIndex; i--)
  {
    byteIndex = i / 8;
    bitIndex = 7 - (i % 8); // Reverse the bit order for big-endian
    temp = (byteArray[byteIndex] >> bitIndex) & 0x01;
    result |= temp << (endBitIndex - i);
  }
  return result;
}

void Write_ByteArray_RXX_Location(int64 locationPosInStruct, byte byteArray[], int64 locIndex, CaplInstanceData *instance)
{
    // switch(locationPosInStruct)
    // {
    // case 1:
    // RXX_Location_Loc1_write(byteArray, locIndex, instance);break;
    // }

    uint64_t raw_value;
    uint64_t location_data_length = 192;
    raw_value = convertPhysicalToRaw(std::sqrt(std::pow(instance->radar_model_.o_xRadarLocation.get()[locIndex],2)+std::pow(instance->radar_model_.o_yRadarLocation.get()[locIndex],2)+std::pow(instance->radar_model_.o_zRadarLocation.get()[locIndex],2)), 0.01, 0.0);
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1024, 16);

    raw_value = convertPhysicalToRaw(instance->radar_model_.o_vRadialRadarLocation.get()[locIndex], 0.01, -150.0);
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1040, 15);

    raw_value = 119;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1056, 11);

    raw_value = 0;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1067, 10);

    raw_value = 489;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1077, 10);

    raw_value = 30;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1088, 9);

    raw_value = 100;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1097, 7);

    raw_value = 0;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1104, 14);

    raw_value = convertPhysicalToRaw(instance->CoeffFlipRadar*instance->radar_model_.o_alphaRadarLocation.get()[locIndex], 0.00175, -1.792);
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1120, 11);

    raw_value = 500;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1131, 10);

    raw_value = convertPhysicalToRaw(instance->CoeffFlipRadar*instance->radar_model_.o_elevationAngleLocation.get()[locIndex], 0.00175, -0.448);
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1141, 9);

    raw_value = 100;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1152, 7);

    raw_value = 100;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1159, 7);

    raw_value = 100;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1166, 7);

    raw_value = 0;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1173, 10);

    raw_value = convertPhysicalToRaw(instance->radar_model_.o_rcsCenterLocation.get()[locIndex], 0.5, -50.0);
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1184, 8);

    raw_value = 1;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1192, 8);

    raw_value = 1;
    copyBitsToByteArrayLE(raw_value, byteArray, (locationPosInStruct-1) * location_data_length + 1200, 7);
    
}

#endif
// EOF