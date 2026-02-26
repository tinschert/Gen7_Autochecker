# -*- coding: utf-8 -*-
# @file g29_handler.py
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


try:
    import pygame
    import socket
    import struct
    import numpy
    import sys
    import win32gui, win32con
except ImportError as e:
    raise e


the_program_to_hide = win32gui.GetForegroundWindow()
win32gui.ShowWindow(the_program_to_hide , win32con.SW_SHOWMINIMIZED)


#start pygame
pygame.init()


client_ip = "192.168.1.29"
client_port = 2929
try:
    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
except Exception as e:
    print(f"Unable to connect to {client_ip} or port {client_port} is filtered.")
    raise e

PDU_header = '0x1D0x18' #in decimal ID = 29; length = 24

#create a numpy array to save 3 variables of 8 bytes float 
PDU = [] 
PDU.append(0.0)
PDU.append(0.0)
PDU.append(0.0)
PDU_np = numpy.array(PDU , dtype=numpy.float64)


def double_to_hex(f):
    """
    

    Args:
      f: 

    Returns:

    """
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])

def map_value(value, from_range_start, from_range_end, to_range_start, to_range_end):
    """
    

    Args:
      value: 
      from_range_start: 
      from_range_end: 
      to_range_start: 
      to_range_end: 

    Returns:

    """
    mapped_value = (value - from_range_start) * (to_range_end - to_range_start) / (from_range_end - from_range_start) + to_range_start
    return mapped_value

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
    #hex_string = hex_string.replace("0x00x", "0x000000000x")
    hex_values = hex_string.split("0x")# Split the input string by "0x" to get individual hexadecimal values
    hex_list = list(filter(None, hex_values))# Filter out empty strings from the split operation
    #print(hex_list)
    result_hex=""
    for string_value in hex_list:
        if(string_value=="0"):
            result_hex=result_hex+"00000000"
        else:
            result_hex=result_hex+string_value
    print(result_hex)
    #result_hex = "".join(hex_list)
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
    #for hex
    hex_format = "!{}B".format(len(data))
    packed_data = struct.pack(hex_format, *data)
    UDPClientSocket.sendto(packed_data, (client_ip, client_port))

def main():
    """ """

    try:
        clock = pygame.time.Clock()

        joysticks = {}

        init_value = 50
        done = False
        while not done:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

                if event.type == pygame.JOYBUTTONDOWN:
                    print("Joystick button pressed.")
                    if event.button == 0:
                        joystick = joysticks[event.instance_id]
                        if joystick.rumble(0, 0.7, 500):
                            print(f"Rumble effect played on joystick {event.instance_id}")

                if event.type == pygame.JOYBUTTONUP:
                    print("Joystick button released.")

                if event.type == pygame.JOYDEVICEADDED:

                    joy = pygame.joystick.Joystick(event.device_index)
                    joysticks[joy.get_instance_id()] = joy
                    print(f"Joystick {joy.get_instance_id()} connencted")

                if event.type == pygame.JOYDEVICEREMOVED:
                    del joysticks[event.instance_id]
                    print(f"Joystick {event.instance_id} disconnected")



            for joystick in joysticks.values():

                PDU_np[0] = round(map_value(joystick.get_axis(0), -1, 1,-450,450 ) , 3) #SWA axe
                PDU_np[1] = round(map_value(joystick.get_axis(2), 1, -1, 0, 100 ) , 3) #brakes
                PDU_np[2] = round(map_value(joystick.get_axis(1), 1, -1, 0, 100 ) , 3) #pedal

                if (PDU_np[1] == init_value):
                    PDU_np[1] = 0
                if (PDU_np[2] == init_value):
                    PDU_np[2] = 0

                # vectorize the function
                vec_int_to_hex = numpy.vectorize(double_to_hex)
                # convert the array of integers to hex values
                hex_arr = vec_int_to_hex(PDU_np)

                #construct the payload and encode it to bytes
                PDU_payload = PDU_header +  hex_arr[0] + hex_arr[1] + hex_arr[2]
                hex_array_to_send=back_to_back_hex(PDU_payload)#hex_array_to_send = [0x1D, 0x18, 0x42, 0x49, 0x90, 0x00, 0x42, 0x49, 0x90, 0x00, 0x42, 0x49, 0x90, 0x00]
                send_array_of_hex(client_ip, client_port, hex_array_to_send)#send_hello_message(client_ip, client_port)

                print(PDU_np)

            # Limit to 30 frames per second.
            clock.tick(120)
    except Exception as e:
        print("Runtime error occurred.")
        raise e


if __name__ == "__main__":
    main()
    pygame.quit()


