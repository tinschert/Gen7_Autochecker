# -*- coding: utf-8 -*-
# @file rpyc_server.py
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
import sys, os
import subprocess
import shutil
import psutil
from threading import Thread
import time
import win32gui
import re
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
print(script_dir)
sys.path.append(script_dir)
import get_monitor_mapping


""" MovieNX RPYC Server 2.17
    Last Modification 06.03.2025 - Bugfix for get_monitor_mapping import and syntax warnings"""

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


def create_log_file(message):
    """Create a log file with the current date and time.
    If log_dir doesn't exist, use default_dir."""

    if os.path.exists(r"X:"):
        path = r"X:"
    else:
        path = fr"D:\CarMaker_Shared"

    # Create a log filename with the current datetime
    log_filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log'
    log_file_path = os.path.join(path, log_filename)

    """Write a log message to the specified log file."""
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


class MyService(rpyc.Service):
    """ Custom class which inherits from RPYC main class """

    def on_connect(self, conn: object) -> None:
        """
        Prints "Client connected" in the stdout when new client is connected to the sever

        Args:
          conn (object): Connection object
        Returns:
          None
        """
        print("Client connected")

    def on_disconnect(self, conn: object) -> None:
        """
        Prints "Client disconnected" in the stdout when client is being disconnected from the sever

        Args:
          conn (object): Connection object
        Returns:
          None
        """

        print("Client disconnected")

    def exposed_redirect(self, stdout) -> None:
        """
        Redirects server stdout to the client stdout

        Args:
          stdout:
        Returns:
          None
        """
        sys.stdout = stdout

    def callback(self, hwnd, extra):
        """
        Currently deprecated

        Args:
          hwnd: 
          extra:
        Returns:
          None
        """
        if win32gui.IsWindowVisible(hwnd):
            print(f"window text: '{win32gui.GetWindowText(hwnd)}'")

    def exposed_server_version(self) -> tuple:
        """
        Returns manually added version of RPYC server and CarMaker

        Args:
        Returns:
          tuple: Version of Rpyc server and CarMaker
        """

        VERSION = "2.17"
        SUPPORTED_CM = "CM 12.0.2 & CM 13.1.2"
        return VERSION, SUPPORTED_CM

    def get_all_windows_titles(self, windows_title):
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

    def check_mvnx_state(self):
        """Get status of MovieNX.exe process"""
        return "MovieNX.exe" in (p.name() for p in psutil.process_iter())
    
    def set_status_in_file(self, path: str, state: str) -> None:
        """
        Write status flag in the file with the provided path

        Args:
          path (str): Path to the status file
          state (str): Status to be written in the file

        Returns:
            None
        """
        with open(path, mode='w') as file:
            file.write(state)

    def create_script(self, file_path, file_type):
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
            
    def exposed_check_shared_drive(self, drive):
        """
        Checks if the network drive is connected and available on the Rendering PC
        if not, it will look for the mounting scripts, crate -if needed- and run them.
        After that it checks again and test if files or folders can be created on the drive.

        Args:
          drive: drive letter to be searched i.e. X:

        Returns:

        """
        drive_letter = drive
        os.path.exists(drive_letter) ## Preconnection to avoid false positives
        connection_status = 'Status            OK'
        drives = os.popen(fr'net use {drive_letter}').read()
        if os.path.isfile("C:\\Scripts\\MapDrives.ps1"):
            print('Mapping script available')
        else:
            print('Script not available, will be created') # Mapping files not found, will be created
            self.create_script(r"C:/Scripts/MapDrives.ps1", 1) # Creates MapDrives.ps1
            self.create_script(r"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\StartUp\\MapDrives.cmd", 2) # Creates MapDrives.cmd
        if connection_status in drives:
            print(f"The network drive {drive_letter} is connected.")
        else:
            try:
                print("Connecting network drives...")
                os.system('PowerShell -NoProfile -ExecutionPolicy Bypass -File "C:\\Scripts\\MapDrives.ps1"')
            except Exception as e:
                print(f"ERROR --> {e}")
                return 2
        if os.path.exists(drive_letter): # Final test also creating a folder in order to check writing permissions.
            try:
                os.mkdir(fr"{drive_letter}\Check")
                os.rmdir(fr"{drive_letter}\Check")
                print('Double check OK')
                return 1        
            except Exception as e:
                print(f"ERROR --> {e}")
                return 2
        else:
            print('Cannot connect, please check the shared drive at the origin PC!')
            return 2

    def exposed_kill_movienx(self) -> tuple:
        """ Terminates All MovieNX instances on Rendering PC and write status in the status file"""
        if self.check_mvnx_state():
            print("Terminate all MovieNx instances")
            try:
                os.system("taskkill /f /im  MovieNX.exe")
                return 0, 0
            except Exception as e:
                print(f"ERROR --> {e}")
                return 3, 3
        else:
            return 0, 0

    def exposed_kill_movienx_fvideo(self) -> None:
        """ Terminates FVideo MovieNX instance on Rendering PC and write status in the status file"""
        if self.check_mvnx_state():
            print("Terminate Front Video MovieNX instance")
            try:
                os.system('taskkill /f /fi "WINDOWTITLE eq Movie NX -*"')
                os.system('taskkill /f /fi "WINDOWTITLE eq Movie NX 1*"')
                os.system('taskkill /f /fi "WINDOWTITLE eq MovieNX -*"')
                os.system('taskkill /f /fi "WINDOWTITLE eq MovieNX 1*"')
                return 0
            except Exception as e:
                print(f"ERROR --> {e}")
                return 3
        else:
            return 0      

    def exposed_kill_movienx_svs(self) -> None:
        """ Terminates SVS MovieNX instance on Rendering PC and write status in the status file """
        if self.check_mvnx_state():
            print("Terminate SVS MovieNX instance")
            try:
                os.system('taskkill /f /fi "WINDOWTITLE eq Movie NX GPUSensor*"')
                os.system('taskkill /f /fi "WINDOWTITLE eq Movie NX 1*"')
                os.system('taskkill /f /fi "WINDOWTITLE eq MovieNX GPUSensor*"')
                os.system('taskkill /f /fi "WINDOWTITLE eq MovieNX 1*"')
                return 0
            except Exception as e:
                print(f"ERROR --> {e}")
                return 3
        else:
            return 0
            
    def check_movienx_state(self) -> bool:
        """ Checks if MovieNX.exe is an active process and returns True or False """

        return "MovieNX.exe" in (p.name() for p in psutil.process_iter())

    def exposed_gpu_order(self, cm_version) -> None:
        """ Extract GPU order and write a file with the received output"""

        try:
            print("Checking GPU ID Order")
            p = subprocess.Popen(["MovieNX.exe", "-listdevices", ">", "X:\\gpu_order.txt"], shell=True,
                                 cwd=fr'C:\IPG\movienx\win64-{cm_version}\bin',
                                 stdout=subprocess.PIPE)  # Parameters for Front Video MovieNX
            p.communicate()
            print("GPU ID order extracted")
        except Exception as e:
            print(f"MovieNX for Front Video was not started --> {e}")
            create_log_file(e)
            self.set_status_in_file(r"X:\movienx_fvideo_status.txt", "2")

    def parse_gpu_ids(self) -> list:
        """
        Perform a search in 'gpu_order.txt' to extract NVIDIA GeForce RTX IDs
        Args:
        Returns:
            list: list of IDs
        """

        gpus = 0
        args = []
        GPU = "NVIDIA GeForce RTX"
        with open(r"X:\gpu_order.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if GPU in line and gpus < 2:
                    gpus += 1
                    pattern = r"(#\d)"
                    matches = re.findall(pattern, line)
                    for match in matches:
                        args.append(match[1])
        return args

    def movie_nx_execute(self, cm_version, camera_view, vehicle_variant, host_ip) -> None:
        """ Starts MovieNX for FVideo"""

        try:
            os.system(r"RD /S /Q C:\Users\%username%\MovieNX")
            print("Starting MovieNX for FVideo")
            camera = f"{vehicle_variant}_{camera_view}"
            subprocess.Popen(["start", "MovieNX.exe", "-apphost", host_ip, "-fullscreen", "-camera", camera], shell=True,
                                 cwd=fr'C:\IPG\movienx\win64-{cm_version}\bin',
                                 stdout=subprocess.PIPE)  # Parameters for Front Video MovieNX
        except Exception as e:
            print(f"MovieNX for Front Video was not started --> {e}")
            create_log_file(e)
            self.set_status_in_file(r"X:\movienx_fvideo_status.txt", "2")

    def rsi_sensors_execute(self, cm_version, host_ip) -> None:
        """ Starts MovieNX for SVS"""

        try:
            args = self.parse_gpu_ids()
            if len(args) != 2:
                self.set_status_in_file(r"X:\movienx_svs_status.txt", "2")
                raise ValueError("Two Nvidia Cards expected!!!")
                
            print("Starting MovieNX for SVS") # GPU ID must be variables
            subprocess.Popen(["start", "/MIN", "MovieNX.exe", "-gpusensor", "-instance", "1", "-directxdevice", args[0], "-apphost", host_ip], shell=True,
                                 cwd=fr'C:\IPG\movienx\win64-{cm_version}\bin',
                                 stdout=subprocess.PIPE)  # Parameters for NRC Cluster 1 MovieNX
            subprocess.Popen(["start", "/MIN", "MovieNX.exe", "-gpusensor", "-instance", "2", "-directxdevice", args[1], "-apphost", host_ip], shell=True,
                                 cwd=fr'C:\IPG\movienx\win64-{cm_version}\bin',
                                 stdout=subprocess.PIPE)  # Parameters for NRC Cluster 2 MovieNX
        except Exception as e:
            print(f"MovieNX for SVS was not started --> {e}")
            create_log_file(e)
            self.set_status_in_file(r"X:\movienx_svs_status.txt", "2")

    def exposed_copy_cm_project_old(self, src, dst):
        """
        Recursively copy new files from src to dst. Function deprecated after using Robocopy

        Args:
          src: 
          dst:

        Returns:

        """
        print("Start copying from shared drive to local drive.")
        self.set_status_in_file(r"X:\movienx_fvideo_status.txt", "0")
        self.set_status_in_file(r"X:\movienx_svs_status.txt", "0")
        try:
            if not os.path.exists(dst):
                os.makedirs(dst)

            for item in os.listdir(src):
                src_item = os.path.join(src, item)
                dst_item = os.path.join(dst, item)

                if os.path.isdir(src_item):
                    self.exposed_copy_cm_project(src_item, dst_item)
                elif os.path.isfile(src_item):
                    if not os.path.exists(dst_item) or os.stat(src_item).st_mtime > os.stat(dst_item).st_mtime:
                        print(f"Copying {src_item}")
                        shutil.copy2(src_item, dst_item)
            print("Copying finished.")
            self.copy_movienx_cfg()
        except PermissionError as e:
            print(f"Permission denied --> {e}")
            raise e
        except Exception as e:
            print(f"Failed to copy CarMaker folder --> {e}")
            raise e

    def exposed_copy_cm_project_inc(self, src: str, dst: str) -> None:
        """
        Copy only new/modified files from src to dst. Leaves newer files in dst.

        Args:
          src: Path to the source dir
          dst: Path to the destination dir
        Returns:
          None
        """

        try:
            print("Start copying from shared drive to local drive.")
            self.set_status_in_file(r"X:\movienx_fvideo_status.txt", "0")
            self.set_status_in_file(r"X:\movienx_svs_status.txt", "0")
            # remove_tree(dst)
            print(f"Start copying shared CM Project to local location")
            subprocess.run(rf'robocopy {src} {dst} /E /XO /NP')
            print(f"Finished copying")
        except PermissionError as e:
            print(f"Permission denied --> {e}")
            raise e
        except Exception as e:
            print(f"Failed to copy CarMaker folder --> {e}")
            raise e

    def exposed_copy_cm_project_full(self, src: str, dst: str, cm_version: str) -> None:
        """
        Full copy of the src to dst.

        Args:
          src (str): Path to the source dir
          dst (str): Path to the destination dir
          cm_version (str): CM version
        Returns:
          None
        """

        try:
            print("Start copying from shared drive to local drive.")
            self.set_status_in_file(r"X:\movienx_fvideo_status.txt", "0")
            self.set_status_in_file(r"X:\movienx_svs_status.txt", "0")
            # remove_tree(dst)
            print(fr"Start copying shared CM Project to local location")
            subprocess.run(rf'robocopy {src} {dst} /W:1 /NP /MIR')
            print(fr"Start copying shared Traffic signs to C:\IPG\carmaker\win64-{cm_version}\TrafficSigns\DEU")
            subprocess.run(rf'robocopy {src}\Data\TrafficSigns C:\IPG\carmaker\win64-{cm_version}\TrafficSigns\DEU /W:1 /NP')
            print(fr"Finished copying")
        except PermissionError as e:
            print(fr"Permission denied --> {e}")
            raise e
        except Exception as e:
            print(fr"Failed to copy CarMaker folder --> {e}")
            raise e

    def exposed_copy_rpyc_server(self, src: str, dst: str) -> None:
        r"""
        Copy rpyc_server.py for X: to D:\CarMaker_Scripts
    
        Args:
          src (str): Path to the source dir
          dst (str): Path to the destination dir
        Returns:
          None
        """
    
        try:
            print(r"Start copying rpyc_server from X: drive to D:\CarMakerScripts.")
            subprocess.run(rf'robocopy {src} {dst} /W:1 /NP /MIR /XX')
            print(f"Finished copying")
        except PermissionError as e:
            print(f"Permission denied --> {e}")
            raise e
        except Exception as e:
            print(f"Failed to copy rpyc_server.py --> {e}")
            raise e

    def copy_movienx_cfg(self, cm_version) -> None:
        """ Copy Camera_default.cfg from projct to MovieNX folder"""

        src = r"D:\CarMaker_Project\CANoe_Test\MovieNX\data\Camera\Camera_default.cfg"
        dst = fr"C:\IPG\movienx\win64-{cm_version}\data\Camera\Camera_default.cfg"
        try:
            print(f"Copy MovieNX Camera config file.")
            shutil.copy2(src, dst)
            print(f"Finished copying")
        except PermissionError as e:
            print(f"Permission denied --> {e}")
            raise e
        except Exception as e:
            print(f"Failed to copy MovieNX camera config file --> {e}")
            raise e

    def exposed_start_movienx_fvideo(self, cm_version, camera_view, vehicle_variant, host_ip) -> None:
        """ Exposed to the client function to start MovieNX for FVideo """

        thread2 = Thread(target=self.movie_nx_execute, args=(cm_version, camera_view, vehicle_variant, host_ip))
        thread2.start()
        if int(cm_version[0:2]) >= 13:
            check_title="Movie NX -"
            time.sleep(30)
        else:
            check_title="MovieNX -"
            time.sleep(20)
        if self.check_movienx_state() and self.get_all_windows_titles(check_title):
            print("MovieNX FVideo started.")

            self.set_status_in_file(r"X:\movienx_fvideo_status.txt", "1")
        else:
            self.set_status_in_file(r"X:\movienx_fvideo_status.txt", "2")
            create_log_file("MovieNX APP unable to start or can't connect to CM HOST.")

    def exposed_start_movienx_svs(self, cm_version, host_ip) -> None:
        """ Exposed to the client function to start MovieNX for SVS """

        thread = Thread(target=self.rsi_sensors_execute, args=(cm_version, host_ip))
        thread.start()
        if int(cm_version[0:2]) >= 13:
            check_title="Movie NX GPU Sensor"
            time.sleep(20)
        else:
            check_title="MovieNX GPUSensor"
            time.sleep(15)
        if self.check_movienx_state() and self.get_all_windows_titles(fr"{check_title} #1") and self.get_all_windows_titles(fr"{check_title} #2"):
            print("MovieNX SVS started.")
            self.set_status_in_file(r"X:\movienx_svs_status.txt", "1")
        else:
            self.set_status_in_file(r"X:\movienx_svs_status.txt", "2")
            create_log_file("MovieNX APP SVS unable to start or can't connect to CM HOST.")


    def exposed_mount_network_drive(self, hostname):
        """
        Deprecated

        Args:
          hostname:
        Returns:

        """
        # Disconnect anything on X
        subprocess.call(r'net use x: /del', shell=True)
        # Connect to shared drive, use drive letter X
        subprocess.call(fr'net use x: \\{hostname}\ADAS_Project', shell=True)

    def exposed_clear_log(self, log_path):
        """
        Deprecated

        Args:
          log_path: 

        Returns:
        """
        file = open(log_path + r"\Platform\Classe\Scripts\Git_sync_tool\Debug.log", "r+")
        file.truncate(0)
        file.close()

    def exposed_read_log(self, log_path):
        """
        Deprecated
        Args:
          log_path:
        Returns:
        """
        file = open(log_path + r"\Platform\Classe\Scripts\Git_sync_tool\Debug.log", 'r')
        print(file.read())
        file.close()


    def exposed_call_batch_or_exe(self, executable: str, path: str) -> bytes:
        """
        Executes any exe or batch file on the server side

        Args:
          executable (str): Batch/Exe file to execute
          path (str): Path to the file
        Returns:
        bytes: Returns back to the client the stdout in case of error
        """
        process = subprocess.run(f"{executable}", stdout=subprocess.PIPE, cwd=path, stderr=subprocess.STDOUT,
                                 shell=True)
        if process.returncode != 0:
            return process.stdout

    def exposed_get_monitor_ids(self):
        """
        Get monitors mapping on Rendering PC

        Args:
        Returns:
        dict: Returns key value pairs (Monitor: ID)
        """
        mon_ids = get_monitor_mapping.get_esi_monitor_mapping().values()
        return list(mon_ids)


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    print("DO NOT CLOSE THIS TERMINAL!!!")
    print("RPYC server is listening on port 18861")
    print("Waiting for client connection")
    t = ThreadedServer(MyService, port=18861)
    t.start()
