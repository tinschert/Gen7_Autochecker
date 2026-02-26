/*
 * FILE:            UdpClient.cpp
 * SW-COMPONENT:    UdpClient.cpp
 * DESCRIPTION:     Method definitions for a UdpClient for transmitting object data
 * COPYRIGHT:       © 2024 Robert Bosch GmbH
 *
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#include "UdpClient.h"

#include <Config.h>
#include <RBSData.h>
#include <UdpPacket.h>

#include <algorithm>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <vector>
#include <string>
#include <iostream>

// Link with ws2_32.lib
#pragma comment(lib, "ws2_32.lib")

/// @brief Maps the CarMaker object to the CANoe data format
/// @param canoe A reference to the CANoe data structure to map to
/// @param carmaker A reference to the CarMaker object data
static void mapCarMakerObjectToCANoeObject(RBSData::ObjectData& canoe, tObject& carmaker)
{
    canoe.m_objID = carmaker.objId;
    canoe.m_classification = carmaker.classification;
    canoe.m_radarType = carmaker.radar_type;
    canoe.m_dxN = carmaker.dxN;
    canoe.m_dyN = carmaker.dyN;
    canoe.m_dzN = carmaker.dzN;
    canoe.m_vxN = carmaker.vxN;
    canoe.m_vyN = carmaker.vyN;
    canoe.m_axN = carmaker.axN;
    canoe.m_ayN = carmaker.ayN;
    canoe.m_dWidthN = carmaker.dWidthN;
    canoe.m_dLengthN = carmaker.dLengthN;
    canoe.m_RCS = carmaker.rcsN;
    canoe.m_SNR = carmaker.snrN;
    canoe.m_alpPiYawAngleN = carmaker.alpPiYawAngleN;
    canoe.m_SignalStrength = carmaker.signalStrengthN;
}

/// @brief Maps the CarMaker Radar instance to the CANoe data format
/// @param canoe A reference to the CANoe data structure to map to
/// @param carmaker A reference to the CarMaker radar/sensor data
static void mapCarMakerRadarToCANoeRadar(RBSData::RadarData& canoe, tSensorData& carmaker)
{
    canoe.m_mountPosX = carmaker.mountPosX;
    canoe.m_mountPosY = carmaker.mountPosY;
    canoe.m_mountPosZ = carmaker.mountPosZ;
    canoe.m_sensorBlocked = 0;
    canoe.m_objectCount = carmaker.object_count;
    
    const int numObjsToCopy = (carmaker.object_count > Config::Radar::MAX_RADAR_OBJECTS) 
                                ? Config::Radar::MAX_RADAR_OBJECTS : carmaker.object_count;

    for (int i = 0; i < numObjsToCopy; i++)
    {
        mapCarMakerObjectToCANoeObject(
            canoe.m_objects[i],
            carmaker.objects[i]
        );
    }
}

/// @brief Serializes the Radar Data into a vector of bytes to transmit via UDP 
/// @param radarData A reference to the radar data to serialize
/// @return A vector of bytes in the format of a tUdpPacket containing the data in radarData
/// @note This relies on tUdpPacket to perform serialization of the data. See the source of this to understand
///       what is happening on the data level
std::vector<char> serializeRadarData(tRbRadarData& radarData)
{
    static tUdpPacket<RBSData::tRBSData> udpPacket;
    RBSData::tRBSData data;

    // Map FC Radar
    mapCarMakerRadarToCANoeRadar(
        data.m_radars[RBSData::Radar::FC], radarData.radarSensorData[RBSData::Radar::FC]);

    // Map FL Radar
    mapCarMakerRadarToCANoeRadar(
        data.m_radars[RBSData::Radar::FL], radarData.radarSensorData[RBSData::Radar::FL]);

    // Map FR Radar
    mapCarMakerRadarToCANoeRadar(
        data.m_radars[RBSData::Radar::FR], radarData.radarSensorData[RBSData::Radar::FR]);

    // Map RL Radar
    mapCarMakerRadarToCANoeRadar(
        data.m_radars[RBSData::Radar::RL], radarData.radarSensorData[RBSData::Radar::RL]);

    // Map RR Radar
    mapCarMakerRadarToCANoeRadar(
        data.m_radars[RBSData::Radar::RR], radarData.radarSensorData[RBSData::Radar::RR]);

    // Create the UDP Packet
    return udpPacket.constructRawPacket(data);
}

/// @brief Sends to Radar Data to the CANoe instance via UDP
/// @param radarData A reference to the radar data to be send via UDP
/// @param ipAddress The IP address of the CANoe UDP Server [Typically the RTRack]
/// @param port The port on the UDP Server to send the data to [Typically 25565]
/// @return A boolean true for a successful transmission or false for a failure
bool sendRadarDataUDP(tRbRadarData& radarData, const std::string& ipAddress, int port)
{
    WSADATA wsaData;
    SOCKET udpSocket = INVALID_SOCKET;
    sockaddr_in serverAddr;

    // Step 1: Initialize Winsock
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0)
    {
        // WSAStartup Failed
        return false;
    }

    // Step 2: Create a UDP socket
    udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket == INVALID_SOCKET)
    {
        // Socket creation failure
        WSACleanup();
        return false;
    }

    // Step 3: Set up the server address structure
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port); // Convert port to network byte order

    // Convert the IP address string to a binary form
    result = inet_pton(AF_INET, ipAddress.c_str(), &serverAddr.sin_addr);
    if (result <= 0)
    {
        // Invalid IP address string
        closesocket(udpSocket);
        WSACleanup();
        return false;
    }

    // Step 4: Send the UDP packet
    std::vector<char> data = serializeRadarData(radarData);
    result = sendto(udpSocket, data.data(), static_cast<int>(data.size()), 0,
                    (sockaddr *)&serverAddr, sizeof(serverAddr));

    if (result == SOCKET_ERROR)
    {
        // sendto failed due to socket error
        closesocket(udpSocket);
        WSACleanup();
        return false;
    }

    // Step 5: Cleanup
    closesocket(udpSocket);
    WSACleanup();

    return true;
}