# -*- coding: utf-8 -*-
# @file Extract_CM_Maneuver_Steps.py
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
import time
import subprocess
import sys
import os
import shutil
import distutils.log
from distutils.dir_util import copy_tree
from pathlib import Path



def Read_CM_Scenario_File(CM_scenario_path,output_file_path):
    """
    

    Args:
      CM_scenario_path: 
      output_file_path: 

    Returns:

    """
    input_file="..\\..\\..\\..\\adas_sim\\CM_Projects\\CANoe_Test\\Data\\TestRun\\"+CM_scenario_path
    #print("!!!DEBUG!!! input_file = ",input_file)
    f1 = open("..\\..\\..\\..\\adas_sim\\CM_Projects\\CANoe_Test\\Data\\TestRun\\"+CM_scenario_path, "r")
    f2 = open(output_file_path, "w+")
    flag_output_to_file=0
    for el in f1:
        if el.find("DrivMan.")>=0:
            f2.write(el.replace("DrivMan.",""))
            flag_output_to_file = 1
        else:
            if el.find("	")>=0 and flag_output_to_file==1:
                f2.write(el)
    f1.close()
    f2.close()


############################################################################################################################################################################################################
##  M A I N  ###############################################################################################################################################################################################
############################################################################################################################################################################################################
def main_sequence():
    """ """
    scenario_name = "ACC_CountryRoad_Test"
    if (len(sys.argv) > 1):
        scenario_name = sys.argv[1]
        print("argument 1 (scenario_name) = ", scenario_name)
    #Read_CM_Scenario_File(scenario_name,scenario_name+f".steps")
    output_file="..\\Record_Screen_Capture_Video\\"+scenario_name.replace("\\","_")+f".CarMaker.Man.Steps"
    Read_CM_Scenario_File(scenario_name,  output_file)
if __name__ == "__main__":

    main_sequence()
