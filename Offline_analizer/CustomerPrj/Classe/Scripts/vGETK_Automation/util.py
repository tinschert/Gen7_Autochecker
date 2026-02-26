# -*- coding: utf-8 -*-
# @file util.py
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


import rpyc
import subprocess

def establish_connection():
    """ """
    DATALOGER_PC_HOST = "192.168.0.25"
    result = subprocess.run(f"ping -n 1 {DATALOGER_PC_HOST}", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    HOST_UP = result.returncode
    ''' Connecto to the remote python server'''

    if HOST_UP == 0:
        try:
            conn = rpyc.connect(DATALOGER_PC_HOST, 18861, config={"allow_public_attrs": True})
            conn._config['sync_request_timeout'] = None  # No timeout
        except Exception as e:
            print(f"Server is down.Please check if server is running on Dataloger")
            print(f"Copy all files from *\Platform\Classe\Scripts\vGETK_Automation\vGETK_Scripts_Datalogger\ to...")
            print(f"...the Datalogger in D:\\vGETK_Trace\\vGETK_Scripts_Datalogger")
            print(f"Run D:\\vGETK_Trace\\vGETK_Scripts_Datalogger\\start_vgetk_rpyc_server.bat")
            return None
        return conn