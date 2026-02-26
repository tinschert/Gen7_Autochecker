# -*- coding: utf-8 -*-
# @file g29_handler_com.py
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

    sys.path.append('../logidrivepy')

    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
    import canoe_client_1


except ImportError as e:
    raise e


the_program_to_hide = win32gui.GetForegroundWindow()
#win32gui.ShowWindow(the_program_to_hide, win32con.SW_SHOWMINIMIZED)
canoeClient = canoe_client_1.CANoeClient()

error0 = 0
integral0 = 0
error1 = 0
integral1 = 0
previous_magnitude = 0

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


def adas_control_g29(current_swa, adas_swa_req, dt):
    """
    

    Args:
      current_swa: 
      adas_swa_req: 
      dt: 

    Returns:

    """
    global previous_magnitude

    magnitude_temp = pid_control(adas_swa_req, current_swa, 1, 0, 0, 0, 0, dt, 0)
    magnitude_tgt = -max(-40, min(40, magnitude_temp))
    magnitude_updated = pid_control(magnitude_tgt, previous_magnitude, 0, 1, 1, 0, 0, dt, 1)
    previous_magnitude = magnitude_updated
    controller.logi_update()
    controller.LogiPlayConstantForce(0, int(magnitude_updated))
    controller.logi_update()
    print("the current swa is", current_swa, "the adas swa is", adas_swa_req, "target mag", magnitude_tgt, "updated mag", magnitude_updated)

def pid_control(target_value, current_value, coeff_err, coeff_int, coeff_int_add, abs_int_max, coeff_der, dt_in_s, idx):
    """
    

    Args:
      target_value: 
      current_value: 
      coeff_err: 
      coeff_int: 
      coeff_int_add: 
      abs_int_max: 
      coeff_der: 
      dt_in_s: 
      idx: 

    Returns:

    """
    global error0, integral0, error1, integral1

    if (idx == 0):
        curr_error = target_value - current_value
        d_error = (curr_error - error0) / dt_in_s
        error0 = curr_error
        integral0 = integral0 + coeff_int_add * (error0 * dt_in_s)
        if (abs_int_max != 0):
            integral0 = max(-abs_int_max, min(abs_int_max, integral0))
        pid_out = coeff_err * error0 + coeff_int * integral0 + coeff_der * d_error
    elif (idx == 1):
        curr_error = target_value - current_value
        d_error = (curr_error - error1) / dt_in_s
        error1 = curr_error
        integral1 = integral1 + coeff_int_add * (error1 * dt_in_s)
        if (abs_int_max != 0):
            integral1 = max(-abs_int_max, min(abs_int_max, integral1))
        pid_out = coeff_err * error1 + coeff_int * integral1 + coeff_der * d_error

    return pid_out

def send_controller_data(current_swa, current_gas_pedal, current_brake_pedal, button_array):
    """
    

    Args:
      current_swa: 
      current_gas_pedal: 
      current_brake_pedal: 
      button_array: 

    Returns:

    """
    canoeClient.setSysVarValue("hil_drv", "steering_wheel_angle_req", current_swa)
    canoeClient.setSysVarValue("hil_drv", "gas_pedal_position", current_gas_pedal)
    canoeClient.setSysVarValue("hil_drv", "brake_pedal_position", current_brake_pedal)
    canoeClient.setSysVarValue("g29", "button_array", button_array)
    print(current_swa, current_gas_pedal, current_brake_pedal, button_array)


def receive_adas_data():
    """ """
    adas_swa_req = canoeClient.getSysVarValue("hil_adas", "wheel_angle_req")
    adas_swa_req_active = canoeClient.getSysVarValue("hil_adas", "latl_req_type")
    return adas_swa_req_active, adas_swa_req


def main_send(controller):
    """
    

    Args:
      controller: 

    Returns:

    """

    #try:
        #clock = pygame.time.Clock()
    start_time = time.time()
    last_time = start_time

    while True:
        current_time = time.time()
        dt = current_time - last_time

        # receive data from ADAS CANoe
        adas_swa_req_active, adas_swa_req = receive_adas_data()

        # Read data from g29
        obj = controller.LogiGetStateENGINES(0)
        controller.logi_update()
        raw_swa = obj.contents.lX  # steering axis
        raw_brake_pedal = obj.contents.lRz  # brake pedal
        raw_gas_pedal = obj.contents.lY  # gas pedal
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

        list = [left_handle, right_handle, triangle, circle, square, cross, plus, minus, enter, l3, l2, r2, r3, start, options, ps]
        button_array = bin(int(''.join(map(str, list)), 2) << 1)
        button_array = int(button_array, 2)

        current_swa = round(map_value(raw_swa, -32768, 32768,-450,450), 3)
        current_brake_pedal = round(map_value(raw_brake_pedal, 32768, -32768, 0, 100), 0)
        current_gas_pedal = round(map_value(raw_gas_pedal, 32768, -32768, 0, 100), 0)

        # Control g29 from ADAS request
        if adas_swa_req_active == 1:
            adas_control_g29(current_swa, adas_swa_req, dt)
        else:
            controller.LogiStopConstantForce(0)

        ## Cyclic sending every 10ms
        send_controller_data(current_swa, current_gas_pedal, current_brake_pedal, button_array)
        last_time = current_time

    #except Exception as e:
    #    print("Runtime error occurred.")
    #    controller.steering_shutdown()
    #    raise e


if __name__ == "__main__":
    # start logidrivepy
    controller = LogitechController()
    steering_initialize = controller.steering_initialize()
    logi_update = controller.logi_update()
    is_connected = controller.is_connected(0)
    print(f"\n---Logitech Controller Test---")
    print(f"steering_initialize: {steering_initialize}")
    print(f"logi_update: {logi_update}")
    print(f"is_connected: {is_connected}")
    main_send(controller)
    controller.steering_shutdown()


