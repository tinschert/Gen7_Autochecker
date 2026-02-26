# -*- coding: utf-8 -*-
# @file Ralo_client_start.py
# @author ADAS_HIL_TEAM
# @date 09-11-2023

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
from threading import Thread
from util import establish_connection
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Control import canoe_client_1

""" vGETK RPYC Server Ver 2.5
    Last Modification 04.09.2023 - Update support of dynamic RALO version"""

def start_measurement(json_file, ralo_version):
    """
    

    Args:
      json_file: 
      ralo_version: 

    Returns:

    """
    c = establish_connection()
    if c is None:
        print("Stopping the measurement!!!")
        com_obj = canoe_client_1.CANoeClient()
        com_obj.write_to_output_window("ERROR: Server is down.Please check if server is running on Datalogger.")
        com_obj.write_to_output_window(fr"ERROR: Copy all files from *\Platform\Classe\Scripts\vGETK_Automation\vGETK_Scripts_Datalogger\ to...")
        com_obj.write_to_output_window("ERROR: ...the Datalogger in D:\\vGETK_Trace\\vGETK_Scripts_Datalogger")
        com_obj.write_to_output_window("ERROR: Run D:\\vGETK_Trace\\vGETK_Scripts_Datalogger\\start_vgetk_rpyc_server.bat")
        com_obj.write_to_output_window("ERROR: Stopping the measurement.")
        com_obj.stopMeasurement()
        com_obj = None
        return
    try:
        version, rl_support = c.root.exposed_server_version(ralo_version)
        if version != "2.5" or rl_support < float(ralo_version):
            print(f"Wrong version of RPYC server is running on Datalogger. Expected version 2.5, found {version}")
            print("Stopping the measurement!!!")
            com_obj = canoe_client_1.CANoeClient()
            com_obj.write_to_output_window("ERROR: Old version of RPYC server/RALO version not available on Datalogger.Please use the latest RPYC server from the Platform repo/update your RALO version.")
            com_obj.write_to_output_window(fr"ERROR: *\Platform\Classe\Scripts\vGETK_Automation\vGETK_Scripts_Datalogger\vgetk_rpyc_server.py")
            com_obj.write_to_output_window("ERROR: Copy all files from *\Platform\Classe\Scripts\vGETK_Automation\vGETK_Scripts_Datalogger\ to...")
            com_obj.write_to_output_window("ERROR: ...the Datalogger in D:\\vGETK_Trace\\vGETK_Scripts_Datalogger")
            com_obj.write_to_output_window("ERROR: Run D:\\vGETK_Trace\\vGETK_Scripts_Datalogger\\start_vgetk_rpyc_server.bat")
            com_obj.write_to_output_window("ERROR: Stopping the measurement.")
            com_obj.stopMeasurement()
            com_obj = None
            print(f"Close client connection to the Datalogger")
            c.close()  # Close connection
            return
        else:
            print(f"Version {version} RPYC server detected with maximum RALO{rl_support} support.")
        status = c.root.exposed_check_file_exist(json_file)
        if status == 0:
            print("Please stop the trace and populate existing json file, then run the trace again.")
            return
        ''' Main sequence to execute'''
        print("Starting Process Manager")
        c.root.exposed_start_processmanager(ralo_version)
        time.sleep(5)
        print("Starting Recorder")
        c.root.exposed_start_recorder(ralo_version)
        time.sleep(5)
        print("Starting Measurement...")
        thread = Thread(target=c.root.exposed_start_mesasurement, args=(json_file, ralo_version))
        thread.start()
        thread.join()
    except Exception as e:
        print(f"Measurement sequence failed --> {e}")
        print(f"Close client connection to the Datalogger")
        c.close()  # Close connection

    finally:
        time.sleep(5)  # Wait all IO operations to finish
        print(f"Close client connection to the Rendering PC")
        c.close()  # Close connection
        del c  # destroy the object


if __name__ == "__main__":
    assert sys.argv[1] != 0, "RALO JSON file is not populated"
    assert sys.argv[2] != 0, "RALO version is not populated"
    start_measurement(sys.argv[1], sys.argv[2])
    




