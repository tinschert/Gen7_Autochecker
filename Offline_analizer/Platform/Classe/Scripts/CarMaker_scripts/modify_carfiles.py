# -*- coding: utf-8 -*-
# @file modify_carfiles.py
# @author ADAS_HIL_TEAM
# @date 08-31-2023

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


import re
import os, time
import sys
import subprocess
import rpyc_client
import getpass


class CarFileParser:
    """Class to parse CarMaker .car files"""

    def __init__(self):
        self.parsedData = None

        # self.commentPattern = re.compile(r'(#\s+)(.+)')
        self.commentPattern = re.compile(r'(#{1,2}\s+)(.+)')
        self.emptyLinePattern = re.compile(r'^\s*$')
        self.singleLineAssignmentPattern = re.compile(r'^\s*(^[^\s]+)\s*=\s*(.*)\s*$')
        self.multiLineAssignmentPattern = re.compile(r'^\s*(^[^\s]+):\s*$')

        self.cwd = os.getcwd()
        self.carFilesPath = "../../../../../adas_sim/cm_project/Data/Vehicle"
        self.cameraFilePath = r'..\..\..\..\..\adas_sim\cm_project\MovieNX\data\Camera\Camera.cfg'
        self.testCasesPath = r'..\..\..\..\..\adas_sim\cm_project\Data\TestRun'
        self.guiFilePath = r'..\..\..\..\..\adas_sim\cm_project\Data\Config\GUI'

    def parseCarFile(self, carFile):
        """
        Parses a CarMaker .car file

        Args:
          carFile: Car file to be parsed
        Returns:
        """

        self.empty_line = 0
        self.comment = 0
        self.parsedData = dict()

        with open(carFile, 'r') as f:
            line = next(f, None)

            if "#INFOFILE1.1" not in line:
                self.parsedData = None

            line = next(f, None)

            while line:
                commentMatch = self.commentPattern.match(line)
                singleLineMatch = self.singleLineAssignmentPattern.match(line)
                multiLineMatch = self.multiLineAssignmentPattern.match(line)
                emptyLineMatch = self.emptyLinePattern.match(line)

                if commentMatch:
                    self.comment += 1
                    self.parsedData[f"{commentMatch.group(1)}{self.comment}"] = commentMatch.group(2)
                    line = next(f, None)

                elif emptyLineMatch:
                    self.empty_line += 1
                    self.parsedData[f"Empty_line_{self.empty_line}"] = '\n'
                    line = next(f, None)

                elif singleLineMatch:
                    self.parsedData[singleLineMatch.group(1)] = singleLineMatch.group(2)
                    line = next(f, None)

                elif multiLineMatch:
                    self.parsedData[multiLineMatch.group(1)] = list()
                    line = next(f, None)

                    while line and not self.singleLineAssignmentPattern.match(
                            line) and not self.multiLineAssignmentPattern.match(line) and not self.commentPattern.match(
                            line):
                        if not self.commentPattern.match(line) and not self.emptyLinePattern.match(line):
                            self.parsedData[multiLineMatch.group(1)].append(line.strip())

                        line = next(f, None)
                else:
                    line = next(f, None)

    def writeCarFile(self, carFile):
        """
        Writes a new CarMaker .car file from the internally parsed (and maybe modified) car values

        Args:
          carFile: Car file to be written
        Returns:
        """

        if self.parsedData:
            def writeDomain(domainName, file):
                """
                Finds a given domainName in the car file
                Args:
                  domainName: 
                  file:
                Returns:
                """

                if type(self.parsedData[domainName]) is list:
                    # multiline
                    file.write(domainName + ":\n")
                    for item in self.parsedData[domainName]:
                        file.write("\t" + item + "\n")
                else:
                    if "Empty_line_" in domainName:
                        file.write('\n')
                    elif "#" in domainName:
                        file.write(f'{domainName.split(" ")[0]} {self.parsedData[domainName]}\n')
                    elif self.parsedData[domainName]:
                        file.write(f"{domainName} = {self.parsedData[domainName]}\n")
                    else:
                        file.write(f"{domainName} =\n")

            f = open(carFile, "w")
            f.write("#INFOFILE1.1 (UTF-8) - Do not remove this line!\n")
            for domainName in self.parsedData:
                writeDomain(domainName, f)

            f.close()
        else:
            pass

    def findNumberOfSensors(self, carFile):
        """
        Parses the given carfile and finds number of sensors defined
        Args:
          carFile: Car file to be searched
        Returns:
        """

        self.parseCarFile(carFile)
        nSensors = int(self.parsedData['Sensor.N'])

        return nSensors

    def findSVCSensorIDs(self, nSensors):
        """
        Extracts the list of Sensor ID for SVC in the Sensor Instance
        Args:
          nSensors: Number of sensors
        Returns:
        """

        ids = list()
        for i in range(nSensors):
            if "SVC" in self.parsedData['Sensor.{}.name'.format(i)]:
                ids.append(i)

        return ids

    def findRSISensorID(self, nSensors):
        """
        Extracts RSI Sensor ID
        Args:
          nSensors: Number of sensors
        Returns:
        """

        for i in range(nSensors):
            if "RadarTS_RSI" in self.parsedData['Sensor.{}.name'.format(i)]:
                return i
        return None

    def findUSSSensorIDs(self, nSensors):
        """
        Extracts the list of Sensor ID for USS in the Sensor Instance
        Args:
          nSensors: Number of sensors
        Returns:
        """

        ussList = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12"]
        ids = list()
        for i in range(nSensors):
            for j in range(len(ussList)):
                if ussList[j] == self.parsedData[f'Sensor.{i}.name']:
                    if i not in ids:
                        ids.append(i)

        return ids

    def enableSVCSensors(self, outfile):
        """
        Activates the RSI Sensors for VIB

        Args:
          outfile: File where the sensors shall be changed to active

        Returns:
        """

        self.parseCarFile(outfile)

        nSensors = int(self.parsedData['Sensor.N'])

        svcSensorIds = self.findSVCSensorIDs(nSensors)

        if len(svcSensorIds) == 4:
            for i in range(len(svcSensorIds)):
                self.parsedData["Sensor.{}.Active".format(svcSensorIds[i])] = "1"

        self.writeCarFile(outfile)

    def enableUSSSensors(self, outfile):
        """
        Activates the USS Sensors for Multitesters

        Args:
          outfile: 

        Returns:

        """

        self.parseCarFile(outfile)

        nSensors = int(self.parsedData['Sensor.N'])

        ussSensorIds = self.findUSSSensorIDs(nSensors)

        if len(ussSensorIds) == 12:
            for i in range(len(ussSensorIds)):
                self.parsedData["Sensor.{}.Active".format(ussSensorIds[i])] = "1"

        self.writeCarFile(outfile)

    def disableSVCSensors(self, outfile):
        """
        Deactivates the RSI Sensors for VIB

        Args:
          outfile: 

        Returns:

        """

        self.parseCarFile(outfile)

        nSensors = int(self.parsedData['Sensor.N'])

        svcSensorIds = self.findSVCSensorIDs(nSensors)

        if len(svcSensorIds) == 4:
            for i in range(len(svcSensorIds)):
                self.parsedData["Sensor.{}.Active".format(svcSensorIds[i])] = "0"

        self.writeCarFile(outfile)

    def disableUSSSensors(self, outfile):
        """
        Deactivates the USS Sensors for Multitesters

        Args:
          outfile: 

        Returns:

        """

        self.parseCarFile(outfile)

        nSensors = int(self.parsedData['Sensor.N'])

        ussSensorIds = self.findUSSSensorIDs(nSensors)

        if len(ussSensorIds) == 12:
            for i in range(len(ussSensorIds)):
                self.parsedData["Sensor.{}.Active".format(ussSensorIds[i])] = "0"

        self.writeCarFile(outfile)

    def modifyRSISensors(self, outfile: str, gui_file_path: str, state: str):
        """
        Activates/Deactivates the RSI Sensors

        Args:
          outfile: path to the carfile
          state (str): Enable/Disable RSI
          gui_file_path (str): Absolute path to the GUI file
        Returns:
        """

        self.parseCarFile(outfile)
        nSensors = int(self.parsedData['Sensor.N'])
        rsiSensorID = self.findRSISensorID(nSensors)
        if rsiSensorID:
            if state == "1" or state == "2":
                self.parsedData[f"Sensor.{rsiSensorID}.Active"] = "1"
            else:
                self.parsedData[f"Sensor.{rsiSensorID}.Active"] = "0"
            self.writeCarFile(outfile)
                

        # Modify GUI file
        self.parseCarFile(gui_file_path)
        print(gui_file_path)

        if state == "1" or state == "2":
            self.parsedData['GPUParameters.FName'] = "gpuconfig_radar_rsi"
        else:
            self.parsedData['GPUParameters.FName'] = "gpuconfig"
        self.writeCarFile(gui_file_path)

    def get_carfiles(self, path):
        """
        Extracts the list of available carfiles from the given path

        Args:
          path: 

        Returns:

        """

        filesList = []
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                filesList.append(f)

        return filesList

    @classmethod
    def set_status_in_file(cls, state):
        """
        Args:
          state: 

        Returns:

        """
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(r'D:\CarMaker_Shared\cf_modify_done.txt'), exist_ok=True)

            # Open the file and write content
            with open(r"D:\CarMaker_Shared\cf_modify_done.txt", mode='w') as file:
                file.write(state)
                print(f"Setting cf_modify_done.txt to status {state}")

        except FileNotFoundError as e:
            print(r"Error: The file path D:\CarMaker_Shared was not found.")
            raise e
        except PermissionError as e:
            print(r"Error: Permission denied when trying to write to D:\CarMaker_Shared.")
            raise e
        except IsADirectoryError as e:
            print(r"Error: Expected a file but found a directory at D:\CarMaker_Shared.")
            raise e
        except OSError as e:
            print(f"Error: An OS error occurred: {e}")
            cls.set_status_in_file("2")
            raise e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            cls.set_status_in_file("2")
            raise e

    def copy_carmaker_files(self, dil: int = 0):
        """
        Function to copy specific CarMaker files from CustomerPrj to adas_sim
        Args:
            dil (int): DIL mode
        """
        script_path = os.path.abspath(__file__)
        vehicle_files_source = script_path + r'..\..\..\..\..\..\CustomerPrj\CarMaker\cm_project'
        vehicle_files_dest = script_path + r'..\..\..\..\..\..\adas_sim\cm_project'
        camera_conf_source = script_path + r'..\..\..\..\..\..\CustomerPrj\CarMaker\Camera'
        camera_conf_dest = script_path + r'..\..\..\..\..\..\adas_sim\cm_project\MovieNX\data\Camera'
        cm_custom_exe_source = script_path + r'..\..\..\..\..\..\Platform\Carmaker'
        cm_custom_exe_dest = script_path + r'..\..\..\..\..\..\adas_sim\cm_project\src'
        movienx_script_source = script_path + r'..\..\..\..\..\..\Platform\Classe\Scripts\CarMaker_scripts'
        movienx_script_dest = script_path + r'..\..\..\..\..\..\adas_sim\cm_project\MovieNX\scripts'
        dil_movie_source = script_path + r'..\..\..\..\..\..\CustomerPrj\CarMaker\DIL\Movie'
        dil_movie_target = fr'C:\Users\{getpass.getuser()}'
        dil_camera_source = script_path + r'..\..\..\..\..\..\CustomerPrj\CarMaker\DIL\Camera'
        dil_camera_target = script_path + r'..\..\..\..\..\..\adas_sim\cm_project\Movie'

        path_list = {vehicle_files_source: vehicle_files_dest,
                     camera_conf_source: camera_conf_dest,
                     cm_custom_exe_source: cm_custom_exe_dest,
                     movienx_script_source: movienx_script_dest,
                     dil_movie_source: dil_movie_target,
                     dil_camera_source: dil_camera_target
                     }
        try:
            for source, destination in path_list.items():
                print(f"Start copying {os.path.abspath(source)} to shared location")

                if source == cm_custom_exe_source:
                    target_file = "CarMaker.win64.exe"
                elif source == movienx_script_source:
                    target_file = "scene_detection.py"
                elif source == dil_movie_source:
                    if dil == 3:
                        target_file = ".IPGMovieDIL"
                    else:
                        target_file = ".IPGMovie"
                elif source == dil_camera_source:
                    if dil == 3:
                        target_file = "Camera_DIL.cfg"
                    else:
                        target_file = "Camera.cfg"
                else:
                    target_file = ""

                p = subprocess.run(
                    rf'robocopy {source} {destination} {target_file} /W:1 /NP /E /IT')  # W:1 = waits 1 second for retry, /NP no progress shown
                if p.returncode < 8:
                    print(f"Finished copying")
                else:
                    assert "Copying failed"

                if target_file == ".IPGMovieDIL":
                    if os.path.exists(fr"{destination}\.IPGMovie"):
                        os.remove(fr"{destination}\.IPGMovie")
                        os.rename(fr"{destination}\{target_file}", fr"{destination}\.IPGMovie")
                    else:
                        os.rename(fr"{destination}\{target_file}", fr"{destination}\.IPGMovie")
                if target_file == "Camera_DIL.cfg":
                    if os.path.exists(fr"{destination}\Camera.cfg"):
                        os.remove(fr"{destination}\Camera.cfg")
                        os.rename(fr"{destination}\{target_file}", fr"{destination}\Camera.cfg")
                    else:
                        os.rename(fr"{destination}\{target_file}", fr"{destination}\Camera.cfg")


        except PermissionError as e:
            print(f"Permission denied --> {e}")
            raise e
        except Exception as e:
            print(f"Failed to copy CarMaker folder --> {e}")
            raise e
        finally:
            if os.path.exists(fr"{camera_conf_dest}\Camera_default.cfg"):
                os.remove(fr"{camera_conf_dest}\Camera_default.cfg")

    def updateMonitorsID(self, ids, outfile):
        """
        Updates monitor IDs for VIB
        Args:
          ids: list of monitor ids
          outfile:
        Returns:
        """
        ESI_FMC5_4K = ids[0]
        ESI_FMC6_4K = ids[1]
        self.parseCarFile(outfile)
        if ESI_FMC5_4K != -1:
            self.parsedData['SensorCluster.0.CameraRSI.MonitorID'] = str(ESI_FMC5_4K)
        if ESI_FMC6_4K != -1:
            self.parsedData['SensorCluster.1.CameraRSI.MonitorID'] = str(ESI_FMC6_4K)

        self.writeCarFile(outfile)

    def updateVehicleType(self, outfile, vehicle):
        """
        Updates Vehicle type in TestRun file
        Args:
          vehicle (str): vehicle type
          outfile:
        Returns:
        """
        self.parseCarFile(outfile)
        self.parsedData['Vehicle'] = vehicle + ".car"
        self.writeCarFile(outfile)

    ################################ Camera file section ####################################
    def modify_camera_file(self, outfile, camera_directions, camera_rotation):
        """
        Modifies Camera_default.cfg

        Args:
          outfile: Camera_default.cfg file
          camera_directions[0] : X_direciton
          camera_directions[1] : Y_direciton
          camera_directions[2] : Z_direction
          camera_rotation[0] : X_roll
          camera_rotation[1] : Y_pitch
          camera_rotation[2] : Z_yaw
        Returns:
        """

        self.parseCarFile(outfile)

        camera_position = (self.parsedData['Camera.0.Pivot.Offset']).split(" ")
        for i in range(3):
            if int(float(camera_directions[i])) != 0:
                camera_position[i] = camera_directions[i]

        camera_local_rotation = self.parsedData['Camera.0.Placement.LocalRotation'].split(" ")
        for i in range(3):
            if int(float(camera_rotation[i])) != 0:
                camera_local_rotation[i] = camera_rotation[i]

        self.parsedData['Camera.0.Pivot.Offset'] = " ".join(camera_position)
        self.parsedData['Camera.0.Placement.LocalRotation'] = " ".join(camera_local_rotation)

        self.writeCarFile(outfile)

    def carfile_sanity_check(self, carFile):
        # Get the file extension
        _, extension = os.path.splitext(carFile)
        if not extension or extension == '.car':
            with open(carFile, 'r') as f:
                first_line = f.readline().strip()

                if "#INFOFILE1.1" not in first_line:
                    print(f"{carFile} is not a valid CarMaker file.Missing #INFOFILE1.1 on line one!!!")
                    return False
            return True
        return False

