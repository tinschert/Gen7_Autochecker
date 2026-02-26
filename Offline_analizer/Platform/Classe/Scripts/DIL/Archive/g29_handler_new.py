# -*- coding: utf-8 -*-
# @file g29_handler_new.py
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
    import sys
    sys.path.append('../logidrivepy')
    from logidrivepy import LogitechController
    import socket
    import struct
    import numpy
    import sys
    import win32gui, win32con
    import threading, time
except ImportError as e:
    raise e


the_program_to_hide = win32gui.GetForegroundWindow()
win32gui.ShowWindow(the_program_to_hide , win32con.SW_SHOWMINIMIZED)

#pygame.init()

def thread_send():
    """ """
    main_send()
    threading.Timer(1, thread_send).start()


#client_ip = "192.168.1.29"
client_port = 2929
client_ip = "127.0.0.1"
server_ip = "127.0.0.1"
#server_ip = "192.168.1.92"
server_port = 9292

saturation_percentage = 100
coefficient_percentage = 40
magnitude_percentage = 30
adas_swa_req_active = 0
adas_swa_req = 0

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
    mapped_value = ((value - from_range_start) * ((to_range_end - to_range_start) / (from_range_end - from_range_start))) + to_range_start
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

def receive_array_of_hex(server_ip, server_port):
    """
    

    Args:
      server_ip: 
      server_port: 

    Returns:

    """
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((server_ip, server_port))
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    print("received message: %s" % data)


def adas_control_g29(current_swa, adas_swa_req):
    """
    

    Args:
      current_swa: 
      adas_swa_req: 

    Returns:

    """
    if adas_swa_req < current_swa:
        controller.logi_update()
        controller.LogiPlayConstantForce(0, -magnitude_percentage)
        controller.logi_update()
    elif adas_swa_req > current_swa:
        controller.logi_update()
        controller.LogiPlayConstantForce(0, magnitude_percentage)
        controller.logi_update()


def main_send():
    """ """

    try:
        #clock = pygame.time.Clock()

        joysticks = {}

        done = False
        while not done:

            receive_array_of_hex(server_ip, server_port)
            #map to internal variables adas_swa_req and adas_swa_req_active

            # Read data from g29
            controller.logi_update()
            obj = controller.get_state_engines(0)
            raw_swa = obj.contents.lX  # steering axis
            raw_brake_pedal = obj.contents.lRz  # brake pedal
            raw_gas_pedal = obj.contents.lY  # gas pedal

            current_swa = round(map_value(raw_swa, -32768, 32768,-450,450), 3)
            current_brake_pedal = round(map_value(raw_brake_pedal, 32768, -32768, 0, 100), 3)
            current_gas_pedal = round(map_value(raw_gas_pedal, 32768, -32768, 0, 100), 3)

            # Control g29 from ADAS request
            if adas_swa_req_active == 1:
                adas_control_g29(current_swa, adas_swa_req)
            else:
                controller.LogiStopConstantForce(0)


            # missing event handling for quit (close window etc - close shutdown?)

            PDU_np[0] = current_swa
            PDU_np[1] = current_brake_pedal
            PDU_np[2] = current_gas_pedal
            # add torque and new buttons here

            # vectorize the function
            vec_int_to_hex = numpy.vectorize(double_to_hex)
            # convert the array of integers to hex values
            hex_arr = vec_int_to_hex(PDU_np)

            #construct the payload and encode it to bytes
            PDU_payload = PDU_header + hex_arr[0] + hex_arr[1] + hex_arr[2]
            hex_array_to_send = back_to_back_hex(PDU_payload)#hex_array_to_send = [0x1D, 0x18, 0x42, 0x49, 0x90, 0x00, 0x42, 0x49, 0x90, 0x00, 0x42, 0x49, 0x90, 0x00]
            #print(PDU_np)

            # Limit to 30 frames per second.
            #clock.tick(0.01)
            send_array_of_hex(client_ip, client_port, hex_array_to_send)#send_hello_message(client_ip, client_port)


            #print("From  before print_time", time.time())

    except Exception as e:
        print("Runtime error occurred.")
        controller.steering_shutdown()
        raise e


if __name__ == "__main__":
    # start logidrivepy
    controller = LogitechController()
    time.sleep(0.1)
    controller.steering_initialize()
    time.sleep(0.1)
    #thread_send()
    main_send()
    controller.steering_shutdown()
    pygame.quit()


