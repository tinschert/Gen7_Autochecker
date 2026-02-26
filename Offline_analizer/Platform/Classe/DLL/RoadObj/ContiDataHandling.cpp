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

#include "ContiDataHandling.hpp"
#include <iostream>

// void ContiDataHandler::ContiCopyBitsToByteArrayBE(uint64_t valueToCopy, uint8_t byteArray[], int64_t startBitIndex, int numBits)//Motorola
// {

//     int i;
//     int byteIndex;
//     int bitIndex;
//     byte bitValue;
  
//     for (i = 0; i < numBits; i++)
//     {
//         byteIndex = (int)startBitIndex / 8;
//         bitIndex = (int)startBitIndex % 8;
  
//         bitValue = (byte) (valueToCopy >> i) & 1;

//         byteArray[byteIndex] |= (byte)(bitValue << bitIndex);
  
//         if (bitIndex == 7)
//         {
//             startBitIndex -= 15;
//         }
//         else
//         {
//             startBitIndex++;
//         }
//     }
// }

void ContiDataHandler::ContiCopyBitsToByteArrayBE(uint64_t valueToCopy, uint8_t byteArray[], int64_t startBitIndex, int numBits)//Motorola
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
    int shift = (byteCnt - 1 - i) * 8 - bitIndex; // Calculate shift for big-endian
    // if(i==0)
    //   byteArray[byteIndex + i] |= (uint8_t)(valueToCopy << bitIndex);
    // else
    //   byteArray[byteIndex + i] |= (uint8_t)(valueToCopy >> (i*8 - bitIndex));
    if (shift >= 0)
    {
        byteArray[byteIndex + i] |= (uint8_t)(valueToCopy >> shift);
    }
    else
    {
        byteArray[byteIndex + i] |= (uint8_t)(valueToCopy << -shift);
    }
  }
}

double ContiDataHandler::ContiReadBitsFromByteArrayBE(const uint8_t byteArray[], int64_t startBitIndex, int numBits, double Factor, double offset)
{
  double physical_value = 0.0;
  uint64_t result = 0;
    
  for (int i = 0; i < numBits; i++)
  {
    int byteIndex = (int)startBitIndex / 8;
    int bitIndex = (int)startBitIndex % 8;
    
    byte bitValue = (byteArray[byteIndex] >> bitIndex) & 1;
    
    result |= (uint64_t)(bitValue << i);
    
    if (bitIndex == 7)
    {
        startBitIndex -= 15;
    }
    else
    {
        startBitIndex++;
    }
  }

  physical_value = result * Factor + offset;

  return physical_value;
}

uint64_t ContiDataHandler::ContiConvertPhysicalToRaw(double physicalValue, double Factor, double offset)
{
    return (uint64_t)((physicalValue - offset) / Factor);
}

double ContiDataHandler::ContiConvertRawToPhysical(double rawValue, double Factor, double offset)
{
    return (double)(rawValue * Factor + offset);
}

