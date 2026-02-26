# -*- coding: utf-8 -*-
# @file g29_handler_com_ethernet.py
# @author ADAS_HIL_TEAM
# @date 10-11-2023

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

    import os, sys
    sys.path.append('../logidrivepy')
    from logidrivepy import LogitechController
    import struct
    import sys
    import win32gui
    import win32con
    import time
    import numpy
    import socket
    import pygame
    import threading

    sys.path.append('../logidrivepy')

    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")


except ImportError as e:
    raise e


the_program_to_hide = win32gui.GetForegroundWindow()
win32gui.ShowWindow(the_program_to_hide, win32con.SW_SHOWMINIMIZED)

# =============================================================================
# Communication protocol settings
# =============================================================================

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#PDU_header = '0x1D0x18' #in decimal ID = 29; length = 24
PDU = []
PDU.append(0.0)
PDU.append(0.0)
PDU.append(0.0)
PDU.append(0.0)
PDU.append(0.0)
PDU.append(0)
PDU_np = numpy.array(PDU , dtype=numpy.float64)
init_value = 50
g_client_ip = "127.0.0.1" #destination IP in this case the RT rack
g_client_port = 2929
g_server_ip = "127.0.0.1" #source IP in this case the Rendering PC with g29
g_server_port = 9292
clock = pygame.time.Clock()

# =============================================================================
# Constants
# =============================================================================

G29_CONTROLLER_EGO = 0
G29_CONTROLLER_TARGET = 1
# message reception cycle time (CANoe -> G29); defined in CANoe
CYCLE_TIME_RX_IN_MS = 10
# message transmission cycle time (G29 -> CANoe)
CYCLE_TIME_TX_IN_MS = 10
# minimum steering force ([0..100])
MIN_STEERING_FORCE = 10

# =============================================================================
# Global data
# =============================================================================

g_torque_dir = 0

# PID data
g_pid_error = [0, 0]
g_pid_integral = [0, 0]

# data received from CANoe
g_swa_req_active = [0, 0]
g_swa_req_in_deg = [0, 0] # (ISO coord system)

# =============================================================================
# Functions
# =============================================================================

def setup_connection():
    global g_client_ip
    global g_client_port
    global g_server_ip
    global g_server_port
    
    n = len(sys.argv)
    i = 0
    for i in range(1, n):
        print("arg", i, ": ", sys.argv[i])
        if(sys.argv[i] == 'single_pc'):
            g_client_ip = "127.0.0.1"    # localhost
            g_server_ip = "127.0.0.1"    # localhost
        elif(sys.argv[i] == 'rt_rack'):
            g_client_ip = "192.168.1.5"  # destination IP in this case the RT rack
            g_server_ip = "192.168.1.15" # source IP in this case the Rendering PC with g29

    try:
        # Create a UDP socket at client side
        UDPClientSocket.bind((g_server_ip, g_server_port))
    except Exception as e:
        print(f"Unable to connect to {client_ip} or port {client_port} is filtered.")
        raise e


def map_value(value, from_range_start, from_range_end, to_range_start, to_range_end):
    """
    Description:
        Normalization function to change the min max of a signal into a customly defined min max
    Args:
        value(double): value to convert
        from_range_start(double): original min
        from_range_end(double): original max
        to_range_start(double): target min
        to_range_end: target max
    Returns:
        Mapped_value(double) the value now normalized to the new min max thresholds
    """
    
    mapped_value = ((value - from_range_start) * ((to_range_end - to_range_start) / (from_range_end - from_range_start))) + to_range_start
    return mapped_value


def pid_control(target_value, current_value, coeff_err, coeff_int, coeff_int_add, abs_int_max, coeff_der, dt_in_s, idx):
    """
    Description:
        PID controller
    Args:
        target_value(double): target value to reach
        current_value(double): current value measured
        coeff_err(double): error coefficient
        coeff_int(double): integrative coefficient
        coeff_int_add(double): integrative coefficient
        abs_int_max(double):  absolute maximum for integrative part
        coeff_der(double): derivative coefficient
        dt_in_s(double): delta time in seconds
        idx(double): index 1 for the first PID and index 2 for a second PID iteration
    Returns: 
        pid_out(double) returns the PID magnitude control
    """
    
    curr_error = target_value - current_value
    d_error = (curr_error - g_pid_error[idx]) / dt_in_s
    g_pid_error[idx] = curr_error
    g_pid_integral[idx] = g_pid_integral[idx] + coeff_int_add * (g_pid_error[idx] * dt_in_s)
    if (abs_int_max != 0):
        g_pid_integral[idx] = max(-abs_int_max, min(abs_int_max, g_pid_integral[idx]))
    pid_out = coeff_err * g_pid_error[idx] + coeff_int * g_pid_integral[idx] + coeff_der * d_error
    
    return pid_out


