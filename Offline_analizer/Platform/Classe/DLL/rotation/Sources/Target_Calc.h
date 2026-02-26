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

#ifndef RADAR_SENSORMODEL_H
#define RADAR_SENSORMODEL_H

/// standard includes
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

/**
 * @brief TODO
*/
struct CoordinateSystem
{
  /// @brief T0DO
  double dx, dy, dz;
  double vx, vy;
  double heading;
};

#endif
// EOF