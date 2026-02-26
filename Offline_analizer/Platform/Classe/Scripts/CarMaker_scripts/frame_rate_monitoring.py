# -*- coding: utf-8 -*-
# @file frame_rate_monitoring.py
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


from movienxapi import Info
from movienxapi.Util import Logger
from movienxapi.Util import apo
import sys

#
# Please place this script in C:\IPG\movienx\win64-12.0\scripts in the rendering PC
#

with open(r"X:\movienx_fps_status.txt", 'w') as file:
    file.write("")

frame_counter = 0
frames_per_log_message = 33
Logger.info(f"Connected host and pid: {apo.get_host()}:{apo.get_pid()}")
Logger.info(f"Apo Data Rate: {apo.get_data_rate()}")


def post_update():
    """ Updates the frame rate every 33ms and print it in the MovieNX window"""
    global frame_counter
    frame_counter += 1
    if frame_counter % frames_per_log_message == 0:
        frame_counter = 0
        Logger.info(f"Current FPS: {Info.get_fps():.2f}")
        if Info.get_fps() < 30:
            with open(r"X:\movienx_fps_status.txt", 'w') as file:
                Logger.error(f"FPS too low --> {Info.get_fps():.2f}")
                file.write("Error")
            if apo.is_connected():
                apo.disconnect()
            else:
                Logger.warning("MovieNX not connected to simulation")