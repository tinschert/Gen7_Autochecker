# -*- coding: utf-8 -*-
# @file logitec.py
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


import sys
sys.path.append('../logidrivepy')
from logidrivepy import LogitechController


def run_test():
    """ """
    controller = LogitechController()

    steering_initialize = controller.steering_initialize()
    logi_update = controller.logi_update()
    is_connected = controller.is_connected(0)

    print(f"\n---Logitech Controller Test---")
    print(f"steering_initialize: {steering_initialize}")
    print(f"logi_update: {logi_update}")
    print(f"is_connected: {is_connected}")

    if steering_initialize and logi_update and is_connected:
        print(f"All tests passed.\n")
    else:
        print(f"Did not pass all tests.\n")

    controller.logi_update()
    obj = controller.LogiGetStateENGINES(0)
    controller.logi_update()
    a = obj.contents.lX
    print(a)

    controller.steering_shutdown()


if __name__ == "__main__":
    run_test()