def double_to_hex(f):
    """
    Description:
        Converts a double into hex
    Args:
        f(double): double number to be converted to Hex
    Returns:
        hex(string) string of hex numbers
    """
    
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])


def split_string_into_chunks(input_string, chunk_size=2):
    """
    Description:
        Inputs a string and it returns a splitted string into desired chunk length
    Args:
        input_string(string): input string to be cut into chunks
        chunk_size(int):  chunck size of the string, default vlaue is 2
    Returns:
        input_string(string) cut into chuncks
    """
    
    return [input_string[i:i+chunk_size] for i in range(0, len(input_string), chunk_size)]


def back_to_back_hex(hex_string):
    """
    Description:
        Transforms string into hex array
    Args:
        hex_string(string): 
    Returns:
        data in hex format
    """
    
    hex_string = hex_string.replace(" ", "")# Remove any spaces in the input string
    hex_string = hex_string.replace("0X", "0x")# Replace any "0X" with "0x" in the input string
    #hex_string = hex_string.replace("0x00x", "0x000000000x")
    hex_values = hex_string.split("0x") # Split the input string by "0x" to get individual hexadecimal values
    hex_list = list(filter(None, hex_values)) # Filter out empty strings from the split operation
    #print(hex_list)
    result_hex=""
    for string_value in hex_list:
        if(string_value=="0"):
            result_hex=result_hex+"00000000"
        else:
            result_hex=result_hex+string_value
    #print(result_hex)
    #result_hex = "".join(hex_list)
    result_chunks = split_string_into_chunks(result_hex, chunk_size=2)
    hex_values =[int(hex_str, 16) for hex_str in result_chunks] #in to int formate
    return hex_values


def send_array_of_hex(client_ip, client_port, data):
    """
    Description:
        Sends the hex array of the data
    Args:
        client_ip(string): IP address
        client_port(string): Port
        data(string): hex string of the pdu payload
    Returns:
        none
    """
    
    #for hex
    hex_format = "!{}B".format(len(data))
    packed_data = struct.pack(hex_format, *data)
    UDPClientSocket.sendto(packed_data, (client_ip, client_port))


def send_controller_data(current_swa, current_brake_pedal, current_gas_pedal, current_clutch_pedal, current_target_swa, button_array, g29_id):
    """
    Description:
        Sends the information from the g29 as an ETH UDP PDU in hex format
    Args:
        current_swa(double): steering wheel angle in degrees (ISO coord system)
        current_brake_pedal(double): brake pedal position from 0 to 100%
        current_gas_pedal(double): gas pedal position from 0 to 100%
        current_target_swa(double): steering wheel angle in degrees (ISO coord system) requested by CANoe
        button_array(int): bit array of the button pressed or not pressed information converted to decimal
        g29_id(int) : When multiple g29_s are connected based on the joystick id, sends the the apporpriate PDU_header
    Returns:
        none
    """
    
    if g29_id == G29_CONTROLLER_EGO:
        PDU_header = '0x1D0x1C'
    elif g29_id == G29_CONTROLLER_TARGET:
        PDU_header = '0x1E0x1C'
    PDU_np[0] = current_swa # SWA axe
    PDU_np[1] = current_gas_pedal
    PDU_np[2] = current_brake_pedal
    PDU_np[3] = current_clutch_pedal
    PDU_np[4] = current_target_swa
    PDU_np[5] = button_array

    if (PDU_np[1] == init_value):
        PDU_np[1] = 0
    if (PDU_np[2] == init_value):
        PDU_np[2] = 0
    if (PDU_np[3] == init_value):
        PDU_np[3] = 0

    # vectorize the function
    vec_int_to_hex = numpy.vectorize(double_to_hex)
    # convert the array of integers to hex values
    hex_arr = vec_int_to_hex(PDU_np)

    # construct the payload and encode it to bytes
    PDU_payload = PDU_header + hex_arr[0] + hex_arr[1] + hex_arr[2] + hex_arr[3] + hex_arr[4] + hex_arr[5]
    hex_array_to_send = back_to_back_hex(PDU_payload)  # hex_array_to_send = [0x1D, 0x18, 0x42, 0x49, 0x90, 0x00, 0x42, 0x49, 0x90, 0x00, 0x42, 0x49, 0x90, 0x00]
    send_array_of_hex(g_client_ip, g_client_port, hex_array_to_send)  # send_hello_message(client_ip, client_port)

    #print(PDU_np)
    #print(PDU_payload)
    
    pygame.time.delay(CYCLE_TIME_TX_IN_MS)


