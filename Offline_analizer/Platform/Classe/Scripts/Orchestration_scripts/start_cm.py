# -*- coding: utf-8 -*-
# @file start_cm.py
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


import time
from pathlib import Path
import subprocess
import sys
import psutil
from distutils.dir_util import copy_tree, remove_tree
import distutils.log
import rpyc
import shutil,os
from threading import Thread

shared_path = r"X:\cm_project"
local_folder = r"D:\CarMaker_Project"

""" Start CarMaker script
    Last Modification 13.10.2023 - updated for CM 12.0.1"""

def copy_new_files_(src, dst):
    """
    Recursively copy new files from src to dst. Function deprecated but mantained here in case needed.

    Args:
      src: 
      dst: 

    Returns:

    """
    set_status_in_file("0")
    try:
        if not os.path.exists(dst):
            os.makedirs(dst)

        for item in os.listdir(src):
            src_item = os.path.join(src, item)
            dst_item = os.path.join(dst, item)

            if os.path.isdir(src_item):
                copy_new_files(src_item, dst_item)
            elif os.path.isfile(src_item):
                if not os.path.exists(dst_item) or os.stat(src_item).st_mtime > os.stat(dst_item).st_mtime:
                    print(f"Copying {src_item}")
                    shutil.copy2(src_item, dst_item)
    except PermissionError as e:
        print(f"Permission denied --> {e}")
        raise e
    except Exception as e:
        print(f"Failed to copy CarMaker folder --> {e}")
        raise e


def copy_new_files_full(src, dst):
    """
    Full copy of the src to dst.

    Args:
      src: 
      dst: 

    Returns:

    """
    try:
        set_status_in_file("0")
        print(f"Start copying shared CM Project to local location")
        subprocess.run(rf'robocopy {src} {dst} /W:1 /NP /MIR')
        print(f"Finished copying")
    except PermissionError as e:
        print(f"Permission denied --> {e}")
        raise e
    except Exception as e:
        print(f"Failed to copy CarMaker folder --> {e}")
        raise e

def copy_new_files_debug(src, dst):
    """
    Copy only new/modified files from src to dst. Leaves newer files in dst.

    Args:
      src: 
      dst: 

    Returns:

    """
    try:
        set_status_in_file("0")
        print(f"Start copying shared CM Project to local location")
        subprocess.run(rf'robocopy {src} {dst} /E /XO /NP')
        print(f"Finished copying")
    except PermissionError as e:
        print(f"Permission denied --> {e}")
        raise e
    except Exception as e:
        print(f"Failed to copy CarMaker folder --> {e}")
        raise e

def copy_cm_project_rendering():
    """Connect to Rendering PC and create a full local copy of CM project"""

    RENDERING_PC_HOST = "192.168.1.15"
    result = subprocess.run(f"ping -n 1 {RENDERING_PC_HOST}", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    HOST_UP = result.returncode
    ''' Connect to to the remote python server'''

    if HOST_UP == 0 and "Destination host unreachable" not in result.stdout.decode("latin-1"):
        print("Rendering PC up and running.")
        try:
            c = rpyc.connect("192.168.1.15", 18861, config={"allow_public_attrs": True})
            c._config['sync_request_timeout'] = None  # No timeout
            print("Client connected to Rendering PC RPYC server.")
        except Exception as e:
            print(f"Server is down.Please check if server is running on Rendering PC")
            print(f"Rendering PC --> D:\CarMakerScripts\start_rpyc_server.bat")
            raise e

        try:
            print("Copy CM project locally on Rendering PC")
            c.root.exposed_copy_cm_project_full(shared_path, local_folder)
            c.root.exposed_gpu_order()
        except Exception as e:
            print(f"Copying CM project locally on Rendering PC failed --> {e}")
        finally:
            time.sleep(5)  # Wait all IO operations to finish
            print(f"Close client connection to the Rendering PC")
            c.close()  # Close connection
            del c  # destroy the object


def check_cm_state():
    """Get status of CM.exe process"""
    return "HIL.exe" in (p.name() for p in psutil.process_iter())


def check_ipgmovie_state():
    """Get status of IPG Movie process"""
    return "Movie.exe" in (p.name() for p in psutil.process_iter())


def start_carmaker(dil_mode):
    """
    Start CM and IPG Movie

    Args:
      dil_mode: 

    Returns:

    """
    # path = Path(__file__).parent / "../../../../adas_sim/cm_project"
    time.sleep(5)
    
    if not check_cm_state():
        path = r"D:\CarMaker_Project"
        path_mt_simulation = r"D:\UserFiles\CarMaker.win64.exe"
        print("Starting CarMaker application.")
        p = subprocess.Popen(["CM.exe", "-grabsensors", "-appl", path_mt_simulation,"-start", path], shell=True, cwd=r'C:\IPG\carmaker\win64-12.0.2\bin', stdout=sys.stdout)
        p.communicate()
        start_ipgmovie(dil_mode)


def start_ipgmovie(dil_mode):
    """
    

    Args:
      dil_mode: 

    Returns:

    """
    if not check_ipgmovie_state():
        print("Starting IPG Movie application.")
        if dil_mode == "false":
            p = subprocess.Popen(["Movie.exe"], shell=True, cwd=r'C:\IPG\carmaker\win64-12.0.2\GUI', stdout=sys.stdout)
            p.communicate()
        elif dil_mode == "true":
            p = subprocess.Popen(["Movie.exe"], shell=True, cwd=r'C:\IPG\carmaker\win64-12.0.2\GUI', stdout=sys.stdout)
            p.communicate()



def set_status_in_file(state):
    """
    

    Args:
      state: 

    Returns:

    """
    with open(r"X:\cm_status.txt", mode='w') as file:
        file.write(state)

def check_status():
    """ """
    time.sleep(10)
    if check_cm_state() and check_ipgmovie_state():
        print("CarMaker and IPG Movie applications started.")
        set_status_in_file("1")
    else:
        print("Unable to start CarMaker or IPG Movie")
        set_status_in_file("2")

if __name__ == "__main__":
    print(f"Start copying shared CM Project to local location")
    if sys.argv[1] == "full_copy":
       copy_new_files_full(shared_path,local_folder)
    elif sys.argv[1] == "debug_copy":
       copy_new_files_debug(shared_path,local_folder)
    print(f"Finished copying")
    if sys.argv[2] == "true":
        copy_cm_project_rendering()
    thread = Thread(target=start_carmaker, args=(sys.argv[3],))
    thread.start()
    check_status()
    time.sleep(2)
    set_status_in_file("0")





