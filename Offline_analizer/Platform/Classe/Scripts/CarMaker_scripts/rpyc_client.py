# -*- coding: utf-8 -*-
# @file rpyc_client.py
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


import rpyc
import time
import subprocess
import sys,os
import psutil
import win32gui
from threading import Thread
try:
    from CarMakerScripts.rpyc_server import create_log_file
except ImportError:
    pass

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

""" RPYC Client Ver 2.17
    Last Modification 06.03.2025 - Bugfix for import and syntax warnings"""


def set_status_in_file(path, state):
    """
    Write status in defined status file

    Args:
      state (str): Status to be written

    Returns:

    """
    # Write current Rendering PC status in file
    with open(path, mode='w') as file:   
        file.write(str(state))

        
def establish_connection(timeout):
    try:
        c = rpyc.connect("192.168.1.15", 18861, config={"allow_public_attrs": True})
        c._config['sync_request_timeout'] = timeout  # No timeout
        print("Client connected to Rendering PC RPYC server.")
        return c
    except Exception as e:
        print(fr"Server is down.Please check if server is running on Rendering PC")
        print(fr"Rendering PC --> D:\CarMakerScripts\start_rpyc_server.bat")
        set_status_in_file(r"D:\CarMaker_Shared\rendering_pc_status.txt", "2")
        time.sleep(5)  # Wait all IO operations to finish
        print(f"Close client connection to the Rendering PC")
        c.close()  # Close connection
        del c  # destroy the object
        raise e


