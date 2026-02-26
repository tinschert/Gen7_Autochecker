# -*- coding: utf-8 -*-
# @file copy_cm_project.py
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


import sys, os
from distutils.dir_util import copy_tree
import subprocess
import time
import datetime
import shutil

""" Copy CarMaker Project Script
    Last Modification 30.08.2023 - Robocopy bugs fixed"""
    
def get_local_time():
    """ """
    with open(r"D:\CarMaker_Shared\done.txt", mode='w') as file:
        file.write(datetime.datetime.now().strftime("%H %M %S"))


def set_status_in_file(state):
    """
    

    Args:
      state: 

    Returns:

    """
    with open(r"D:\CarMaker_Shared\done.txt", mode='w') as file:
        file.write(state)


def get_path():
    """ """
    dirname = os.path.realpath(os.path.dirname(__file__))
    main_dir = dirname.split("\\Platform")[0]
    cm_folder = main_dir + "\\adas_sim\\cm_project"
    return cm_folder


def copy_cm_project(path):
    """
    

    Args:
      path: 

    Returns:

    """
    try:
        simout_path = r"D:\CarMaker_Shared\cm_project\simOutput"
        time.sleep(3)   # wait for the file handler to write the rendering pc status value. No wait == Problem in CANoe.
        set_status_in_file("0")  # Set initial value in the text value which for canoe means files still not coped
        print(f"Start copying {path} to shared location")
        # copy_tree(path, r"D:\CarMaker_Shared")
        p = subprocess.run(rf'robocopy {path} D:\CarMaker_Shared\cm_project /W:1 /NP /MIR') #W:1 = waits 1 second for retry, /NP no progress shown /MIR mirrors the folder structure and MUST ALWAYS BE THE LAST ARGUMENT
        # check if the file exists with path.exists()
        if os.path.exists(simout_path):
            shutil.rmtree(simout_path)
            print('SimOutput folder deleted')
        if p.returncode < 8:
            print(f"Finished copying")
            set_status_in_file("1")  # Set value "1" means files are copied
        else:
            set_status_in_file("3")  # Set value "3" means any other error
    except PermissionError as e:
        set_status_in_file("2")  # Set value "2" means error permission denied
        print(f"Permission denied --> {e}")
        raise e
    except Exception as e:
        set_status_in_file("3")  # Set value "3" means any other error
        print(f"Failed to copy CarMaker folder --> {e}")
        raise e


if __name__ == "__main__":
    start_time = time.time()
    path = get_path()
    copy_cm_project(path)
    print(f"CarMaker project is copied for {time.time() - start_time} seconds")
    time.sleep(1)
    set_status_in_file("0")