# -*- coding: utf-8 -*-
# @file copy_back.py
# @author ADAS_HIL_TEAM
# @date 10-05-2023

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
from pathlib import Path
import subprocess
import time
import os


def set_status_in_file_x(state) -> None:
    """
    Set the status in X:\copy_back_to_repo_status.txt

    Args:
      state (str): Status that shall be written
    Returns:
    """
    with open(r"X:\copy_back_to_repo_status.txt", mode='w') as file:
        file.write(state)


def set_status_in_file_d(state) -> None:
    """
    Set the status in D:\CarMaker_Shared\copy_back_to_repo_status.txt
    Args:
      state (str): Status that shall be written
    Returns:
    """
    with open(r"D:\CarMaker_Shared\copy_back_to_repo_status.txt", mode='w') as file:
        file.write(state)


def copy_project_back_to_repo():
    """
    Function to copy project back to local repository location
    """
    try:
        set_status_in_file_d("0")
        abs_path = os.path.abspath(__file__) + "..\\..\\..\\..\\..\\..\\"
        dst = os.path.abspath(abs_path + "\\adas_sim\\cm_project")
        print("Project root directory is:", dst)
        p = subprocess.run(rf'robocopy D:\CarMaker_Shared\cm_project {dst} /W:1 /NP /MIR')
        if p.returncode < 8:
            print(f"Finished copying")
            set_status_in_file_d("2")  # Set value "2" means files are copied back to repo
        else:
            set_status_in_file_d("3")  # Set value "3" means any other error
    except Exception as e:
        print(f"Error occurred during copying --> {e}")
        set_status_in_file_d("3")  # Set value "3" means any other error
        time.sleep(10)


def copy_project_back_to_shared():
    """
    Function to copy project back to shared X: drive
    """
    try:
        set_status_in_file_x("0")
        p = subprocess.run(rf'robocopy D:\Carmaker_project X:\cm_project /W:1 /NP /MIR')
        set_status_in_file_x("1")
        if p.returncode < 8:
            print(f"Finished copying")
            set_status_in_file_x("1")  # Set value "1" means files are copied to x
        else:
            set_status_in_file_x("3")  # Set value "3" means any other error
    except Exception as e:
        print(f"Error occurred during copying --> {e}")
        set_status_in_file_x("3")  # Set value "3" means any other error


if __name__ == "__main__":
    if sys.argv[1] == "local":
        copy_project_back_to_repo()
    elif sys.argv[1] == "remote":
        copy_project_back_to_shared()
