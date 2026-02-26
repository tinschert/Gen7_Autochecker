/*!
********************************************************************************
@class CBoolVector
@ingroup framework
@brief Defines a vector class of type CBool

@author Robert Erhart, ett2si (30.09.2011)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- typedef of STL class valarray
********************************************************************************
*/
#ifndef CBoolVector_H
#define CBoolVector_H

#include "CBool.h"
#include <valarray>

using CBoolVector = ::std::valarray<CBool>;

#endif // CBoolVector_H
