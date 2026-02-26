# -*- coding: utf-8 -*-
# @file vgetk_rpyc_server.py
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
import sys, os
import subprocess
import time

""" vGETK RPYC Server Ver 2.5
    Last Modification 04.09.2023 - Add function to check the supported RALO version on Datalogger PC"""

class MyService(rpyc.Service):
    """ """

    def on_connect(self, conn):
        """
        

        Args:
          conn: 

        Returns:

        """
        print("Client connected")

    def on_disconnect(self, conn):
        """
        

        Args:
          conn: 

        Returns:

        """
        print("Client disconnected")

    def exposed_redirect(self, stdout):
        """
        

        Args:
          stdout: 

        Returns:

        """
        sys.stdout = stdout
   
    def set_status_in_file(self, path, state):
        """
        

        Args:
          path: 
          state: 

        Returns:

        """
        with open(path, mode='w') as file:
            file.write(state)

    def check_ralo_folder(self, ralo_version: str) -> str:

        """
        Function to check installed RALO versions on Datalogger PC
        arg: RALO version from CANoe system variable (str)
        returns: Last available RALO version on Datalogger PC (str)

        Args:
          ralo_version: str: 

        Returns:

        """

        available_ralo_versions = []
        PATH = r'C:\Program Files\ETAS'
        for ralo_dir in os.scandir(PATH):
            if ralo_dir.is_dir():
                available_ralo_versions.append(float(ralo_dir.path.split("RALO")[-1]))
        print(f"Installed RALO versions on Datalogger PC --> {available_ralo_versions}")
        last_version = max(available_ralo_versions)
        if float(ralo_version) > last_version:
            return f"Max RALO version supported on the Datagaloger is {last_version}.Please update!!!"
        else:
            return last_version

    def exposed_check_file_exist(self, json_file):
        """
        

        Args:
          json_file: 

        Returns:

        """
        folder_path = r'D:\vGETK_Trace\vGETK_Scripts_Datalogger'
        ralo_file = json_file + ".json"
        file_path = os.path.join(folder_path, ralo_file)

        if os.path.exists(file_path):
            return 1
        else:
            self.set_status_in_file(r"D:\vGETK_Trace\vGETK_Scripts_Datalogger\vGETK_status.txt", "3")
            return 0
    
    def exposed_server_version(self, ralo_version):
        """
        

        Args:
          ralo_version: 

        Returns:

        """
        VERSION = "2.5"
        SUPPORTED_RL = self.check_ralo_folder(ralo_version)
        return VERSION, SUPPORTED_RL
    
    def exposed_start_processmanager(self, ralo_version):
        """
        

        Args:
          ralo_version: 

        Returns:

        """
        try:
            print("Starting Process Manager")
            self.set_status_in_file(r"D:\vGETK_Trace\vGETK_Scripts_Datalogger\vGETK_status.txt", "0")
            p = subprocess.Popen(["start", "/MIN", "processmanager.exe", "-i", "M2_"], shell=True,
                                cwd=fr'C:\Program Files\ETAS\RALO{ralo_version}\bin',
                                stdout=sys.stdout) # Start Processmanager.exe
            p.communicate()
        except Exception as e:
            print(f"Starting recorder.exe failed --> {e}")
            self.set_status_in_file(r"D:\vGETK_Trace\vGETK_Scripts_Datalogger\\vGETK_status.txt", "2")

    def exposed_start_recorder(self, ralo_version):
        """
        

        Args:
          ralo_version: 

        Returns:

        """
        try:
            print("Starting Recorder")
            p = subprocess.Popen(["start", "/MIN", "recorder.exe"], shell=True,
                                cwd=fr'C:\Program Files\ETAS\RALO{ralo_version}\bin',
                                stdout=sys.stdout) # Start recorder.exe
            p.communicate()
        except Exception as e:
            print(f"Starting recorder.exe failed --> {e}")
            self.set_status_in_file(r"D:\vGETK_Trace\vGETK_Scripts_Datalogger\vGETK_status.txt", "2")
            
    def exposed_start_mesasurement(self, json_file, ralo_version):
        """
        

        Args:
          json_file: 
          ralo_version: 

        Returns:

        """
        ralo_file = json_file + ".json"
        ver = ralo_version.replace(".", "_")
        try:
            print("Starting Measurement")
            p = subprocess.Popen(["start", "X:\Tools\venv\Scripts\python.exe", "-3.7", f"measurement_control_RALO_{ver}.py", ralo_file, "start"], shell=True,
                                    cwd=r'D:\vGETK_Trace\vGETK_Scripts_Datalogger',
                                    stdout=sys.stdout) # Start measurement with new py script using Py v 3.7
            p.communicate()
            time.sleep(10)
            print("Measurement is starting...")
        except Exception as e:
            print(f"Starting recorder.exe failed --> {e}")
            self.set_status_in_file(r"D:\vGETK_Trace\vGETK_Scripts_Datalogger\vGETK_status.txt", "2")

    def exposed_stop_measurement(self):
        """ """
        print("Stopping the measurement.")
        os.system('taskkill /F /FI "IMAGENAME eq recorder*"')
        time.sleep(1)
        os.system('taskkill /F /FI "IMAGENAME eq LiMaServer*"')
        time.sleep(1)
        os.system('taskkill /F /FI "WINDOWTITLE eq C:\Windows\py.exe"')
        time.sleep(1)
        os.system('taskkill /F /FI "IMAGENAME eq processmanager*"')
        self.set_status_in_file(r"D:\vGETK_Trace\vGETK_Scripts_Datalogger\vGETK_status.txt", "0")

    def exposed_stop_ralo(self, ralo_version):
        """
        

        Args:
          ralo_version: 

        Returns:

        """
        ver = ralo_version.replace(".", "_")
        #if self.check_ralo_is_running():
        p = subprocess.Popen(["X:\Tools\venv\Scripts\python.exe", "-3.7", f"measurement_control_RALO_{ver}.py", "dummy", "stop"], shell=True,
                             cwd=r'D:\vGETK_Trace\vGETK_Scripts_Datalogger',
                             stdout=sys.stdout)  # Stop measurement with new py script using Py v 3.7


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    print("DO NOT CLOSE THIS TERMINAL!!!")
    print("RPYC server is listening on port 18861")
    print("Waiting for client connection")
    t = ThreadedServer(MyService, port=18861)
    t.start()
