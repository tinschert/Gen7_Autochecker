/*
 * FILE:            UdpClient.h
 * SW-COMPONENT:    UdpClient.h
 * DESCRIPTION:     Method declarations for a UdpClient for transmitting object data
 * COPYRIGHT:       © 2024 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#ifndef UDP_CLIENT_H_
#define UDP_CLIENT_H_

#include <UdpPacket.h>

#include "common/objectData.h"


/// @brief Sends to Radar Data to the CANoe instance via UDP
/// @param radarData A reference to the radar data to be send via UDP
/// @param ipAddress The IP address of the CANoe UDP Server [Typically the RTRack]
/// @param port The port on the UDP Server to send the data to [Typically 25565]
/// @return A boolean true for a successful transmission or false for a failure
bool sendRadarDataUDP(tRbRadarData& radarData, const std::string& ipAddress, int port);


#endif // UDP_CLIENT_H_