def auto_steering_torque(g29_idx, swa_req, current_swa, is_auto_controlled):
    """
    Description:
        Calculated torque for auto steering (G29 value range: [-100..100])

    Args:
        swa_req(double): requested steering wheel angle (ISO coord system)
        current_swa(double): acutal steering wheel angle (ISO coord system)
    Returns:
        torque(int): needed G29 torque for auto steering
    """
    
    # get PID base (current) value from requested and actual steering wheel angles
    pid_current_value = -(swa_req - current_swa) / 120
    if pid_current_value >= 0:
        pid_current_value = min(1, max(0, pid_current_value))
    else:
        pid_current_value = min(0, max(-1, pid_current_value))
    
    # calculate multiplier for torque (force applied on G29 steering wheel)
    torque = pid_control(0, pid_current_value, 1, 0, 1, 1, 0, CYCLE_TIME_RX_IN_MS*0.001, g29_idx)
    
    global g_torque_dir
    
    if (torque > 0):
        g_torque_dir = 1
    elif (torque < 0):
        g_torque_dir = -1
    
    auto_ctrl_coeff_0 = 0
    auto_ctrl_coeff_1 = 0
    auto_ctrl_coeff_min = 0
    if (is_auto_controlled == 1):
        auto_ctrl_coeff_0 = 100 - MIN_STEERING_FORCE
        auto_ctrl_coeff_1 = 0
        auto_ctrl_coeff_min = MIN_STEERING_FORCE
    else:
        auto_ctrl_coeff_0 = max(0, 20 - MIN_STEERING_FORCE)
        auto_ctrl_coeff_1 = int(6 * min(1, abs(torque) / 0.05))
        auto_ctrl_coeff_min  = MIN_STEERING_FORCE
    
    # final torque value
    torque_int = min(100, int(torque * auto_ctrl_coeff_0) + g_torque_dir * (auto_ctrl_coeff_1 + auto_ctrl_coeff_min))
    
    #print("torque_int = ", torque_int)
    
    return torque_int


def control_g29(g29_idx, swa_req, is_auto_controlled):
    """
    Description:
        Handles the force feedback control when ADAS function is active through a PID controller
    Args:
        current_swa(double): current steering wheel angle from the g29
        adas_swa_req(double): requested ADAS steering wheel angle from ECU
        dt(double): delta time to evaluate the PID controller
    Returns:
        none

    """
    [current_swa, current_brake_pedal, current_gas_pedal, current_clutch_pedal, button_array, g29_id] = g29_joystick_key_assignment(g29_idx)
    torque = auto_steering_torque(g29_idx, swa_req, current_swa, is_auto_controlled)
    
    controller.logi_update()
    controller.stop_spring_force(g29_idx)
    controller.play_constant_force(g29_idx, torque)
    controller.logi_update()
    

def receive_array_of_hex(g29_idx):
    """ 
    Description: 
        Receives the UDP from the CANoe and intreprets the data to set the appropriate steering angle
        Updates steering wheel angle requested by CANoe
    Args:
        g29_idx(int): G29 controller ID
    Returns:
        none
    """
    
    data, addr = UDPClientSocket.recvfrom(1024) # buffer size
    g_swa_req_active[g29_idx] = data[3]  #Assigns the swa control active req in LKA state
    swa_req_int = int(data[8:10].hex(), 16) #SWA from hvm
    
    if (data[2] == 1):
        g_swa_req_in_deg[g29_idx] = swa_req_int
    else:
        g_swa_req_in_deg[g29_idx] = swa_req_int * -1


