/*!
********************************************************************************
@class CIntVector
@ingroup framework
@brief Defines a vector class of type CInt

@author Robert Erhart, ett2si (18.10.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- typedef of STL class valarray
********************************************************************************

********************************************************************************
*/
#ifndef CINTVECTOR_H
#define CINTVECTOR_H

#include "CInt.h"
#include <valarray>

using CIntVector = ::std::valarray<CInt>;

#endif // CINTVECTOR_H
