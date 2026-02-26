# -*- coding: utf-8 -*-
# @file logidrivepy_test.py
# @author ADAS_HIL_TEAM
# @date 10-03-2023

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


import sys
sys.path.append('../logidrivepy')
from logidrivepy import LogitechController
import time
import pprint
saturation_percentage = 100
coefficient_percentage = 40

def spin_controller(controller):
    """
    

    Args:
      controller: 

    Returns:

    """
    for i in range(-100, 102, 2):
        controller.LogiPlaySpringForce(0, i, 100, 40)
        controller.logi_update()
        time.sleep(0.1)

def read_engines(controller):
    """
    

    Args:
      controller: 

    Returns:

    """
    controller.logi_update()
    obj = controller.LogiGetStateENGINES(0)
    controller.logi_update()
    a = obj.contents.lX
    print(a)
    time.sleep(0.1)
    controller.logi_update()
    print(obj.contents.lX)
    print("array 0")
    time.sleep(0.1)
    controller.logi_update()
    print(obj.contents.lX)
    print("array 0")
    time.sleep(0.1)
    controller.logi_update()
    print(obj.contents.lX)
    print("array 0")
    time.sleep(0.1)
    controller.logi_update()
    print(obj.contents.lX)
    print("array 0")
    time.sleep(0.1)


def swa_value(controller):
    """
    

    Args:
      controller: 

    Returns:

    """

    print(controller.LogiGetStateENGINES(0))
    controller.logi_update()
    controller.LogiPlaySpringForce(0, -10, saturation_percentage, coefficient_percentage)
    controller.logi_update()
    print("-10")
    time.sleep(5)
    print(controller.LogiGetStateENGINES(0))
    controller.logi_update()
    controller.LogiPlaySpringForce(0, 0, saturation_percentage, coefficient_percentage)
    controller.logi_update()
    print("0")
    time.sleep(5)
    print(controller.LogiGetStateENGINES(0))
    controller.logi_update()
    controller.LogiPlaySpringForce(0, 10, saturation_percentage, coefficient_percentage)
    controller.logi_update()
    print("10")
    time.sleep(5)
    print(controller.LogiGetStateENGINES(0))
    controller.logi_update()
    controller.LogiPlaySpringForce(0, 0, saturation_percentage, coefficient_percentage)
    controller.logi_update()
    print("0")
    time.sleep(5)


def constant_force(controller):
    """
    

    Args:
      controller: 

    Returns:

    """
    controller.logi_update()
    controller.LogiPlayConstantForce(0, 20)
    controller.logi_update()
    #obj = controller.get_state_engines(0)
    #controller.logi_update()
    #print(obj.contents.lFX)
    #print("20")
    time.sleep(3)
    controller.logi_update()
    controller.LogiPlayConstantForce(0, -20)
    controller.logi_update()
    #obj = controller.get_state_engines(0)
    #controller.logi_update()
    #print(obj.contents.lFX)
    print("-20")
    time.sleep(3)
    controller.logi_update()
    controller.LogiPlayConstantForce(0, 30)
    controller.logi_update()
    #obj = controller.get_state_engines(0)
    #controller.logi_update()
    #print(obj.contents.lFX)
    print("30")
    time.sleep(3)
    controller.logi_update()
    controller.LogiPlayConstantForce(0, -30)
    controller.logi_update()
    #obj = controller.get_state_engines(0)
    #controller.logi_update()
    #print(obj.contents.lFX)
    print("-30")
    time.sleep(3)

def spin_test():
    """ """
    controller = LogitechController()
    controller.steering_initialize()
    print("\n---Logitech Spin Test---")
    #spin_controller(controller)
    #swa_value(controller)
    constant_force(controller)
    #read_engines(controller)
    print("Spin test passed.\n")

    controller.steering_shutdown()


if __name__ == "__main__":
    spin_test()