def g29_joystick_key_assignment(idx):
    #while True:
        # Read data from g29
        obj = controller.LogiGetStateENGINES(idx)
        controller.logi_update()
        raw_swa = obj.contents.lX # steering axis
        raw_brake_pedal = obj.contents.lY  # brake pedal
        raw_gas_pedal = obj.contents.lRz  # gas pedal
        raw_clutch_pedal = obj.contents.rglSlider[0]  #clutch pedal
        left_handle = obj.contents.rgbButtons[5]  # left blinker
        right_handle = obj.contents.rgbButtons[4]  # right blinker
        triangle = obj.contents.rgbButtons[3]  # ACC button  3
        circle = obj.contents.rgbButtons[2]  # HF/ALC button
        square = obj.contents.rgbButtons[1]  # AEB button
        cross = obj.contents.rgbButtons[0]  # LKS button
        plus = obj.contents.rgbButtons[19]  # Set +
        minus = obj.contents.rgbButtons[20]  # Set -
        enter = obj.contents.rgbButtons[23]  # ADAS Abort
        l3 = obj.contents.rgbButtons[11]  # unused
        l2 = obj.contents.rgbButtons[7]  # Gear toggle
        r2 = obj.contents.rgbButtons[6]  # unused
        r3 = obj.contents.rgbButtons[10]  # unused
        start = obj.contents.rgbButtons[8]  # Init rbs
        options = obj.contents.rgbButtons[9]  # Stop sim
        ps = obj.contents.rgbButtons[24]  # unused
        clockwise = obj.contents.rgbButtons[21] # unused
        anti_clockwise = obj.contents.rgbButtons[22] # unused
        dpad_N = 1 if obj.contents.rgdwPOV[idx] == 0 * 4500 else 0  # Drive Gear
        dpad_NE = 1 if obj.contents.rgdwPOV[idx] == 1 * 4500 else 0  # unused
        dpad_E = 1 if obj.contents.rgdwPOV[idx] == 2 * 4500 else 0  # unused
        dpad_ES = 1 if obj.contents.rgdwPOV[idx] == 3 * 4500 else 0  # unused
        dpad_S = 1 if obj.contents.rgdwPOV[idx] == 4 * 4500 else 0  # Reverse Gear
        dpad_SW = 1 if obj.contents.rgdwPOV[idx] == 5 * 4500 else 0  # unused
        dpad_W = 1 if obj.contents.rgdwPOV[idx] == 6 * 4500 else 0  # unused
        dpad_NW = 1 if obj.contents.rgdwPOV[idx] == 7 * 4500 else 0  # unused
        left_handle = 1 if left_handle == -128 else 0
        right_handle = 1 if right_handle == -128 else 0
        triangle = 1 if triangle == -128 else 0
        circle = 1 if circle == -128 else 0
        square = 1 if square == -128 else 0
        cross = 1 if cross == -128 else 0
        plus = 1 if plus == -128 else 0
        minus = 1 if minus == -128 else 0
        enter = 1 if enter == -128 else 0
        l3 = 1 if l3 == -128 else 0
        l2 = 1 if l2 == -128 else 0
        r2 = 1 if r2 == -128 else 0
        r3 = 1 if r3 == -128 else 0
        start = 1 if start == -128 else 0
        options = 1 if options == -128 else 0
        ps = 1 if ps == -128 else 0
        clockwise = 1 if clockwise == -128 else 0
        anti_clockwise = 1 if anti_clockwise == -128 else 0
        list = [left_handle, right_handle, triangle, circle, square, cross, plus, minus, enter, l3, l2, r2, r3, start, options, ps, clockwise,anti_clockwise, dpad_N, dpad_NE, dpad_E, dpad_ES, dpad_S, dpad_SW, dpad_W, dpad_NW]
        button_array = bin(int(''.join(map(str, list)), 2) << 1)
        button_array = int(button_array, 2)
        g29_id = idx
        current_swa = raw_swa
        current_swa = round(map_value(raw_swa, -32768, 32768,-450,450), 0)
        current_brake_pedal = round(map_value(raw_brake_pedal, 32768, -32768, 0, 100), 0)
        current_gas_pedal = round(map_value(raw_gas_pedal, 32768, -32768, 0, 100), 0)
        current_clutch_pedal = round(map_value(raw_clutch_pedal, 32768, -32768, 0, 100), 0)
        return(-current_swa, current_brake_pedal, current_gas_pedal, current_clutch_pedal, button_array, g29_id)


