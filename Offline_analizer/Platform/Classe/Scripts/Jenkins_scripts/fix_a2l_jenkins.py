# -*- coding: utf-8 -*-
# @file fix_a2l_jenkins.py
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


import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
import canape_stuff
import canape_client
import time
import pyautogui
import fileinput
from logging_config import logger
import argparse

a2l_add_info = """        /begin EVENT
          "STIMSTIM1"
          "STIMSTIM1"
          0x1C
          STIM
          0xFF
          0x01
          0x07
          0x00
        /end EVENT
        /begin EVENT
          "DAQSTIM1"
          "DAQSTIM1"
          0x1B
          DAQ
          0xFF
          0x01
          0x07
          0x00
        /end EVENT\n"""


def fix_a2l(a2l):
    """
    

    Args:
      a2l: 

    Returns:

    """
    searched_row = False
    with open(a2l, 'r+') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if '/end TIMESTAMP_SUPPORTED' in line:
                lines[i] = lines[i] + a2l_add_info
                f.seek(0)
                searched_row = True
        if not searched_row:
            raise ValueError("Missing information in A2L file.Please check the integrity of the A2L")
        else:
            for line in lines:
                f.write(line)

def fix_canape(a2l):
    """
    

    Args:
      a2l: 

    Returns:

    """

    canape_str = "/begin IF_DATA CANAPE_EXT"
    lines_canape = []

    with open(a2l, "r") as f:
        for line_no, line in enumerate(f):
            if canape_str in line:
                lines_canape.append(line_no)
                lines_canape.append(line_no + 1)
                lines_canape.append(line_no + 2)
                lines_canape.append(line_no + 3)
                lines_canape.append(line_no + 4)

    try:
        for line_num, line in enumerate(fileinput.input(a2l, inplace=1)):
            if line_num in lines_canape:
                continue
            else:
                sys.stdout.write(line)
    except Exception as e:
        print(f"Failed due to --> {e}")


def main_sequence(canape_project_path, a2l_path):
    """
    

    Args:
      canape_project_path: 
      a2l_path: 

    Returns:

    """
    
    canape_project_file = canape_project_path
    if canape_project_file is None:
        raise Exception("Missing path to  Canape project file")
    else:
        logger.info(f"Canape project path --> {canape_project_file}")
    canape_ini_path = canape_project_path + '\\canape.ini'

    if a2l_path is None:
        raise Exception("Missing absolute path to customer A2L")
    else:
        logger.info(f"Customer A2L path --> {a2l_path}")

    ecu_name_temp = a2l_path.rsplit(".")[0]
    ecu_name = ecu_name_temp.split(os.sep)[-1]

    screen_size = pyautogui.size()
    if screen_size.height != 1080 or screen_size.width != 1920:
        raise Exception(
            "Incorrect resolution. Please change the bench screen resolution to 1920x1080 in order to use A2L fixer.")

    contents = canape_stuff.read_init(canape_ini_path)
    canape_stuff.modify(ecu_name, contents, canape_ini_path)

    canapeClient = canape_client.CanapeClient()
    canapeClient.open(canape_project_path)
    time.sleep(4)
    ### Vision section ###
    moveToX = 1902
    moveToY = 13
    moveToX_yes = 955
    moveToY_yes = 553
    moveToX_yes_a2l = 955
    moveToY_yes_al2 = 602
    pyautogui.click(x=moveToX, y=moveToY, clicks=2, interval=1, button='left')
    time.sleep(2)
    pyautogui.click(x=moveToX_yes, y=moveToY_yes, clicks=2, interval=1, button='left')
    time.sleep(2)
    pyautogui.click(x=moveToX_yes_a2l, y=moveToY_yes_al2, clicks=2, interval=1, button='left')
    ##### End vision section ####
    time.sleep(60)
    canapeClient = None
    fix_canape(a2l_path)
    fix_a2l(a2l_path)
    pyautogui.alert("Finished fixing of the A2L")


    

    






