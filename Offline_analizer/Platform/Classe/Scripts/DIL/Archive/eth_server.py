# -*- coding: utf-8 -*-
# @file eth_server.py
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

SERVER_UDP_IP = "127.0.0.1"
SERVER_UDP_PORT = 2929
#UDP_IP = "192.168.1.92"
#UDP_PORT = 2929
MESSAGE = b"Hello, World!"

print("UDP target IP: %s" % SERVER_UDP_IP)
print("UDP target port: %s" % SERVER_UDP_PORT)
print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (SERVER_UDP_IP, SERVER_UDP_PORT))