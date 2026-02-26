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
import shutil, os
from threading import Thread

shared_path = r"X:\cm_project"
shared_path_local = r"D:\CarMaker_Shared"
shared_path_local_proj = shared_path_local + r"\cm_project"
local_folder = r"D:\CarMaker_Project"

r""" Start CarMaker script
    Last Modification 10.12.2024 - Copy TrafficSigns from X drive to C:\IPG\carmaker\win64-{cm_version}\TrafficSigns\DEU"""

Mapping_script = r'''# Mapping Script
$i=3
while($True){
    $error.clear()
    $MappedDrives = Get-SmbMapping |where -property Status -Value Unavailable -EQ | select LocalPath,RemotePath
    foreach( $MappedDrive in $MappedDrives)
    {
        try {
            New-SmbMapping -LocalPath $MappedDrive.LocalPath -RemotePath $MappedDrive.RemotePath -Persistent $True
        } catch {
            Write-Host "There was an error mapping $MappedDrive.RemotePath to $MappedDrive.LocalPath"
        }
    }
    $i = $i - 1
    if($error.Count -eq 0 -Or $i -eq 0) {break}
 
    Start-Sleep -Seconds 30
}
'''
Startup_script = r'''REM Startup Script
PowerShell -Command "Set-ExecutionPolicy -Scope CurrentUser Unrestricted" >> "%TEMP%\StartupLog.txt" 2>&1
PowerShell -File "%SystemDrive%\Scripts\MapDrives.ps1" >> "%TEMP%\StartupLog.txt" 2>&1
'''
def create_script(file_path, file_type):
    """
    Creates automounting scripts in case they're not available on the RT Rack

    Args:
      file_path: destination path with filename
      file_type: type of script 1 for MapDrives.ps1 and 2 for MapDrives.cmd

    Returns:

    """
    if file_type == 1:
        if not os.path.exists(r"C:\Scripts"):
            os.mkdir(r"C:\Scripts")
        else:
            print("Path exists")
        script_list = [Mapping_script]
        with open(file_path, 'w') as file:
            file.write('\n'.join(script_list))
        print(file_path + ' created successfully.')
    elif file_type == 2:
        script_list = [Startup_script]
        with open(file_path, 'w') as file:
            file.write('\n'.join(script_list))
        print(file_path + ' created successfully.')
        
