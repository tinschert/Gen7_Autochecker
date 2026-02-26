# -*- coding: utf-8 -*-
# @file eth_client.py
# @author ADAS_HIL_TEAM
# @date 10-09-2023

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


import socket
import struct

CLIENT_UDP_IP = "192.168.1.5" # destination IP receiving RT rack
CLIENT_UDP_PORT = 2929 
UDP_IP = "192.168.1.15" # server sending data Rendering PC
UDP_PORT = 9292

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    print("wait")
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print(data[17])
    print(data[9])
    #for i in data:
    #     print(i)
