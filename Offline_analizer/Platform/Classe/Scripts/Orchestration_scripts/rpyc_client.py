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
from threading import Thread

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Control import canoe_client_1

""" RPYC Client Ver 2.4
    Last Modification 13.10.2023 - updated for CM 12.0.1"""


def set_status_in_file(state):
    """
    

    Args:
      state: 

    Returns:

    """
    # Write current Rendering PC status in file
    with open(r"D:\CarMaker_Shared\rendering_pc_status.txt", mode='w') as file:
        file.write(state)


def check_connection():
    """ """
    # Set rendering_pc_status.txt to initial value
    set_status_in_file("0")
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
            if version != "2.4":
                print(f"Wrong version of RPYC server is running on Rendering PC. Expected version 2.4, found {version}")
                print(fr"*\Platform\Classe\Scripts\CarMaker_scripts\rpyc_server.py")
                print("Copy rpyc_server.py on Rendering PC in D:\CarMakerScripts")
                print(f"Close client connection to the Rendering PC")
                c.close()  # Close connection
                set_status_in_file("3")
            else:
                print(f"Version {version} RPYC server detected with {cm_support} support.")
                set_status_in_file("1")
        except Exception as e:
            print(f"Server is down.Please check if server is running on Rendering PC")
            print(f"Rendering PC --> D:\CarMakerScripts\start_rpyc_server.bat")
            set_status_in_file("2")
            time.sleep(10)
            raise e
        finally:
            time.sleep(5)  # Wait all IO operations to finish
            print(f"Close client connection to the Rendering PC")
            c.close()  # Close connection
    else:
        print(f"No communication with Rendering PC")
        set_status_in_file("2")


def start_movienx():
    """Connect to Rendering PC and start MovieNX for Front Video"""

    try:
        c = rpyc.connect("192.168.1.15", 18861, config={"allow_public_attrs": True})
        c._config['sync_request_timeout'] = None  # No timeout
        print("Client connected to Rendering PC RPYC server.")
    except Exception as e:
        print(f"Server is down.Please check if server is running on Rendering PC")
        print(f"Rendering PC --> D:\CarMakerScripts\start_rpyc_server.bat")
        set_status_in_file("2")
        time.sleep(10)
        raise e
    try:
        print("Starting MovieNX via RPYC server.")
        thread = Thread(target=c.root.exposed_start_movienx_fvideo)
        thread.start()
    except Exception as e:
        print(f"Starting MovieNX failed --> {e}")

    finally:
        time.sleep(5)  # Wait all IO operations to finish
        print(f"Close client connection to the Rendering PC")
        c.close()  # Close connection
        del c  # destroy the object


def start_movienx_svs():
    """Connect to Rendering PC and start MovieNX for SVS"""
    try:
        c = rpyc.connect("192.168.1.15", 18861, config={"allow_public_attrs": True})
        c._config['sync_request_timeout'] = None  # No timeout
        print("Client connected to Rendering PC RPYC server.")
    except Exception as e:
        print(f"Server is down.Please check if server is running on Rendering PC")
        print(f"Rendering PC --> D:\CarMakerScripts\start_rpyc_server.bat")
        set_status_in_file("2")
        time.sleep(10)
        raise e

    try:
        print("Starting MovieNX for SVS via RPYC server.")
        thread_svs = Thread(target=c.root.exposed_start_movienx_svs)
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

    try:
        c = rpyc.connect("192.168.1.15", 18861, config={"allow_public_attrs": True})
        c._config['sync_request_timeout'] = 10  # No timeout
        if sys.argv[2] == "all_instances":
            print("Stop all instances of MovieNX on Rendering PC")
            c.root.exposed_kill_movienx()
        elif sys.argv[2] == "fvideo":
            print("Stop FVideo MovieNX instance on Rendering PC")
            c.root.exposed_kill_movienx_fvideo()
        elif sys.argv[2] == "svs":
            print("Stop SVS MovieNX instance on Rendering PC")
            c.root.exposed_kill_movienx_svs()
    except Exception as e:
        print(f"Server is down.Please check if server is running on Rendering PC")
        print(f"Rendering PC --> D:\CarMakerScripts\start_rpyc_server.bat")
        set_status_in_file("2")
        raise e
    finally:
        time.sleep(5)  # Wait all IO operations to finish
        print(f"Close client connection to the Rendering PC")
        c.close()  # Close connection
        del c  # destroy the object


if __name__ == "__main__":
    if sys.argv[1] == "movienx_fvideo":
        start_movienx()
    elif sys.argv[1] == "movienx_svs":
        start_movienx_svs()
    elif sys.argv[1] == "terminate_movienx":
        terminate_movienx()
    elif sys.argv[1] == "check_connection":
        check_connection()