def check_shared_drive(drive):
    """
    Checks if the network drive is connected and available on the RT Rack
    if not, it will look for the mounting scripts, crate -if needed- and run them.
    After that it checks again and test if files or folders can be created on the drive.

    Args:
      drive: drive letter to be searched i.e. X:

    Returns:

    """
    set_status_in_file(r"D:\UserFiles\Mapped_Drives_Status.txt", "0")
    drive_letter = drive
    os.path.exists(drive_letter) ## Preconnection to avoid false positives
    connection_status = 'Status            OK'
    drives = os.popen(fr'net use {drive_letter}').read()
    if os.path.isfile(r"C:\Scripts\MapDrives.ps1"):
        print('Mapping script available')
    else:
        print('Script not available, will be created') # Mapping files not found, will be created
        create_script(r"C:/Scripts/MapDrives.ps1", 1) # Creates MapDrives.ps1
        create_script(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\MapDrives.cmd", 2) # Creates MapDrives.cmd        
    if connection_status in drives:
        print(f"The network drive {drive_letter} is connected.")
    else:
        try:
            print("Connecting network drives...")
            os.system('PowerShell -NoProfile -ExecutionPolicy Bypass -File "C:\\Scripts\\MapDrives.ps1"')
        except Exception as e:
            print(f"ERROR --> {e}")
            set_status_in_file(r"D:\UserFiles\Mapped_Drives_Status.txt", "2")# Status=2, error flag raised
            raise e
    if os.path.exists(drive_letter): # Final test also creating a folder in order to check writing permissions.
        try:
            os.mkdir(fr"{drive_letter}\Check")
            os.rmdir(fr"{drive_letter}\Check")
            print('Double check OK') 
            set_status_in_file(r"D:\UserFiles\Mapped_Drives_Status.txt", "1")# Status=1, no error
        except Exception as e:
            print(f"ERROR --> {e}")
            set_status_in_file(r"D:\UserFiles\Mapped_Drives_Status.txt", "2")# Status=2, error flag raised
            raise e
    else:
        print('Cannot connect, please check the shared drive at the origin PC!')
        set_status_in_file(r"D:\UserFiles\Mapped_Drives_Status.txt", "2") # Status=2, error flag raised
        raise e
        
def copy_new_files_(src, dst):
    """
    Recursively copy new files from src to dst. Function deprecated but mantained here in case needed.

    Args:
      src:
      dst:

    Returns:

    """
    set_status_in_file(r"X:\cm_status.txt", "0")
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
                    print(rf"Copying {src_item}")
                    shutil.copy2(src_item, dst_item)
    except PermissionError as e:
        print(f"Permission denied --> {e}")
        raise e
    except Exception as e:
        print(f"Failed to copy CarMaker folder --> {e}")
        raise e


def copy_new_files_full(src, dst, sta, cm_version):
    """
    Full copy of the src to dst.

    Args:
      src: Path to the source file
      dst: Destination path

    Returns:
    """
    try:
        set_status_in_file(rf"{sta}\cm_status.txt", "0")
        print("Start copying shared CM Project to local location")
        subprocess.run(rf'robocopy {src} {dst} /W:1 /NP /MIR')
        print(rf"Start copying shared Traffic signs to C:\IPG\carmaker\win64-{cm_version}\TrafficSigns\DEU")
        subprocess.run(rf'robocopy {src}\Data\TrafficSigns C:\IPG\carmaker\win64-{cm_version}\TrafficSigns\DEU /W:1 /NP')
        print("Finished copying")
    except PermissionError as e:
        print(f"Permission denied --> {e}")
        raise e
    except Exception as e:
        print(f"Failed to copy.Error --> {e}")
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
        set_status_in_file(r"X:\cm_status.txt", "0")
        print("Start copying shared CM Project to local location")
        subprocess.run(rf'robocopy {src} {dst} /E /XO /NP')
        print("Finished copying")
    except PermissionError as e:
        print(f"Permission denied --> {e}")
        raise e
    except Exception as e:
        print(f"Failed to copy CarMaker folder --> {e}")
        raise e


def copy_cm_project_rendering(cm_version, status_path):
    """Connect to Rendering PC and create a full local copy of CM project"""
    c = None
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
            print("Server is down.Please check if server is running on Rendering PC")
            print(r"Rendering PC --> D:\CarMakerScripts\start_rpyc_server.bat")
            raise e

        try:
            set_status_in_file(rf"D:\{status_path}\Mapped_Drives_Status_Rendering.txt", "0")
            print("Checking Network Drive Status")
            net_drive_status = c.root.exposed_check_shared_drive("X:")
            if net_drive_status == 1:
                set_status_in_file(rf"D:\{status_path}\Mapped_Drives_Status_Rendering.txt", "1")
                print("Copy CM project locally on Rendering PC")
                c.root.exposed_copy_cm_project_full(shared_path, local_folder, cm_version)
                c.root.exposed_gpu_order(cm_version)
            elif net_drive_status == 2:
                set_status_in_file(rf"D:\{status_path}\Mapped_Drives_Status_Rendering.txt", "2")
        except Exception as e:
            print(f"Copying CM project locally on Rendering PC failed --> {e}")
        finally:
            time.sleep(5)  # Wait all IO operations to finish
            print("Close client connection to the Rendering PC")
            if c is not None:
                c.close()  # Close connection
                del c  # destroy the object


def check_cm_state():
    """Get status of CM.exe process"""
    return "HIL.exe" in (p.name() for p in psutil.process_iter())


def check_ipgmovie_state():
    """Get status of IPG Movie process"""
    return "Movie.exe" in (p.name() for p in psutil.process_iter())


def start_carmaker(dil_mode, cm_version):
    """
    Start CM and IPG Movie

    Args:
      dil_mode: DIL Mode state
      cm_version (str) : Version ot the CM
    Returns:
    """
    # path = Path(__file__).parent / "../../../../adas_sim/cm_project"
    time.sleep(5)

    if not check_cm_state():
        path = r"D:\CarMaker_Project"
        path_mt_simulation = r"D:\CarMaker_Project\src\CarMaker.win64.exe"
        print("Starting CarMaker application.")
        if cm_version.split(".")[0] == "12":
            cm_exe = "CM.exe"
        else:
            cm_exe = "CM_Office.exe"

        subprocess.Popen([cm_exe, "-nosensorstart", "-grabsensors", "-appl", path_mt_simulation, "-start", path],
                             shell=True, cwd=fr'C:\IPG\carmaker\win64-{cm_version}\bin', stdout=sys.stdout)
        
        start_ipgmovie(dil_mode, cm_version)


def start_ipgmovie(dil_mode, cm_version):
    """
    Start IPG Movie

    Args:
      dil_mode: DIL mode state
      cm_version (str) : Version ot the CM
    Returns:

    """
    if not check_ipgmovie_state():
        print("Starting IPG Movie application.")
        if dil_mode == "false":
            p = subprocess.Popen(["Movie.exe"], shell=True, cwd=fr'C:\IPG\carmaker\win64-{cm_version}\GUI', stdout=sys.stdout)
            p.communicate()
        elif dil_mode == "true":
            p = subprocess.Popen(["Movie.exe"], shell=True, cwd=fr'C:\IPG\carmaker\win64-{cm_version}\GUI', stdout=sys.stdout)
            p.communicate()


def set_status_in_file(path, state):
    """
    Set status in 'X:/cm_status.txt or 'D:/UserFiles/Mapped_Drives_Status.txt'

    Args:
      state: State to be written in the status file

    Returns:

    """
    with open(path, mode='w') as file:   
        file.write(state)


def check_status():
    """ Checks if CM and IPG Movie processes are started correctly"""
    set_status_in_file(r"X:\cm_status.txt", "0")
    time.sleep(10)
    if check_cm_state() and check_ipgmovie_state():
        print("CarMaker and IPG Movie applications started.")
        set_status_in_file(r"X:\cm_status.txt", "1")
    else:
        print("Unable to start CarMaker or IPG Movie")
        set_status_in_file(r"X:\cm_status.txt", "2")


if __name__ == "__main__":
    print(f"Start copying shared CM Project to local location")
    if sys.argv[1] == "full_copy":
        check_shared_drive("X:")
        copy_new_files_full(shared_path, local_folder, "X:", sys.argv[4])
    elif sys.argv[1] == "full_copy_local":
        copy_new_files_full(shared_path_local_proj, local_folder, shared_path_local, sys.argv[4])
        set_status_in_file(r"D:\CarMaker_Shared\Mapped_Drives_Status_Rendering.txt", "0")        
    elif sys.argv[1] == "debug_copy":
        check_shared_drive("X:")
        copy_new_files_debug(shared_path, local_folder)
    print(f"Finished copying")
    if sys.argv[2] == "true":
        copy_cm_project_rendering(sys.argv[4], sys.argv[5])
    if sys.argv[1] != "full_copy_local":
        thread = Thread(target=start_carmaker, args=(sys.argv[3], sys.argv[4]))
        thread.start()
        check_status()
        time.sleep(2)
        set_status_in_file(r"X:\cm_status.txt", "0")
        set_status_in_file(r"D:\UserFiles\Mapped_Drives_Status.txt", "0")
