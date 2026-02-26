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

#include <Config.h>
#include <RBSData.h>
#include <UdpPacket.h>

#include <algorithm>
#include <chrono>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <vector>
#include <string>
#include <iostream>
#include <thread>

// Link with ws2_32.lib
#pragma comment(lib, "ws2_32.lib")

/// @brief Sends to Radar Data to the CANoe instance via UDP
/// @param data A reference to the data to send
/// @return A boolean true for a successful transmission or false for a failure
bool sendUdpPacket(const std::vector<char>& data)
{
    const std::string ipAddress = Config::UdpClient::CARMAKER_UDP_TARGET_IP_ADDRESS;
    const int port = Config::UdpClient::SENDING_PORT;

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

void testCRCMismatch()
{
    printf("running: testCRCMismatch\n");
    tUdpPacket<RBSData::tRBSData> packet;
    RBSData::tRBSData data;

    // Send a valid packet
    packet.update(data);
    sendUdpPacket(packet.constructRawPacket());

    // wait for 5 milliseconds
    std::this_thread::sleep_for(std::chrono::milliseconds(5));

    // Send an invalid crc packet
    const int packetsToSend = Config::UdpServerApp::ErrorLimits::MAX_CRC_MISMATCHES + 1;
    for (int i = 0; i < packetsToSend; i++)
    {
        packet.update(data);
        packet.m_crcSection.m_crc32 = 0x55555555;
        sendUdpPacket(packet.constructRawPacket());
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
}

void testPacketOverflow()
{
    printf("running: testPacketOverflow\n");
    tUdpPacket<RBSData::tRBSData> packet;
    RBSData::tRBSData data;

    // Send a ton of packets above the max queue size to trigger an overflow
    const int packetsToSend = Config::UdpServerApp::MAX_PACKETS_IN_QUEUE * 3;
    for (int i = 0; i < packetsToSend; i++)
    {
        sendUdpPacket(packet.constructRawPacket(data));
    }
}

void testOutOfOrderPackets()
{
    printf("running: testOutOfOrderPackets\n");
    tUdpPacket<RBSData::tRBSData> packet;
    RBSData::tRBSData data;

    // Send a valid packet
    packet.update(data);
    sendUdpPacket(packet.constructRawPacket());

    // wait for 5 milliseconds
    std::this_thread::sleep_for(std::chrono::milliseconds(5));

    // Send a second valid packet
    packet.update(data);
    sendUdpPacket(packet.constructRawPacket());
    
    // wait for 5 milliseconds
    std::this_thread::sleep_for(std::chrono::milliseconds(5));

    const int numInvalidPacketsToTrigger = 2;
    for (int i = 0; i < numInvalidPacketsToTrigger; i++)
    {
        packet.update(data);
        packet.m_headerSection.m_counter = 0x10 + (i * 3);
        sendUdpPacket(packet.constructRawPacket());
    }
}

void testMessageSizeMismatch()
{
    printf("running: testMessageSizeMismatch\n");
    tUdpPacket<RBSData::tRBSData> packet;
    RBSData::tRBSData data;

    // Send a valid packet
    packet.update(data);
    sendUdpPacket(packet.constructRawPacket());

    // wait for 5 milliseconds
    std::this_thread::sleep_for(std::chrono::milliseconds(5));

    // Send a invalid valid packet
    packet.update(data);
    packet.m_headerSection.m_dataLength = sizeof(data) - 1;
    sendUdpPacket(packet.constructRawPacket());
}

void testInvalidDataType()
{
    printf("running: testInvalidDataType\n");
    tUdpPacket<RBSData::tRBSData> packet;
    RBSData::tRBSData data;

    // Send a valid packet
    packet.update(data);
    sendUdpPacket(packet.constructRawPacket());

    // wait for 5 milliseconds
    std::this_thread::sleep_for(std::chrono::milliseconds(5));

    // Send a invalid valid packet
    tUdpPacket<int> invalidPacket;
    invalidPacket.update(5);
    invalidPacket.m_headerSection.m_counter = packet.m_headerSection.m_counter + 1;
    sendUdpPacket(invalidPacket.constructRawPacket());
}

int main(int argc, char* argv[])
{
    if (argc != 2)
    {
        printf("no command specified\n");
        return 0;
    }

    const std::string command = argv[1];

    printf("Executing testcase - %s\n", command.c_str());

    if (command.compare("UDP_CRC_MISMATCH") == 0)
    {
        testCRCMismatch();
    }
    else if (command.compare("UDP_PACKET_OVERFLOW") == 0)
    {
        testPacketOverflow();
    }
    else if (command.compare("UDP_OUT_OF_ORDER_PACKETS") == 0)
    {
        testOutOfOrderPackets();
    }
    else if (command.compare("UDP_MESSAGE_SIZE_MISMATCH") == 0)
    {
        testMessageSizeMismatch();
    }
    else if (command.compare("INVALID") == 0)
    {
        testInvalidDataType();
    }
    else if (command.compare("ALL") == 0)
    {
        testCRCMismatch();
        printf("Delay 3 seconds\n");
        std::this_thread::sleep_for(std::chrono::seconds(3));
        
        testPacketOverflow();
        printf("Delay 3 seconds\n");
        std::this_thread::sleep_for(std::chrono::seconds(3));
        
        testOutOfOrderPackets();
        printf("Delay 3 seconds\n");
        std::this_thread::sleep_for(std::chrono::seconds(3));
        
        testMessageSizeMismatch();
        printf("Delay 3 seconds\n");
        std::this_thread::sleep_for(std::chrono::seconds(3));
        
        testInvalidDataType();
    }

    printf("Execution complete\n");
    return 1;
}