def check_connection():
    """ Check connection with the Rendering PC"""
    # Set rendering_pc_status.txt to initial value
    set_status_in_file(r"D:\CarMaker_Shared\rendering_pc_status.txt", "0")
    # Ping Rendering PC is order to check if its up and running
    RENDERING_PC_HOST = "192.168.1.15"
    result = subprocess.run(f"ping -n 1 -w 1 {RENDERING_PC_HOST}", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    HOST_UP = result.returncode
    if HOST_UP == 0 and "Destination host unreachable" not in result.stdout.decode("latin-1"):
        print("Rendering PC up and running.")
        try:
            c = rpyc.connect("192.168.1.15", 18861, config={"allow_public_attrs": True})
            c._config['sync_request_timeout'] = 10  # No timeout
            version, cm_support = c.root.exposed_server_version()
            if version != "2.17":
                print(fr"Wrong version of RPYC server is running on Rendering PC. Expected version 2.17, found {version}")
                print(r"*\Platform\Classe\Scripts\CarMaker_scripts\rpyc_server.py")
                print(r"Copy rpyc_server.py on Rendering PC in D:\CarMakerScripts")
                print(f"Close client connection to the Rendering PC")
                c.close()  # Close connection
                set_status_in_file(r"D:\CarMaker_Shared\rendering_pc_status.txt", "3")
                ret_code=3
            else:
                print(fr"Version {version} RPYC server detected with {cm_support} support.")
                set_status_in_file(r"D:\CarMaker_Shared\rendering_pc_status.txt", "1")
                ret_code=1
                time.sleep(5)  # Wait all IO operations to finish
                print(f"Close client connection to the Rendering PC")
                c.close()  # Close connection
                del c # destroy the object
        except Exception as e:
            print(fr"Server is down.Please check if server is running on Rendering PC")
            print(fr"Rendering PC --> D:\CarMakerScripts\start_rpyc_server.bat")
            set_status_in_file(r"D:\CarMaker_Shared\rendering_pc_status.txt", "2")
            time.sleep(10)
            ret_code=2
        finally:
            return ret_code
    else:
        print(fr"No communication with Rendering PC")
        set_status_in_file(r"D:\CarMaker_Shared\rendering_pc_status.txt", "2")
        return 2


def start_movienx(cm_version, camera_view, vehicle_variant, host_ip):
    """
    Connect to Rendering PC and start MovieNX for Front Video

    Args:
        cm_version (str): Version of CM
        camera_view (str): Camera View
        vehicle_variant (str) : Vehicle Variant
    """

    c = establish_connection(None)
    try:
        print("Starting MovieNX via RPYC server.")
        thread = Thread(target=c.root.exposed_start_movienx_fvideo, args=(cm_version, camera_view, vehicle_variant, host_ip))
        thread.start()
    except Exception as e:
        print(f"Starting MovieNX failed --> {e}")

    finally:
        time.sleep(5)  # Wait all IO operations to finish
        print(f"Close client connection to the Rendering PC")
        c.close()  # Close connection
        del c  # destroy the object
        
        
def start_movienx_byo(cm_version, camera_view, vehicle_variant):
    """
    Start MovieNX for Front Video on BYO RT Rack

    Args:
        cm_version (str): Version of CM
        camera_view (str): Camera View
        vehicle_variant (str) : Vehicle Variant
    """
    set_status_in_file(r"D:\\UserFiles\\movienx_fvideo_status.txt", "0")
    try:
        os.system(r"RD /S /Q C:\Users\%username%\MovieNX")
        print("Starting MovieNX for FVideo")
        # os.system(r"taskkill /f /im Movie.exe")
        camera = f"{vehicle_variant}_{camera_view}"
        if int(cm_version[0:2]) >= 13:
            subprocess.Popen(["start", "MovieNX.exe", "-apphost", "localhost", "-fullscreen", "-camera", camera], shell=True,
                                 cwd=fr'C:\IPG\movienx\win64-{cm_version}\bin',
                                 stdout=subprocess.PIPE)  # Parameters for Front Video MovieNX
            check_title="Movie NX -"
            time.sleep(20)
            
        else:
            subprocess.Popen(
                ["start", "/MIN", "MovieNX.exe", "-apphost", "localhost", "-fullscreen", "-camera", camera], shell=True,
                cwd=fr'C:\IPG\movienx\win64-{cm_version}\bin',
                stdout=subprocess.PIPE)  # Parameters for Front Video MovieNX
            check_title="MovieNX -"
            time.sleep(15)
        if check_movienx_state() and get_all_windows_titles(check_title):
            print("MovieNX FVideo started.")
            subprocess.run("cm_affinity.bat MovieNX", cwd=r"D:\\UserFiles")

            set_status_in_file(r"D:\\UserFiles\\movienx_fvideo_status.txt", "1")
        else:
            set_status_in_file(r"D:\\UserFiles\\movienx_fvideo_status.txt", "2")
    except Exception as e:
        print(f"MovieNX for Front Video was not started --> {e}")
        set_status_in_file(r"D:\\UserFiles\\movienx_fvideo_status.txt", "2")
        

def start_movienx_single_pc(cm_version, camera_view, vehicle_variant):
    """
    Start MovieNX for Front Video on BYO RT Rack

    Args:
        cm_version (str): Version of CM
        camera_view (str): Camera View
        vehicle_variant (str) : Vehicle Variant
    """
    try:
        
        localpath=os.getcwd()+r"\Platform\Classe\Scripts\CarMaker_scripts"
        set_status_in_file(fr"{localpath}\movienx_fvideo_status.txt", "0") # Resets flag file in local repo 
        os.system(r"RD /S /Q C:\Users\%username%\MovieNX") # Deletes local user MovieNX folder to avoid camera cfg issues
        x=localpath.replace('\\', '\\\\')
        
        print("Starting MovieNX for FVideo")
        #os.system(r"taskkill /f /im Movie.exe")
        camera = f"{vehicle_variant}_{camera_view}"
        if int(cm_version[0:2]) >= 13:
            p = subprocess.Popen(["start", "MovieNX.exe", "-apphost", "localhost", "-fullscreen", "1", "-camera", camera], shell=True,
                             cwd=fr'C:\IPG\movienx\win64-{cm_version}\bin',
                             stdout=subprocess.PIPE)  # Parameters for Front Video MovieNX
            check_title="Movie NX -"
            time.sleep(20)
            
        else:
            p = subprocess.Popen(["start", "/MIN", "MovieNX.exe", "-apphost", "localhost", "-fullscreen", "1", "-camera", camera], shell=True,
                cwd=fr'C:\IPG\movienx\win64-{cm_version}\bin',
                stdout=subprocess.PIPE)  # Parameters for Front Video MovieNX
            check_title="MovieNX -"
            time.sleep(15)

        if check_movienx_state() and get_all_windows_titles(check_title):
            print("MovieNX FVideo started.")
            subprocess.run("cm_affinity.bat MovieNX", cwd=x, shell=True)

            set_status_in_file(fr"{localpath}\movienx_fvideo_status.txt", "1")
        else:
            set_status_in_file(fr"{localpath}\movienx_fvideo_status.txt", "2")
            create_log_file("MovieNX APP unable to start or can't connect to CM HOST.")

    except Exception as e:
        print(fr"MovieNX for Front Video was not started --> {e}")
        localpath = os.getcwd() + r"\Platform\Classe\Scripts\CarMaker_scripts"
        localpath.replace('\\', '\\\\')
        create_log_file(e)
        set_status_in_file(fr"{localpath}\movienx_fvideo_status.txt", "2")

        
def get_all_windows_titles(windows_title):
    """
    Gets the titles of all running windows.
    """
    titles = []

    def callback(hwnd, extra):
        titles.append(win32gui.GetWindowText(hwnd))

    win32gui.EnumWindows(callback, None)
    for title in titles:
        if windows_title in title:
            return True
    return False
        
        
def check_movienx_state() -> bool:
        """ Checks if MovieNX.exe is an active process and returns True or False """

        return "MovieNX.exe" in (p.name() for p in psutil.process_iter())

        
def start_movienx_svs(cm_version, host_ip):
    """
    Connect to Rendering PC and start MovieNX for SVS

    Args:
        cm_version (str): Version of CM
    """

    c = establish_connection(None)
    try:
        print("Starting MovieNX for SVS via RPYC server.")
        thread_svs = Thread(target=c.root.exposed_start_movienx_svs, args=(cm_version, host_ip))
        thread_svs.start()
    except Exception as e:
        print(f"Starting MovieNX failed --> {e}")

    finally:
        time.sleep(5)  # Wait all IO operations to finish
        print(f"Close client connection to the Rendering PC")
        c.close()  # Close connection
        del c  # destroy the object


def terminate_movienx():
    """Connect to Rendering PC and start MovieNX for SVS"""
    set_status_in_file(r"D:\CarMaker_Shared\rendering_pc_status.txt", "0")

    c = establish_connection(10)
    try:
        if sys.argv[2] == "all_instances":
            print("Stop all instances of MovieNX on Rendering PC")
            status_mvnx_fvideo, status_mvnx_svs = c.root.exposed_kill_movienx()
            set_status_in_file(r"D:\CarMaker_Shared\movienx_fvideo_status.txt", status_mvnx_fvideo)
            set_status_in_file(r"D:\CarMaker_Shared\movienx_svs_status.txt", status_mvnx_svs)
        elif sys.argv[2] == "fvideo":
            print("Stop FVideo MovieNX instance on Rendering PC")
            status_mvnx_fvideo = c.root.exposed_kill_movienx_fvideo()
            set_status_in_file(r"D:\CarMaker_Shared\movienx_fvideo_status.txt", status_mvnx_fvideo)
        elif sys.argv[2] == "svs":
            print("Stop SVS MovieNX instance on Rendering PC")
            status_mvnx_svs = c.root.exposed_kill_movienx_svs()
            set_status_in_file(r"D:\CarMaker_Shared\movienx_svs_status.txt", status_mvnx_svs)
    except Exception as e:
        print(e)
        print(f"Server is down.Please check if server is running on Rendering PC")
        print(fr"Rendering PC --> D:\CarMakerScripts\start_rpyc_server.bat")
        set_status_in_file(r"D:\CarMaker_Shared\rendering_pc_status.txt", "2")
        raise e
    finally:
        time.sleep(5)  # Wait all IO operations to finish
        print(f"Close client connection to the Rendering PC")
        c.close()  # Close connection
        del c  # destroy the object


def terminate_movienx_byo():
    """Terminate MovieNX for FVideo on BYO RT Rack"""
    try:
        #os.system(r"taskkill /f /im MovieNX.exe")
        if not check_movienx_state():
            set_status_in_file(r"D:\\UserFiles\\movienx_fvideo_status.txt", "0")
        else:
            set_status_in_file(r"D:\\UserFiles\\movienx_fvideo_status.txt", "3")
    except Exception as e:
        print(e)
        set_status_in_file(r"D:\\UserFiles\\movienx_fvideo_status.txt", "2")
        raise e        

def terminate_movienx_single_pc():
    """Terminate MovieNX for FVideo on BYO RT Rack"""
    try:
        os.system(r"taskkill /f /im MovieNX.exe")
        if not check_movienx_state():
            set_status_in_file(r"D:\CarMaker_Shared\movienx_fvideo_status.txt", "0")
        else:
            set_status_in_file(r"D:\CarMaker_Shared\movienx_fvideo_status.txt", "3")
    except Exception as e:
        print(e)
        set_status_in_file(r"D:\CarMaker_Shared\movienx_fvideo_status.txt", "2")
        raise e  
        
        
def start_custom_app(executable, path):
    """Connect to Rendering PC and start custom app/script"""

    c = establish_connection(None)
    try:
        wrapper = rpyc.async_(c.root.exposed_call_batch_or_exe)
        wrapper(executable, path)
    except Exception as e:
        print(e)
        set_status_in_file(r"D:\CarMaker_Shared\rendering_pc_status.txt", "2")
        time.sleep(10)
        raise e
    finally:
        time.sleep(5)  # Wait all IO operations to finish
        print(f"Close client connection to the Rendering PC")
        c.close()  # Close connection
        del c  # destroy the object


def check_shared_drive(drive):
    """Calls function check_shared_drive on RPYC and sends the Drive to check for. This function is only used when CANoe starts"""
    c = establish_connection(None)
    try:
        print("Check connection of Network Drive on Rendering PC")
        net_drive_status = c.root.exposed_check_shared_drive(drive)
        if net_drive_status == 1:
            print(f"Network Drive {drive} connected")
        elif net_drive_status == 2:
            print(f"Connection check to Network Drive {drive} on Rendering PC failed --> Please check shared drive in source PC:")
            exit(2)            
    except Exception as e:
        print(f"Network-Drive-Check fuction not available.")
        # exit(2)
    finally:
        print("Close client connection to the Rendering PC")
        c.close()  # Close connection
        del c  # destroy the object
    

def copy_rpyc_server_rendering():
    """Connect to Rendering PC and copy rpyc_server.py"""

    RPYC_SERVER_SRC = r"X:\CarMakerScripts"
    RPYC_SERVER_DEST = r"D:\CarMakerScripts"
    c = establish_connection(None)
    try:
        print("Copying CM project locally on Rendering PC")
        c.root.exposed_copy_rpyc_server(RPYC_SERVER_SRC, RPYC_SERVER_DEST)
    except Exception as e:
        print(f"Copying rpyc_server.py on Rendering PC failed --> {e}")
    finally:
        print("Close client connection to the Rendering PC")
        c.close()  # Close connection
        del c  # destroy the object


if __name__ == "__main__":
    if sys.argv[1] == "movienx_fvideo":
        start_movienx(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == "movienx_fvideo_byo":
        start_movienx_byo(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "movienx_fvideo_single_pc":
        start_movienx_single_pc(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "movienx_svs":
        start_movienx_svs(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "terminate_movienx":
        terminate_movienx()
    elif sys.argv[1] == "terminate_movienx_byo":
        terminate_movienx_byo()
    elif sys.argv[1] == "terminate_movienx_single_pc":
        terminate_movienx_single_pc()
    elif sys.argv[1] == "check_connection" and sys.argv[2] != "copy_server":
        check_connection()
    elif sys.argv[1] == "custom_app":
        if sys.argv[2] and sys.argv[3]:
            start_custom_app(sys.argv[2], sys.argv[3])
        else:
            print("Missing positional argument")
    elif sys.argv[1] == "check_connection" and sys.argv[2] == "copy_server":
        ret_value=check_connection()
        if ret_value != 2:
            time.sleep(5)
            check_shared_drive("X:")
            copy_rpyc_server_rendering()
        set_status_in_file(r"D:\CarMaker_Shared\rendering_pc_status.txt", "0") ## check functionality 

