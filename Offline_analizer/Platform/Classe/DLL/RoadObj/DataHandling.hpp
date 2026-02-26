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

#ifndef DATA_HANDLING_HPP
#define DATA_HANDLING_HPP

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
#include "../Includes/cdll.h"
#include "../Includes/VIA.h"
#include "../Includes/VIA_CDLL.h"
#include "Radar.hpp"

class DataHandler {
    public:
    DataHandler() {
    }

    void copyBitsToByteArrayLE(uint64_t,uint8_t[],int64,int);
    double readBitsFromByteArrayLE(const uint8_t[],int64_t,int,double,double);
    uint64_t convertPhysicalToRaw(double,double,double);
    double convertRawToPhysical(double,double,double);
    void Write_ByteArray_RXX_Location(int64,Radar*,int);


    double Read_ByteArray_Location_Distance(const uint8_t[],int);
    double Read_ByteArray_Location_Velocity(const uint8_t[],int);
    double Read_ByteArray_Location_Azimuth(const uint8_t[],int);
    double Read_ByteArray_Location_RCS(const uint8_t[],int);
    double Read_ByteArray_Mounting_Position_X(const uint8_t[]);
    double Read_ByteArray_Mounting_Position_Y(const uint8_t[]);
    double Read_ByteArray_Mounting_Position_Z(const uint8_t[]);
    double Read_ByteArray_Mounting_Position_Yaw(const uint8_t[]);
    double Read_ByteArray_Num_Valid_Loc(const uint8_t[]);
};

#endif
// EOF