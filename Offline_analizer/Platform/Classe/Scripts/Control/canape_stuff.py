# -*- coding: utf-8 -*-
# @file canape_stuff.py
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


import os

gCurrPyDir = os.getcwd()
gWorkDir = os.path.dirname(gCurrPyDir)


def read_init(canape_ini_path):
    """
    Reads canape ini file from path

    Args:
      canape_ini_path: 

    Returns:

    """
    # canapeini_path = r'C:\Users\HRR1LR\Desktop\RadarFC\Measurement\Canape\canape.INI'
    read_canapeini = open(canape_ini_path, 'r')
    contents = read_canapeini.readlines()
    read_canapeini.close()
    return contents


def modify(device_name, contents, canapeini_path):
    """
    Modify canape ini file based on device name

    Args:
      device_name: ECU name
      contents: What should be modified
      canapeini_path: Path to the canape ini file

    Returns:

    """
    deviceName = device_name  # "RadarFC"
    dict_newlines = {}
    lineNum = 0
    stillInSection = False
    for line in contents:
        if "[" in line:
            if "[Module_" + deviceName + "]" in line:
                stillInSection = True
            else:
                stillInSection = False

        if stillInSection:
            if "ReadOnlyDatabase" in line or "SAVE_ORIGINAL_IF_DATA" in line:
                linestripped = line.strip("\n")
                param, value = linestripped.split("=")
                if value == "1":
                    dict_newlines.update({line.replace("1", "0"): lineNum})
        lineNum += 1

    # Modifying contents
    for key in list(dict_newlines):
        contents[dict_newlines[key]] = key

    write_canapeini = open(canapeini_path, 'w')
    write_canapeini.writelines(contents)
    write_canapeini.close()
