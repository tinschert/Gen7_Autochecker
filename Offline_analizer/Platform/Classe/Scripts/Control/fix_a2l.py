# -*- coding: utf-8 -*-
# @file fix_a2l.py
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


import canape_stuff
import canape_client
import time
import pyautogui
import easygui
import os,sys
import fileinput

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


def read_daq_stim_file():
    """ """
    file_name = "events_daq_stim.txt"
    with open(file_name, 'r') as f:
        struct_data = f.read() + "\n"
    return struct_data


def fix_a2l(a2l, daq_struct):
    """
    

    Args:
      a2l: 
      daq_struct: 

    Returns:

    """
    searched_row = False
    with open(a2l, 'r+') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if '/end PROTOCOL_LAYER' in line:
                lines[i] = lines[i] + daq_struct
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


if __name__ == '__main__':
    #pyautogui.screenshot(r"D:\test.png")
    pyautogui.alert("Screen resolution shall be 1920x1080 and remote desktop on full screen")

    canape_project_file = easygui.fileopenbox("Please select Canape project file")
    if canape_project_file is None:
        pyautogui.alert("Canape project file is not selected")
        raise Exception("Missing Canape project file")
    canape_project_path = '\\'.join(canape_project_file.split('\\')[0:-1])
    canape_ini_path = canape_project_path + '\\canape.ini'

    a2l_path = easygui.fileopenbox("Please select the A2L file")
    if a2l_path is None:
        pyautogui.alert("A2L file is not selected")
        raise Exception("Missing A2L file")

    ecu_name_temp = a2l_path.rsplit(".")[0]
    ecu_name = ecu_name_temp.split(os.sep)[-1]

    # parse command line arguments
    # commandLineParser = argparse.ArgumentParser(description='Automated fix of A2L file with Canape.')
    # commandLineParser.add_argument('--canape_ini_path', action="store", dest="canape_ini_path", required=True, help= "Path to canape.INI")
    # commandLineParser.add_argument('--ecu_name', action="store", dest="ecu_name", required=True, help= "Name of the ECU [Example : RadarFC")
    # commandLineParser.add_argument('--canape_prоject_path', action="store", dest="canape_prоject_path", required=True, help= "Absolute path to Canape project folder")
    # arguments = commandLineParser.parse_args()

    screen_size = pyautogui.size()
    if screen_size.height != 1080 or screen_size.width != 1920:
        pyautogui.alert('Please change the screen resolution to 1920x1080 in order to use A2L fixer.')
        raise Exception("Incorrect resolution")

    contents = canape_stuff.read_init(canape_ini_path)
    canape_stuff.modify(ecu_name, contents, canape_ini_path)

    canapeClient = canape_client.CanapeClient()
    canapeClient.open(canape_project_path)
    #canapeClient.load_cna(canape_project_file)
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
    daq_data = read_daq_stim_file()
    fix_a2l(a2l_path, daq_data)
    pyautogui.alert("Finished fixing of the A2L")






