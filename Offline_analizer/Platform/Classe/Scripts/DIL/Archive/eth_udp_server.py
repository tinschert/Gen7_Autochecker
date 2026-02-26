# -*- coding: utf-8 -*-
# @file eth_udp_server.py
# @author ADAS_HIL_TEAM
# @date 08-21-2023

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
import time
import struct

def create_udp_server(ip, port):
    """
    

    Args:
      ip: 
      port: 

    Returns:

    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    return server_socket

def split_string_into_chunks(input_string, chunk_size=2):
    """
    

    Args:
      input_string: 
      chunk_size:  (Default value = 2)

    Returns:

    """
    return [input_string[i:i+chunk_size] for i in range(0, len(input_string), chunk_size)]

def back_to_back_hex(hex_string):
    """
    

    Args:
      hex_string: 

    Returns:

    """
    hex_string = hex_string.replace(" ", "")# Remove any spaces in the input string
    hex_string = hex_string.replace("0X", "0x")# Replace any "0X" with "0x" in the input string
    hex_values = hex_string.split("0x")# Split the input string by "0x" to get individual hexadecimal values
    hex_list = list(filter(None, hex_values))# Filter out empty strings from the split operation

    #for value in hex_list:
    #    print(value)
    
    result_hex = "".join(hex_list)
    result_chunks = split_string_into_chunks(result_hex, chunk_size=2)
    hex_values =[int(hex_str, 16) for hex_str in result_chunks] #in to int formate
    return hex_values

def send_array_of_hex(client_ip, client_port, data):
    """
    

    Args:
      client_ip: 
      client_port: 
      data: 

    Returns:

    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #for hex
    hex_format = "!{}B".format(len(data))
    packed_data = struct.pack(hex_format, *data)

    client_socket.sendto(packed_data, (client_ip, client_port))

if __name__ == "__main__":
    server_ip = "0.0.0.0"
    server_port = 2929
    client_ip = "192.168.1.29"
    client_port = 2929

    #server_socket = create_udp_server(server_ip, server_port)

    try:
        while True:
            input_hex_string = "0x1D180x424990000x424990000x42499000"
            hex_array_to_send=back_to_back_hex(input_hex_string)#hex_array_to_send = [0x1D, 0x18, 0x42, 0x49, 0x90, 0x00, 0x42, 0x49, 0x90, 0x00, 0x42, 0x49, 0x90, 0x00]
            send_array_of_hex(client_ip, client_port, hex_array_to_send)#send_hello_message(client_ip, client_port)
            print(f"Sent {hex_array_to_send} message to {client_ip}:{client_port}")
            time.sleep(1)  # Sending message every 1 second
    except KeyboardInterrupt:
        server_socket.close()




