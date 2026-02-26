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


import argparse
import re
import os
import sys

class CarFileParser:
    """Class to parse CarMaker .car files"""

    def __init__(self):
        self.parsedData = None

        self.commentPattern = re.compile(r'^\s*#.*\s*$')
        self.emptyLinePattern = re.compile(r'^\s*$')
        self.singleLineAssignmentPattern = re.compile(r'^\s*(^[^\s]+)\s*=\s*(.*)\s*$')
        self.multiLineAssignmentPattern = re.compile(r'^\s*(^[^\s]+):\s*$')

        self.cwd = os.getcwd()
        self.carFilesPath = "../../../../../adas_sim/cm_project/Data/Vehicle"

    def parseCarFile(self, carFile):
        """
        Parses a CarMaker .car file

        Args:
          carFile: 

        Returns:

        """

        self.parsedData = dict()

        with open(carFile, 'r') as f:
            line = next(f,None)

            if not "#INFOFILE1.1" in line:
                self.parsedData = None
                raise Exception("No #INFOFILE1.1 in carfile {}".format(carFile))

            line = next(f,None)

            while line:
                commentMatch = self.commentPattern.match(line)
                singleLineMatch = self.singleLineAssignmentPattern.match(line)
                multiLineMatch = self.multiLineAssignmentPattern.match(line)
                emptyLineMatch = self.emptyLinePattern.match(line)

                if commentMatch or emptyLineMatch:
                    line = next(f,None)

                elif singleLineMatch:
                    self.parsedData[singleLineMatch.group(1)] = singleLineMatch.group(2)
                    line = next(f,None)
                
                elif multiLineMatch:
                    self.parsedData[multiLineMatch.group(1)] = list()
                    line = next(f,None)
                    
                    while line and not self.singleLineAssignmentPattern.match(line) and not self.multiLineAssignmentPattern.match(line):
                        if not self.commentPattern.match(line) and not self.emptyLinePattern.match(line):
                            self.parsedData[multiLineMatch.group(1)].append(line.strip())

                        line = next(f,None)
                else:
                    line = next(f,None)
        
    def writeCarFile(self, carFile):
        """
        Writes a new CarMaker .car file from the internally parsed (and maybe modified) car values

        Args:
          carFile: 

        Returns:

        """

        if self.parsedData:
            def writeDomain(domainName, file):
                """
                

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
                    # singleline
                    file.write(domainName + " = " + self.parsedData[domainName] + "\n")

            f = open(carFile, "w")
            f.write("#INFOFILE1.1 - Do not remove this line!\n")
            for domainName in self.parsedData:
                writeDomain(domainName, f)

            f.close()
        else:
            pass

    def findNumberOfSensors(self, carFile):
        """
        Parses the given carfile and finds number of sensors defined

        Args:
          carFile: 

        Returns:

        """

        self.parseCarFile(carFile)
        nSensors = int(self.parsedData['Sensor.N'])

        return nSensors
    
    def findSVCSensorIDs(self,nSensors):
        """
        Extracts the list of Sensor ID for SVC in the Sensor Instance

        Args:
          nSensors: 

        Returns:

        """

        ids = list()
        for i in range(nSensors):
            if("SVC" in self.parsedData['Sensor.{}.name'.format(i)]):
                ids.append(i)
        
        return ids

    def findUSSSensorIDs(self,nSensors):
        """
        Extracts the list of Sensor ID for USS in the Sensor Instance

        Args:
          nSensors: 

        Returns:

        """
        
        ussList = ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10","S11","S12"]
        ids = list()
        for i in range(nSensors):
            for j in range(len(ussList)):
                if(ussList[j] in self.parsedData['Sensor.{}.name'.format(i)]):
                    if i not in ids:
                        ids.append(i)
        
        return ids

    def enableSVCSensors(self, outfile):
        """
        Activates the RSI Sensors for VIB

        Args:
          outfile: 

        Returns:

        """

        self.parseCarFile(outfile)

        nSensors = int(self.parsedData['Sensor.N'])

        svcSensorIds = self.findSVCSensorIDs(nSensors)

        if(len(svcSensorIds) == 4):
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

        if(len(ussSensorIds) == 12):
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

        if(len(svcSensorIds) == 4):
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

        if(len(ussSensorIds) == 12):
            for i in range(len(ussSensorIds)):
                self.parsedData["Sensor.{}.Active".format(ussSensorIds[i])] = "0"

        self.writeCarFile(outfile)
    
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
    
    def set_status_in_file(self, state):
        """
        

        Args:
          state: 

        Returns:

        """

        with open(r"D:\CarMaker_Shared\cf_modify_done.txt", mode='w') as file:
            file.write(state)

def main():
    """ """
    
    carfilesList = []

    parser = CarFileParser()
    
    carfilesPath = parser.cwd + parser.carFilesPath
    absCarfilesPath = os.path.abspath(carfilesPath)

    filesList= parser.get_carfiles(absCarfilesPath)
    try:
        parser.set_status_in_file("0")  # Set initial value in the text value which for canoe means files still not coped
        for item in filesList:
            carfile = absCarfilesPath + "\\" + item
            nSensors = parser.findNumberOfSensors(carfile)
            svcSensorIds = parser.findSVCSensorIDs(nSensors)
            ussSensorIds = parser.findUSSSensorIDs(nSensors)

            if(len(svcSensorIds) == 4 or len(ussSensorIds) == 12):
                carfilesList.append(item)

        for item in carfilesList:
            outfile = absCarfilesPath + "\\" + item
            
            if sys.argv[1] == "1": #SVS
                parser.enableSVCSensors(outfile)
            elif sys.argv[1] == "2" or sys.argv[1] == "0":
                parser.disableSVCSensors(outfile)
            if sys.argv[2] == "1": # USS
                parser.enableUSSSensors(outfile)
            elif sys.argv[2] == "2" or sys.argv[2] == "0":
                parser.disableUSSSensors(outfile)

        parser.set_status_in_file("1")  # Set value "1" means files are copied
    except PermissionError as e:
        parser.set_status_in_file("2")  # Set value "2" means error permission denied
        print(f"Permission denied --> {e}")
        raise e
    except Exception as e:
        parser.set_status_in_file("3")  # Set value "3" means any other error
        print(f"Failed to copy CarMaker folder --> {e}")
        raise e
        
if __name__ == "__main__":
    main()