void ContiDataHandler::Write_ByteArray_Conti_Location(int64 locIndex, Radar *radar_ptr, int flip)
{
    // switch(locIndex)
    // {
    // case 0:
    // ContiDataHandler::Conti_Location_Loc0_write(locIndex, radar_ptr, flip);break;
    // }

    uint64_t raw_value;
    uint64_t location_data_length = 544;

    union FloatUnion {
        float f_val;
        uint32_t u_bits;
    };

    union FloatUnion FloatToBits;

    FloatToBits.f_val = (float)radar_ptr->Loc[locIndex].o_radial_distance;
    ContiDataHandler::ContiCopyBitsToByteArrayBE(FloatToBits.u_bits, radar_ptr->byte_array_loc, locIndex * location_data_length + 704, 32);

    FloatToBits.f_val = (float)radar_ptr->Loc[locIndex].o_radial_velocity;
    ContiDataHandler::ContiCopyBitsToByteArrayBE(FloatToBits.u_bits, radar_ptr->byte_array_loc, locIndex * location_data_length + 736, 32);

    FloatToBits.f_val = flip*((float)radar_ptr->Loc[locIndex].o_azimuth);
    ContiDataHandler::ContiCopyBitsToByteArrayBE(FloatToBits.u_bits, radar_ptr->byte_array_loc, locIndex * location_data_length + 768, 32);

    FloatToBits.f_val = flip*((float)radar_ptr->Loc[locIndex].o_elevation);
    ContiDataHandler::ContiCopyBitsToByteArrayBE(FloatToBits.u_bits, radar_ptr->byte_array_loc, locIndex * location_data_length + 800, 32);

    FloatToBits.f_val = (float)radar_ptr->Loc[locIndex].o_radar_cross_section;
    ContiDataHandler::ContiCopyBitsToByteArrayBE(FloatToBits.u_bits, radar_ptr->byte_array_loc, locIndex * location_data_length + 832, 32);

    FloatToBits.f_val = (float)radar_ptr->Loc[locIndex].o_snr;
    ContiDataHandler::ContiCopyBitsToByteArrayBE(FloatToBits.u_bits, radar_ptr->byte_array_loc, locIndex * location_data_length + 864, 32);

    raw_value = 0;//peakDetectionThreshold
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 896, 8);

    raw_value = 0;//existanceProbability
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 904, 8);

    raw_value = 0;//multiTargetProb
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 912, 8);

    raw_value = 0;//receivedSignalStrength
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 920, 8);

    FloatToBits.f_val = 0.0f;//radialVelocityVariance
    ContiDataHandler::ContiCopyBitsToByteArrayBE(FloatToBits.u_bits, radar_ptr->byte_array_loc, locIndex * location_data_length + 928, 32);

    raw_value = 0;//measurementModel
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 960, 8);

    FloatToBits.f_val = 0.0f;//azimuthAngleVariance
    ContiDataHandler::ContiCopyBitsToByteArrayBE(FloatToBits.u_bits, radar_ptr->byte_array_loc, locIndex * location_data_length + 968, 32);

    FloatToBits.f_val = 0.0f;//elevationAngleVariance
    ContiDataHandler::ContiCopyBitsToByteArrayBE(FloatToBits.u_bits, radar_ptr->byte_array_loc, locIndex * location_data_length + 1000, 32);

    FloatToBits.f_val = 0.0f;//rangeVariance
    ContiDataHandler::ContiCopyBitsToByteArrayBE(FloatToBits.u_bits, radar_ptr->byte_array_loc, locIndex * location_data_length + 1032, 32);

    raw_value = 0;//azimuthQuality
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1064, 8);

    raw_value = 0;//elevationQuality
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1072, 8);

    raw_value = 0;//dopplerAmbiguityFlag
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1080, 8);

    raw_value = 0;//radarSignalProcessingClusterID
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1088, 16);

    raw_value = 0;//ambiguityProbability
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1104, 8);

    raw_value = 0;//azimuthModelError
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1112, 16);

    raw_value = 0;//nacomArtifact
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1128, 8);

    raw_value = 0;//dopplerSpectrumArtifact
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1136, 8);

    raw_value = 0;//interferenceArtifact
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1144, 8);

    raw_value = 0;//sidelobeArtifact
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1152, 8);

    raw_value = 0;//elevationBeamFormModelError
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1160, 8);

    raw_value = 0;//detectionInvalid
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1168, 8);

    raw_value = 0;//rangeExtrapolated
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1176, 32);

    raw_value = 0;//heightAvgerageMultiCycle
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1208, 16);

    raw_value = 0;//qualityHeightAverage
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1224, 16);

    raw_value = 0;//RadialVelocityAmbiguityID
    ContiDataHandler::ContiCopyBitsToByteArrayBE(raw_value, radar_ptr->byte_array_loc, locIndex * location_data_length + 1240, 8);

}    