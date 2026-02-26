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

#ifndef CONTI_DATA_HANDLING_HPP
#define CONTI_DATA_HANDLING_HPP

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

class ContiDataHandler {
    public:
    ContiDataHandler() {
    }

    void ContiCopyBitsToByteArrayBE(uint64_t,uint8_t[],int64,int);
    double ContiReadBitsFromByteArrayBE(const uint8_t[],int64_t,int,double,double);
    uint64_t ContiConvertPhysicalToRaw(double,double,double);
    double ContiConvertRawToPhysical(double,double,double);
    void Write_ByteArray_Conti_Location(int64,Radar*,int);
};

#endif
// EOF