# =============================================================================
# Main functions of created threads
# =============================================================================

def main_receive():
    """
    Description:
        Contains a while loop orchestrating the functions to receive data from CANoe ADAS
    Args:
        none
    Returns: 
        none
    """
    while True:
        receive_array_of_hex(G29_CONTROLLER_EGO)


def main_control():
    """ 
    Description:
        Main function of G29 control process (thread)
    Args:
        none
    Returns: 
        none
    """
    
    while True:
        control_g29(G29_CONTROLLER_EGO, g_swa_req_in_deg[G29_CONTROLLER_EGO], g_swa_req_active[G29_CONTROLLER_EGO])
        pygame.time.delay(CYCLE_TIME_RX_IN_MS)

    

def main_send(controller):
    """
    Description:
        Contains a while loop orchestrating the functions to  
        - receive data from CANoe ADAS
        - get the data of SWA, pedals and buttons from the g29 controller object
        - prepare the hex array and send the info from the g29 back to CANoe
    Args:
        controller(int): Controller ID meaning g29 object 
    Returns:
        none
    """

    while True:
        controller.logi_update()
        if (controller.is_connected(G29_CONTROLLER_EGO) == 1 & controller.is_connected(G29_CONTROLLER_TARGET) == 1):
            
            [current_swa, current_brake_pedal, current_gas_pedal, current_clutch_pedal, button_array, g29_id] = g29_joystick_key_assignment(G29_CONTROLLER_EGO)
            send_controller_data(current_swa, current_brake_pedal, current_gas_pedal, current_clutch_pedal, g_swa_req_in_deg[g29_id], button_array, g29_id)
            
            [current_swa, current_brake_pedal, current_gas_pedal, current_clutch_pedal, button_array,g29_id] = g29_joystick_key_assignment(G29_CONTROLLER_TARGET)
            send_controller_data(current_swa, current_brake_pedal, current_gas_pedal, current_clutch_pedal, g_swa_req_in_deg[g29_id], button_array, g29_id)
            
            controller.logi_update()
            controller.play_leds(G29_CONTROLLER_TARGET,11,10,20)
            controller.play_leds(G29_CONTROLLER_EGO,5,10,20)

        elif controller.is_connected(G29_CONTROLLER_EGO) == 1 | controller.is_connected(G29_CONTROLLER_TARGET) == 1:
            
            [current_swa, current_brake_pedal, current_gas_pedal, current_clutch_pedal, button_array, g29_id] = g29_joystick_key_assignment(G29_CONTROLLER_EGO)
            send_controller_data(current_swa, current_brake_pedal, current_gas_pedal, current_clutch_pedal, g_swa_req_in_deg[g29_id], button_array, g29_id)
            controller.play_leds(G29_CONTROLLER_EGO,5,10,20)
        else:
            print(f'Check G29 controller connection')
            break


# =============================================================================
# Main function
# =============================================================================

if __name__ == "__main__":
    setup_connection()
    
    # start logidrivepy
    controller = LogitechController()
    steering_initialize = controller.steering_initialize()
    logi_update = controller.logi_update()
    is_connected_ego = controller.is_connected(G29_CONTROLLER_EGO)
    is_connected_target = controller.is_connected(G29_CONTROLLER_TARGET)
  
    print(f"\n---Logitech Controller Test Sim---")
    print(f"steering_initialize: {steering_initialize}")
    print(f"logi_update: {logi_update}")
    print(f"is_connected_ego: {is_connected_ego}")
    print(f"is_connected_target: {is_connected_target}")
    
    # thread for cyclic message transmission from G29
    send_thread = threading.Thread(target= main_send, args=(controller,))
    # thread for cyclic message reception on G29 side
    receive_thread = threading.Thread(target= main_receive)
    # thread for cyclic data processing and G29 control
    control_thread = threading.Thread(target= main_control)
    
    send_thread.start() 
    receive_thread.start()
    control_thread.start()
    
    send_thread.join()
    receive_thread.join()
    control_thread.join()

    # Shutdown steering
    controller.steering_shutdown()