def main():
    """ """
    c = None
    carfilesList = []

    parser = CarFileParser()
    parser.copy_carmaker_files(int(sys.argv[9]))

    carfilesPath = parser.cwd + parser.carFilesPath
    absCarfilesPath = os.path.abspath(carfilesPath)
    filesList = parser.get_carfiles(absCarfilesPath)

    cameraFilePath = parser.cwd + parser.cameraFilePath
    absCameraFilePath = os.path.abspath(cameraFilePath)

    guiFilePath = parser.cwd + parser.guiFilePath
    absGuiFilePath = os.path.abspath(guiFilePath)


    try:
        # parser.set_status_in_file("0")  # Set initial value in the text value which for canoe means files still not coped

        #############  Get monitors ID ################

        RENDERING_PC_HOST = "192.168.1.15"
        result = subprocess.run(f"ping -n 1 -w 1 {RENDERING_PC_HOST}", stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        HOST_UP = result.returncode
        if HOST_UP == 0 and "Destination host unreachable" not in result.stdout.decode("latin-1"):
            try:
                c = rpyc_client.establish_connection(None)
                mon_ids = c.root.exposed_get_monitor_ids()
            except Exception as e:
                print("Rendering PC not available")
                mon_ids = [-1, -1]
        else:
            print("Rendering PC not available")
            mon_ids = [-1, -1]

        ###############################################
        for item in filesList:
            carfile = absCarfilesPath + "\\" + item
            if parser.carfile_sanity_check(carfile):
                nSensors = parser.findNumberOfSensors(carfile)
                svcSensorIds = parser.findSVCSensorIDs(nSensors)
                ussSensorIds = parser.findUSSSensorIDs(nSensors)
                parser.updateMonitorsID(mon_ids, carfile)

                if len(svcSensorIds) == 4 or len(ussSensorIds) == 12:
                    carfilesList.append(item)

        for item in carfilesList:
            outfile = absCarfilesPath + "\\" + item
            print(f"Start modification of vehicle file -> {item}")
            if sys.argv[1] == "1":  # SVS
                parser.enableSVCSensors(outfile)
            elif sys.argv[1] == "2" or sys.argv[1] == "0":
                parser.disableSVCSensors(outfile)
            if sys.argv[2] == "1":  # USS
                parser.enableUSSSensors(outfile)
            elif sys.argv[2] == "2" or sys.argv[2] == "0":
                parser.disableUSSSensors(outfile)
            parser.modifyRSISensors(outfile, absGuiFilePath, sys.argv[10])

        camera_directions = sys.argv[3:6]
        camera_rotations = sys.argv[6:9]
        parser.modify_camera_file(absCameraFilePath, camera_directions, camera_rotations)
        print("Camera file modified successfully.")

        # Modify Test Runs Vehicle= property only if vehicle variant is passed as an argument
        if len(sys.argv) == 12: # Check if Vehicle arg was passed
            testCasesPath = parser.cwd + parser.testCasesPath
            absTestCasesPath = os.path.abspath(testCasesPath)

            # List all subdirectories recursively
            directories = [absTestCasesPath]
            for root, dirs, files in os.walk(absTestCasesPath):
                for dir in dirs:
                    directories.append(os.path.join(root, dir))


            for path in directories:
                testCasesList = parser.get_carfiles(path)
                for item in testCasesList:
                    test_run = path + "\\" + item
                    if parser.carfile_sanity_check(test_run):
                        parser.updateVehicleType(test_run, sys.argv[11])
                        print(f"Update Vehicle type to {sys.argv[11]} for test run -> {test_run}")

        parser.set_status_in_file("1")  # Set value "1" means files are copied

    except Exception as e:
        # Set value "3" means any other error
        parser.set_status_in_file("2")
        print(f"General failure --> {e}")
        raise e
    finally:
        time.sleep(5)
        parser.set_status_in_file("0")
        if c is not None:
            c.close()


if __name__ == "__main__":
    main()
